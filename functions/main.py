import json
import random

import firebase_functions
import requests
import src.firebase_init as firebase_init
import src.firestore_functions as firestore_functions
import src.help_functions as help_functions
import src.regions as regions
from firebase_functions import https_fn, scheduler_fn

cors_options = firebase_functions.options.CorsOptions(
    cors_methods=["GET", "POST", "OPTIONS"],
    cors_origins="*",
)
cors_get_options = firebase_functions.options.CorsOptions(
    cors_methods=["GET", "OPTIONS"],
    cors_origins="*",
)

firebase_init.initialize_app()


@https_fn.on_request(region="europe-central2", cors=cors_options)
def test_connection(
    req: https_fn.Request,
) -> https_fn.Response:
    return https_fn.Response(json.dumps("Hello world"), status=200)


@https_fn.on_request(region="europe-central2", cors=cors_options)
def account_details(
    req: https_fn.Request,
) -> https_fn.Response:
    base_url = "https://europe.api.riotgames.com/riot/account/v1/accounts"

    try:
        request_data = req.get_json(force=True)
    except:
        return https_fn.Response(
            json.dumps({"error": "Invalid request data"}), status=400
        )

    try:
        username = request_data.get("username", None)
        tag = request_data.get("tag", None)
        puuid = request_data.get("puuid", None)
    except:
        return https_fn.Response(
            json.dumps({"error": "Invalid request data"}), status=400
        )

    if puuid:
        request_url = f"{base_url}/by-puuid/{puuid}"
    else:
        request_url = f"{base_url}/by-riot-id/{username}/{tag}"

    try:
        response = requests.get(
            request_url,
            headers={"X-Riot-Token": firebase_init.app.options.get("riot_api_key")},
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
    required_keys = ["puuid", "region"]

    try:
        request_data = req.get_json(force=True)
    except:
        return https_fn.Response(
            json.dumps({"error": "Invalid request data"}), status=400
        )

    try:
        required_data, _ = help_functions.get_existing_request_data(
            request_data, required_keys
        )
    except Exception as e:
        return https_fn.Response(json.dumps({"error": str(e)}), status=400)

    puuid = required_data["puuid"]
    region = required_data["region"]

    if region not in regions.api_regions_2:
        return https_fn.Response(json.dumps({"error": "Invalid region"}), status=400)

    region = regions.api_regions_2[region].lower()

    request_url = (
        f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
    )

    try:
        response = requests.get(
            request_url,
            headers={"X-Riot-Token": firebase_init.app.options.get("riot_api_key")},
        )

        return https_fn.Response(
            json.dumps(response.json()), status=response.status_code
        )

    except Exception as e:
        return https_fn.Response(
            json.dumps({"Riot API error": f"Error occurred: {str(e)}"}), status=500
        )


@https_fn.on_request(region="europe-central2", cors=cors_get_options)
def league_entry(
    req: https_fn.Request,
) -> https_fn.Response:
    # url: /league_entry/{region}/{summonerId}

    try:
        url_params = req.path.split("/")

        region = url_params[1]
        summoner_id = url_params[2]
    except:
        return https_fn.Response(
            json.dumps({"error": "Invalid request data"}), status=400
        )

    try:
        region = regions.api_regions_2[region].lower()
    except:
        return https_fn.Response(json.dumps({"error": "Invalid region"}), status=400)

    request_url = f"https://{region}.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}"

    try:
        response = requests.get(
            request_url,
            headers={"X-Riot-Token": firebase_init.app.options.get("riot_api_key")},
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
    required_keys = ["puuid", "region"]

    try:
        request_data = req.get_json(force=True)
    except:
        return https_fn.Response(
            json.dumps({"error": "Invalid request data"}), status=400
        )

    try:
        required_data, _ = help_functions.get_existing_request_data(
            request_data, required_keys
        )
    except Exception as e:
        return https_fn.Response(json.dumps({"error": str(e)}), status=400)

    puuid = required_data["puuid"]
    region = regions.api_regions_2[required_data["region"]].lower()

    request_url = f"https://{region}.api.riotgames.com/lol/spectator/v5/active-games/by-summoner/{puuid}"

    try:
        response = requests.get(
            request_url,
            headers={"X-Riot-Token": firebase_init.app.options.get("riot_api_key")},
        )

        return https_fn.Response(
            json.dumps(response.json()), status=response.status_code
        )

    except Exception as e:
        return https_fn.Response(
            json.dumps({"Riot API error": f"Error occurred: {str(e)}"}), status=500
        )


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
        required_data, _ = help_functions.get_existing_request_data(
            request_data, required_keys
        )
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
        champion_id: help_functions.find_highest_playrate_role(
            api_champions, str(champion_id)
        )
        for champion_id in champion_ids
    }

    return https_fn.Response(json.dumps(champion_positions), status=200)


@https_fn.on_request(region="europe-central2", cors=cors_options)
def featured_games(
    req: https_fn.Request,
) -> https_fn.Response:
    regions_to_feature = ["euw1", "na1"]

    base_url = f"https://{random.choice(regions_to_feature)}.api.riotgames.com/lol/spectator/v5/featured-games"

    try:
        response = requests.get(
            base_url,
            headers={"X-Riot-Token": firebase_init.app.options.get("riot_api_key")},
        )

        response_data = response.json()
        game_list = list(response_data["gameList"])

        return https_fn.Response(json.dumps(game_list), status=response.status_code)

    except Exception as e:
        return https_fn.Response(
            json.dumps({"Riot API error": f"Error occurred: {str(e)}"}), status=500
        )


@https_fn.on_request(region="europe-central2", cors=cors_options)
def champion_mastery_by_puuid(
    req: https_fn.Request,
) -> https_fn.Response:
    required_keys = ["puuid", "region"]

    try:
        request_data = req.get_json(force=True)
    except:
        return https_fn.Response(
            json.dumps({"error": "Invalid request data"}), status=400
        )

    try:
        required_data, _ = help_functions.get_existing_request_data(
            request_data, required_keys
        )
    except Exception as e:
        return https_fn.Response(json.dumps({"error": str(e)}), status=400)

    puuid = required_data["puuid"]
    region = regions.api_regions_2[required_data["region"]].lower()

    request_url = f"https://{region}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}"

    try:
        response = requests.get(
            request_url,
            headers={"X-Riot-Token": firebase_init.app.options.get("riot_api_key")},
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
    required_keys = ["puuid", "region"]
    optional_keys = ["startTime", "endTime", "queue", "type", "start", "count"]

    try:
        request_data = req.get_json(force=True)
    except:
        return https_fn.Response(
            json.dumps({"error": "Invalid request data"}), status=400
        )

    try:
        required_data, optional_data = help_functions.get_existing_request_data(
            request_data, required_keys, optional_keys
        )
    except Exception as e:
        return https_fn.Response(json.dumps({"error": str(e)}), status=400)

    puuid = required_data["puuid"]
    region = regions.api_regions_1[required_data["region"]].lower()

    optional_params = "&".join(
        [f"{key}={value}" for key, value in optional_data.items()]
    )

    request_url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?{optional_params}"

    try:
        response = requests.get(
            request_url,
            headers={"X-Riot-Token": firebase_init.app.options.get("riot_api_key")},
        )

        return https_fn.Response(
            json.dumps(response.json()), status=response.status_code
        )

    except Exception as e:
        return https_fn.Response(
            json.dumps({"Riot API error": f"Error occurred: {str(e)}"}), status=500
        )


@https_fn.on_request(region="europe-central2", cors=cors_options)
def accounts_in_all_regions(
    req: https_fn.Request,
) -> https_fn.Response:
    required_keys = ["gameName", "tagLine"]

    try:
        request_data = req.get_json(force=True)
    except:
        return https_fn.Response(
            json.dumps({"error": "Invalid request data"}), status=400
        )

    try:
        required_data, _ = help_functions.get_existing_request_data(
            request_data, required_keys
        )
    except Exception as e:
        return https_fn.Response(json.dumps({"error": str(e)}), status=400)

    game_name = required_data["gameName"]
    tag_line = required_data["tagLine"]

    try:
        accounts = firestore_functions.get_accounts_from_all_regions(
            game_name, tag_line
        )

        return https_fn.Response(json.dumps(accounts), status=200)

    except Exception as e:
        return https_fn.Response(
            json.dumps({"Firebase error": f"Error occurred: {str(e)}"}), status=500
        )


@https_fn.on_request(region="europe-central2", cors=cors_get_options)
def match_data(
    req: https_fn.Request,
) -> https_fn.Response:
    # url: /match_data/{match_id}

    try:
        match_id = req.path.split("/")[1]
    except:
        return https_fn.Response(
            json.dumps({"error": "Invalid request data"}), status=400
        )

    try:
        region = match_id.split("_")[0]

        request_region = regions.api_region_2_to_server_region[region]
    except:
        return https_fn.Response(json.dumps({"error": "Invalid region"}), status=400)

    request_url = (
        f"https://{request_region}.api.riotgames.com/lol/match/v5/matches/{match_id}"
    )

    try:
        response = requests.get(
            request_url,
            headers={"X-Riot-Token": firebase_init.app.options.get("riot_api_key")},
        )

        response_data = response.json()

        participant_puuids = response_data["metadata"]["participants"]
        game_region = response_data["info"]["platformId"]

        firestore_functions.save_participants_to_firebase(
            participant_puuids, game_region
        )

        return https_fn.Response(json.dumps(response_data), status=response.status_code)

    except Exception as e:
        return https_fn.Response(
            json.dumps({"Riot API error": f"Error occurred: {str(e)}"}), status=500
        )


@scheduler_fn.on_schedule(region="europe-central2", schedule="every day 00:00")
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


@scheduler_fn.on_schedule(region="europe-central2", schedule="every day 00:00")
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
