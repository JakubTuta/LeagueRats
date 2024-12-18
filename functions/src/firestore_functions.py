import datetime
import re
import threading

import requests
import src.firebase_init as firebase_init
import src.regions as regions
from google.cloud.firestore_v1.base_query import FieldFilter
from src.models.match_history import MatchData


def get_account_from_firestore(
    puuid=None, region=None, game_name=None, tag_line=None, summoner_id=None
):
    if puuid:
        doc_ref = firebase_init.collections["accounts"].document(puuid)
        doc = doc_ref.get()

        return doc.to_dict() if doc.exists else None

    elif game_name and tag_line and region:
        query = (
            firebase_init.collections["accounts"]
            .where(
                filter=FieldFilter("gameName", "==", game_name),
            )
            .where(filter=FieldFilter("tagLine", "==", tag_line))
            .where(filter=FieldFilter("region", "==", region))
        )

        docs = query.stream()
        doc = next(docs, None)

        return doc.to_dict() if doc else None

    elif summoner_id:
        query = firebase_init.collections["accounts"].where(
            filter=FieldFilter("id", "==", summoner_id),
        )

        docs = query.stream()
        doc = next(docs, None)

        return doc.to_dict() if doc else None

    return None


def get_api_account(region, puuid=None, game_name=None, tag_line=None):
    if not (
        account_details := _get_account_from_region(
            region, puuid=puuid, game_name=game_name, tag_line=tag_line
        )
    ):
        return None

    if not (
        summoner_details := _get_summoner_from_region(
            region, account_details.get("puuid")
        )
    ):
        return None

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

    return account_model


def get_api_account_from_summoner_id(region, summoner_id):
    if account := get_account_from_firestore(summoner_id=summoner_id):
        return account

    if not (summoner_details := _get_summoner_with_summoner_id(region, summoner_id)):
        return None

    if not (
        account_details := _get_account_from_region(
            region, puuid=summoner_details.get("puuid")
        )
    ):
        return None

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

    return account_model


def get_league_entry(region, summoner_id):
    request_url = f"https://{region}.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}"

    response = requests.get(
        request_url,
        headers={"X-Riot-Token": firebase_init.app.options.get("riot_api_key")},
    )

    return response.json()


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

        if response.status_code == 200:
            return response.json()

        else:
            return None

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

        if response.status_code != 200:
            return None

        return response.json()

    except:
        return None


def _get_summoner_with_summoner_id(region, summoner_id):
    request_region = regions.api_regions_2[region].lower()
    request_url = f"https://{request_region}.api.riotgames.com/lol/summoner/v4/summoners/{summoner_id}"

    try:
        response = requests.get(
            request_url,
            headers={"X-Riot-Token": firebase_init.app.options.get("riot_api_key")},
        )

        if response.status_code != 200:
            return None

        return response.json()

    except:
        return None


def _save_account_from_region(regions, my_region, game_name, tag):
    if account := get_account_from_firestore(
        region=my_region, game_name=game_name, tag_line=tag
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

    save_accounts([account_model])

    regions[my_region] = account_model


def get_accounts_from_all_regions(game_name, tag):
    account_per_region = {}
    threads = []

    for region in regions.select_regions:
        account_per_region[region] = None

        new_thread = threading.Thread(
            target=_save_account_from_region,
            args=(account_per_region, region, game_name, tag),
        )
        threads.append(new_thread)
        new_thread.start()

    for thread in threads:
        thread.join()

    return account_per_region


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


def get_pro_team_documents(region, team):
    player_docs = firebase_init.firestore_client.collection(
        f"pro_players/{region}/{team}"
    ).stream()

    return player_docs


def get_pro_player_document(region, team, player):
    player_doc = (
        firebase_init.firestore_client.collection(f"pro_players/{region}/{team}")
        .document(player.lower())
        .get()
    )

    return player_doc if player_doc.exists else None


def _find_pro_region_for_team(team):
    for region, teams in regions.teams_per_region.items():
        if team in teams:
            return region


def _get_active_game(region, puuid):
    request_region = regions.api_regions_2[region].lower()
    request_url = f"https://{request_region}.api.riotgames.com/lol/spectator/v5/active-games/by-summoner/{puuid}"

    try:
        response = requests.get(
            request_url,
            headers={
                "X-Riot-Token": firebase_init.app.options.get("riot_api_key"),
                "Origin": "https://developer.riotgames.com",
            },
        )

        if response.status_code != 200:
            return None

        return response.json()

    except:
        return None


def _append_active_game(games, player):
    for puuid in player["puuid"]:
        if not (account := get_account_from_firestore(puuid=puuid)):
            continue

        if not (game := _get_active_game(account["region"], puuid)):
            continue

        player_participant = next(
            (
                participant
                for participant in game["participants"]
                if participant["puuid"] == puuid
            ),
            None,
        )

        mapped_game = {
            "account": account,
            "player": player,
            "participant": player_participant,
            "gameStartTime": datetime.datetime.fromtimestamp(
                game["gameStartTime"] / 1000
            ),
        }

        games.append(mapped_game)

        return


def _get_pro_games_for_team(active_games, team):
    region = _find_pro_region_for_team(team)

    player_docs = get_pro_team_documents(region, team)
    player_data = [doc.to_dict() for doc in player_docs]

    threads = [
        threading.Thread(target=_append_active_game, args=(active_games, player))
        for player in player_data
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()


def get_active_games_per_team(teams):
    active_games = []

    threads = [
        threading.Thread(target=_get_pro_games_for_team, args=(active_games, team))
        for team in teams
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    previous_games = firebase_init.collections["active_pro_games"].stream()

    previous_games_dict = {
        doc.to_dict()["participant"]["puuid"]: doc.to_dict() for doc in previous_games
    }
    current_games_list = [game["participant"]["puuid"] for game in active_games]

    # Remove games that are no longer active
    for previous_game in previous_games:
        previous_game_data = previous_game.to_dict()
        if previous_game_data["participant"]["puuid"] not in current_games_list:
            previous_game.reference.delete()

    # Add new games
    new_games = [
        game
        for game in active_games
        if game["participant"]["puuid"] not in previous_games_dict
    ]

    return new_games


def _get_match_history_ids(account, hours):
    now = datetime.datetime.now()
    past = now - datetime.timedelta(hours=hours)

    optional_keys = {
        "count": 100,
        "queue": 420,
        "type": "ranked",
        "startTime": int(past.timestamp()),
        "endTime": int(now.timestamp()),
    }

    url_params = "&".join([f"{key}={value}" for key, value in optional_keys.items()])

    region = regions.api_regions_1[account["region"]].lower()
    puuid = account["puuid"]

    request_url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?{url_params}"

    response = requests.get(
        request_url,
        headers={"X-Riot-Token": firebase_init.app.options.get("riot_api_key")},
    )

    if response.status_code != 200:
        return []

    match_ids: list[str] = response.json()

    return match_ids


def get_match_history(account, hours):
    match_ids = _get_match_history_ids(account, hours)

    matches = []
    region = regions.api_regions_1[account["region"]]

    for match_id in match_ids:
        request_url = (
            f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}"
        )

        response = requests.get(
            request_url,
            headers={"X-Riot-Token": firebase_init.app.options.get("riot_api_key")},
        )

        if response.status_code != 200:
            continue

        response_data = response.json()

        match_data = MatchData.from_dict(response_data).to_dict()
        save_match_to_firebase(match_data)

        matches.append(match_data)

    return matches


def clear_collection(collection_name):
    docs = firebase_init.collections[collection_name].stream()

    for doc in docs:
        doc.reference.delete()


def set_document_in_collection(collection_name, document_id, document_data):
    firebase_init.collections[collection_name].document(document_id).set(document_data)


def save_documents_to_collection(collection_name, documents):
    for document in documents:
        firebase_init.collections[collection_name].add(document)


def delete_document_from_collection(collection_name, document_id):
    firebase_init.collections[collection_name].document(document_id).delete()


def save_accounts(accounts):
    for account in accounts:
        if account["puuid"]:
            firebase_init.collections["accounts"].document(account["puuid"]).set(
                account
            )


def get_live_streams():
    doc_ref = firebase_init.collections["live_streams"].document("live")
    doc = doc_ref.get()

    return doc if doc.exists else None


def get_not_live_streams():
    doc_ref = firebase_init.collections["live_streams"].document("not_live")
    doc = doc_ref.get()

    return doc if doc.exists else None


def add_document_to_champion_history(champion_id, champion_stats, match_data):
    champion_reference = firebase_init.collections["champion_history"].document(
        str(champion_id)
    )
    champion_document = champion_reference.get()

    if champion_document.exists:
        champion_data = champion_document.to_dict()

        if "games" in champion_data:
            champion_data["games"] += champion_stats.get("games", 0)
        else:
            champion_data["games"] = champion_stats.get("games", 0)

        if "wins" in champion_data:
            champion_data["wins"] += champion_stats.get("wins", 0)
        else:
            champion_data["wins"] = champion_stats.get("wins", 0)

        if "losses" in champion_data:
            champion_data["losses"] += champion_stats.get("losses", 0)
        else:
            champion_data["losses"] = champion_stats.get("losses", 0)

        champion_reference.update(champion_data)

    else:
        champion_reference.set(champion_stats)

    champion_matches_reference = firebase_init.firestore_client.collection(
        f"champion_history/{str(champion_id)}/matches"
    )
    champion_matches_reference.document(match_data["match"]["metadata"]["matchId"]).set(
        match_data
    )


def save_leaderboard_accounts(region, rank, accounts):
    collection_ref = firebase_init.firestore_client.collection(
        f"leaderboard/{region}/{rank}"
    )

    for account in accounts:
        if account["puuid"]:
            collection_ref.document(account["puuid"]).set(account)
