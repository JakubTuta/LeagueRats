import os


def get_headers() -> dict[str, str]:
    return {
        "X-Riot-Token": os.getenv("RIOT_API_KEY", ""),
    }
