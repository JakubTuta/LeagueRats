import datetime

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
        players = firestore_functions.get_pro_players(region, team)

        for player in players:
            player_data = player.to_dict()

            account_data = firestore_functions._get_account_from_firestore(
                player_data["region"], puuid=player_data["puuid"]
            )

            if (
                account_data["gameName"] != player_data["gameName"]
                or account_data["tagLine"] != player_data["tagLine"]
            ):
                player_data["gameName"] = account_data["gameName"]
                player_data["tagLine"] = account_data["tagLine"]

                player.reference.update(player_data)
