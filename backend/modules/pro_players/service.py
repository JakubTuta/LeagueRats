import asyncio
import typing

import constants
import utils
from modules.match import service as match_service_module

from . import models, repository


class ProPlayerService:
    def __init__(
        self,
        firestore: utils.FirestoreClient,
        redis: utils.RedisClient,
    ):
        self.firestore = firestore
        self.redis = redis

        self.cache_repo = repository.ProPlayersCache()
        self.redis_repo = repository.ProPlayersRedis(redis)
        self.firestore_repo = repository.ProPlayersFirestore(firestore)

    async def get_players(
        self,
        region: typing.Optional[str] = None,
        team: typing.Optional[str] = None,
        player: typing.Optional[str] = None,
    ) -> typing.Optional[dict[str, dict[str, list[models.ProPlayer]]]]:
        """
        Unified player fetch with L1→L2→L3 caching strategy.
        Returns different types based on query parameters:
        - No params: All players (all regions, all teams)
        - Region only: All teams in region
        - Region + team: All players in team
        - Region + team + player: Single player
        """
        print("get_players called with:", region, team, player)
        if player and region and team:
            print("Fetching single player:", region, team, player)
            pro_player = await self._get_single_player(
                region=region, team=team, player=player
            )
            print("Found player:", pro_player)

            return {region: {team: [pro_player]}} if pro_player else None

        cached_players = self.cache_repo.get_players(region=region, team=team)
        if cached_players:
            return cached_players

        redis_players = await self.redis_repo.get_players(region=region, team=team)
        if redis_players:
            self.cache_repo.set_players(players=redis_players, region=region, team=team)
            return redis_players

        firestore_players = await self.firestore_repo.get_players(
            region=region, team=team
        )
        if firestore_players:
            await self.redis_repo.set_players(
                players=firestore_players, region=region, team=team
            )
            self.cache_repo.set_players(
                players=firestore_players, region=region, team=team
            )
            return firestore_players

        return {}

    async def _get_single_player(
        self, region: str, team: str, player: str
    ) -> typing.Optional[models.ProPlayer]:
        region = region.upper()
        team = team.upper()
        player_lower = player.lower()

        team_players = await self.get_players(region=region, team=team)

        if isinstance(team_players, dict):
            players_list = team_players.get(region, {}).get(team, [])
        else:
            return None

        found_player = next(
            (p for p in players_list if p.player.lower() == player_lower), None
        )
        return found_player

    async def create_or_update_player(
        self,
        player: models.ProPlayer,
        riot_api: utils.RiotAPIClient,
        username: typing.Optional[str] = None,
        tag: typing.Optional[str] = None,
        region: typing.Optional[str] = None,
    ) -> models.ProPlayer:
        if username and tag and region:
            mapped_region = constants.REGION_TO_CONTINENT.get(region.lower())
            if mapped_region:
                request_url = f"/riot/account/v1/accounts/by-riot-id/{username}/{tag}"
                if account_response := await riot_api.get(mapped_region, request_url):
                    new_puuid = account_response.get(  # pyright: ignore[reportAttributeAccessIssue]
                        "puuid"
                    )
                    if new_puuid and new_puuid not in player.puuid:
                        player.puuid.append(new_puuid)

        await self.firestore_repo.set_player(player=player)
        return player

    async def transfer_player(
        self, player_name: str, from_team: str, to_team: str
    ) -> typing.Optional[models.ProPlayer]:
        from_region = self._find_region_for_team(team=from_team)
        to_region = self._find_region_for_team(team=to_team)

        if not from_region or not to_region:
            return None

        found_player = await self._get_single_player(
            region=from_region, team=from_team, player=player_name
        )
        if not found_player:
            return None

        success = await self.firestore_repo.delete_player(
            region=from_region, team=from_team, player_name=player_name.lower()
        )
        if not success:
            return None

        found_player.team = to_team.upper()
        found_player.region = to_region

        await self.firestore_repo.set_player(player=found_player)
        return found_player

    async def get_account_names(self) -> typing.Optional[dict[str, dict[str, str]]]:
        cached_names = self.cache_repo.get_account_names()
        if cached_names:
            return cached_names

        redis_names = await self.redis_repo.get_account_names()
        if redis_names:
            self.cache_repo.set_account_names(account_names=redis_names)
            return redis_names

        firestore_names = await self.firestore_repo.get_account_names()
        if firestore_names:
            await self.redis_repo.set_account_names(account_names=firestore_names)
            self.cache_repo.set_account_names(account_names=firestore_names)
            return firestore_names

        return None

    async def get_live_streams(
        self, live: bool = True
    ) -> typing.Optional[dict[str, dict[str, str]]]:
        cached_streams = self.cache_repo.get_live_streams(live=live)
        if cached_streams:
            return cached_streams

        redis_streams = await self.redis_repo.get_live_streams(live=live)
        if redis_streams:
            self.cache_repo.set_live_streams(streams=redis_streams, live=live)
            return redis_streams

        firestore_streams = await self.firestore_repo.get_live_streams(live=live)
        if firestore_streams:
            await self.redis_repo.set_live_streams(streams=firestore_streams, live=live)
            self.cache_repo.set_live_streams(streams=firestore_streams, live=live)
            return firestore_streams

        return None

    def _find_region_for_team(
        self, team: str
    ) -> typing.Optional[typing.Literal["LEC", "LCS", "LCK", "LPL"]]:
        team = team.upper()
        for region_name, teams in constants.TEAMS_PER_REGION.items():
            if team in teams:
                return region_name
        return None

    async def get_player_history_stats(
        self,
        team: str,
        player: str,
        amount: int,
        riot_api: utils.RiotAPIClient,
    ) -> typing.Optional[typing.Dict[int, models.ChampionStats]]:
        region = self._find_region_for_team(team=team)
        if not region:
            return None

        found_player = await self._get_single_player(
            region=region, team=team, player=player
        )
        if not found_player:
            return None

        game_region = constants.PRO_REGION_TO_GAME_REGION.get(region)
        if not game_region:
            return None

        match_service = match_service_module.MatchService(
            redis_client=self.redis,
            firestore_client=self.firestore,
            riot_api=riot_api,
        )

        all_match_ids: list[str] = []
        for puuid in found_player.puuid:
            match_ids = await match_service._fetch_match_history_ids(
                puuid=puuid,
                region=game_region,
                start=0,
                count=amount,
                queue="420",
                type="ranked",
            )
            all_match_ids.extend(match_ids)

        if not all_match_ids:
            return {}

        match_histories_dict = await match_service._fetch_match_data_batch(
            match_ids=all_match_ids, region=game_region
        )

        match_histories = sorted(
            match_histories_dict.values(),
            key=lambda x: x.info.gameStartTimestamp,
            reverse=True,
        )[:amount]

        champion_stats: typing.Dict[int, models.ChampionStats] = {}

        for match in match_histories:
            player_participant = next(
                (
                    participant
                    for participant in match.info.participants
                    if participant.puuid in found_player.puuid
                ),
                None,
            )

            if not player_participant:
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
