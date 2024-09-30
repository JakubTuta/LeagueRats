import time

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


def update_pro_accounts(region) -> None:
    teams = regions.teams_per_region[region]

    for team in teams:
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

                if account := firestore_functions.get_account_from_firestore(
                    puuid=puuid
                ):
                    if any(
                        api_player_data[key] != account[key]
                        for key in api_player_data
                        if key in account
                    ):
                        account.reference.update(api_player_data)
                else:
                    firestore_functions.save_documents_to_collection(
                        "accounts", [api_player_data]
                    )

            time.sleep(0.5)


def update_player_game_names() -> None:
    firestore_functions.delete_document_from_collection("pro_players", "account_names")

    document_data = {}

    for region in ["LEC", "LCS", "LCK"]:
        teams_in_region = regions.teams_per_region[region]

        for team in teams_in_region:
            player_docs = firestore_functions.get_pro_player_documents(region, team)
            player_data = [doc.to_dict() for doc in player_docs]

            for player in player_data:
                for puuid in player["puuid"]:
                    if firestore_functions.get_account_from_firestore(puuid=puuid):
                        document_data[puuid] = {
                            "player": player["player"],
                            "team": team,
                        }

                time.sleep(0.5)

    firestore_functions.set_document_in_collection(
        "pro_players",
        "account_names",
        document_data,
    )


def update_bootcamp_leaderboard():
    accounts = []

    for region in regions.pro_regions:
        teams_in_region = regions.teams_per_region[region]

        for team in teams_in_region:
            player_docs = firestore_functions.get_pro_player_documents(region, team)

            for player_doc in player_docs:
                player_data = player_doc.to_dict()

                for puuid in player_data["puuid"]:
                    request_region = regions.pro_region_to_api_region_2[region]

                    if (
                        account_data := firestore_functions.get_account_from_firestore(
                            puuid=puuid
                        )
                    ) and (
                        league_entry := firestore_functions.get_league_entry(
                            request_region, account_data["id"]
                        )
                    ):
                        if soloq_entry := next(
                            (
                                entry
                                for entry in league_entry
                                if entry["queueType"] == "RANKED_SOLO_5x5"
                            ),
                            None,
                        ):
                            data = {
                                **player_data,
                                **account_data,
                                **soloq_entry,
                            }
                            accounts.append(data)

                time.sleep(0.5)

    firestore_functions.save_documents_to_collection(
        "eu_bootcamp_leaderboard", accounts
    )
