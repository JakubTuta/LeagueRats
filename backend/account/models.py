import typing

import pydantic


class Account(pydantic.BaseModel):
    gameName: str
    tagLine: str
    puuid: str
    region: str
    accountId: str
    id: str
    profileIconId: int
    summonerLevel: int
