import asyncio
import typing

import account.functions as account_functions
import database.database as db
import database.functions as db_functions
import helpers.regions as regions
import httpx

from . import models


async def create_or_update_player(
    client: httpx.AsyncClient,
    player: models.ProPlayer,
    account_data: typing.Optional[typing.Dict[str, str]] = None,
):
    found_player = await get_player(player.region, player.team, player.player)

    if account_data is not None:
        new_account = await account_functions.create_account(client, **account_data)

        if new_account is not None and (
            found_player is None or new_account.puuid not in found_player.puuid
        ):
            player.puuid.append(new_account.puuid)

    if found_player is None:
        db_functions.add_or_update_document(
            f"pro_players/{player.region.upper()}/{player.team.upper()}",
            player.model_dump(),
            document_id=player.player.lower(),
        )

    else:
        new_puuids = [
            puuid for puuid in player.puuid if puuid not in found_player.puuid
        ]

        for new_puuid in new_puuids:
            await account_functions.create_account(client, puuid=new_puuid)

            found_player.puuid.append(new_puuid)
            db_functions.add_or_update_document(
                "pro_players",
                found_player.model_dump(),
                document_id=found_player.player.lower(),
            )


async def get_players_for_region(
    region: str,
) -> typing.Dict[str, typing.List[models.ProPlayer]]:
    region = region.upper()

    if region not in regions.pro_regions:
        return {}

    teams = regions.teams_per_region[region]

    jobs = [get_player_for_team(region, team) for team in teams]

    results = await asyncio.gather(*jobs)

    players = {result[0].team: result for result in results}

    return players


async def get_player_for_team(region: str, team: str) -> typing.List[models.ProPlayer]:
    region = region.upper()
    team = team.upper()

    if region not in regions.pro_regions:
        return []

    if team not in regions.teams_per_region[region]:
        return []

    players = db_functions.get_pro_team_documents(region, team)  # type: ignore

    return players


async def get_player(
    region: str, team: str, player: str
) -> typing.Optional[models.ProPlayer]:
    players = await get_player_for_team(region, team)

    found_player = next(
        (item for item in players if item.player.lower() == player.lower()), None
    )

    return found_player


def get_account_names() -> typing.Optional[typing.Dict[str, typing.Dict[str, str]]]:
    document = db_functions.get_document("pro_players", "account_names")

    return document  # type: ignore


def get_bootcamp_accounts() -> typing.List[models.BootcampAccount]:
    collection = db.get_collection("eu_bootcamp_leaderboard")

    if collection is None:
        return []

    accounts = collection.stream()

    return [models.BootcampAccount(**account.to_dict()) for account in accounts]


def get_live_streams() -> typing.Optional[typing.Dict[str, typing.Dict[str, str]]]:
    document = db_functions.get_document("live_streams", "live")

    return document  # type: ignore


def get_not_live_streams() -> typing.Optional[typing.Dict[str, typing.Dict[str, str]]]:
    document = db_functions.get_document("live_streams", "not_live")

    return document  # type: ignore
