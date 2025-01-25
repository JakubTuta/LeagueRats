import os
import typing

import dotenv
import firebase_admin
from firebase_admin import App, firestore
from google.cloud.firestore_v1.client import Client
from google.cloud.firestore_v1.collection import CollectionReference

dotenv.load_dotenv()

service_account = {
    "type": os.getenv("TYPE"),
    "project_id": os.getenv("PROJECT_ID"),
    "private_key_id": os.getenv("PRIVATE_KEY_ID"),
    "private_key": str(os.getenv("PRIVATE_KEY")).replace(r"\n", "\n"),
    "client_email": os.getenv("CLIENT_EMAIL"),
    "client_id": os.getenv("CLIENT_ID"),
    "auth_uri": os.getenv("AUTH_URI"),
    "token_uri": os.getenv("TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("AUTH_PROVIDER_X509_CERT_URL"),
    "client_x509_cert_url": os.getenv("CLIENT_X509_CERT_URL"),
    "universe_domain": os.getenv("UNIVERSE_DOMAIN"),
}

config = {
    "apiKey": os.getenv("API_KEY"),
    "authDomain": os.getenv("AUTH_DOMAIN"),
    "projectId": os.getenv("PROJECT_ID"),
    "storageBucket": os.getenv("STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("MESSAGING_SENDER_ID"),
    "appId": os.getenv("APP_ID"),
    "measurementId": os.getenv("MEASUREMENT_ID"),
    "riot_api_key": os.getenv("RIOT_API_KEY"),
}


collections: typing.Dict[str, CollectionReference] = {}
firebase_app: typing.Optional[App] = None
firestore_client: typing.Optional[Client] = None


def add_collection(collection_name: str):
    if firestore_client is None:
        return

    global collections

    collections[collection_name] = firestore_client.collection(collection_name)


def get_collection(collection_name: str) -> typing.Optional[CollectionReference]:
    if firestore_client is None:
        return None

    collection = firestore_client.collection(collection_name)

    return collection


def get_firestore_client() -> None | Client:
    return firestore_client


def initialize_app() -> tuple[App, Client]:
    global firebase_app
    global firestore_client

    credentials = firebase_admin.credentials.Certificate(service_account)
    firebase_app = firebase_admin.initialize_app(credentials, config, "League Rats")

    firestore_client = firestore.client(firebase_app)

    collection_names = [
        "accounts",
        "help",
        "match_history",
        "pro_players",
        "active_pro_games",
        "eu_bootcamp_leaderboard",
        "live_streams",
        "champion_history",
        "leaderboard/EUW/CHALLENGER",
        "leaderboard/EUNE/CHALLENGER",
        "leaderboard/NA/CHALLENGER",
        "leaderboard/KR/CHALLENGER",
    ]

    for collection_name in collection_names:
        add_collection(collection_name)

    return firebase_app, firestore_client
