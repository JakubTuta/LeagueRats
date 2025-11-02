import contextlib

import dotenv
import fastapi
import firebase_admin
import httpx
from database.database import initialize_app
from fastapi.middleware.cors import CORSMiddleware

from scheduler.schedules import scheduler

dotenv.load_dotenv()


def init_app():
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            # "http://localhost:3000",
            # "https://leaguerats.net",
            "*"
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def initialize_httpx_client() -> httpx.AsyncClient:
    client = httpx.AsyncClient()

    return client


@contextlib.asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    try:
        firebase_app, firestore_client = initialize_app()
        app.state.firebase_app = firebase_app
        app.state.firestore_client = firestore_client

        httpx_client = initialize_httpx_client()
        app.state.httpx_client = httpx_client
    except Exception as e:
        raise e

    scheduler.start()

    yield

    firebase_admin.delete_app(firebase_app)
    await httpx_client.aclose()
    scheduler.shutdown()


app = fastapi.FastAPI(lifespan=lifespan)

init_app()
