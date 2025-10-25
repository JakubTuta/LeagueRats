import os

_CACHED_HEADERS = {
    "X-Riot-Token": os.getenv("RIOT_API_KEY", ""),
}


def get_headers() -> dict[str, str]:
    return _CACHED_HEADERS
