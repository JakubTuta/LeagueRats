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
    return https_fn.Response(json.dumps("Hello world"), status=200)
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
            request_url, headers={"X-Riot-Token": app.options["riot_api_key"]}
        )

        return https_fn.Response(
            json.dumps(response.json()), status=response.status_code
        )

    except Exception as e:
        return https_fn.Response(json.dumps({"error": "Error occurred"}), status=500)
