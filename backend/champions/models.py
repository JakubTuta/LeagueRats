import typing

import pro_players.models as pro_players_models
import pydantic
from match import models as match_models


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
