import typing

import pydantic
from modules.match import models as match_models
from modules.pro_players import models as pro_players_models


class ChampionName(pydantic.BaseModel):
    title: str = ""
    value: str = ""


class ChampionStats(pydantic.BaseModel):
    games: int = 0
    wins: int = 0
    losses: int = 0


class ChampionMastery(pydantic.BaseModel):
    championId: int = 0
    championLevel: int = 0
    championPoints: int = 0


class ChampionHistory(pydantic.BaseModel):
    player: pro_players_models.ProPlayer
    match: match_models.MatchHistory
    enemy: typing.Optional[int] = None
    lane: typing.Optional[
        typing.Literal["TOP", "JUNGLE", "MIDDLE", "BOTTOM", "UTILITY"]
    ] = None
