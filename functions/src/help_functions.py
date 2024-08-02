import requests
import src.firebase_init as firebase_init
from google.cloud.firestore_v1.base_query import FieldFilter

select_regions = [
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
]
api_regions_1 = {
    "EUW": "EUROPE",
    "EUNE": "EUROPE",
    "NA": "AMERICAS",
    "KR": "ASIA",
    "BR": "AMERICAS",
    "JP": "ASIA",
    "LAN": "AMERICAS",
    "LAS": "AMERICAS",
    "OCE": "ASIA",
    "PH": "ASIA",
    "RU": "EUROPE",
    "SG": "ASIA",
    "TH": "ASIA",
    "TR": "EUROPE",
    "TW": "ASIA",
    "VN": "ASIA",
}
api_regions_2 = {
    "EUW": "EUW1",
    "EUNE": "EUN1",
    "NA": "NA1",
    "KR": "KR",
    "BR": "BR1",
    "JP": "JP1",
    "LAN": "LA1",
    "LAS": "LA2",
    "OCE": "OC1",
    "PH": "PH2",
    "RU": "RU",
    "SG": "SG2",
    "TH": "TH2",
    "TR": "TR1",
    "TW": "TW2",
    "VN": "VN2",
}

Account = {
    "gameName": "",
    "tagLine": "",
    "puuid": "",
    "region": "",
    "accountId": "",
    "id": "",
}


def find_highest_playrate_role(champion_data, champion_key):
    roles = champion_data.get(champion_key, None)

    if not roles:
        return None

    highest_playrate_role = list(roles.keys())[0]
    highest_playrate = 0

    for role, stats in roles.items():
        play_rate = stats.get("playRate", 0)
        if play_rate > highest_playrate:
            highest_playrate = play_rate
            highest_playrate_role = role

    return highest_playrate_role


def get_existing_request_data(data, required_keys=[], optional_keys=[]):
    required_data = {}
    optional_data = {}

    for key in required_keys:
        if key not in data:
            raise Exception(f"Missing required key: {key}")

        required_data[key] = data[key]

    for key in optional_keys:
        if key in data:
            optional_data[key] = data[key]

    return required_data, optional_data


def find_accounts_in_database(game_name, tag):
    query = (
        firebase_init.collections["accounts"]
        .where(filter=FieldFilter("gameName", "==", game_name))
        .where(filter=FieldFilter("tagLine", "==", tag))
    )

    docs = [doc.to_dict() for doc in query.stream()]
    return docs


def find_account_in_region(game_name, tag, region):
    request_region = api_regions_1[region].lower()
    url = f"https://{request_region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag}"

    try:
        response = requests.get(
            url,
            headers={"X-Riot-Token": firebase_init.app.options.get("riot_api_key")},
        )

        return response.json()

    except:
        return None


def find_summoner_in_region(puuid, region):
    request_region = api_regions_2[region].lower()
    url = f"https://{request_region}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"

    try:
        response = requests.get(
            url,
            headers={"X-Riot-Token": firebase_init.app.options.get("riot_api_key")},
        )

        return response.json()

    except:
        return None


def find_accounts_in_api(game_name, tag, regions=[]):
    accounts = {}

    for region in regions:
        account = find_account_in_region(game_name, tag, region)

        if not account:
            continue

        summoner = find_summoner_in_region(game_name, tag, region)

        if not summoner:
            continue

        accounts[region] = {
            "gameName": game_name,
            "tagLine": tag,
            "puuid": account.get("puuid"),
            "region": region,
            "accountId": summoner.get("accountId"),
            "id": summoner.get("id"),
        }

    return accounts


def find_accounts_in_all_regions(game_name, tag):
    account_per_region = {region: None for region in select_regions}

    database_accounts = find_accounts_in_database(game_name, tag)

    for account in database_accounts:
        account_per_region[account.get("region")] = account

    not_found_regions = [
        region for region, account in account_per_region.items() if not account
    ]

    api_accounts = find_accounts_in_api(game_name, tag, not_found_regions)

    for key, value in api_accounts.items():
        account_per_region[key] = value

    return account_per_region
