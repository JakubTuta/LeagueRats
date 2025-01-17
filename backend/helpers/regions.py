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


def get_region(region: str) -> typing.Optional[typing.Tuple[str, str, str]]:
    for region_row in regions:
        if region in region_row:
            return region_row
