import contextlib

import dotenv
import fastapi
import firebase_admin
import httpx
from account.routes import router as account_router
from champions.routes import router as champion_router
from database.database import initialize_app
from fastapi.middleware.cors import CORSMiddleware
from league.routes import router as league_router
from match.routes import router as match_router
from pro_players.routes import router as pro_players_router
from runes.routes import router as runes_router
from scheduler.schedules import router as scheduler_router
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

    routers = [
        account_router,
        match_router,
        champion_router,
        league_router,
        scheduler_router,
        champion_router,
        runes_router,
        pro_players_router,
    ]

    for router in routers:
        app.include_router(router)


def initialize_httpx_client() -> httpx.AsyncClient:
    client = httpx.AsyncClient()

    return client


@contextlib.asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    try:
        firebase_app, firestore_client = initialize_app()
        app.firebase_app = firebase_app  # type: ignore
        app.firestore_client = firestore_client  # type: ignore

        httpx_client = initialize_httpx_client()
        app.httpx_client = httpx_client  # type: ignore
    except Exception as e:
        raise e

    scheduler.start()

    yield

    firebase_admin.delete_app(firebase_app)
    await httpx_client.aclose()
    scheduler.shutdown()


app = fastapi.FastAPI(lifespan=lifespan)

init_app()
