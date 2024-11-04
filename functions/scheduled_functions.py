import threading

import requests
import src.firebase_init as firebase_init
import src.firestore_functions as firestore_functions
import src.help_functions as help_functions
import src.regions as regions

minutes_5 = "5,10,15,20,25,30,35,40,45,50,55 * * * *"
minutes_10 = "10,20,30,40,50 * * * *"
minutes_15 = "15,30,45 * * * *"
hours_1 = "0 * * * *"


def current_version() -> None:
    base_url = "https://ddragon.leagueoflegends.com/api/versions.json"

    response = requests.get(base_url)

    if not response.status_code == 200:
        return

    current_version = response.json()[0]

    firestore_functions.save_current_version(current_version)


def rune_description() -> None:
    recent_version = firestore_functions.get_current_version()

    if not recent_version:
        return

    languages = ["en_US", "pl_PL"]
    rune_data_per_language = {}

    for language in languages:
        base_url = f"https://ddragon.leagueoflegends.com/cdn/{recent_version}/data/{language}/runesReforged.json"

        try:
            response = requests.get(base_url)
            rune_data = response.json()
        except Exception as e:
            continue

        short_language = language.split("_")[0]
        rune_data_per_language[short_language] = rune_data

    firestore_functions.save_rune_data(rune_data_per_language)


def _get_champion_list_data() -> dict | None:
    recent_version = firestore_functions.get_current_version()

    if not recent_version:
        return

    base_url = f"https://ddragon.leagueoflegends.com/cdn/{recent_version}/data/en_US/champion.json"

    response = requests.get(base_url)

    if not response.status_code == 200:
        return None

    try:
        response_data = response.json()
        champions_data = response_data["data"]
    except:
        return None

    return champions_data


def champion_list() -> None:
    champions_data = _get_champion_list_data()

    if champions_data is None:
        return

    champions = {
        champion_data["key"]: {
            "title": champion_data["name"],
            "value": champion_data["id"],
        }
        for champion_data in champions_data.values()
    }

    firestore_functions.set_document_in_collection("help", "champions", champions)


def _update_pro_accounts_for_team(new_documents, update_documents, region, team):
    player_documents = firestore_functions.get_pro_team_documents(region, team)

    for player_document in player_documents:
        player_document_data = player_document.to_dict()

        if not player_document_data:
            continue

        for puuid in player_document_data["puuid"]:
            if not (
                api_player_data := firestore_functions.get_api_account(
                    player_document_data["region"], puuid=puuid
                )
            ):
                continue

            if account := firestore_functions.get_account_from_firestore(puuid=puuid):
                if any(
                    api_player_data[key] != account[key]
                    for key in api_player_data
                    if key in account
                ):
                    update_document = {
                        "reference": account.reference,
                        **api_player_data,
                    }
                    update_documents.append(update_document)
            else:
                new_documents.append(api_player_data)


def update_pro_accounts(region) -> None:
    new_documents = []
    update_documents = []

    threads = [
        threading.Thread(
            target=_update_pro_accounts_for_team,
            args=(new_documents, update_documents, region, team),
        )
        for team in regions.teams_per_region[region]
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    firestore_functions.save_documents_to_collection("pro_players", new_documents)

    for document in update_documents:
        del document["reference"]
        document.reference.update(document)


def _update_player_names_for_team(documents, region, team):
    player_docs = firestore_functions.get_pro_team_documents(region, team)

    for player_doc in player_docs:
        player = player_doc.to_dict()

        if not player:
            continue

        for puuid in player["puuid"]:
            documents[puuid] = {
                "player": player["player"],
                "team": team,
                "region": region,
            }


def update_player_game_names() -> None:
    new_documents = {}

    threads = [
        threading.Thread(
            target=_update_player_names_for_team,
            args=(new_documents, region, team),
        )
        for region in regions.pro_regions
        for team in regions.teams_per_region[region]
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    firestore_functions.set_document_in_collection(
        "pro_players",
        "account_names",
        new_documents,
    )


def _get_league_entries_for_team(accounts, region, team):
    player_docs = firestore_functions.get_pro_team_documents(region, team)

    for player_doc in player_docs:
        player_data = player_doc.to_dict()

        if not player_data:
            continue

        for puuid in player_data["puuid"]:
            request_region = "EUW1"

            account_data = firestore_functions.get_account_from_firestore(puuid=puuid)
            if not account_data:
                continue

            league_entry = firestore_functions.get_league_entry(
                request_region, account_data["id"]
            )
            if not league_entry:
                continue

            soloq_entry = next(
                (
                    entry
                    for entry in league_entry
                    if isinstance(entry, dict)
                    and entry.get("queueType") == "RANKED_SOLO_5x5"
                ),
                None,
            )
            if not soloq_entry:
                continue

            data = {
                **account_data,
                **soloq_entry,
                "player": player_data["player"],
                "team": team,
                "role": player_data["role"],
            }
            accounts.append(data)


def update_bootcamp_leaderboard():
    worlds_teams = (
        ("LEC", "G2"),
        ("LEC", "FNC"),
        ("LEC", "MAD"),
        ("LCS", "FLY"),
        ("LCS", "TL"),
        ("LCK", "HLE"),
        ("LCK", "GENG"),
        ("LCK", "DK"),
        ("LCK", "T1"),
        ("LPL", "BLG"),
        ("LPL", "TES"),
        ("LPL", "LNG"),
        ("LPL", "WBG"),
    )

    accounts = []

    threads = [
        threading.Thread(
            target=_get_league_entries_for_team, args=(accounts, region, team)
        )
        for region, team in worlds_teams
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    if len(accounts) > 0:
        firestore_functions.clear_collection("eu_bootcamp_leaderboard")

        firestore_functions.save_documents_to_collection(
            "eu_bootcamp_leaderboard", accounts
        )


def _get_live_streams_for_team(region, team, live_streams, not_live_streams):
    player_docs = firestore_functions.get_pro_team_documents(region, team)

    for player_doc in player_docs:
        player_data = player_doc.to_dict()

        if not player_data:
            continue

        player_name = player_data["player"]

        if player_data.get("socialMedia", {}).get("twitch"):
            if help_functions.check_if_channel_is_live(
                player_data["socialMedia"]["twitch"]
            ):
                live_streams[player_name] = {
                    "player": player_name,
                    "team": team,
                    "region": player_data["region"],
                    "twitch": player_data["socialMedia"]["twitch"],
                }
            else:
                not_live_streams[player_name] = {
                    "player": player_name,
                    "team": team,
                    "region": player_data["region"],
                    "twitch": player_data["socialMedia"]["twitch"],
                }


def check_for_live_streams():
    live_streams = {}
    not_live_streams = {}

    threads = [
        threading.Thread(
            target=_get_live_streams_for_team,
            args=(region, team, live_streams, not_live_streams),
        )
        for region, teams in regions.teams_per_region.items()
        for team in teams
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    firestore_functions.set_document_in_collection("live_streams", "live", live_streams)
    firestore_functions.set_document_in_collection(
        "live_streams", "not_live", not_live_streams
    )


def _update_champion_history_for_team(region, team):
    player_docs = firestore_functions.get_pro_team_documents(region, team)

    for player_doc in player_docs:
        player_data = player_doc.to_dict()

        if not player_data:
            continue

        for puuid in player_data["puuid"]:
            if not (
                account := firestore_functions.get_account_from_firestore(puuid=puuid)
            ):
                continue

            match_history = firestore_functions.get_match_history(account, hours=1)

            for match in match_history:
                player_participant = next(
                    (
                        participant
                        for participant in match["info"]["participants"]
                        if participant["puuid"] == puuid
                    ),
                    None,
                )

                if player_participant is None:
                    continue

                player_champion = player_participant["championId"]

                champion_stats = {
                    "games": 1,
                    "wins": 1 if player_participant["win"] else 0,
                    "losses": 0 if player_participant["win"] else 1,
                }

                match_data = {
                    "player": player_data,
                    "match": match,
                }

                firestore_functions.add_document_to_champion_history(
                    player_champion, champion_stats, match_data
                )


def update_champion_history():
    threads = [
        threading.Thread(
            target=_update_champion_history_for_team,
            args=("LEC", team),
        )
        for team in regions.teams_per_region["LEC"]
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()


def update_leaderboard():
    request_regions = list(regions.important_api_region_2_to_select_region.keys())

    for region in request_regions:
        select_region = regions.api_region_2_to_select_region[region]

        request_url = base_url = (
            f"https://{region}.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5"
        )

        response = requests.get(
            request_url,
            headers={"X-Riot-Token": firebase_init.app.options.get("riot_api_key")},
        )

        if not response.status_code == 200:
            continue

        entries = response.json()["entries"]
        leaderboard_accounts = []

        for index, entry in enumerate(entries, start=1):
            summoner_id = entry["summonerId"]

            if not (
                account := firestore_functions.get_account_from_firestore(
                    summoner_id=summoner_id
                )
            ):
                if not (
                    account := firestore_functions.get_api_account_from_summoner_id(
                        select_region, summoner_id=summoner_id
                    )
                ):
                    continue
                firestore_functions.save_accounts([account])

            leaderboard_account = {
                "gameName": account["gameName"],
                "tagLine": account["tagLine"],
                "puuid": account["puuid"],
                "rank": index,
                "wins": entry["wins"],
                "losses": entry["losses"],
                "leaguePoints": entry["leaguePoints"],
                "league": "CHALLENGER",
            }

            leaderboard_accounts.append(leaderboard_account)

        if len(leaderboard_accounts) > 0:
            firestore_functions.clear_collection(
                f"leaderboard/{select_region}/CHALLENGER"
            )
            firestore_functions.save_leaderboard_accounts(
                select_region, "CHALLENGER", leaderboard_accounts
            )
