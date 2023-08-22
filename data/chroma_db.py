import sys

import chromadb
from chromadb.config import Settings as chroma_settings
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma

from config import Config
from document_handling import DocumentHandling

# Load config settings
configs = Config()

# Set Logging
logger = configs.logger

# Document Loaders and handling
handler = DocumentHandling()

embedding_function = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2")

CHROMA_CLIENT = chromadb.HttpClient(host='chroma_db', port=8000, settings=chroma_settings(anonymized_telemetry=False))


def chroma_create_vectordb(filename, collection_name):
    docs = handler.get_loader(filename)
    db = Chroma.from_documents(docs, embedding_function, collection_name=collection_name, client=CHROMA_CLIENT,)
    logger.info("Loaded %s to Chroma Collection  %s", filename, collection_name)
    return db


def chroma_vectordb(collection_name):
    db = Chroma(client=CHROMA_CLIENT, embedding_function=embedding_function, collection_name=collection_name,)
    logger.debug("Accessing Chroma Collection %s", collection_name)
    return db


def list_collections():
    try:
        collection_list = CHROMA_CLIENT.list_collections()
        for collection in collection_list:
            yield collection
    except ValueError as e:
        logger.warning("%s The Vector Store does not have any collections", e)


def create_collection(collection_name):
    CHROMA_CLIENT.create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},  # l2 is the default
        # distance function are "l2", "ip, "or "cosine"
        )
    for coll in list_collections():
        print(coll)


def delete_collection(collection_name):
    CHROMA_CLIENT.delete_collection(collection_name)
    logger.info("Deleting Chroma Collection %s", collection_name)


if __name__ == "__main__":
    if CHROMA_CLIENT.heartbeat():
        list_collections()
    else:
        "Chroma Server Is not Running"
        sys.exit(1)
