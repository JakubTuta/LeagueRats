import typing

import pydantic


class ProPlayer(pydantic.BaseModel):
    player: str
    puuid: list[str]
    region: typing.Literal["LCK", "LEC", "LCS", "LPL"]
    role: typing.Literal["TOP", "JNG", "MID", "ADC", "SUP"]
    team: str
    socialMedia: typing.Optional[typing.Dict[str, str]] = None


class ChampionStats(pydantic.BaseModel):
    kills: int
    deaths: int
    assists: int
    wins: int
    losses: int
