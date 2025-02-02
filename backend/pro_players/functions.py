import asyncio
import typing

import account.functions as account_functions
import database.database as db
import database.functions as db_functions
import helpers.regions as regions
import httpx
import match.functions as match_functions
import match.models as match_models

from . import models


async def get_player_history_stats(
    client: httpx.AsyncClient, team: str, player: str, amount: int
) -> typing.Dict[int, models.ChampionStats]:
    if (region := _find_region_for_team(team)) is None:
        return {}

    if (found_player := await get_player(region, team, player)) is None:
        return {}

    matches = await _get_match_history_for_player(found_player, amount, client)

    champion_stats: typing.Dict[int, models.ChampionStats] = {}

    for match in matches:
        if (
            player_participant := next(
                (
                    participant
                    for participant in match.info.participants
                    if participant.puuid in found_player.puuid
                ),
                None,
            )
        ) is None:
            continue

        champion_id = player_participant.championId

        if champion_id not in champion_stats:
            champion_stats[champion_id] = models.ChampionStats(
                kills=0, deaths=0, assists=0, wins=0, losses=0
            )

        champion_stats[champion_id].kills += player_participant.kills
        champion_stats[champion_id].deaths += player_participant.deaths
        champion_stats[champion_id].assists += player_participant.assists
        champion_stats[champion_id].wins += 1 if player_participant.win else 0
        champion_stats[champion_id].losses += 1 if not player_participant.win else 0

    return champion_stats


async def create_or_update_player(
    client: httpx.AsyncClient,
    player: models.ProPlayer,
    account_data: typing.Optional[typing.Dict[str, str]] = None,
):
    found_player = await get_player(player.region, player.team, player.player)

    if (
        account_data is not None
        and (
            new_account := await account_functions.create_account(
                client, **account_data
            )
        )
        is not None
    ):
        if found_player is not None and new_account.puuid not in found_player.puuid:
            player.puuid = found_player.puuid + [new_account.puuid]

        elif found_player is None:
            player.puuid = [new_account.puuid]

    db_functions.add_or_update_document(
        f"pro_players/{player.region.upper()}/{player.team.upper()}",
        player.model_dump(),
        document_id=player.player.lower(),
    )


async def get_all_players() -> (
    typing.Dict[str, typing.Dict[str, typing.List[models.ProPlayer]]]
):
    players: typing.Dict[str, typing.Dict[str, typing.List[models.ProPlayer]]] = {}

    for region in regions.pro_regions:
        players[region] = {}

        for team in regions.teams_per_region[region]:  # type: ignore
            player_data = await get_players_for_team(region, team)
            players[region][team] = player_data

    return players


async def get_players_for_region(
    region: str,
) -> typing.Dict[str, typing.List[models.ProPlayer]]:
    region = region.upper()

    if region not in regions.pro_regions:
        return {}

    teams = regions.teams_per_region[region]  # type: ignore

    jobs = [get_players_for_team(region, team) for team in teams]

    results = await asyncio.gather(*jobs)

    players = {result[0].team: result for result in results}

    return players


async def get_players_for_team(region: str, team: str) -> typing.List[models.ProPlayer]:
    region = region.upper()
    team = team.upper()

    if region not in regions.pro_regions:
        return []

    if team not in regions.teams_per_region[region]:  # type: ignore
        return []

    players = db_functions.get_pro_team_documents(region, team)  # type: ignore

    return players


async def get_player(
    region: str, team: str, player: str
) -> typing.Optional[models.ProPlayer]:
    player = player.lower()
    players = await get_players_for_team(region, team)

    found_player = next(
        (item for item in players if item.player.lower() == player), None
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


async def transfer_player(
    player: str, from_team: str, to_team: str
) -> typing.Optional[models.ProPlayer]:
    from_region = _find_region_for_team(from_team)
    to_region = _find_region_for_team(to_team)
    if from_region is None or to_region is None:
        return None

    if (found_player := await get_player(from_region, from_team, player)) is None:
        return None

    if not db_functions.delete_document(
        f"pro_players/{from_region}/{from_team}", player.lower()
    ):
        return None

    found_player.team = to_team
    found_player.region = to_region

    if (
        db_functions.add_or_update_document(
            f"pro_players/{to_region}/{to_team}",
            found_player.model_dump(),
            document_id=player.lower(),
        )
        is None
    ):
        return None

    return found_player


def _find_region_for_team(
    team: str,
) -> typing.Optional[typing.Literal["LEC", "LCS", "LCK", "LPL"]]:
    team = team.upper()

    for region, teams in regions.teams_per_region.items():
        if team in teams:
            return region

    return None


async def _get_match_history_for_player(
    player: models.ProPlayer, amount: int, client: httpx.AsyncClient
) -> typing.List[match_models.MatchHistory]:
    game_ids = []

    query_params = {
        "count": amount,
        "queue": 420,
        "type": "ranked",
    }

    for puuid in player.puuid:
        if (
            account := await account_functions.get_account(client, puuid=puuid)
        ) is None:
            continue

        if (
            games := await match_functions.get_match_history(
                client, account=account, query_params=query_params
            )
        ) == []:
            continue

        game_ids.extend(games)

    match_data = [
        await match_functions.get_match_data(client, game_id) for game_id in game_ids
    ]
    sorted_match_data = sorted(
        (data for data in match_data if data is not None),
        key=lambda x: x.info.gameStartTimestamp,
        reverse=True,
    )

    return (
        sorted_match_data[:amount]
        if len(sorted_match_data) > amount
        else sorted_match_data
    )
