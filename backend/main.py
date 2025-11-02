import contextlib
import os

import dotenv
import fastapi
import firebase_admin
import httpx
from account.routes import router as account_router
from champions.routes import router as champion_router
from database.database import initialize_app
from fastapi.middleware.gzip import GZipMiddleware
from league.routes import router as league_router
from match.routes import router as match_router
from pro_players.routes import router as pro_players_router
from runes.routes import router as runes_router

dotenv.load_dotenv()


def init_app():
    # CORS is handled by nginx reverse proxy

    app.add_middleware(GZipMiddleware, minimum_size=500)

    routers = [
        account_router,
        match_router,
        champion_router,
        league_router,
        runes_router,
        pro_players_router,
    ]

    for router in routers:
        app.include_router(router)


def initialize_httpx_client() -> httpx.AsyncClient:
    client = httpx.AsyncClient(
        timeout=httpx.Timeout(10.0, connect=5.0),
        limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
        http2=True,
    )

    return client


@contextlib.asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    try:
        firebase_app, firestore_client = initialize_app()

        app.state.firestore_client = firestore_client
        app.state.firebase_app = firebase_app

        httpx_client = initialize_httpx_client()
        app.state.httpx_client = httpx_client
    except Exception as e:
        raise e

    yield

    firebase_admin.delete_app(firebase_app)
    await httpx_client.aclose()


app = fastapi.FastAPI(lifespan=lifespan)

init_app()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
