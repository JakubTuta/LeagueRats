import typing

import utils

from . import models, repository


class RunesService:
    def __init__(
        self,
        firestore: utils.FirestoreClient,
        redis: utils.RedisClient,
    ):
        self.firestore = firestore
        self.redis = redis

        self.cache_repo = repository.RunesCache()
        self.redis_repo = repository.RunesRedis(redis)
        self.firestore_repo = repository.RunesFirestore(firestore)

    async def get_runes(self) -> typing.Optional[list[models.Rune]]:
        cached_runes = self.cache_repo.get_runes()
        if cached_runes:
            return cached_runes

        redis_runes = await self.redis_repo.get_runes()
        if redis_runes:
            self.cache_repo.set_runes(runes=redis_runes)
            return redis_runes

        firestore_runes = await self.firestore_repo.get_runes()
        if firestore_runes:
            await self.redis_repo.set_runes(runes=firestore_runes)
            self.cache_repo.set_runes(runes=firestore_runes)
            return firestore_runes

        return None
