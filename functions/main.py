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


def get_existing_request_data(data, required_keys=[], optional_keys=[]):
    required_data = {}
    optional_data = {}

    for key in required_keys:
        if key not in data:
            raise Exception(f"Missing required key: {key}")

        required_data[key] = data[key]

    for key in optional_keys:
        if key in data:
            optional_data[key] = data[key]

    return required_data, optional_data


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
    required_keys = ["username", "tag"]

    try:
        request_data = req.get_json(force=True)
    except:
        return https_fn.Response(
            json.dumps({"error": "Invalid request data"}), status=400
        )

    try:
        required_data, _ = get_existing_request_data(request_data, required_keys)
    except Exception as e:
        return https_fn.Response(json.dumps({"error": str(e)}), status=400)

    username = required_data["username"]
    tag = required_data["tag"]

    request_url = f"{base_url}/{username}/{tag}"

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
def summoner_details_by_puuid(
    req: https_fn.Request,
) -> https_fn.Response:
    base_url = "https://eun1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid"
    required_keys = ["puuid"]

    try:
        request_data = req.get_json(force=True)
    except:
        return https_fn.Response(
            json.dumps({"error": "Invalid request data"}), status=400
        )

    try:
        required_data, _ = get_existing_request_data(request_data, required_keys)
    except Exception as e:
        return https_fn.Response(json.dumps({"error": str(e)}), status=400)

    puuid = required_data["puuid"]

    request_url = f"{base_url}/{puuid}"

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
def league_entry_by_summoner_id(
    req: https_fn.Request,
) -> https_fn.Response:
    base_url = "https://eun1.api.riotgames.com/lol/league/v4/entries/by-summoner"
    required_keys = ["summonerId"]

    try:
        request_data = req.get_json(force=True)
    except:
        return https_fn.Response(
            json.dumps({"error": "Invalid request data"}), status=400
        )

    try:
        required_data, _ = get_existing_request_data(request_data, required_keys)
    except Exception as e:
        return https_fn.Response(json.dumps({"error": str(e)}), status=400)

    summoner_id = required_data["summonerId"]

    request_url = f"{base_url}/{summoner_id}"

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
    required_keys = ["puuid"]

    try:
        request_data = req.get_json(force=True)
    except:
        return https_fn.Response(
            json.dumps({"error": "Invalid request data"}), status=400
        )

    try:
        required_data, _ = get_existing_request_data(request_data, required_keys)
    except Exception as e:
        return https_fn.Response(json.dumps({"error": str(e)}), status=400)

    puuid = required_data["puuid"]

    request_url = f"{base_url}/{puuid}"

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
    required_keys = ["championIds"]

    try:
        request_data = req.get_json(force=True)

    except:
        return https_fn.Response(
            json.dumps({"error": "Invalid request data"}), status=400
        )

    try:
        required_data, _ = get_existing_request_data(request_data, required_keys)
    except Exception as e:
        return https_fn.Response(json.dumps({"error": str(e)}), status=400)

    champion_ids = required_data["championIds"]

    try:
        response = requests.get(base_url)

        response_data = response.json()

    except:
        return https_fn.Response(
            json.dumps({"error": "Error occurred while fetching data"}), status=500
        )

    api_champions = response_data.get("data", None)

    if not api_champions:
        return https_fn.Response(
            json.dumps({"error": "Error occurred while fetching data"}), status=500
        )

    champion_positions = {
        champion_id: find_highest_playrate_role(api_champions, str(champion_id))
        for champion_id in champion_ids
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


@https_fn.on_request(region="europe-central2", cors=cors_options)
def champion_mastery_by_puuid(
    req: https_fn.Request,
) -> https_fn.Response:
    base_url = "https://eun1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid"
    required_keys = ["puuid"]

    try:
        request_data = req.get_json(force=True)
    except:
        return https_fn.Response(
            json.dumps({"error": "Invalid request data"}), status=400
        )

    try:
        required_data, _ = get_existing_request_data(request_data, required_keys)
    except Exception as e:
        return https_fn.Response(json.dumps({"error": str(e)}), status=400)

    puuid = required_data["puuid"]

    request_url = f"{base_url}/{puuid}"

    try:
        response = requests.get(
            request_url, headers={"X-Riot-Token": app.options.get("riot_api_key")}
        )

        # filtered_champions = list(
        #     filter(lambda champion: champion["championPoints"] > 0, response.json())
        # )

        return https_fn.Response(
            json.dumps(response.json()), status=response.status_code
        )

    except Exception as e:
        return https_fn.Response(
            json.dumps({"Riot API error": f"Error occurred: {str(e)}"}), status=500
        )


@https_fn.on_request(region="europe-central2", cors=cors_options)
def match_history_by_puuid(
    req: https_fn.Request,
) -> https_fn.Response:
    base_url = "https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid"
    required_keys = ["puuid"]
    optional_keys = ["startTime", "endTime", "queue", "type", "start", "count"]

    try:
        request_data = req.get_json(force=True)
    except:
        return https_fn.Response(
            json.dumps({"error": "Invalid request data"}), status=400
        )

    try:
        required_data, optional_data = get_existing_request_data(
            request_data, required_keys, optional_keys
        )
    except Exception as e:
        return https_fn.Response(json.dumps({"error": str(e)}), status=400)

    puuid = required_data["puuid"]

    optional_params = "&".join(
        [f"{key}={value}" for key, value in optional_data.items()]
    )

    request_url = f"{base_url}/{puuid}/ids?{optional_params}"

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
