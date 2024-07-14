import json

import firebase_admin
import firebase_functions
from firebase_functions import https_fn

firebase_admin.initialize_app()

cors_options = firebase_functions.options.CorsOptions(
    cors_methods=["POST", "OPTIONS"],
    cors_origins="*",
)


@https_fn.on_request(region="europe-central2", cors=cors_options)
def test_connection(
    req: https_fn.Request,
) -> https_fn.Response:
    return https_fn.Response(json.dumps("Hello world"), status=200)
