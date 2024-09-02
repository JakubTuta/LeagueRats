import dataclasses
import inspect
import typing


@dataclasses.dataclass(kw_only=True, frozen=True, order=False)
class Metadata:
    matchId: str = ""
    participants: typing.List[str] = dataclasses.field(default_factory=list)

    def to_dict(self):
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(
            **{
                key: value
                for key, value in data.items()
                if key in inspect.signature(cls).parameters
            }
        )


@dataclasses.dataclass(kw_only=True, frozen=True, order=False)
class Perks:
    statPerks: typing.Dict[str, int] = dataclasses.field(
        default_factory=lambda: {
            "defense": 0,
            "flex": 0,
            "offense": 0,
        }
    )
    styles: typing.List[typing.Dict[str, object]] = dataclasses.field(
        default_factory=list
    )

    def to_dict(self):
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(
            **{
                key: value
                for key, value in data.items()
                if key in inspect.signature(cls).parameters
            }
        )


@dataclasses.dataclass(kw_only=True, frozen=True, order=False)
class Participant:
    kills: int = 0
    assists: int = 0
    deaths: int = 0
    champLevel: int = 0
    championId: int = 0
    championName: str = ""
    goldEarned: int = 0
    damageDealtToBuildings: int = 0
    item0: int = 0
    item1: int = 0
    item2: int = 0
    item3: int = 0
    item4: int = 0
    item5: int = 0
    item6: int = 0
    physicalDamageDealtToChampions: int = 0
    physicalDamageTaken: int = 0
    magicDamageDealtToChampions: int = 0
    magicDamageTaken: int = 0
    trueDamageDealtToChampions: int = 0
    trueDamageTaken: int = 0
    neutralMinionsKilled: int = 0
    totalMinionsKilled: int = 0
    participantId: int = 0
    perks: Perks
    puuid: str = ""
    riotIdGameName: str = ""
    riotIdTagline: str = ""
    summoner1Id: int = 0
    summoner2Id: int = 0
    summonerId: str = ""
    summonerName: str = ""
    teamId: int = 0
    teamPosition: str = ""  # TOP | JUNGLE | MIDDLE | BOTTOM | UTILITY
    totalHealsOnTeammates: int = 0
    visionScore: int = 0
    win: bool = False
    gameEndedInEarlySurrender: bool = False
    doubleKills: int = 0
    tripleKills: int = 0
    quadraKills: int = 0
    pentaKills: int = 0

    def to_dict(self):
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(
            **{
                key: value
                for key, value in data.items()
                if key in inspect.signature(cls).parameters
            }
        )


@dataclasses.dataclass(kw_only=True, frozen=True, order=False)
class Team:
    bans: typing.List[typing.Dict[str, int]] = dataclasses.field(default_factory=list)
    objectives: typing.Dict[str, dict] = dataclasses.field(
        default_factory=lambda: {
            "baron": {
                "kills": 0,
                "first": False,
            },
            "champion": {
                "kills": 0,
                "first": False,
            },
            "dragon": {
                "kills": 0,
                "first": False,
            },
            "tower": {
                "kills": 0,
                "first": False,
            },
        }
    )
    teamId: int = 0
    win: bool = False

    def to_dict(self):
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(
            **{
                key: value
                for key, value in data.items()
                if key in inspect.signature(cls).parameters
            }
        )


@dataclasses.dataclass(kw_only=True, frozen=True, order=False)
class GameInfo:
    gameDuration: int = 0
    gameMode: str = ""
    gameStartTimestamp: int = 0
    gameType: str = ""
    gameVersion: str = ""
    mapId: int = 0
    participants: typing.List[Participant] = dataclasses.field(default_factory=list)
    platformId: str = ""
    queueId: int = 0
    teams: typing.List[Team] = dataclasses.field(default_factory=list)

    def to_dict(self):
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, data):
        participants = data.pop("participants", [])
        teams = data.pop("teams", [])
        game_version = data.pop("gameVersion", "")

        return cls(
            **{
                key: value
                for key, value in data.items()
                if key in inspect.signature(cls).parameters
            },
            gameVersion=".".join(game_version.split(".")[:2]),
            participants=[
                Participant.from_dict(participant) for participant in participants
            ],
            teams=[Team.from_dict(team) for team in teams]
        )


@dataclasses.dataclass(kw_only=True, frozen=True, order=False)
class MatchData:
    metadata: Metadata
    info: GameInfo

    def to_dict(self):
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(
            metadata=Metadata.from_dict(data.get("metadata", {})),
            info=GameInfo.from_dict(data.get("info", {})),
        )
