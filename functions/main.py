import json
import random

import firebase_functions
import requests
import scheduled_functions
import src.firebase_init as firebase_init
import src.firestore_functions as firestore_functions
import src.help_functions as help_functions
import src.regions as regions
from firebase_functions import https_fn, scheduler_fn
from src.models.match_history import MatchData

# cors_options = firebase_functions.options.CorsOptions(
#     cors_methods=["GET", "POST", "OPTIONS"],
#     cors_origins="*",
# )
cors_get_options = firebase_functions.options.CorsOptions(
    cors_methods=["GET", "OPTIONS"],
    cors_origins="*",
)

firebase_init.initialize_app()


@https_fn.on_request(region="europe-central2", cors=cors_get_options)
def test_connection(
    req: https_fn.Request,
) -> https_fn.Response:
    # url: /test_connection

    return https_fn.Response(json.dumps("Hello world"), status=200)


@https_fn.on_request(region="europe-central2", cors=cors_get_options)
def account_details(
    req: https_fn.Request,
) -> https_fn.Response:
    # url: /account_details?username={username}&tag={tag} or /account_details?puuid={puuid}

    base_url = "https://europe.api.riotgames.com/riot/account/v1/accounts"

    try:
        username = req.args.get("username", None)
        tag = req.args.get("tag", None)
        puuid = req.args.get("puuid", None)
    except:
        return https_fn.Response(
            json.dumps({"error": "Invalid request data"}), status=400
        )

    if puuid:
        request_url = f"{base_url}/by-puuid/{puuid}"
    elif username and tag:
        request_url = f"{base_url}/by-riot-id/{username}/{tag}"
    else:
        return https_fn.Response(
            json.dumps({"error": "Invalid request data"}), status=400
        )

    try:
        response = requests.get(
            request_url,
            headers={"X-Riot-Token": firebase_init.app.options.get("riot_api_key")},
        )

        if response.status_code != 200:
            return https_fn.Response(
                json.dumps(response.json()), status=response.status_code
            )

        return https_fn.Response(json.dumps(response.json()), status=200)

    except Exception as e:
        return https_fn.Response(
            json.dumps({"Riot API error": f"Error occurred: {str(e)}"}), status=500
        )


@https_fn.on_request(region="europe-central2", cors=cors_get_options)
def summoner_details(
    req: https_fn.Request,
) -> https_fn.Response:
    # url: /summoner_details/{region}/{puuid}

    try:
        url_params = req.path.split("/")

        region = url_params[1]
        puuid = url_params[2]

        if not region or not puuid:
            raise Exception("Missing region or puuid")
    except:
        return https_fn.Response(
            json.dumps({"error": "Invalid request data"}), status=400
        )

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

        if response.status_code != 200:
            return https_fn.Response(
                json.dumps(response.json()), status=response.status_code
            )

        return https_fn.Response(json.dumps(response.json()), status=200)

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

        if not region or not summoner_id:
            raise Exception("Missing region or summonerId")
    except:
        return https_fn.Response(
            json.dumps({"error": "Invalid request data"}), status=400
        )

    if region not in regions.api_regions_2:
        return https_fn.Response(json.dumps({"error": "Invalid region"}), status=400)

    region = regions.api_regions_2[region].lower()

    try:
        response = firestore_functions.get_league_entry(region, summoner_id)

        return https_fn.Response(json.dumps(response), status=200)

    except Exception as e:
        return https_fn.Response(
            json.dumps({"Riot API error": f"Error occurred: {str(e)}"}), status=500
        )


@https_fn.on_request(region="europe-central2", cors=cors_get_options)
def active_game(
    req: https_fn.Request,
) -> https_fn.Response:
    # url: /active_game/{region}/{puuid}

    try:
        url_params = req.path.split("/")

        region = url_params[1]
        puuid = url_params[2]

        if not region or not puuid:
            raise Exception("Missing region or puuid")
    except:
        return https_fn.Response(
            json.dumps({"error": "Invalid request data"}), status=400
        )

    if region not in regions.api_regions_2:
        return https_fn.Response(json.dumps({"error": "Invalid region"}), status=400)

    region = regions.api_regions_2[region].lower()

    request_url = f"https://{region}.api.riotgames.com/lol/spectator/v5/active-games/by-summoner/{puuid}"

    try:
        response = requests.get(
            request_url,
            headers={"X-Riot-Token": firebase_init.app.options.get("riot_api_key")},
        )

        if response.status_code != 200:
            return https_fn.Response(
                json.dumps(response.json()), status=response.status_code
            )

        return https_fn.Response(json.dumps(response.json()), status=200)

    except Exception as e:
        return https_fn.Response(
            json.dumps({"Riot API error": f"Error occurred: {str(e)}"}), status=500
        )


@https_fn.on_request(region="europe-central2", cors=cors_get_options)
def champion_positions(
    req: https_fn.Request,
) -> https_fn.Response:
    # url: /champion_positions/{championIds}

    base_url = "https://cdn.merakianalytics.com/riot/lol/resources/latest/en-US/championrates.json"

    try:
        url_params = req.path.split("/")

        champion_ids = url_params[1]
        champion_ids = list(map(int, champion_ids.split(".")))
    except:
        return https_fn.Response(
            json.dumps({"error": "Invalid request data"}), status=400
        )

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


@https_fn.on_request(region="europe-central2", cors=cors_get_options)
def featured_games(
    req: https_fn.Request,
) -> https_fn.Response:
    # url: /featured_games

    regions_to_feature = ["euw1", "na1"]
    base_url = f"https://{random.choice(regions_to_feature)}.api.riotgames.com/lol/spectator/v5/featured-games"

    try:
        response = requests.get(
            base_url,
            headers={"X-Riot-Token": firebase_init.app.options.get("riot_api_key")},
        )

        if response.status_code != 200:
            return https_fn.Response(
                json.dumps(response.json()), status=response.status_code
            )

        response_data = response.json()
        game_list = list(response_data["gameList"])

        return https_fn.Response(json.dumps(game_list), status=200)

    except Exception as e:
        return https_fn.Response(
            json.dumps({"Riot API error": f"Error occurred: {str(e)}"}), status=500
        )


@https_fn.on_request(region="europe-central2", cors=cors_get_options)
def champion_mastery(
    req: https_fn.Request,
) -> https_fn.Response:
    # url: /champion_mastery/{region}/{puuid}

    try:
        url_params = req.path.split("/")

        region = url_params[1]
        puuid = url_params[2]

        if not region or not puuid:
            raise Exception("Missing region or puuid")
    except:
        return https_fn.Response(
            json.dumps({"error": "Invalid request data"}), status=400
        )

    if region not in regions.api_regions_2:
        return https_fn.Response(json.dumps({"error": "Invalid region"}), status=400)

    region = regions.api_regions_2[region].lower()

    request_url = f"https://{region}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}"

    try:
        response = requests.get(
            request_url,
            headers={"X-Riot-Token": firebase_init.app.options.get("riot_api_key")},
        )

        if response.status_code != 200:
            return https_fn.Response(
                json.dumps(response.json()), status=response.status_code
            )

        # filtered_champions = list(
        #     filter(lambda champion: champion["championPoints"] > 0, response.json())
        # )

        return https_fn.Response(json.dumps(response.json()), status=200)

    except Exception as e:
        return https_fn.Response(
            json.dumps({"Riot API error": f"Error occurred: {str(e)}"}), status=500
        )


@https_fn.on_request(region="europe-central2", cors=cors_get_options)
def match_history(
    req: https_fn.Request,
) -> https_fn.Response:
    # url: /match_history/{region}/{puuid}?startTime={startTime}&endTime={endTime}&queue={queue}&type={type}&start={start}&count={count}

    try:
        url_params = req.path.split("/")

        region = url_params[1]
        puuid = url_params[2]

        if not region or not puuid:
            raise Exception("Missing region or puuid")
    except:
        return https_fn.Response(
            json.dumps({"error": "Invalid request data"}), status=400
        )

    if not region in regions.api_regions_1:
        return https_fn.Response(json.dumps({"error": "Invalid region"}), status=400)

    region = regions.api_regions_1[region].lower()

    if len(req.args):
        optional_keys = ["startTime", "endTime", "queue", "type", "start", "count"]
        optional_params = help_functions.get_optional_params(req.args, optional_keys)

        request_url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?{optional_params}"

    else:
        request_url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"

    try:
        response = requests.get(
            request_url,
            headers={"X-Riot-Token": firebase_init.app.options.get("riot_api_key")},
        )

        if response.status_code != 200:
            return https_fn.Response(
                json.dumps(response.json()), status=response.status_code
            )

        return https_fn.Response(json.dumps(response.json()), status=200)

    except Exception as e:
        return https_fn.Response(
            json.dumps({"Riot API error": f"Error occurred: {str(e)}"}), status=500
        )


@https_fn.on_request(region="europe-central2", cors=cors_get_options)
def accounts_in_all_regions(
    req: https_fn.Request,
) -> https_fn.Response:
    # url: /accounts_in_all_regions/{gameName}/{tagLine}

    try:
        url_params = req.path.split("/")

        game_name = url_params[1]
        tag_line = url_params[2]

        if not game_name or not tag_line:
            raise Exception("Missing gameName or tagLine")
    except:
        return https_fn.Response(
            json.dumps({"error": "Invalid request data"}), status=400
        )

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

    try:
        firebase_match_data = firestore_functions.get_match_data_from_firebase(match_id)

        if firebase_match_data:
            return https_fn.Response(json.dumps(firebase_match_data), status=200)
    except Exception as e:
        return https_fn.Response(
            json.dumps({"Firebase error": f"Error occurred: {str(e)}"}), status=500
        )

    request_url = (
        f"https://{request_region}.api.riotgames.com/lol/match/v5/matches/{match_id}"
    )

    try:
        response = requests.get(
            request_url,
            headers={"X-Riot-Token": firebase_init.app.options.get("riot_api_key")},
        )

        if response.status_code != 200:
            return https_fn.Response(
                json.dumps(response.json()), status=response.status_code
            )

        response_data = response.json()

        match_data = MatchData.from_dict(response_data).to_dict()
        firestore_functions.save_match_to_firebase(match_data)

        return https_fn.Response(json.dumps(match_data), status=200)

    except Exception as e:
        return https_fn.Response(
            json.dumps({"Riot API error": f"Error occurred: {str(e)}"}), status=500
        )


@https_fn.on_request(region="europe-central2", cors=cors_get_options)
def active_pro_games(
    req: https_fn.Request,
) -> https_fn.Response:
    # url: /active_pro_games

    tier_1_teams = ["G2", "T1", "GENG", "TL"]
    tier_2_teams = ["FNC", "C9", "HLE", "DK"]
    tier_3_teams = ["TH", "KT", "FLY", "MAD"]

    active_pro_games = []

    for teams_in_tier in [tier_1_teams, tier_2_teams, tier_3_teams]:
        tier_games = firestore_functions.get_active_games_per_team(teams_in_tier)

        active_pro_games.extend(tier_games)

        if len(active_pro_games) >= 4:
            break

    mapped_games = list(
        map(lambda game: {"player": game[0], "game": game[1]}, active_pro_games)
    )
    return https_fn.Response(json.dumps(mapped_games), status=200)


@https_fn.on_request(region="europe-central2", cors=cors_get_options)
def add_account(
    req: https_fn.Request,
) -> https_fn.Response:
    # url: /add_account/region/gameName/tagLine

    try:
        url_params = req.path.split("/")

        region = url_params[1]
        game_name = url_params[2]
        tag_line = url_params[3]

        if not region or not game_name or not tag_line:
            raise Exception("Missing region, gameName or tagLine")
    except:
        return https_fn.Response(
            json.dumps({"error": "Invalid request data"}), status=400
        )

    try:
        if firestore_account := firestore_functions.get_account_from_firestore(
            region=region, game_name=game_name, tag_line=tag_line
        ):
            return https_fn.Response(
                json.dumps(
                    {
                        "error": "Account already exists",
                        "account": firestore_account,
                    }
                ),
                status=200,
            )

        if not (
            api_account := firestore_functions.get_api_account(
                region, game_name=game_name, tag_line=tag_line
            )
        ):
            return https_fn.Response(
                json.dumps({"error": "Account not found"}), status=404
            )

        firestore_functions.save_documents_to_collection("accounts", [api_account])

        return https_fn.Response(
            json.dumps(
                {
                    "message": "Account added",
                    "account": api_account,
                }
            ),
            status=200,
        )

    except Exception as e:
        return https_fn.Response(
            json.dumps({"Firebase error": f"Error occurred: {str(e)}"}), status=500
        )


@scheduler_fn.on_schedule(region="europe-central2", schedule="every day 03:00")
def current_version(
    event: scheduler_fn.ScheduledEvent,
) -> None:
    scheduled_functions.current_version(event)


@scheduler_fn.on_schedule(region="europe-central2", schedule="every day 03:00")
def rune_description(event: scheduler_fn.ScheduledEvent) -> None:
    scheduled_functions.rune_description(event)


@scheduler_fn.on_schedule(region="europe-central2", schedule="every day 03:02")
def update_LEC_accounts(event: scheduler_fn.ScheduledEvent) -> None:
    scheduled_functions.update_pro_accounts("LEC")


@scheduler_fn.on_schedule(region="europe-central2", schedule="every day 03:04")
def update_LCS_accounts(event: scheduler_fn.ScheduledEvent) -> None:
    scheduled_functions.update_pro_accounts("LCS")


@scheduler_fn.on_schedule(region="europe-central2", schedule="every day 03:06")
def update_LCK_accounts(event: scheduler_fn.ScheduledEvent) -> None:
    scheduled_functions.update_pro_accounts("LCK")


@scheduler_fn.on_schedule(region="europe-central2", schedule="every day 03:08")
def update_LPL_accounts(event: scheduler_fn.ScheduledEvent) -> None:
    scheduled_functions.update_pro_accounts("LPL")


@scheduler_fn.on_schedule(region="europe-central2", schedule="every day 03:12")
def update_player_game_names(event: scheduler_fn.ScheduledEvent) -> None:
    scheduled_functions.update_player_game_names()


@scheduler_fn.on_schedule(region="europe-central2", schedule="every hour")
def update_bootcamp_leaderboard(event: scheduler_fn.ScheduledEvent) -> None:
    scheduled_functions.update_bootcamp_leaderboard()


@https_fn.on_request(region="europe-central2", cors=cors_get_options)
def request_update_bootcamp_leaderboard(
    req: https_fn.Request,
) -> https_fn.Response:
    # url: /request_update_bootcamp_leaderboard

    try:
        scheduled_functions.update_bootcamp_leaderboard()
        return https_fn.Response(
            json.dumps({"message": "Leaderboard updated"}), status=200
        )
    except Exception as e:
        return https_fn.Response(
            json.dumps({"error": f"Error occurred: {str(e)}"}), status=500
        )


@scheduler_fn.on_schedule(region="europe-central2", schedule="every 10 minutes")
def check_for_active_pro_games(event: scheduler_fn.ScheduledEvent) -> None:
    tier_1_teams = ["G2", "T1", "GENG", "BLG"]
    tier_2_teams = ["FNC", "LNG", "HLE", "DK"]
    tier_3_teams = ["FLY", "MAD", "TES", "LNG", "TL"]

    active_pro_games = []

    for teams_in_tier in [tier_1_teams, tier_2_teams, tier_3_teams]:
        tier_games = firestore_functions.get_active_games_per_team(teams_in_tier)

        active_pro_games.extend(tier_games)

    firestore_functions.clear_collection("active_pro_games")
    firestore_functions.save_documents_to_collection(
        "active_pro_games",
        active_pro_games,
    )
