import typing

import pydantic


class RuneData(pydantic.BaseModel):
    id: int
    key: str
    icon: str
    name: str
    shortDesc: str
    longDesc: str


class Rune(pydantic.BaseModel):
    id: int
    key: str
    icon: str
    name: str
    slots: typing.List[typing.Dict[str, typing.List[RuneData]]]
