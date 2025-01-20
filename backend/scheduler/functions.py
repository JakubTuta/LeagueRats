import asyncio
import re
import typing

import account.functions as account_functions
import account.models as account_models
import database.functions as db_functions
import helpers.regions as regions
import helpers.riot_api as riot_api
import httpx


async def update_current_version():
    async with httpx.AsyncClient() as client:
        request_url = "https://ddragon.leagueoflegends.com/api/versions.json"

        response = await client.get(request_url)

    if response.status_code == 200:
        version = response.json()[0]

        db_functions.add_or_update_document(
            "help", {"version": version}, document_id="version"
        )


async def update_rune_description() -> typing.Optional[dict]:
    current_version_doc = db_functions.get_document("help", "version")

    if current_version_doc is None:
        return

    current_version = current_version_doc["version"]
    languages = ["en_US"]
    rune_data_per_language = {}

    async with httpx.AsyncClient() as client:
        for language in languages:
            request_url = f"https://ddragon.leagueoflegends.com/cdn/{current_version}/data/{language}/runesReforged.json"

            response = await client.get(request_url)

            if response.status_code == 200:
                language_key = language.split("_")[0]
                rune_data_per_language[language_key] = response.json()

    _save_rune_data(rune_data_per_language)


async def update_champion_data():
    current_version_doc = db_functions.get_document("help", "version")

    if current_version_doc is None:
        return

    current_version = current_version_doc["version"]

    async with httpx.AsyncClient() as client:
        request_url = f"https://ddragon.leagueoflegends.com/cdn/{current_version}/data/en_US/champion.json"

        response = await client.get(request_url)

    if response.status_code == 200:
        champion_data = response.json()["data"]

        _save_champion_data(champion_data)


async def update_pro_accounts():
    jobs = [update_pro_accounts_for_region(region) for region in regions.pro_regions]

    await asyncio.gather(*jobs)


async def update_pro_accounts_for_region(region):
    jobs = [
        _update_pro_accounts_for_team(region, team)
        for team in regions.teams_per_region[region]
    ]

    documents = await asyncio.gather(*jobs)

    joined_documents = []
    for document in documents:
        joined_documents.extend(document)

    for document in joined_documents:
        db_functions.add_or_update_document("accounts", document)


async def update_player_game_names():
    jobs = [
        _get_player_names_for_team(region, team)
        for region in regions.pro_regions
        for team in regions.teams_per_region[region]
    ]

    player_game_names = await asyncio.gather(*jobs)

    player_game_names_dict = {}
    for player_names in player_game_names:
        player_game_names_dict.update(player_names)

    db_functions.add_or_update_document(
        "pro_players", player_game_names_dict, document_id="account_names"
    )


async def update_leaderboard():
    jobs = [
        _update_leaderboard_for_region(region) for region in regions.important_regions
    ]

    await asyncio.gather(*jobs)


def _clear_text(text):
    text = text.encode().decode("unicode_escape")
    text = text.encode("latin1").decode("utf-8")

    clean_text = re.sub(r"<.*?>", "", text)
    clean_text = re.sub(r"&([a-zA-Z0-9]+);", r"\1", clean_text)

    return clean_text


def _save_rune_data(rune_data_per_language):
    for rune_data in rune_data_per_language.values():
        for rune_data_item in rune_data:
            for slot in rune_data_item["slots"]:
                for rune in slot["runes"]:
                    rune["shortDesc"] = _clear_text(rune["shortDesc"])
                    rune["longDesc"] = _clear_text(rune["longDesc"])

    db_functions.add_or_update_document(
        "help", rune_data_per_language, document_id="runes"
    )


def _save_champion_data(champions_data):
    mapped_champions = {
        champion_data["key"]: {
            "title": champion_data["name"],
            "value": champion_data["id"],
        }
        for champion_data in champions_data.values()
    }

    db_functions.add_or_update_document(
        "help", mapped_champions, document_id="champions"
    )


async def _get_player_names_for_team(region, team):
    player_docs = db_functions.get_pro_team_documents(region, team)

    documents = {
        puuid: {
            "player": player["player"],
            "team": team,
            "region": region,
        }
        for player in player_docs
        for puuid in player["puuid"]
    }
    return documents


async def _update_pro_accounts_for_team(region, team):
    player_documents = db_functions.get_pro_team_documents(region, team)

    documents = []

    client = httpx.AsyncClient()

    for player in player_documents:
        for puuid in player["puuid"]:
            if (
                database_account := account_functions.get_account_from_database(
                    puuid=puuid
                )
            ) is None:
                continue

            if (
                api_account := await account_functions.get_account_from_api(
                    client, database_account.region, puuid=puuid
                )
            ) is None:
                continue

            if any(
                api_account.model_dump()[key] != database_account.model_dump()[key]
                for key in database_account.model_dump()
                if key in api_account.model_dump()
            ):
                documents.append(api_account.model_dump())

    await client.aclose()

    return documents


async def _update_leaderboard_for_region(region):
    region_row = regions.get_region(region)

    if region_row is None:
        return

    request_region = region_row[1]
    request_url = f"https://{request_region}.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5"

    httpx_client = httpx.AsyncClient()
    response = await httpx_client.get(request_url, headers=riot_api.get_headers())

    if response.status_code != 200:
        return

    entries = response.json()["entries"]
    leaderboard_accounts = []

    for index, entry in enumerate(entries, start=1):
        if (
            account := await account_functions.get_account(
                httpx_client, summoner_id=entry["summonerId"], save_account=True
            )
        ) is None:
            return

        model = account_models.LeaderboardAccount(
            **account.model_dump(),
            rank=index,
            league="CHALLENGER",
        )
        leaderboard_accounts.append(model)

    await httpx_client.aclose()

    db_functions.clear_collection(f"leaderboard/{region}/CHALLENGER")
    db_functions.save_leaderboard_accounts(region, "CHALLENGER", leaderboard_accounts)
