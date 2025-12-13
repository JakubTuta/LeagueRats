from enum import Enum
import typing

__all__ = [
    "Region",
    "REGIONS",
    "PLATFORM_REGIONS",
    "REGION_TO_PLATFORM",
    "REGION_TO_CONTINENT",
    "PRO_REGIONS",
    "TEAMS_PER_REGION",
    "PRO_REGION_TO_GAME_REGION",
]


class Region(str, Enum):
    EUW = "EUW"
    EUNE = "EUNE"
    NA = "NA"
    KR = "KR"
    BR = "BR"
    JP = "JP"
    LAN = "LAN"
    LAS = "LAS"
    OCE = "OCE"
    PH = "PH"
    RU = "RU"
    SG = "SG"
    TH = "TH"
    TR = "TR"
    TW = "TW"
    VN = "VN"
    ME = "ME"

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            value_upper = value.upper()
            for member in cls:
                if member.value == value_upper:
                    return member
        return None


REGIONS = [
    "EUW",
    "EUNE",
    "NA",
    "KR",
    "BR",
    "JP",
    "LAN",
    "LAS",
    "OCE",
    "PH",
    "RU",
    "SG",
    "TH",
    "TR",
    "TW",
    "VN",
    "ME",
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
    "EUW": "europe",
    "euw1": "europe",
    "eune": "europe",
    "EUNE": "europe",
    "eun1": "europe",
    "na": "americas",
    "NA": "americas",
    "na1": "americas",
    "kr": "asia",
    "KR": "asia",
    "br": "americas",
    "BR": "americas",
    "br1": "americas",
    "jp": "asia",
    "JP": "asia",
    "jp1": "asia",
    "lan": "americas",
    "LAN": "americas",
    "la1": "americas",
    "las": "americas",
    "LAS": "americas",
    "la2": "americas",
    "oce": "asia",
    "OCE": "asia",
    "oc1": "asia",
    "ph": "asia",
    "PH": "asia",
    "ph2": "asia",
    "ru": "europe",
    "RU": "europe",
    "sg": "asia",
    "SG": "asia",
    "sg2": "asia",
    "th": "asia",
    "TH": "asia",
    "th2": "asia",
    "tr": "europe",
    "TR": "europe",
    "tr1": "europe",
    "tw": "asia",
    "TW": "asia",
    "tw2": "asia",
    "vn": "asia",
    "VN": "asia",
    "vn2": "asia",
    "me": "europe",
    "ME": "europe",
    "me1": "europe",
}

PRO_REGIONS = ["LCK", "LPL", "LEC", "LCS"]

TEAMS_PER_REGION: typing.Dict[
    typing.Literal["LEC", "LCS", "LCK", "LPL"], typing.List[str]
] = {
    "LCK": ["T1", "GENG", "DK", "DRX", "HLE", "DNF", "KT", "FOX", "BRO", "NS"],
    "LPL": [
        "AL",
        "BLG",
        "EDG",
        "FPX",
        "IG",
        "JDG",
        "LGD",
        "LNG",
        "NIP",
        "OMG",
        "RA",
        "RNG",
        "WE",
        "TES",
        "TT",
        "UP",
        "WBG",
    ],
    "LCS": ["TL", "C9", "FLY", "DIG", "100", "SR", "DSG", "LYN"],
    "LEC": ["FNC", "G2", "GX", "KC", "MKOI", "RGE", "SK", "BDS", "TH", "VIT"],
}

PRO_REGION_TO_GAME_REGION: typing.Dict[
    typing.Literal["LEC", "LCS", "LCK", "LPL"], str
] = {
    "LCK": "kr",
    "LPL": "kr",
    "LEC": "euw",
    "LCS": "na",
}
