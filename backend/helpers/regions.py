import typing

regions = [
    ("EUW", "EUW1", "EUROPE"),
    ("EUNE", "EUN1", "EUROPE"),
    ("NA", "NA1", "AMERICAS"),
    ("KR", "KR", "ASIA"),
    ("BR", "BR1", "AMERICAS"),
    ("JP", "JP1", "ASIA"),
    ("LAN", "LA1", "AMERICAS"),
    ("LAS", "LA2", "AMERICAS"),
    ("OCE", "OC1", "ASIA"),
    ("PH", "PH2", "ASIA"),
    ("RU", "RU", "EUROPE"),
    ("SG", "SG2", "ASIA"),
    ("TH", "TH2", "ASIA"),
    ("TR", "TR1", "EUROPE"),
    ("TW", "TW2", "ASIA"),
    ("VN", "VN2", "ASIA"),
    ("ME", "ME1", "EUROPE"),
]

pro_regions = ["LCK", "LPL", "LEC", "LCS"]

teams_per_region = {
    "LCK": ["T1", "GENG", "DK", "DRX", "HLE", "KDF", "KT", "FOX", "BRO", "NS"],
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
    "LCS": ["TL", "C9", "FLY", "DIG", "100", "NRG", "SR", "IMT"],
    "LEC": ["FNC", "G2", "GX", "KC", "MAD", "RGE", "SK", "BDS", "TH", "VIT"],
}

important_regions = ["EUW", "NA", "KR"]


def get_region(region: str) -> typing.Optional[typing.Tuple[str, str, str]]:
    for region_row in regions:
        for region_col in region_row:
            if region_col.lower() == region.lower():
                return region_row


def get_region_column(index: int) -> typing.List[str]:
    return [region[index] for region in regions]
