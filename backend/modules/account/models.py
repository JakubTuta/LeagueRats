import pydantic


class Account(pydantic.BaseModel):
    gameName: str
    tagLine: str
    puuid: str
    region: str
