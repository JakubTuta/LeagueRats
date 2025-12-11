import logging
import os
import typing

import structlog
import tenacity
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from google.oauth2 import service_account

logger = structlog.get_logger(__name__)

_firestore_client: typing.Optional["FirestoreClient"] = None


class FirestoreClient:
    def __init__(self, project_id: str, credentials: service_account.Credentials):
        self._client = firestore.AsyncClient(
            project=project_id, credentials=credentials
        )
        self._project_id = project_id
        logger.info("firestore_client_initialized", project=project_id)

    @tenacity.retry(
        retry=tenacity.retry_if_exception_type((Exception,)),
        stop=tenacity.stop_after_attempt(3),
        wait=tenacity.wait_exponential(multiplier=1, min=1, max=5),
        before_sleep=tenacity.before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    async def get_document(
        self, collection: str, document_id: str
    ) -> typing.Optional[dict[str, typing.Any]]:
        try:
            doc_ref = self._client.collection(collection).document(document_id)
            doc = await doc_ref.get()

            if doc.exists:
                logger.debug(
                    "document_found", collection=collection, doc_id=document_id
                )
                return doc.to_dict()
            else:
                logger.debug(
                    "document_not_found", collection=collection, doc_id=document_id
                )
                return None

        except Exception as e:
            logger.error(
                "firestore_get_error",
                collection=collection,
                doc_id=document_id,
                error=str(e),
            )
            raise

    @tenacity.retry(
        retry=tenacity.retry_if_exception_type((Exception,)),
        stop=tenacity.stop_after_attempt(3),
        wait=tenacity.wait_exponential(multiplier=1, min=1, max=5),
        before_sleep=tenacity.before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    async def set_document(
        self,
        collection: str,
        document_id: str,
        data: dict[str, typing.Any],
        merge: bool = False,
    ) -> bool:
        try:
            doc_ref = self._client.collection(collection).document(document_id)
            await doc_ref.set(data, merge=merge)

            logger.debug(
                "document_set",
                collection=collection,
                doc_id=document_id,
                merge=merge,
            )
            return True

        except Exception as e:
            logger.error(
                "firestore_set_error",
                collection=collection,
                doc_id=document_id,
                error=str(e),
            )
            raise

    @tenacity.retry(
        retry=tenacity.retry_if_exception_type((Exception,)),
        stop=tenacity.stop_after_attempt(3),
        wait=tenacity.wait_exponential(multiplier=1, min=1, max=5),
        before_sleep=tenacity.before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    async def update_document(
        self, collection: str, document_id: str, updates: dict[str, typing.Any]
    ) -> bool:
        try:
            doc_ref = self._client.collection(collection).document(document_id)
            await doc_ref.update(updates)

            logger.debug(
                "document_updated",
                collection=collection,
                doc_id=document_id,
                fields=list(updates.keys()),
            )
            return True

        except Exception as e:
            logger.error(
                "firestore_update_error",
                collection=collection,
                doc_id=document_id,
                error=str(e),
            )
            raise

    @tenacity.retry(
        retry=tenacity.retry_if_exception_type((Exception,)),
        stop=tenacity.stop_after_attempt(3),
        wait=tenacity.wait_exponential(multiplier=1, min=1, max=5),
        before_sleep=tenacity.before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    async def delete_document(self, collection: str, document_id: str) -> bool:
        try:
            doc_ref = self._client.collection(collection).document(document_id)
            await doc_ref.delete()

            logger.debug("document_deleted", collection=collection, doc_id=document_id)
            return True

        except Exception as e:
            logger.error(
                "firestore_delete_error",
                collection=collection,
                doc_id=document_id,
                error=str(e),
            )
            raise

    async def query_collection(
        self,
        collection: str,
        filters: typing.Optional[list[tuple[str, str, typing.Any]]] = None,
        order_by: typing.Optional[str] = None,
        order_direction: str = "ASCENDING",
        limit: typing.Optional[int] = None,
        offset: typing.Optional[int] = None,
        start_after: typing.Optional[str] = None,
        **kwargs,
    ) -> typing.Sequence[dict[str, typing.Any]]:
        try:
            query = self._client.collection(collection)

            if filters:
                for field, operator, value in filters:
                    query = query.where(filter=FieldFilter(field, operator, value))

            if order_by:
                direction = (
                    firestore.Query.DESCENDING
                    if order_direction == "DESCENDING"
                    else firestore.Query.ASCENDING
                )
                query = query.order_by(order_by, direction=direction)

                if start_after:
                    start_after_doc = (
                        await self._client.collection(collection)
                        .document(start_after)
                        .get()
                    )
                    if start_after_doc.exists:
                        query = query.start_after(start_after_doc)

            if offset:
                query = query.offset(offset)

            if limit:
                query = query.limit(limit)

            if kwargs:
                for key, value in kwargs.items():
                    query = query.where(key, "==", value)

            docs = query.stream()
            results = [doc.to_dict() async for doc in docs]

            logger.debug(
                "collection_queried",
                collection=collection,
                count=len(results),
                filters=filters,
            )
            return results  # pyright: ignore[reportReturnType]

        except Exception as e:
            logger.error(
                "firestore_query_error",
                collection=collection,
                error=str(e),
            )
            raise

    async def get_all_documents(
        self, collection: str
    ) -> typing.Sequence[dict[str, typing.Any]]:
        try:
            docs = self._client.collection(collection).stream()
            results = [doc.to_dict() async for doc in docs]

            logger.debug(
                "collection_fetched", collection=collection, count=len(results)
            )
            return results  # pyright: ignore[reportReturnType]

        except Exception as e:
            logger.error(
                "firestore_get_all_error",
                collection=collection,
                error=str(e),
            )
            raise

    async def batch_get(
        self, collection: str, document_ids: list[str]
    ) -> list[dict[str, typing.Any]]:
        try:
            results = []

            for doc_id in document_ids:
                doc_ref = self._client.collection(collection).document(doc_id)
                doc = await doc_ref.get()

                if doc.exists:
                    results.append(doc.to_dict())
                else:
                    logger.debug(
                        "document_not_found_in_batch",
                        collection=collection,
                        doc_id=doc_id,
                    )

            logger.info(
                "batch_get_completed",
                collection=collection,
                requested=len(document_ids),
                found=len(results),
            )
            return results

        except Exception as e:
            logger.error(
                "firestore_batch_get_error",
                collection=collection,
                error=str(e),
            )
            raise

    async def batch_set(
        self, collection: str, documents: dict[str, dict[str, typing.Any]]
    ) -> bool:
        try:
            batch = self._client.batch()

            for doc_id, data in documents.items():
                doc_ref = self._client.collection(collection).document(doc_id)
                batch.set(doc_ref, data)

            await batch.commit()

            logger.info(
                "batch_set_completed",
                collection=collection,
                count=len(documents),
            )
            return True

        except Exception as e:
            logger.error(
                "firestore_batch_set_error",
                collection=collection,
                error=str(e),
            )
            raise

    async def batch_delete(self, collection: str, document_ids: list[str]) -> bool:
        try:
            batch = self._client.batch()

            for doc_id in document_ids:
                doc_ref = self._client.collection(collection).document(doc_id)
                batch.delete(doc_ref)

            await batch.commit()

            logger.info(
                "batch_delete_completed",
                collection=collection,
                count=len(document_ids),
            )
            return True

        except Exception as e:
            logger.error(
                "firestore_batch_delete_error",
                collection=collection,
                error=str(e),
            )
            raise

    async def document_exists(self, collection: str, document_id: str) -> bool:
        try:
            doc_ref = self._client.collection(collection).document(document_id)
            doc = await doc_ref.get()
            return doc.exists

        except Exception as e:
            logger.error(
                "firestore_exists_error",
                collection=collection,
                doc_id=document_id,
                error=str(e),
            )
            raise

    async def get_collection_count(self, collection: str) -> int:
        try:
            docs = self._client.collection(collection).stream()
            count = 0
            async for _ in docs:
                count += 1

            logger.debug("collection_counted", collection=collection, count=count)
            return count

        except Exception as e:
            logger.error(
                "firestore_count_error",
                collection=collection,
                error=str(e),
            )
            raise

    async def get_subcollection(
        self,
        parent_collection: str,
        parent_document: str,
        subcollection: str,
    ) -> list[dict[str, typing.Any]]:
        try:
            docs = (
                self._client.collection(parent_collection)
                .document(parent_document)
                .collection(subcollection)
                .stream()
            )
            results = [doc.to_dict() async for doc in docs]

            logger.debug(
                "subcollection_fetched",
                parent=f"{parent_collection}/{parent_document}",
                subcollection=subcollection,
                count=len(results),
            )
            return results

        except Exception as e:
            logger.error(
                "firestore_subcollection_error",
                parent=f"{parent_collection}/{parent_document}",
                subcollection=subcollection,
                error=str(e),
            )
            raise

    def get_raw_client(self) -> firestore.AsyncClient:
        return self._client

    def close(self) -> None:
        self._client.close()
        logger.info("firestore_client_closed")


def get_firestore_client() -> FirestoreClient:
    global _firestore_client

    if _firestore_client is None:
        service_account_path = os.getenv(
            "SERVICE_ACCOUNT_PATH",
            "service_account.json",
        )
        project_id = os.getenv("FIREBASE_PROJECT_ID", "league-rats")

        credentials = service_account.Credentials.from_service_account_file(
            service_account_path
        )
        _firestore_client = FirestoreClient(
            project_id=project_id,
            credentials=credentials,
        )

    return _firestore_client


async def close_firestore_client() -> None:
    global _firestore_client

    if _firestore_client is not None:
        _firestore_client.close()
        _firestore_client = None
