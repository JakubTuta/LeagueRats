import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from . import functions

timezone = pytz.timezone("EST")

scheduler = AsyncIOScheduler(timezone=timezone)


# GAME DATA


@scheduler.scheduled_job("cron", hour=2, minute=0)
async def update_current_version():
    await functions.update_current_version()


@scheduler.scheduled_job("cron", hour=2, minute=1)
async def update_rune_description():
    await functions.update_rune_description()


@scheduler.scheduled_job("cron", hour=2, minute=1)
async def update_champion_data():
    await functions.update_champion_data()


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


@scheduler.scheduled_job("cron", hour=2, minute=6)
async def update_player_game_names():
    await functions.update_player_game_names()


# LEADERBOARD


@scheduler.scheduled_job("cron", hour=2, minute=7)
async def update_leaderboard():
    await functions.update_leaderboard()


# LIVE STREAMS


@scheduler.scheduled_job("interval", minutes=10)
async def update_live_streams():
    await functions.update_live_streams()


# ACTIVE GAMES


@scheduler.scheduled_job("interval", minutes=10)
async def update_active_games():
    await functions.update_active_games()


# CHAMPION HISTORY


@scheduler.scheduled_job("interval", hours=1)
async def update_champion_history():
    await functions.update_champion_history()
