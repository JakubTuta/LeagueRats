from . import database


def add_document(collection_name: str, document_data: dict):
    collection = database.get_collection(collection_name)

    if document_data.get("puuid", None) is not None:
        document = collection.document(document_data["puuid"])
        document.set(document_data)

    collection.add(document_data)
