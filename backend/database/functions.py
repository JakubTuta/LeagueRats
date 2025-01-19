from . import database


def is_document_in_collection(collection_name: str, document_id: str) -> bool:
    collection = database.get_collection(collection_name)
    document = collection.document(document_id)

    return document.get().exists


def add_document(collection_name: str, document_data: dict):
    collection = database.get_collection(collection_name)

    if (
        doc_id := document_data.get("puuid", None)
    ) is not None and not is_document_in_collection(collection_name, doc_id):
        document = collection.document(doc_id)
        document.set(document_data)

    collection.add(document_data)
