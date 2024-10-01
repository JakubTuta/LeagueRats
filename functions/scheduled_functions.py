import threading

import requests
import src.firestore_functions as firestore_functions
import src.regions as regions
from firebase_functions import scheduler_fn


def current_version(
    event: scheduler_fn.ScheduledEvent,
) -> None:
    base_url = "https://ddragon.leagueoflegends.com/api/versions.json"

    try:
        response = requests.get(base_url)

        current_version = response.json()[0]

        firestore_functions.save_current_version(current_version)

    except Exception as e:
        print(f"Error occurred: {str(e)}")


def rune_description(event: scheduler_fn.ScheduledEvent) -> None:
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
            print(f"Error occurred: {str(e)}")

        short_language = language.split("_")[0]
        rune_data_per_language[short_language] = rune_data

    firestore_functions.save_rune_data(rune_data_per_language)


def _update_pro_accounts_for_team(new_documents, update_documents, region, team):
    player_documents = firestore_functions.get_pro_player_documents(region, team)

    for player_document in player_documents:
        player_document_data = player_document.to_dict()

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
    player_docs = firestore_functions.get_pro_player_documents(region, team)

    for player_doc in player_docs:
        player = player_doc.to_dict()

        for puuid in player["puuid"]:
            if firestore_functions.get_account_from_firestore(puuid=puuid):
                documents.append(
                    {
                        "player": player["player"],
                        "team": team,
                        "puuid": puuid,
                    }
                )


def update_player_game_names() -> None:
    firestore_functions.delete_document_from_collection("pro_players", "account_names")

    new_documents = []

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

    mapped_document = {
        doc["puuid"]: {"player": doc["player"], "team": doc["team"]}
        for doc in new_documents
    }

    firestore_functions.set_document_in_collection(
        "pro_players",
        "account_names",
        mapped_document,
    )


def _get_league_entries_for_team(accounts, region, team):
    player_docs = firestore_functions.get_pro_player_documents(region, team)

    for player_doc in player_docs:
        player_data = player_doc.to_dict()
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
