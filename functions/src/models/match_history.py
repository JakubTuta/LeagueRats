import dataclasses
import inspect
import typing


@dataclasses.dataclass(kw_only=True, frozen=True, order=False)
class Metadata:
    matchId: str
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
    perks: Perks
    puuid: str
    riotIdGameName: str
    riotIdTagline: str
    summoner1Id: int
    summoner2Id: int
    summonerId: str
    summonerName: str
    teamId: int
    teamPosition: str  # TOP | JUNGLE | MIDDLE | BOTTOM | UTILITY
    totalHealsOnTeammates: int
    visionScore: int
    win: bool
    gameEndedInEarlySurrender: bool

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
    teamId: int
    win: bool

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
    gameDuration: int
    gameMode: str
    gameStartTimestamp: int
    gameType: str
    gameVersion: str
    mapId: int
    participants: typing.List[Participant] = dataclasses.field(default_factory=list)
    platformId: str
    queueId: int
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
