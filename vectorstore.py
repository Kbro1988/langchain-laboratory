import subprocess
from pathlib import Path

import chromadb
from chromadb.config import Settings as chroma_settings
from langchain.document_loaders import (Docx2txtLoader, PyMuPDFLoader,
                                        ReadTheDocsLoader)
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from streamlit.logger import get_logger

# Set Logging
logger = get_logger(__name__)
db_directory = Path("./chroma_db")
DOC_DIRECTORY = Path("./document_repo")
embedding_function = SentenceTransformerEmbeddings(
    model_name="all-MiniLM-L6-v2")

# Loaders


def readthedocs_loader(file_path):
    loader = ReadTheDocsLoader(
        path=file_path,
        features="html.parser",
        custom_html_tag=("article", {"role": "main"})
        )
    raw_docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,)
    docs = text_splitter.split_documents(raw_docs)
    return docs


def worddoc_loader(file_path):
    loader = Docx2txtLoader(file_path)
    raw_docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    docs = text_splitter.split_documents(raw_docs)
    return docs


def pdf_loader(file_path):
    loader = PyMuPDFLoader(file_path)
    raw_docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    docs = text_splitter.split_documents(raw_docs)
    return docs


def get_loader(filename):
    file_path = DOC_DIRECTORY.joinpath(filename)
    doc_extension = file_path.suffix
    method_mapping = {".docx": worddoc_loader,
                      ".pdf": pdf_loader,
                      ".rtdocs": readthedocs_loader,
                      }

    if doc_extension in method_mapping:
        method_to_call = method_mapping[doc_extension]
        docs = method_to_call(file_path.as_posix())
        return docs
    else:
        # Handle the case when the object's value is not in the dictionary
        raise "No method defined for this object's value."


# Chroma Functions


def chroma_client():
    chroma_client = chromadb.PersistentClient(db_directory.as_posix(),
                                              chroma_settings(
                                              anonymized_telemetry=False))
    return chroma_client


def create_vectordb(filename, collection_name):
    print('Creating Chroma DB...\n', f'Creating {collection_name}')
    docs = get_loader(filename)
    db = Chroma.from_documents(
                            docs,
                            embedding_function,
                            persist_directory=db_directory.as_posix(),
                            collection_name=collection_name,)
    return db


def vectordb(collection_name):
    db = Chroma(
        client=chroma_client(),
        embedding_function=embedding_function,
        collection_name=collection_name,)
    return db


def list_collections():
    try:
        collection_list = chroma_client().list_collections()
        for collection in collection_list:
            yield collection
    except ValueError as e:
        logger.warning("%s The Vector Store does not have any collections", e)


def create_collection(collection_name):
    chroma_client().create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},  # l2 is the default
        # distance function are "l2", "ip, "or "cosine"
         )
    for coll in list_collections():
        print(coll)


def delete_collection(collection_name):
    chroma_client().delete_collection(collection_name)
    for coll in list_collections():
        print(coll)


if __name__ == "__main__":
    filename = "progit.pdf"
    file_path = DOC_DIRECTORY.joinpath(filename).as_posix()
    if db_directory.exists():
        response = input("Overwrite the Vector Store?(y/n):  ")
        if response[0].lower() == 'y':
            subprocess.run(['rm', '-rf', db_directory])
            docs = pdf_loader(file_path)
            collection_name = input("Please create a collection name: ")
            create_collection(collection_name)
            create_vectordb(docs, collection_name)
        else:
            print('No Changes Made...')
            list_collections()
    else:
        docs = pdf_loader(file_path)
        print("No Chroma DB found...\n")
        collection_name = input("Please create a collection name: ")
        create_collection(collection_name)
        create_vectordb(docs, collection_name)
