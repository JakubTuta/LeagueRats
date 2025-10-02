from datetime import datetime

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from . import functions

timezone = pytz.timezone("EST")

scheduler = AsyncIOScheduler(timezone=timezone)


# GAME DATA


@scheduler.scheduled_job("cron", hour=2, minute=0)
async def update_current_version():
    print(
        f"Starting update_current_version at {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )
    try:
        await functions.update_current_version()
        print("update_current_version ended correctly")
    except Exception as e:
        print(f"update_current_version ended with an error: {e}")


@scheduler.scheduled_job("cron", hour=2, minute=1)
async def update_rune_description():
    print(
        f"Starting update_rune_description at {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )
    try:
        await functions.update_rune_description()
        print("update_rune_description ended correctly")
    except Exception as e:
        print(f"update_rune_description ended with an error: {e}")


@scheduler.scheduled_job("cron", hour=2, minute=1)
async def update_champion_data():
    print(
        f"Starting update_champion_data at {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )
    try:
        await functions.update_champion_data()
        print("update_champion_data ended correctly")
    except Exception as e:
        print(f"update_champion_data ended with an error: {e}")


# PRO ACCOUNTS


@scheduler.scheduled_job("cron", hour=2, minute=2)
async def update_pro_accounts_LEC():
    print(
        f"Starting update_pro_accounts_LEC at {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )
    try:
        await functions.update_pro_accounts_for_region("LEC")
        print("update_pro_accounts_LEC ended correctly")
    except Exception as e:
        print(f"update_pro_accounts_LEC ended with an error: {e}")


@scheduler.scheduled_job("cron", hour=2, minute=3)
async def update_pro_accounts_LCS():
    print(
        f"Starting update_pro_accounts_LCS at {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )
    try:
        await functions.update_pro_accounts_for_region("LCS")
        print("update_pro_accounts_LCS ended correctly")
    except Exception as e:
        print(f"update_pro_accounts_LCS ended with an error: {e}")


@scheduler.scheduled_job("cron", hour=2, minute=4)
async def update_pro_accounts_LCK():
    print(
        f"Starting update_pro_accounts_LCK at {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )
    try:
        await functions.update_pro_accounts_for_region("LCK")
        print("update_pro_accounts_LCK ended correctly")
    except Exception as e:
        print(f"update_pro_accounts_LCK ended with an error: {e}")


@scheduler.scheduled_job("cron", hour=2, minute=5)
async def update_pro_accounts_LPL():
    print(
        f"Starting update_pro_accounts_LPL at {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )
    try:
        await functions.update_pro_accounts_for_region("LPL")
        print("update_pro_accounts_LPL ended correctly")
    except Exception as e:
        print(f"update_pro_accounts_LPL ended with an error: {e}")


@scheduler.scheduled_job("cron", hour=2, minute=6)
async def update_player_game_names():
    print(
        f"Starting update_player_game_names at {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )
    try:
        await functions.update_player_game_names()
        print("update_player_game_names ended correctly")
    except Exception as e:
        print(f"update_player_game_names ended with an error: {e}")


# LEADERBOARD


@scheduler.scheduled_job("cron", hour=2, minute=7)
async def update_leaderboard():
    print(f"Starting update_leaderboard at {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    try:
        await functions.update_leaderboard()
        print("update_leaderboard ended correctly")
    except Exception as e:
        print(f"update_leaderboard ended with an error: {e}")


# LIVE STREAMS


@scheduler.scheduled_job("interval", minutes=10)
async def update_live_streams():
    print(
        f"Starting update_live_streams at {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )
    try:
        await functions.update_live_streams()
        print("update_live_streams ended correctly")
    except Exception as e:
        print(f"update_live_streams ended with an error: {e}")


# ACTIVE GAMES


@scheduler.scheduled_job("interval", minutes=10)
async def update_active_games():
    print(
        f"Starting update_active_games at {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )
    try:
        await functions.update_active_games()
        print("update_active_games ended correctly")
    except Exception as e:
        print(f"update_active_games ended with an error: {e}")


# CHAMPION HISTORY


@scheduler.scheduled_job("interval", hours=1)
async def update_champion_history():
    print(
        f"Starting update_champion_history at {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )
    try:
        await functions.update_champion_history()
        print("update_champion_history ended correctly")
    except Exception as e:
        print(f"update_champion_history ended with an error: {e}")
