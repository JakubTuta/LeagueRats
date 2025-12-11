from enum import Enum

__all__ = [
    "Region",
    "REGIONS",
    "PLATFORM_REGIONS",
    "REGION_TO_PLATFORM",
    "REGION_TO_CONTINENT",
]


class Region(str, Enum):
    EUW = "euw"
    EUNE = "eune"
    NA = "na"
    KR = "kr"
    BR = "br"
    JP = "jp"
    LAN = "lan"
    LAS = "las"
    OCE = "oce"
    PH = "ph"
    RU = "ru"
    SG = "sg"
    TH = "th"
    TR = "tr"
    TW = "tw"
    VN = "vn"
    ME = "me"


REGIONS = [
    "euw",
    "eune",
    "na",
    "kr",
    "br",
    "jp",
    "lan",
    "las",
    "oce",
    "ph",
    "ru",
    "sg",
    "th",
    "tr",
    "tw",
    "vn",
    "me",
]

PLATFORM_REGIONS = [
    "euw1",
    "eun1",
    "na1",
    "kr",
    "br1",
    "jp1",
    "la1",
    "la2",
    "oc1",
    "ph2",
    "ru",
    "sg2",
    "th2",
    "tr1",
    "tw2",
    "vn2",
    "me1",
]

REGION_TO_PLATFORM = {
    "euw": "euw1",
    "eune": "eun1",
    "na": "na1",
    "kr": "kr",
    "br": "br1",
    "jp": "jp1",
    "lan": "la1",
    "las": "la2",
    "oce": "oc1",
    "ph": "ph2",
    "ru": "ru",
    "sg": "sg2",
    "th": "th2",
    "tr": "tr1",
    "tw": "tw2",
    "vn": "vn2",
    "me": "me1",
}

REGION_TO_CONTINENT = {
    "euw": "europe",
    "euw1": "europe",
    "eune": "europe",
    "eun1": "europe",
    "na": "americas",
    "na1": "americas",
    "kr": "asia",
    "br": "americas",
    "br1": "americas",
    "jp": "asia",
    "jp1": "asia",
    "lan": "americas",
    "la1": "americas",
    "las": "americas",
    "la2": "americas",
    "oce": "asia",
    "oc1": "asia",
    "ph": "asia",
    "ph2": "asia",
    "ru": "europe",
    "sg": "asia",
    "sg2": "asia",
    "th": "asia",
    "th2": "asia",
    "tr": "europe",
    "tr1": "europe",
    "tw": "asia",
    "tw2": "asia",
    "vn": "asia",
    "vn2": "asia",
    "me": "europe",
    "me1": "europe",
}
