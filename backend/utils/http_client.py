import logging
import typing

import httpx
import structlog
import tenacity

logger = structlog.get_logger(__name__)

_http_client: typing.Optional["HTTPClient"] = None


class HTTPError(Exception):
    def __init__(
        self,
        message: str,
        status_code: int,
        url: str,
        response_data: typing.Optional[typing.Any] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.url = url
        self.response_data = response_data
        super().__init__(self.message)


class HTTPClient:
    def __init__(
        self,
        client: httpx.AsyncClient,
        default_timeout: float = 10.0,
        max_retries: int = 3,
    ):
        self._client = client
        self._default_timeout = default_timeout
        self._max_retries = max_retries

        logger.info(
            "http_client_initialized",
            timeout=default_timeout,
            max_retries=max_retries,
        )

    @tenacity.retry(
        retry=tenacity.retry_if_exception_type(
            (httpx.TimeoutException, httpx.NetworkError)
        ),
        stop=tenacity.stop_after_attempt(3),
        wait=tenacity.wait_exponential(multiplier=1, min=1, max=10),
        before_sleep=tenacity.before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    async def _request(
        self,
        method: str,
        url: str,
        headers: typing.Optional[dict[str, str]] = None,
        params: typing.Optional[dict[str, typing.Any]] = None,
        json: typing.Optional[typing.Any] = None,
        data: typing.Optional[typing.Any] = None,
        timeout: typing.Optional[float] = None,
        follow_redirects: bool = True,
    ) -> httpx.Response:
        try:
            response = await self._client.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json,
                data=data,
                timeout=timeout or self._default_timeout,
                follow_redirects=follow_redirects,
            )

            logger.debug(
                "http_request_completed",
                method=method,
                url=url,
                status=response.status_code,
            )

            return response

        except httpx.TimeoutException as e:
            logger.error("http_timeout", method=method, url=url, error=str(e))
            raise
        except httpx.NetworkError as e:
            logger.error("http_network_error", method=method, url=url, error=str(e))
            raise
        except Exception as e:
            logger.exception(
                "http_unexpected_error", method=method, url=url, error=str(e)
            )
            raise

    async def get(
        self,
        url: str,
        headers: typing.Optional[dict[str, str]] = None,
        params: typing.Optional[dict[str, typing.Any]] = None,
        timeout: typing.Optional[float] = None,
        raise_for_status: bool = True,
    ) -> httpx.Response:
        response = await self._request(
            method="GET",
            url=url,
            headers=headers,
            params=params,
            timeout=timeout,
        )

        if raise_for_status:
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                logger.error(
                    "http_status_error",
                    url=url,
                    status=e.response.status_code,
                    error=str(e),
                )
                raise HTTPError(
                    message=f"HTTP {e.response.status_code} error",
                    status_code=e.response.status_code,
                    url=url,
                )

        return response

    async def post(
        self,
        url: str,
        json: typing.Optional[typing.Any] = None,
        data: typing.Optional[typing.Any] = None,
        headers: typing.Optional[dict[str, str]] = None,
        timeout: typing.Optional[float] = None,
        raise_for_status: bool = True,
    ) -> httpx.Response:
        response = await self._request(
            method="POST",
            url=url,
            headers=headers,
            json=json,
            data=data,
            timeout=timeout,
        )

        if raise_for_status:
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                logger.error(
                    "http_status_error",
                    url=url,
                    status=e.response.status_code,
                    error=str(e),
                )
                raise HTTPError(
                    message=f"HTTP {e.response.status_code} error",
                    status_code=e.response.status_code,
                    url=url,
                )

        return response

    async def put(
        self,
        url: str,
        json: typing.Optional[typing.Any] = None,
        data: typing.Optional[typing.Any] = None,
        headers: typing.Optional[dict[str, str]] = None,
        timeout: typing.Optional[float] = None,
        raise_for_status: bool = True,
    ) -> httpx.Response:
        response = await self._request(
            method="PUT",
            url=url,
            headers=headers,
            json=json,
            data=data,
            timeout=timeout,
        )

        if raise_for_status:
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                logger.error(
                    "http_status_error",
                    url=url,
                    status=e.response.status_code,
                    error=str(e),
                )
                raise HTTPError(
                    message=f"HTTP {e.response.status_code} error",
                    status_code=e.response.status_code,
                    url=url,
                )

        return response

    async def delete(
        self,
        url: str,
        headers: typing.Optional[dict[str, str]] = None,
        timeout: typing.Optional[float] = None,
        raise_for_status: bool = True,
    ) -> httpx.Response:
        response = await self._request(
            method="DELETE",
            url=url,
            headers=headers,
            timeout=timeout,
        )

        if raise_for_status:
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                logger.error(
                    "http_status_error",
                    url=url,
                    status=e.response.status_code,
                    error=str(e),
                )
                raise HTTPError(
                    message=f"HTTP {e.response.status_code} error",
                    status_code=e.response.status_code,
                    url=url,
                )

        return response

    async def get_json(
        self,
        url: str,
        headers: typing.Optional[dict[str, str]] = None,
        params: typing.Optional[dict[str, typing.Any]] = None,
        timeout: typing.Optional[float] = None,
    ) -> typing.Optional[typing.Any]:
        try:
            response = await self.get(
                url=url,
                headers=headers,
                params=params,
                timeout=timeout,
                raise_for_status=True,
            )

            return response.json()

        except HTTPError as e:
            if e.status_code == 404:
                logger.info("resource_not_found", url=url)
                return None
            raise
        except Exception as e:
            logger.error("json_decode_error", url=url, error=str(e))
            return None

    async def get_text(
        self,
        url: str,
        headers: typing.Optional[dict[str, str]] = None,
        params: typing.Optional[dict[str, typing.Any]] = None,
        timeout: typing.Optional[float] = None,
    ) -> typing.Optional[str]:
        try:
            response = await self.get(
                url=url,
                headers=headers,
                params=params,
                timeout=timeout,
                raise_for_status=True,
            )

            return response.text

        except HTTPError as e:
            if e.status_code == 404:
                logger.info("resource_not_found", url=url)
                return None
            raise
        except Exception as e:
            logger.error("text_decode_error", url=url, error=str(e))
            return None

    async def get_bytes(
        self,
        url: str,
        headers: typing.Optional[dict[str, str]] = None,
        params: typing.Optional[dict[str, typing.Any]] = None,
        timeout: typing.Optional[float] = None,
    ) -> typing.Optional[bytes]:
        try:
            response = await self.get(
                url=url,
                headers=headers,
                params=params,
                timeout=timeout,
                raise_for_status=True,
            )

            return response.content

        except HTTPError as e:
            if e.status_code == 404:
                logger.info("resource_not_found", url=url)
                return None
            raise
        except Exception as e:
            logger.error("bytes_read_error", url=url, error=str(e))
            return None

    async def post_json(
        self,
        url: str,
        json: typing.Any,
        headers: typing.Optional[dict[str, str]] = None,
        timeout: typing.Optional[float] = None,
    ) -> typing.Optional[typing.Any]:
        try:
            response = await self.post(
                url=url,
                json=json,
                headers=headers,
                timeout=timeout,
                raise_for_status=True,
            )

            return response.json()

        except HTTPError:
            raise
        except Exception as e:
            logger.error("json_decode_error", url=url, error=str(e))
            return None

    def get_raw_client(self) -> httpx.AsyncClient:
        return self._client


def get_http_client() -> HTTPClient:
    global _http_client

    if _http_client is None:
        client = httpx.AsyncClient(
            timeout=httpx.Timeout(10.0, connect=5.0),
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
            http2=True,
            follow_redirects=True,
        )
        _http_client = HTTPClient(client=client)

    return _http_client


async def close_http_client() -> None:
    global _http_client

    if _http_client is not None:
        await _http_client.get_raw_client().aclose()
        _http_client = None
