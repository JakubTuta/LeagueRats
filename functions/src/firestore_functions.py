import threading

import requests
import src.firebase_init as firebase_init
import src.regions as regions
from google.cloud.firestore_v1.base_query import FieldFilter

Account = {
    "gameName": "",
    "tagLine": "",
    "puuid": "",
    "region": "",
    "accountId": "",
    "id": "",
}


def _find_accounts_in_firestore(game_name, tag):
    query = (
        firebase_init.collections["accounts"]
        .where(filter=FieldFilter("gameName", "==", game_name))
        .where(filter=FieldFilter("tagLine", "==", tag))
    )

    docs = [doc.to_dict() for doc in query.stream()]

    return docs


def _find_account_in_firestore(puuid):
    query = firebase_init.collections["accounts"].where(
        filter=FieldFilter("puuid", "==", puuid)
    )

    docs = list(query.stream())

    return docs[0].to_dict() if len(docs) else None


def _find_account_in_region_riot_id(game_name, tag, region):
    request_region = regions.api_regions_1[region].lower()
    url = f"https://{request_region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag}"

    try:
        response = requests.get(
            url,
            headers={"X-Riot-Token": firebase_init.app.options.get("riot_api_key")},
        )

        return response.json()

    except:
        return None


def _find_account_in_region_puuid(puuid, region):
    request_region = regions.api_regions_1[region].lower()
    request_url = f"https://{request_region}.api.riotgames.com/riot/account/v1/accounts/by-puuid/{puuid}"

    try:
        response = requests.get(
            request_url,
            headers={"X-Riot-Token": firebase_init.app.options.get("riot_api_key")},
        )

        return response.json()

    except:
        return None


def _find_summoner_in_region_puuid(puuid, region):
    request_region = regions.api_regions_2[region].lower()
    request_url = f"https://{request_region}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"

    try:
        response = requests.get(
            request_url,
            headers={"X-Riot-Token": firebase_init.app.options.get("riot_api_key")},
        )

        return response.json()

    except:
        return None


def _find_accounts_in_api(game_name, tag, regions=[]):
    accounts = {}

    for region in regions:
        account = _find_account_in_region_riot_id(game_name, tag, region)

        if not account:
            continue

        summoner = _find_summoner_in_region_puuid(account["puuid"], region)

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
    account_per_region = {region: None for region in regions.select_regions}

    database_accounts = _find_accounts_in_firestore(game_name, tag)

    for account in database_accounts:
        account_per_region[account.get("region")] = account

    not_found_regions = [
        region for region, account in account_per_region.items() if not account
    ]

    api_accounts = _find_accounts_in_api(game_name, tag, not_found_regions)

    for key, value in api_accounts.items():
        account_per_region[key] = value

    return account_per_region


def _save_participant_to_firebase(participant, region):
    if _find_account_in_firestore(participant["puuid"]):
        return

    account_details = _find_account_in_region_puuid(participant["puuid"], region)
    summoner_details = _find_summoner_in_region_puuid(participant["puuid"], region)

    if account_details is None or summoner_details is None:
        return

    account = {
        "gameName": account_details.get("gameName"),
        "tagLine": account_details.get("tagLine"),
        "puuid": account_details.get("puuid"),
        "region": region,
        "accountId": summoner_details.get("accountId"),
        "id": summoner_details.get("id"),
    }

    firebase_init.collections["accounts"].add(account)


def save_participants_to_firebase(game_list):
    for game in game_list:
        region = regions.api_regions_2_to_select_regions[game["platformId"]]
        for participant in game["participants"]:
            threading.Thread(
                target=_save_participant_to_firebase, args=(participant, region)
            ).start()
