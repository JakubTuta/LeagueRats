import datetime
import typing
from re import S

import pydantic


class BannedChampion(pydantic.BaseModel):
    pickTurn: int
    championId: int
    teamId: int


class Perks(pydantic.BaseModel):
    perkIds: typing.List[int]
    perkStyle: int
    perkSubStyle: int


class Participant(pydantic.BaseModel):
    championId: int
    perks: Perks
    teamId: int
    summonerId: str
    riotId: str
    gameName: str = ""
    tagLine: str = ""
    puuid: str
    spell1Id: int
    spell2Id: int

    @pydantic.model_validator(mode="before")
    def split_riot_id(cls, values):
        riot_id = values.get("riotId")

        if riot_id and "#" in riot_id:
            game_name, tag_line = riot_id.split("#", 1)
            values["gameName"] = game_name
            values["tagLine"] = tag_line

        return values


class ActiveMatch(pydantic.BaseModel):
    gameId: int
    gameType: str
    gameStartTime: datetime.datetime
    mapId: int
    gameLength: int
    gameMode: str
    bannedChampions: typing.List[BannedChampion]
    participants: typing.List[Participant]
    platformId: str
    gameQueueConfigId: typing.Literal["NORMAL", "SOLOQ", "FLEXQ"]

    @pydantic.field_validator("gameStartTime", mode="before")
    def parse_game_start_time(cls, value) -> datetime.datetime:
        if isinstance(value, int):
            return datetime.datetime.fromtimestamp(value / 1000)

        elif isinstance(value, str):
            return datetime.datetime.fromisoformat(value)

        return value

    @pydantic.field_validator("gameQueueConfigId", mode="before")
    def validate_game_queue_config_id(
        cls, value
    ) -> typing.Literal["NORMAL", "SOLOQ", "FLEXQ"]:
        match (value):
            case 420:
                return "SOLOQ"
            case 440:
                return "FLEXQ"
            case _:
                return "NORMAL"


class MatchMetadata(pydantic.BaseModel):
    matchId: str
    participants: typing.List[str]


class StatPerks(pydantic.BaseModel):
    defense: int
    flex: int
    offense: int


class PerkSelection(pydantic.BaseModel):
    perk: int
    var1: int
    var2: int
    var3: int


class PerkStyle(pydantic.BaseModel):
    description: str
    selections: typing.List[PerkSelection]
    style: int


class MatchHistoryPerks(pydantic.BaseModel):
    statPerks: StatPerks
    styles: typing.List[PerkStyle]


class ParticipantStats(pydantic.BaseModel):
    kills: int
    assists: int
    deaths: int
    champLevel: int
    championId: int
    championName: str
    goldEarned: int
    damageDealtToBuildings: int
    item0: int
    item1: int
    item2: int
    item3: int
    item4: int
    item5: int
    item6: int
    physicalDamageDealtToChampions: int
    physicalDamageTaken: int
    magicDamageDealtToChampions: int
    magicDamageTaken: int
    trueDamageDealtToChampions: int
    trueDamageTaken: int
    neutralMinionsKilled: int
    totalMinionsKilled: int
    participantId: int
    perks: MatchHistoryPerks
    puuid: str
    riotIdGameName: str
    riotIdTagline: str
    summoner1Id: int
    summoner2Id: int
    summonerId: str
    summonerName: str
    teamId: int
    teamPosition: typing.Literal["TOP", "JUNGLE", "MIDDLE", "BOTTOM", "UTILITY", ""]
    totalHealsOnTeammates: int
    visionScore: int
    win: bool
    gameEndedInEarlySurrender: bool
    doubleKills: int
    tripleKills: int
    quadraKills: int
    pentaKills: int


class Ban(pydantic.BaseModel):
    championId: int
    pickTurn: int


class Objective(pydantic.BaseModel):
    first: bool
    kills: int


class Objectives(pydantic.BaseModel):
    baron: Objective
    champion: Objective
    dragon: Objective
    tower: Objective


class Team(pydantic.BaseModel):
    bans: typing.List[Ban]
    objectives: Objectives
    teamId: int
    win: bool


class MatchInfo(pydantic.BaseModel):
    gameDuration: int
    gameMode: str
    gameStartTimestamp: datetime.datetime
    gameType: str
    gameVersion: str
    mapId: int
    participants: typing.List[ParticipantStats]
    platformId: str
    queueId: int
    teams: typing.List[Team]

    @pydantic.field_validator("gameStartTimestamp", mode="before")
    def parse_game_start_timestamp(cls, value) -> datetime.datetime:
        if isinstance(value, int):
            return datetime.datetime.fromtimestamp(value / 1000)

        elif isinstance(value, str):
            return datetime.datetime.fromisoformat(value)

        return value


class MatchHistory(pydantic.BaseModel):
    metadata: MatchMetadata
    info: MatchInfo
