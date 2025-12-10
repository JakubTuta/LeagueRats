import asyncio
import logging
import os
import typing

import httpx
import pybreaker
import structlog
import tenacity

logger = structlog.get_logger(__name__)

_riot_api_client: typing.Optional["RiotAPIClient"] = None


class RateLimitError(Exception):
    pass


class RiotAPIError(Exception):
    def __init__(
        self,
        message: str,
        status_code: int,
        response_data: typing.Optional[dict] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(self.message)


class AsyncRateLimiter:
    def __init__(self, rate: int, period: float):
        self.rate = rate
        self.period = period
        self.allowance = rate
        self.last_check = asyncio.get_event_loop().time()
        self._lock = asyncio.Lock()

    async def acquire(self):
        async with self._lock:
            current = asyncio.get_event_loop().time()
            time_passed = current - self.last_check
            self.last_check = current
            self.allowance += time_passed * (self.rate / self.period)

            if self.allowance > self.rate:
                self.allowance = self.rate

            if self.allowance < 1.0:
                sleep_time = (1.0 - self.allowance) * (self.period / self.rate)
                logger.warning(
                    "rate_limit_waiting",
                    sleep_time=sleep_time,
                    rate=self.rate,
                    period=self.period,
                )
                await asyncio.sleep(sleep_time)
                self.allowance = 0.0
            else:
                self.allowance -= 1.0


class RiotAPIClient:
    BASE_URLS = {
        "br1": "https://br1.api.riotgames.com",
        "eun1": "https://eun1.api.riotgames.com",
        "euw1": "https://euw1.api.riotgames.com",
        "jp1": "https://jp1.api.riotgames.com",
        "kr": "https://kr.api.riotgames.com",
        "la1": "https://la1.api.riotgames.com",
        "la2": "https://la2.api.riotgames.com",
        "na1": "https://na1.api.riotgames.com",
        "oc1": "https://oc1.api.riotgames.com",
        "tr1": "https://tr1.api.riotgames.com",
        "ru": "https://ru.api.riotgames.com",
        "ph2": "https://ph2.api.riotgames.com",
        "sg2": "https://sg2.api.riotgames.com",
        "th2": "https://th2.api.riotgames.com",
        "tw2": "https://tw2.api.riotgames.com",
        "vn2": "https://vn2.api.riotgames.com",
        "americas": "https://americas.api.riotgames.com",
        "asia": "https://asia.api.riotgames.com",
        "europe": "https://europe.api.riotgames.com",
        "sea": "https://sea.api.riotgames.com",
    }

    def __init__(
        self, http_client: httpx.AsyncClient, api_key: typing.Optional[str] = None
    ):
        self._http_client = http_client
        self._api_key = api_key or os.getenv("RIOT_API_KEY", "")

        if not self._api_key:
            logger.error("riot_api_key_missing")
            raise ValueError("RIOT_API_KEY environment variable is not set")

        self._rate_limiter_per_second = AsyncRateLimiter(rate=20, period=1.0)
        self._rate_limiter_per_two_minutes = AsyncRateLimiter(rate=100, period=120.0)

        self._circuit_breaker = pybreaker.CircuitBreaker(
            fail_max=5,
            reset_timeout=60,
            name="riot_api_circuit_breaker",
        )

        logger.info("riot_api_client_initialized")

    def _get_headers(self) -> dict[str, str]:
        return {
            "X-Riot-Token": self._api_key,
            "Accept": "application/json",
        }

    async def _apply_rate_limiting(self):
        await self._rate_limiter_per_second.acquire()
        await self._rate_limiter_per_two_minutes.acquire()

    @tenacity.retry(
        retry=tenacity.retry_if_exception_type(
            (httpx.TimeoutException, httpx.NetworkError)
        ),
        stop=tenacity.stop_after_attempt(3),
        wait=tenacity.wait_exponential(multiplier=1, min=1, max=10),
        before_sleep=tenacity.before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    async def _make_request(
        self,
        method: str,
        url: str,
        **kwargs,
    ) -> httpx.Response:
        try:
            await self._apply_rate_limiting()

            response = await self._circuit_breaker.call_async(
                self._http_client.request,
                method,
                url,
                headers=self._get_headers(),
                **kwargs,
            )  # pyright: ignore[reportGeneralTypeIssues]

            return response

        except pybreaker.CircuitBreakerError:
            logger.error("circuit_breaker_open", url=url)
            raise RiotAPIError("Circuit breaker is open", 503)
        except httpx.TimeoutException as e:
            logger.error("request_timeout", url=url, error=str(e))
            raise
        except httpx.NetworkError as e:
            logger.error("network_error", url=url, error=str(e))
            raise

    async def _handle_response(
        self, response: httpx.Response, url: str
    ) -> dict[str, typing.Any]:
        if response.status_code == 200:
            try:
                data = response.json()
                logger.debug("request_success", url=url, status=200)
                return data
            except Exception as e:
                logger.error("json_decode_error", url=url, error=str(e))
                raise RiotAPIError(
                    f"Failed to decode JSON: {str(e)}", response.status_code
                )

        elif response.status_code == 404:
            logger.info("resource_not_found", url=url)
            raise RiotAPIError("Resource not found", 404)

        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After", "60")
            logger.warning("rate_limited_by_api", url=url, retry_after=retry_after)
            raise RateLimitError(f"Rate limited. Retry after {retry_after} seconds")

        elif response.status_code == 403:
            logger.error("forbidden_invalid_api_key", url=url)
            raise RiotAPIError("Invalid or expired API key", 403)

        elif response.status_code >= 500:
            logger.error("server_error", url=url, status=response.status_code)
            raise RiotAPIError(f"Riot API server error", response.status_code)

        else:
            logger.error("unexpected_status", url=url, status=response.status_code)
            raise RiotAPIError(
                f"Unexpected status code: {response.status_code}",
                response.status_code,
            )

    async def get(
        self, region: str, endpoint: str, **params
    ) -> typing.Optional[dict[str, typing.Any] | list[typing.Any]]:
        if region not in self.BASE_URLS:
            logger.error("invalid_region", region=region)
            raise ValueError(f"Invalid region: {region}")

        base_url = self.BASE_URLS[region]
        url = f"{base_url}{endpoint}"

        try:
            response = await self._make_request("GET", url, params=params)
            return await self._handle_response(response, url)

        except RateLimitError as e:
            logger.warning("rate_limit_error", url=url, error=str(e))
            return None

        except RiotAPIError as e:
            if e.status_code == 404:
                return None
            raise

        except Exception as e:
            logger.exception("unexpected_error", url=url, error=str(e))
            return None


def get_riot_api_client() -> RiotAPIClient:
    global _riot_api_client
    if _riot_api_client is None:
        httpx_client = httpx.AsyncClient(timeout=10.0)
        _riot_api_client = RiotAPIClient(httpx_client)
    return _riot_api_client


async def close_riot_api_client() -> None:
    global _riot_api_client
    if _riot_api_client is not None:
        await _riot_api_client._http_client.aclose()
        _riot_api_client = None
