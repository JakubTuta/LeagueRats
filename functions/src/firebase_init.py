import os

import dotenv
import firebase_admin
from firebase_admin import firestore

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


collections = {}
app = None
firestore_client = None


def add_collection(collection_name):
    global collections

    if not firestore_client:
        return

    collections[collection_name] = firestore_client.collection(collection_name)


def initialize_app():
    global app
    global firestore_client

    credentials = firebase_admin.credentials.Certificate(service_account)
    app = firebase_admin.initialize_app(credentials, config, "League Rats")

    firestore_client = firestore.client(app)

    collection_names = [
        "accounts",
        "help",
        "match_history",
        "pro_players",
        "active_pro_games",
        "eu_bootcamp_leaderboard",
        "live_streams",
    ]

    for collection_name in collection_names:
        add_collection(collection_name)
