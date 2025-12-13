import contextlib
import logging
import os

import dotenv
import fastapi
import ledger
import ledger.integrations.fastapi as ledger_fastapi
import modules
import utils
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

dotenv.load_dotenv()


@contextlib.asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    utils.get_redis_client()
    utils.get_firestore_client()
    utils.get_http_client()
    utils.get_riot_api_client()

    logger.info("application_started")

    yield

    logger.info("application_shutting_down")

    await utils.close_redis_client()
    await utils.close_firestore_client()
    await utils.close_http_client()
    await utils.close_riot_api_client()


app = fastapi.FastAPI(
    lifespan=lifespan,
    title="League Rats API",
    version="3.0.0",
    description="API for League of Legends data",
    contact={
        "name": "League Rats",
        "url": "https://leaguerats.net",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    redirect_slashes=False,
)

if os.getenv("ENVIRONMENT", "development") == "development":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "https://leaguerats.net",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.add_middleware(GZipMiddleware, minimum_size=500)

ledger_client = ledger.LedgerClient(api_key=os.getenv("LEDGER_API_KEY"))  # type: ignore
app.add_middleware(
    ledger_fastapi.LedgerMiddleware,
    ledger_client=ledger_client,
)


routers = [
    modules.account_router,
    modules.champions_router,
    modules.league_router,
    modules.match_router,
    modules.pro_players_router,
    modules.runes_router,
]

for router in routers:
    app.include_router(router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/health")
async def health_check():
    redis_client = utils.get_redis_client()
    redis_healthy = await redis_client.ping()

    return {
        "status": "healthy",
        "redis": "connected" if redis_healthy else "disconnected",
    }


@app.post("/admin/clear-cache")
async def clear_cache():
    redis_client = utils.get_redis_client()

    await redis_client.flush_db()

    utils.clear_all_caches()

    logger.info("all_caches_cleared")

    return {
        "status": "success",
        "message": "All caches (Redis and in-memory) have been cleared",
    }
