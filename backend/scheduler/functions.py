import asyncio
import re
import typing

import account.functions as account_functions
import account.models as account_models
import database.functions as db_functions
import helpers.regions as regions
import helpers.riot_api as riot_api
import httpx
import league.models as league_models
import match.functions as match_functions


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

    if not isinstance(current_version_doc, dict):
        return

    current_version = current_version_doc["version"]

    async with httpx.AsyncClient() as client:
        request_url = f"https://ddragon.leagueoflegends.com/cdn/{current_version}/data/en_US/runesReforged.json"

        response = await client.get(request_url)

        if response.status_code == 200:
            _save_rune_data(response.json())


async def update_champion_data():
    current_version_doc = db_functions.get_document("help", "version")

    if not isinstance(current_version_doc, dict):
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
    joined_documents = [doc for sublist in documents for doc in sublist]

    for document in joined_documents:
        db_functions.add_or_update_document("accounts", document)


async def update_player_game_names():
    jobs = [
        _get_player_names_for_team(region, team)
        for region in regions.pro_regions
        for team in regions.teams_per_region[region]
    ]

    player_game_names = await asyncio.gather(*jobs)

    player_game_names_dict = {
        player_name: details
        for player_names in player_game_names
        for player_name, details in player_names.items()
    }

    db_functions.add_or_update_document(
        "pro_players", player_game_names_dict, document_id="account_names"
    )


async def update_leaderboard():
    jobs = [
        _update_leaderboard_for_region(region) for region in regions.important_regions
    ]

    await asyncio.gather(*jobs)


async def update_live_streams():
    client = httpx.AsyncClient()

    jobs = [
        _get_live_streams_for_team(client, region, team)
        for region in regions.pro_regions
        for team in regions.teams_per_region[region]
    ]

    results = await asyncio.gather(*jobs)
    live_streams_dict = {k: v for result in results for k, v in result[0].items()}
    not_live_streams_dict = {k: v for result in results for k, v in result[1].items()}

    await client.aclose()

    db_functions.add_or_update_document(
        "live_streams", live_streams_dict, document_id="live"
    )
    db_functions.add_or_update_document(
        "not_live_streams", not_live_streams_dict, document_id="not_live"
    )


async def update_active_games():
    teams = (
        ("G2", "LEC"),
        ("FNC", "LEC"),
        ("T1", "LCK"),
        ("GENG", "LCK"),
        ("BLG", "LPL"),
        ("IG", "LPL"),
        ("C9", "LCS"),
        ("TL", "LCS"),
    )

    client = httpx.AsyncClient()

    jobs = [_get_active_games_for_team(client, team, region) for team, region in teams]

    results = await asyncio.gather(*jobs)
    active_games = [game for result in results for game in result]

    db_functions.clear_collection("active_pro_games")
    for game in active_games:
        db_functions.add_or_update_document(
            "active_pro_games", game, document_id=game.metadata.matchId
        )

    await client.aclose()


async def update_champion_history():
    teams = (
        ("G2", "LEC"),
        ("FNC", "LEC"),
        ("T1", "LCK"),
        ("GENG", "LCK"),
        ("BLG", "LPL"),
        ("IG", "LPL"),
        ("C9", "LCS"),
        ("TL", "LCS"),
    )

    client = httpx.AsyncClient()

    jobs = [
        _update_champion_history_for_team(client, region, team)
        for team, region in teams
    ]

    results = await asyncio.gather(*jobs)

    all_champions_data = {}
    for result in results:
        for champion_id, champion_data in result.items():
            if champion_id in all_champions_data:
                all_champions_data[champion_id]["stats"]["games"] += champion_data[
                    "stats"
                ]["games"]
                all_champions_data[champion_id]["stats"]["wins"] += champion_data[
                    "stats"
                ]["wins"]
                all_champions_data[champion_id]["stats"]["losses"] += champion_data[
                    "stats"
                ]["losses"]
                all_champions_data[champion_id]["matches"].append(
                    *champion_data["matches"]
                )

            else:
                all_champions_data[champion_id] = champion_data

    db_functions.update_champion_history(all_champions_data)

    await client.aclose()


def _clear_text(text):
    text = text.encode().decode("unicode_escape")
    text = text.encode("latin1").decode("utf-8")

    clean_text = re.sub(r"<.*?>", "", text)
    clean_text = re.sub(r"&([a-zA-Z0-9]+);", r"\1", clean_text)

    return clean_text


def _save_rune_data(rune_data):
    for rune_data_item in rune_data:
        for slot in rune_data_item["slots"]:
            for rune in slot["runes"]:
                rune["shortDesc"] = _clear_text(rune["shortDesc"])
                rune["longDesc"] = _clear_text(rune["longDesc"])

    db_functions.add_or_update_document(
        "help", {"data": rune_data}, document_id="runes1"
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
            "player": player.player,
            "team": team,
            "region": region,
        }
        for player in player_docs
        for puuid in player.puuid
    }
    return documents


async def _update_pro_accounts_for_team(region, team):
    player_documents = db_functions.get_pro_team_documents(region, team)

    documents = []

    client = httpx.AsyncClient()

    for player in player_documents:
        for puuid in player.puuid:
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

        model = league_models.LeaderboardEntry(
            **account.model_dump(),
            rank=index,
            league="CHALLENGER",
        )
        leaderboard_accounts.append(model)

    await httpx_client.aclose()

    db_functions.clear_collection(f"leaderboard/{region}/CHALLENGER")
    db_functions.save_leaderboard_accounts(region, "CHALLENGER", leaderboard_accounts)


async def _get_live_streams_for_team(client: httpx.AsyncClient, region, team):
    player_docs = db_functions.get_pro_team_documents(region, team)
    live_streams = {}
    not_live_streams = {}

    for player in player_docs:
        player_name = player.player

        if (
            player.socialMedia
            and (twitch_name := player.socialMedia.get("twitch", None)) is not None
        ):
            if await _check_if_channel_is_live(client, twitch_name):
                live_streams[player_name] = {
                    "player": player_name,
                    "team": team,
                    "region": player.region,
                    "twitch": twitch_name,
                }
            else:
                not_live_streams[player_name] = {
                    "player": player_name,
                    "team": team,
                    "region": player.region,
                    "twitch": twitch_name,
                }

    return live_streams, not_live_streams


async def _check_if_channel_is_live(client: httpx.AsyncClient, channel):
    request_url = f"https://www.twitch.tv/{channel}"
    response = await client.get(request_url)

    contents = response.content.decode("utf-8")

    return "isLiveBroadcast" in contents


async def _get_active_games_for_team(client, team, region):
    active_games = []

    player_docs = db_functions.get_pro_team_documents(region, team)

    for player in player_docs:
        for puuid in player.puuid:
            if (
                account := account_functions.get_account_from_database(puuid=puuid)
            ) is None:
                continue

            if (
                active_match := await match_functions.get_active_match(client, puuid)
            ) is None:
                continue

            active_games.append(active_match)

    return active_games


async def _update_champion_history_for_team(client, region, team):
    player_docs = db_functions.get_pro_team_documents(region, team)
    champion_history = {}

    for player in player_docs:
        for puuid in player.puuid:
            if (
                account := account_functions.get_account_from_database(puuid=puuid)
            ) is None:
                continue

            matches = await match_functions.get_ranked_matches_from_period(
                client, account, 1
            )

            for match in matches:
                player_participant = next(
                    (
                        participant
                        for participant in match.info.participants
                        if participant.puuid == puuid
                    ),
                    None,
                )

                if player_participant is None:
                    continue

                player_champion = player_participant.championId

                match_data = {
                    "player": player.model_dump(),
                    "match": match.model_dump(),
                }

                if player_champion in champion_history:
                    champion_history[player_champion]["stats"]["games"] += 1
                    champion_history[player_champion]["stats"]["wins"] += (
                        1 if player_participant.win else 0
                    )
                    champion_history[player_champion]["stats"]["losses"] += (
                        0 if player_participant.win else 1
                    )
                    champion_history[player_champion]["matches"].append(match_data)

                else:
                    champion_history[player_champion] = {
                        "stats": {
                            "games": 1,
                            "wins": 1 if player_participant.win else 0,
                            "losses": 0 if player_participant.win else 1,
                        },
                        "matches": [match_data],
                    }

    return champion_history
