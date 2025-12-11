import json
import logging
import os
import typing

import redis.asyncio as redis
import structlog
import tenacity

logger = structlog.get_logger(__name__)

_redis_client: typing.Optional["RedisClient"] = None


class RedisClient:

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: typing.Optional[str] = None,
        decode_responses: bool = True,
    ):
        self._client = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=decode_responses,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30,
        )
        logger.info(
            "redis_client_initialized",
            host=host,
            port=port,
            db=db,
        )

    @tenacity.retry(
        retry=tenacity.retry_if_exception_type(
            (redis.ConnectionError, redis.TimeoutError)
        ),
        stop=tenacity.stop_after_attempt(3),
        wait=tenacity.wait_exponential(multiplier=1, min=1, max=5),
        before_sleep=tenacity.before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    async def get(self, key: str) -> typing.Optional[str]:
        try:
            value = await self._client.get(key)
            if value is not None:
                logger.debug("cache_hit", key=key)
            else:
                logger.debug("cache_miss", key=key)
            return value
        except Exception as e:
            logger.error("redis_get_error", key=key, error=str(e))
            raise

    @tenacity.retry(
        retry=tenacity.retry_if_exception_type(
            (redis.ConnectionError, redis.TimeoutError)
        ),
        stop=tenacity.stop_after_attempt(3),
        wait=tenacity.wait_exponential(multiplier=1, min=1, max=5),
        before_sleep=tenacity.before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    async def set(
        self,
        key: str,
        value: str,
        ex: typing.Optional[int] = None,
        px: typing.Optional[int] = None,
        nx: bool = False,
        xx: bool = False,
    ) -> bool:
        try:
            result = await self._client.set(key, value, ex=ex, px=px, nx=nx, xx=xx)
            logger.debug("cache_set", key=key, ttl=ex or px)
            return bool(result)
        except Exception as e:
            logger.error("redis_set_error", key=key, error=str(e))
            raise

    @tenacity.retry(
        retry=tenacity.retry_if_exception_type(
            (redis.ConnectionError, redis.TimeoutError)
        ),
        stop=tenacity.stop_after_attempt(3),
        wait=tenacity.wait_exponential(multiplier=1, min=1, max=5),
        before_sleep=tenacity.before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    async def delete(self, *keys: str) -> int:
        try:
            count = await self._client.delete(*keys)
            logger.debug("cache_delete", keys=keys, count=count)
            return count
        except Exception as e:
            logger.error("redis_delete_error", keys=keys, error=str(e))
            raise

    @tenacity.retry(
        retry=tenacity.retry_if_exception_type(
            (redis.ConnectionError, redis.TimeoutError)
        ),
        stop=tenacity.stop_after_attempt(3),
        wait=tenacity.wait_exponential(multiplier=1, min=1, max=5),
        before_sleep=tenacity.before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    async def exists(self, *keys: str) -> int:
        try:
            count = await self._client.exists(*keys)
            return count
        except Exception as e:
            logger.error("redis_exists_error", keys=keys, error=str(e))
            raise

    @tenacity.retry(
        retry=tenacity.retry_if_exception_type(
            (redis.ConnectionError, redis.TimeoutError)
        ),
        stop=tenacity.stop_after_attempt(3),
        wait=tenacity.wait_exponential(multiplier=1, min=1, max=5),
        before_sleep=tenacity.before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    async def expire(self, key: str, seconds: int) -> bool:
        try:
            result = await self._client.expire(key, seconds)
            logger.debug("cache_expire_set", key=key, seconds=seconds)
            return bool(result)
        except Exception as e:
            logger.error("redis_expire_error", key=key, error=str(e))
            raise

    @tenacity.retry(
        retry=tenacity.retry_if_exception_type(
            (redis.ConnectionError, redis.TimeoutError)
        ),
        stop=tenacity.stop_after_attempt(3),
        wait=tenacity.wait_exponential(multiplier=1, min=1, max=5),
        before_sleep=tenacity.before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    async def ttl(self, key: str) -> int:
        try:
            return await self._client.ttl(key)
        except Exception as e:
            logger.error("redis_ttl_error", key=key, error=str(e))
            raise

    async def get_json(self, key: str) -> typing.Optional[typing.Any]:
        value = await self.get(key)
        if value is None:
            return None
        try:
            return json.loads(value)
        except json.JSONDecodeError as e:
            logger.error("json_decode_error", key=key, error=str(e))
            return None

    async def set_json(
        self,
        key: str,
        value: typing.Any,
        ex: typing.Optional[int] = None,
        px: typing.Optional[int] = None,
        nx: bool = False,
        xx: bool = False,
    ) -> bool:
        try:
            json_value = json.dumps(value)
            return await self.set(key, json_value, ex=ex, px=px, nx=nx, xx=xx)
        except (TypeError, ValueError) as e:
            logger.error("json_encode_error", key=key, error=str(e))
            raise

    async def get_value(
        self, key: str
    ) -> typing.Optional[typing.Union[str, dict, list]]:
        value = await self.get(key)
        if value is None:
            return None

        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value

    async def set_value(
        self,
        key: str,
        value: typing.Union[str, dict, list, int, float, bool],
        ex: typing.Optional[int] = None,
        px: typing.Optional[int] = None,
        nx: bool = False,
        xx: bool = False,
    ) -> bool:
        if isinstance(value, str):
            return await self.set(key, value, ex=ex, px=px, nx=nx, xx=xx)
        else:
            try:
                json_value = json.dumps(value)
                return await self.set(key, json_value, ex=ex, px=px, nx=nx, xx=xx)
            except (TypeError, ValueError) as e:
                logger.error(
                    "value_encode_error",
                    key=key,
                    value_type=type(value).__name__,
                    error=str(e),
                )
                raise

    async def get_many_json(self, *keys: str) -> list[typing.Optional[typing.Any]]:
        values = await self.get_many(*keys)
        results = []
        for idx, value in enumerate(values):
            if value is None:
                results.append(None)
            else:
                try:
                    results.append(json.loads(value))
                except json.JSONDecodeError as e:
                    logger.error(
                        "json_decode_error_in_batch", key=keys[idx], error=str(e)
                    )
                    results.append(None)
        return results

    async def set_many_json(
        self,
        mapping: dict[str, typing.Any],
        ex: typing.Optional[int] = None,
        px: typing.Optional[int] = None,
    ) -> bool:
        try:
            json_mapping = {k: json.dumps(v) for k, v in mapping.items()}
            return await self.set_many(json_mapping, ex=ex, px=px)
        except (TypeError, ValueError) as e:
            logger.error("json_encode_error_in_batch", error=str(e))
            raise

    async def increment(self, key: str, amount: int = 1) -> int:
        try:
            result = await self._client.incrby(key, amount)
            return result
        except Exception as e:
            logger.error("redis_increment_error", key=key, error=str(e))
            raise

    async def decrement(self, key: str, amount: int = 1) -> int:
        try:
            result = await self._client.decrby(key, amount)
            return result
        except Exception as e:
            logger.error("redis_decrement_error", key=key, error=str(e))
            raise

    async def get_many(self, *keys: str) -> list[typing.Optional[str]]:
        try:
            values = await self._client.mget(*keys)
            logger.debug("cache_get_many", keys=keys, found=sum(1 for v in values if v))
            return values
        except Exception as e:
            logger.error("redis_get_many_error", keys=keys, error=str(e))
            raise

    async def set_many(
        self,
        mapping: dict[str, str],
        ex: typing.Optional[int] = None,
        px: typing.Optional[int] = None,
    ) -> bool:
        try:
            for key, value in mapping.items():
                await self.set(key, value, ex=ex, px=px)
            logger.debug("cache_set_many", count=len(mapping), ttl=ex or px)
            return True
        except Exception as e:
            logger.error("redis_set_many_error", error=str(e))
            raise

    async def flush_db(self) -> bool:
        try:
            result = await self._client.flushdb()
            logger.warning("cache_flushed")
            return bool(result)
        except Exception as e:
            logger.error("redis_flush_error", error=str(e))
            raise

    async def ping(self) -> bool:
        try:
            result = (
                await self._client.ping()  # pyright: ignore[reportGeneralTypeIssues]
            )
            return bool(result)
        except Exception as e:
            logger.error("redis_ping_error", error=str(e))
            return False

    async def close(self) -> None:
        try:
            await self._client.aclose()
            logger.info("redis_client_closed")
        except Exception as e:
            logger.error("redis_close_error", error=str(e))


def get_redis_client() -> RedisClient:
    global _redis_client

    if _redis_client is None:
        _redis_client = RedisClient(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            db=int(os.getenv("REDIS_DB", "0")),
            password=os.getenv("REDIS_PASSWORD"),
        )

    return _redis_client


async def close_redis_client() -> None:
    global _redis_client

    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None
