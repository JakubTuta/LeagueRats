import typing

import pydantic


class ProPlayer(pydantic.BaseModel):
    player: str
    puuid: list[str]
    region: typing.Literal["LCK", "LEC", "LCS", "LPL"]
    role: typing.Literal["TOP", "JNG", "MID", "ADC", "SUP"]
    team: str
    socialMedia: typing.Optional[typing.Dict[str, str]] = None


class BootcampAccount(pydantic.BaseModel):
    # LeagueEntry
    leagueId: str
    queueType: str
    tier: str
    rank: str
    leaguePoints: int
    wins: int
    losses: int

    # ProPlayer
    player: str
    role: typing.Literal["TOP", "JNG", "MID", "ADC", "SUP"]
    team: str

    # Account
    gameName: str
    tagLine: str
    puuid: str
    region: str


class ChampionStats(pydantic.BaseModel):
    kills: int
    deaths: int
    assists: int
    wins: int
    losses: int
