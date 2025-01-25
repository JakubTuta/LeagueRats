import pydantic


class LeagueEntry(pydantic.BaseModel):
    leagueId: str
    summonerId: str
    queueType: str
    tier: str
    rank: str
    leaguePoints: int
    wins: int
    losses: int
    hotStreak: bool
    veteran: bool
    freshBlood: bool
    inactive: bool


class LeaderboardEntry(pydantic.BaseModel):
    gameName: str
    tagLine: str
    puuid: str
    rank: int
    leaguePoints: int
    wins: int
    losses: int
    league: str
