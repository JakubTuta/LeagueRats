import re
import threading
import time

import requests
import src.firebase_init as firebase_init
import src.regions as regions
from google.cloud.firestore_v1.base_query import FieldFilter

""" Account
{
    "gameName": str,
    "tagLine": str,
    "puuid": str,
    "region": str,
    "accountId": str,
    "id": str,   
}
"""


"""Rune
{
    "id": int,
    "key": str,
    "icon": str,
    "name": str,
    "slots": [
        {
            "runes": [
                {
                    "id": int,
                    "key": str,
                    "icon": str,
                    "name": str,
                    "shortDesc": str,
                    "longDesc": str,
                }
            ]
        }
    ]
}
"""


def _get_account_from_firestore(region, puuid=None, game_name=None, tag_line=None):
    if puuid:
        query = (
            firebase_init.collections["accounts"]
            .where(filter=FieldFilter("puuid", "==", puuid))
            .where(filter=FieldFilter("region", "==", region))
        )
    elif game_name and tag_line:
        query = (
            firebase_init.collections["accounts"]
            .where(
                filter=FieldFilter("gameName", "==", game_name),
            )
            .where(filter=FieldFilter("tagLine", "==", tag_line))
            .where(filter=FieldFilter("region", "==", region))
        )
    else:
        return None

    docs = list(query.stream())

    return docs[0].to_dict() if len(docs) else None


def _get_account_from_region(region, puuid=None, game_name=None, tag_line=None):
    request_region = regions.api_regions_1[region].lower()

    if puuid:
        url = f"https://{request_region}.api.riotgames.com/riot/account/v1/accounts/by-puuid/{puuid}"
    elif game_name and tag_line:
        url = f"https://{request_region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    else:
        return

    try:
        response = requests.get(
            url,
            headers={"X-Riot-Token": firebase_init.app.options.get("riot_api_key")},
        )

        return response.json()

    except:
        return None


def _get_summoner_from_region(region, puuid):
    request_region = regions.api_regions_2[region].lower()
    request_url = f"https://{request_region}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"

    try:
        response = requests.get(
            request_url,
            headers={"X-Riot-Token": firebase_init.app.options.get("riot_api_key")},
        )

        if response.status_code == 404:
            return None

        return response.json()

    except:
        return None


def get_account(regions, my_region, game_name, tag):
    account = _get_account_from_firestore(my_region, game_name=game_name, tag_line=tag)

    if account:
        regions[my_region] = account

        return

    account = _get_account_from_region(my_region, game_name=game_name, tag_line=tag)

    if not account:
        return

    summoner = _get_summoner_from_region(my_region, account["puuid"])

    if not summoner:
        return

    new_account = {
        "gameName": game_name,
        "tagLine": tag,
        "puuid": account["puuid"],
        "region": my_region,
        "accountId": summoner["accountId"],
        "id": summoner["id"],
    }

    firebase_init.collections["accounts"].add(new_account)

    regions[my_region] = new_account


def get_accounts_from_all_regions(game_name, tag):
    account_per_region = {}
    threads = []

    for region in regions.select_regions:
        account_per_region[region] = None

        new_thread = threading.Thread(
            target=get_account,
            args=(account_per_region, region, game_name, tag),
        )
        threads.append(new_thread)
        new_thread.start()

    for thread in threads:
        thread.join()

    return account_per_region


def _save_participant_to_firebase(puuid, region):
    if _get_account_from_firestore(region, puuid=puuid):
        return

    account_details = _get_account_from_region(region, puuid=puuid)
    summoner_details = _get_summoner_from_region(region, puuid)

    if account_details is None or summoner_details is None:
        return

    account = {
        "gameName": account_details.get("gameName"),
        "tagLine": account_details.get("tagLine"),
        "puuid": puuid,
        "region": region,
        "accountId": summoner_details.get("accountId"),
        "id": summoner_details.get("id"),
    }

    firebase_init.collections["accounts"].add(account)


def save_participants_to_firebase(game_list):
    def func():
        for game in game_list:
            region = regions.api_region_2_to_select_region[game["platformId"]]

            for participant in game["participants"]:
                _save_participant_to_firebase(participant["puuid"], region)
                time.sleep(0.1)

    threading.Thread(target=func).start()


def save_current_version(version):
    firebase_init.collections["help"].document("current_version").set(
        {"version": version}
    )


def get_current_version():
    doc = firebase_init.collections["help"].document("current_version").get()

    return doc.to_dict()["version"] if doc.exists else None


def _clear_text(text):
    text = text.encode().decode("unicode_escape")

    clean_text = re.sub(r"<.*?>", "", text)

    return clean_text


def save_rune_data(rune_data_per_language):
    for language, rune_data in rune_data_per_language.items():
        for rune_tree in rune_data:
            for slot in rune_tree["slots"]:
                for rune_row in slot:
                    for rune in rune_row["runes"]:
                        rune["shortDesc"] = _clear_text(rune["shortDesc"])
                        rune["longDesc"] = _clear_text(rune["longDesc"])

    firebase_init.collections["runes"].document(language).set({"runes": rune_data})
