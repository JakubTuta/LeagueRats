import pydantic


class ChampionMastery(pydantic.BaseModel):
    championId: int = 0
    championLevel: int = 0
    championPoints: int = 0
