import fastapi
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from . import functions

timezone = pytz.timezone("EST")

scheduler = AsyncIOScheduler(timezone=timezone)

router = fastapi.APIRouter(prefix="/v2/scheduler")


# GAME DATA


@scheduler.scheduled_job("cron", hour=2, minute=0)
async def update_current_version():
    await functions.update_current_version()


@router.get("/current-version")
async def call_update_current_version():
    await functions.update_current_version()
    return {"message": "Current version updated"}


@scheduler.scheduled_job("cron", hour=2, minute=1)
async def update_rune_description():
    await functions.update_rune_description()


@router.get("/rune-description")
async def call_update_rune_description():
    await functions.update_rune_description()
    return {"message": "Rune description updated"}


@scheduler.scheduled_job("cron", hour=2, minute=1)
async def update_champion_data():
    await functions.update_champion_data()


@router.get("/champion-data")
async def call_update_champion_data():
    await functions.update_champion_data()
    return {"message": "Champion data updated"}


# PRO ACCOUNTS


@scheduler.scheduled_job("cron", hour=2, minute=2)
async def update_pro_accounts_LEC():
    await functions.update_pro_accounts_for_region("LEC")


@scheduler.scheduled_job("cron", hour=2, minute=3)
async def update_pro_accounts_LCS():
    await functions.update_pro_accounts_for_region("LCS")


@scheduler.scheduled_job("cron", hour=2, minute=4)
async def update_pro_accounts_LCK():
    await functions.update_pro_accounts_for_region("LCK")


@scheduler.scheduled_job("cron", hour=2, minute=5)
async def update_pro_accounts_LPL():
    await functions.update_pro_accounts_for_region("LPL")


@router.get("/pro-accounts")
async def call_update_pro_accounts():
    await functions.update_pro_accounts()
    return {"message": "Pro accounts updated"}


@scheduler.scheduled_job("cron", hour=2, minute=6)
async def update_player_game_names():
    await functions.update_player_game_names()


@router.get("/player-game-names")
async def call_update_player_game_names():
    await functions.update_player_game_names()
    return {"message": "Player game names updated"}


@scheduler.scheduled_job("cron", hour=2, minute=7)
async def update_leaderboard():
    await functions.update_leaderboard()


@router.get("/leaderboard")
async def call_update_leaderboard():
    await functions.update_leaderboard()
    return {"message": "Leaderboard updated"}
