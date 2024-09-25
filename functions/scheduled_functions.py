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
    for team in regions.teams_per_region[region]:
        player_documents = firestore_functions.get_pro_player_documents(region, team)

        for player_document in player_documents:
            database_player_data = player_document.to_dict()

            api_player_data = firestore_functions._get_account_from_firestore(
                database_player_data["region"], puuid=database_player_data["puuid"]
            )

            if any(
                database_player_data[key] != api_player_data[key]
                for key in api_player_data
                if key in database_player_data
            ):
                player_document.reference.update(api_player_data)

            time.sleep(1)


def update_player_game_names() -> None:
    firestore_functions.delete_document_from_collection("pro_players", "game_names")

    document_data = {}

    for region in regions.pro_regions:
        teams_in_region = regions.teams_per_region[region]

        document_data[region] = {}

        for team in teams_in_region:
            document_data[region][team] = []

            player_docs = firestore_functions.get_pro_player_documents(region, team)
            player_data = [doc.to_dict() for doc in player_docs]

            for player in player_data:
                player_name = player["player"]
                game_name = player["gameName"]
                tag_line = player["tagLine"]

                document_data[region][team].append(
                    {
                        "player": player_name,
                        "gameName": game_name,
                        "tagLine": tag_line,
                    }
                )

    firestore_functions.set_document_in_collection(
        "pro_players",
        "game_names",
        document_data,
    )
