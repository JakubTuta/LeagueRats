import re
import threading

import requests
import src.firebase_init as firebase_init
import src.regions as regions
from google.cloud.firestore_v1.base_query import FieldFilter
from src.models.match_history import MatchData

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


"""Rune data
[
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
]
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
    if account := _get_account_from_firestore(
        my_region, game_name=game_name, tag_line=tag
    ):
        regions[my_region] = account

        return

    if not (
        account_details := _get_account_from_region(
            my_region, game_name=game_name, tag_line=tag
        )
    ):
        return

    if not (
        summoner_details := _get_summoner_from_region(
            my_region, account_details.get("puuid")
        )
    ):
        return

    account_model = {
        "gameName": game_name,
        "tagLine": tag,
        "puuid": account_details.get("puuid"),
        "region": my_region,
        "accountId": summoner_details.get("accountId"),
        "id": summoner_details.get("id"),
        "profileIconId": summoner_details.get("profileIconId"),
        "summonerLevel": summoner_details.get("summonerLevel"),
    }

    firebase_init.collections["accounts"].add(account_model)

    regions[my_region] = account_model


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


def save_participant_to_firebase(region, puuid=None, game_name=None, tag_line=None):
    if account := _get_account_from_firestore(
        region, puuid=puuid, game_name=game_name, tag_line=tag_line
    ):
        return account

    if not (
        account_details := _get_account_from_region(
            region, puuid=puuid, game_name=game_name, tag_line=tag_line
        )
    ):
        return

    if not (
        summoner_details := _get_summoner_from_region(
            region, account_details.get("puuid")
        )
    ):
        return

    account_model = {
        "gameName": account_details.get("gameName"),
        "tagLine": account_details.get("tagLine"),
        "puuid": account_details.get("puuid"),
        "region": region,
        "accountId": summoner_details.get("accountId"),
        "id": summoner_details.get("id"),
        "profileIconId": summoner_details.get("profileIconId"),
        "summonerLevel": summoner_details.get("summonerLevel"),
    }

    firebase_init.collections["accounts"].add(account_model)

    regions[region] = account_model


def save_participants_to_firebase(puuids, game_region):
    def func():
        request_region = regions.api_region_2_to_select_region[game_region]

        for puuid in puuids:
            save_participant_to_firebase(puuid, request_region)

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
    text = text.encode("latin1").decode("utf-8")

    clean_text = re.sub(r"<.*?>", "", text)
    clean_text = re.sub(r"&([a-zA-Z0-9]+);", r"\1", clean_text)

    return clean_text


def save_rune_data(rune_data_per_language):
    for rune_data in rune_data_per_language.values():
        for rune_data_item in rune_data:
            for slot in rune_data_item["slots"]:
                for rune in slot["runes"]:
                    rune["shortDesc"] = _clear_text(rune["shortDesc"])
                    rune["longDesc"] = _clear_text(rune["longDesc"])

    firebase_init.collections["help"].document("runes").set(rune_data_per_language)


def get_match_data_from_firebase(match_id):
    doc = firebase_init.collections["match_history"].document(match_id).get()

    if not doc.exists:
        return None

    model = MatchData.from_dict(doc.to_dict())

    return model.to_dict()


def save_match_to_firebase(match):
    def func():
        firebase_init.collections["match_history"].document(
            match["metadata"]["matchId"]
        ).set(match)

    threading.Thread(target=func).start()


def _get_pro_player_documents(region, team):
    player_docs = firebase_init.firestore_client.collection(
        f"pro_players/{region}/{team}"
    ).stream()

    return player_docs


def _find_pro_region_for_team(team):
    for region, teams in regions.teams_per_region.items():
        if team in teams:
            return region


def _get_active_game(region, puuid):
    region = regions.api_regions_2[region]
    request_url = f"https://{region}.api.riotgames.com/lol/spectator/v5/active-games/by-summoner/{puuid}"

    try:
        response = requests.get(
            request_url,
            headers={"X-Riot-Token": firebase_init.app.options.get("riot_api_key")},
        )

        print(response.status_code)

        if response.status_code != 200:
            return None

        return response.json()

    except:
        return None


def _append_active_game(games, player):
    game = _get_active_game(player["region"], player["puuid"])

    if game:
        games.append((player, game))


def get_pro_games_for_team(active_games, team):
    threads = []

    region = _find_pro_region_for_team(team)

    player_docs = _get_pro_player_documents(region, team)
    player_data = [doc.to_dict() for doc in player_docs]

    for player in player_data:
        thread = threading.Thread(
            target=_append_active_game,
            args=(active_games, player),
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


def get_active_games_per_team(teams):
    threads = []
    active_games = []

    for team in teams:
        thread = threading.Thread(
            target=get_pro_games_for_team, args=(active_games, team)
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return active_games
