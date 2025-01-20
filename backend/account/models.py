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


class LeaderboardAccount(pydantic.BaseModel):
    gameName: str
    tagLine: str
    puuid: str
    rank: int
    wins: int
    losses: int
    leaguePoints: int
    league: str
