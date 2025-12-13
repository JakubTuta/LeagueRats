import typing

import constants
import utils

from . import models

CACHE_SETTINGS = {
    "pro_players": {
        "cache_name": "pro_players",
        "ttl": 3600,  # 1 hour
        "cache_prefix": "pro_players",
    },
    "account_names": {
        "cache_name": "account_names",
        "ttl": 3600,  # 1 hour
        "cache_prefix": "account_names",
    },
    "live_streams": {
        "cache_name": "live_streams",
        "ttl": 900,  # 15 minutes
        "cache_prefix": "live_streams",
    },
}


class ProPlayersCache:
    def __init__(self):
        self.cache_prefix = CACHE_SETTINGS["pro_players"]["cache_prefix"]
        self.players_cache = utils.get_ttl_cache_client(
            name=CACHE_SETTINGS["pro_players"]["cache_name"],
            ttl=CACHE_SETTINGS["pro_players"]["ttl"],
        )
        self.account_names_cache = utils.get_ttl_cache_client(
            name=CACHE_SETTINGS["account_names"]["cache_name"],
            ttl=CACHE_SETTINGS["account_names"]["ttl"],
        )
        self.live_streams_cache = utils.get_ttl_cache_client(
            name=CACHE_SETTINGS["live_streams"]["cache_name"],
            ttl=CACHE_SETTINGS["live_streams"]["ttl"],
        )

    def get_players(
        self,
        region: typing.Optional[str] = None,
        team: typing.Optional[str] = None,
    ) -> dict[str, dict[str, list[models.ProPlayer]]]:
        if region and team:
            cache_key = f"{self.cache_prefix}:{region}:{team}"
            cached_data = self.players_cache.get(cache_key)
            if cached_data:
                return {region: {team: [models.ProPlayer(**p) for p in cached_data]}}
        elif region:
            cache_key = f"{self.cache_prefix}:{region}"
            cached_data = self.players_cache.get(cache_key)
            if cached_data:
                return {region: cached_data}
        else:
            cache_key = f"{self.cache_prefix}:all"
            cached_data = self.players_cache.get(cache_key)
            if cached_data:
                return cached_data

        return {}

    def set_players(
        self,
        players: dict[str, dict[str, list[models.ProPlayer]]],
        region: typing.Optional[str] = None,
        team: typing.Optional[str] = None,
    ) -> None:
        if region and team:
            cache_key = f"{self.cache_prefix}:{region}:{team}"
            team_players = players.get(region, {}).get(team, [])
            self.players_cache.set(cache_key, [p.model_dump(mode='json') for p in team_players])
        elif region:
            cache_key = f"{self.cache_prefix}:{region}"
            region_data = players.get(region, {})
            self.players_cache.set(cache_key, region_data)
        else:
            cache_key = f"{self.cache_prefix}:all"
            self.players_cache.set(cache_key, players)

    def get_account_names(self) -> typing.Optional[dict[str, dict[str, str]]]:
        cache_key = "account_names:data"
        cached_data = self.account_names_cache.get(cache_key)
        return cached_data

    def set_account_names(self, account_names: dict[str, dict[str, str]]) -> None:
        cache_key = "account_names:data"
        self.account_names_cache.set(cache_key, account_names)

    def get_live_streams(
        self, live: bool = True
    ) -> typing.Optional[dict[str, dict[str, str]]]:
        cache_key = f"live_streams:{'live' if live else 'not_live'}"
        cached_data = self.live_streams_cache.get(cache_key)
        return cached_data

    def set_live_streams(
        self, streams: dict[str, dict[str, str]], live: bool = True
    ) -> None:
        cache_key = f"live_streams:{'live' if live else 'not_live'}"
        self.live_streams_cache.set(cache_key, streams)


class ProPlayersRedis:
    def __init__(self, redis_client: utils.RedisClient):
        self.redis_client = redis_client
        self.cache_prefix = CACHE_SETTINGS["pro_players"]["cache_prefix"]

    async def get_players(
        self,
        region: typing.Optional[str] = None,
        team: typing.Optional[str] = None,
    ) -> dict[str, dict[str, list[models.ProPlayer]]]:
        if region and team:
            redis_key = f"{self.cache_prefix}:{region}:{team}"
            cached_data = await self.redis_client.get_json(redis_key)
            if cached_data:
                return {region: {team: [models.ProPlayer(**p) for p in cached_data]}}
        elif region:
            redis_key = f"{self.cache_prefix}:{region}"
            cached_data = await self.redis_client.get_json(redis_key)
            if cached_data:
                reconstructed_data = {}
                for team_name, team_players in cached_data.items():
                    reconstructed_data[team_name] = [
                        models.ProPlayer(**p) for p in team_players
                    ]
                return {region: reconstructed_data}
        else:
            redis_key = f"{self.cache_prefix}:all"
            cached_data = await self.redis_client.get_json(redis_key)
            if cached_data:
                reconstructed_data = {}
                for region_name, region_teams in cached_data.items():
                    reconstructed_data[region_name] = {}
                    for team_name, team_players in region_teams.items():
                        reconstructed_data[region_name][team_name] = [
                            models.ProPlayer(**p) for p in team_players
                        ]
                return reconstructed_data

        return {}

    async def set_players(
        self,
        players: dict[str, dict[str, list[models.ProPlayer]]],
        region: typing.Optional[str] = None,
        team: typing.Optional[str] = None,
    ) -> None:
        ttl = CACHE_SETTINGS["pro_players"]["ttl"]

        if region and team:
            redis_key = f"{self.cache_prefix}:{region}:{team}"
            team_players = players.get(region, {}).get(team, [])
            await self.redis_client.set_json(
                redis_key, [p.model_dump(mode='json') for p in team_players], ex=ttl
            )
        elif region:
            redis_key = f"{self.cache_prefix}:{region}"
            region_data = players.get(region, {})
            serialized_data = {
                team_name: [p.model_dump(mode='json') for p in team_players]
                for team_name, team_players in region_data.items()
            }
            await self.redis_client.set_json(redis_key, serialized_data, ex=ttl)
        else:
            redis_key = f"{self.cache_prefix}:all"
            serialized_data = {
                region_name: {
                    team_name: [p.model_dump(mode='json') for p in team_players]
                    for team_name, team_players in region_teams.items()
                }
                for region_name, region_teams in players.items()
            }
            await self.redis_client.set_json(redis_key, serialized_data, ex=ttl)

    async def get_account_names(self) -> typing.Optional[dict[str, dict[str, str]]]:
        redis_key = "account_names:data"
        cached_data = await self.redis_client.get_json(redis_key)
        return cached_data

    async def set_account_names(self, account_names: dict[str, dict[str, str]]) -> None:
        redis_key = "account_names:data"
        ttl = CACHE_SETTINGS["account_names"]["ttl"]
        await self.redis_client.set_json(redis_key, account_names, ex=ttl)

    async def get_live_streams(
        self, live: bool = True
    ) -> typing.Optional[dict[str, dict[str, str]]]:
        redis_key = f"live_streams:{'live' if live else 'not_live'}"
        cached_data = await self.redis_client.get_json(redis_key)
        return cached_data

    async def set_live_streams(
        self, streams: dict[str, dict[str, str]], live: bool = True
    ) -> None:
        redis_key = f"live_streams:{'live' if live else 'not_live'}"
        ttl = CACHE_SETTINGS["live_streams"]["ttl"]
        await self.redis_client.set_json(redis_key, streams, ex=ttl)


class ProPlayersFirestore:
    def __init__(self, firestore_client: utils.FirestoreClient):
        self.firestore_client = firestore_client

    async def get_players(
        self,
        region: typing.Optional[str] = None,
        team: typing.Optional[str] = None,
    ) -> dict[str, dict[str, list[models.ProPlayer]]]:
        players: dict[str, dict[str, list[models.ProPlayer]]] = {}

        if region and team:
            collection_path = f"pro_players/{region.upper()}/{team.upper()}"
            documents = await self.firestore_client.query_collection(
                collection=collection_path
            )
            players[region.upper()] = {
                team.upper(): [models.ProPlayer(**doc) for doc in documents]
            }
        elif region:
            region = region.upper()
            teams = constants.TEAMS_PER_REGION.get(region, [])  # type: ignore
            players[region] = {}
            for team in teams:
                collection_path = f"pro_players/{region}/{team}"
                documents = await self.firestore_client.query_collection(
                    collection=collection_path
                )
                players[region][team] = [  # pyright: ignore[reportArgumentType]
                    models.ProPlayer(**doc) for doc in documents
                ]
        else:
            for region_name in constants.PRO_REGIONS:
                players[region_name] = {}
                teams = constants.TEAMS_PER_REGION.get(region_name, [])  # type: ignore
                for team in teams:
                    collection_path = f"pro_players/{region_name}/{team}"
                    documents = await self.firestore_client.query_collection(
                        collection=collection_path
                    )
                    players[region_name][team] = [  # type: ignore
                        models.ProPlayer(**doc) for doc in documents
                    ]

        return players

    async def set_player(self, player: models.ProPlayer) -> None:
        collection_path = f"pro_players/{player.region.upper()}/{player.team.upper()}"
        await self.firestore_client.set_document(
            collection=collection_path,
            document_id=player.player.lower(),
            data=player.model_dump(mode='json'),
        )

    async def delete_player(self, region: str, team: str, player_name: str) -> bool:
        collection_path = f"pro_players/{region.upper()}/{team.upper()}"
        try:
            await self.firestore_client.delete_document(
                collection=collection_path, document_id=player_name.lower()
            )
            return True
        except Exception:
            return False

    async def get_account_names(self) -> typing.Optional[dict[str, dict[str, str]]]:
        document = await self.firestore_client.get_document(
            collection="pro_players", document_id="account_names"
        )
        return document

    async def get_live_streams(
        self, live: bool = True
    ) -> typing.Optional[dict[str, dict[str, str]]]:
        document_id = "live" if live else "not_live"
        document = await self.firestore_client.get_document(
            collection="live_streams", document_id=document_id
        )
        return document
