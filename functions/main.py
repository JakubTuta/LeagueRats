import json

import firebase_functions
import requests
from firebase_functions import https_fn
from src.firebase_init import initialize_app

app = initialize_app()

cors_options = firebase_functions.options.CorsOptions(
    cors_methods=["POST", "OPTIONS"],
    cors_origins="*",
)


@https_fn.on_request(region="europe-central2", cors=cors_options)
def test_connection(
    req: https_fn.Request,
) -> https_fn.Response:
    return https_fn.Response(json.dumps("Hello world"), status=200)


@https_fn.on_request(region="europe-central2", cors=cors_options)
def account_details_by_riot_id(
    req: https_fn.Request,
) -> https_fn.Response:
    base_url = "https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id"

    try:
        request_data = req.get_json(force=True)
    except:
        return https_fn.Response(
            json.dumps({"error": "Invalid request data"}), status=400
        )

    if not request_data.get("username", None):
        return https_fn.Response(json.dumps({"error": "Missing username"}), status=400)

    if not request_data.get("tag", None):
        return https_fn.Response(json.dumps({"error": "Missing tag"}), status=400)

    request_url = f"{base_url}/{request_data['username']}/{request_data['tag']}"

    try:
        response = requests.get(
            request_url, headers={"X-Riot-Token": app.options.get("riot_api_key")}
        )

        return https_fn.Response(
            json.dumps(response.json()), status=response.status_code
        )

    except Exception as e:
        return https_fn.Response(
            json.dumps({"Riot API error": f"Error occurred: {str(e)}"}), status=500
        )


@https_fn.on_request(region="europe-central2", cors=cors_options)
def active_game_by_puuid(
    req: https_fn.Request,
) -> https_fn.Response:
    base_url = (
        "https://eun1.api.riotgames.com/lol/spectator/v5/active-games/by-summoner"
    )

    try:
        request_data = req.get_json(force=True)
    except:
        return https_fn.Response(
            json.dumps({"error": "Invalid request data"}), status=400
        )

    if not request_data.get("puuid", None):
        return https_fn.Response(json.dumps({"error": "Missing puuid"}), status=400)

    request_url = f"{base_url}/{request_data['puuid']}"

    try:
        response = requests.get(
            request_url, headers={"X-Riot-Token": app.options.get("riot_api_key")}
        )

        return https_fn.Response(
            json.dumps(response.json()), status=response.status_code
        )

    except Exception as e:
        return https_fn.Response(
            json.dumps({"Riot API error": f"Error occurred: {str(e)}"}), status=500
        )


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


@https_fn.on_request(region="europe-central2", cors=cors_options)
def champion_positions(
    req: https_fn.Request,
) -> https_fn.Response:
    base_url = "https://cdn.merakianalytics.com/riot/lol/resources/latest/en-US/championrates.json"

    try:
        request_data = req.get_json(force=True)

    except:
        return https_fn.Response(
            json.dumps({"error": "Invalid request data"}), status=400
        )

    if not request_data.get("championIds", None):
        return https_fn.Response(json.dumps({"error": "Missing champions"}), status=400)

    try:
        response = requests.get(base_url)

        response_data = response.json()

    except:
        return https_fn.Response(
            json.dumps({"error": "Error occurred while fetching data"}), status=500
        )

    champions = request_data["championIds"]
    api_champions = response_data.get("data", None)

    if not api_champions:
        return https_fn.Response(
            json.dumps({"error": "Error occurred while fetching data"}), status=500
        )

    champion_positions = {
        champion_id: find_highest_playrate_role(api_champions, str(champion_id))
        for champion_id in champions
    }

    return https_fn.Response(json.dumps(champion_positions), status=200)


@https_fn.on_request(region="europe-central2", cors=cors_options)
def featured_games(
    req: https_fn.Request,
) -> https_fn.Response:
    base_url = "https://eun1.api.riotgames.com/lol/spectator/v5/featured-games"

    try:
        response = requests.get(
            base_url, headers={"X-Riot-Token": app.options.get("riot_api_key")}
        )

        return https_fn.Response(
            json.dumps(response.json()), status=response.status_code
        )

    except Exception as e:
        return https_fn.Response(
            json.dumps({"Riot API error": f"Error occurred: {str(e)}"}), status=500
        )
