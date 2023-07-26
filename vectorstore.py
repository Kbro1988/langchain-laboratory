from pathlib import Path
import subprocess
import logging

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import ReadTheDocsLoader
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.vectorstores import Chroma

logger = logging.basicConfig(level='INFO')
embedding_function = SentenceTransformerEmbeddings(
    model_name="all-MiniLM-L6-v2")

def create_vectordb():
    loader = ReadTheDocsLoader(
        path="./rtdocs/tts.readthedocs.io/en/latest/",
        features="html.parser",
        custom_html_tag=("article", {"role": "main"})
        )

    raw_docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    docs = text_splitter.split_documents(raw_docs)
    db = Chroma.from_documents(
                            docs,
                            embedding_function, 
                            persist_directory="./chroma_db",
                            collection_name="TTS_readthedocs",)

    return db

def vectordb():
    db = Chroma(
        embedding_function=embedding_function,
        persist_directory="./chroma_db",
        collection_name="TTS_readthedocs",)

    return db

if __name__ == "__main__":
    path = Path("./chroma_db")
    if path.exists():
        response = input("Do you wish to overwrite the Vector Store?(y/n):  ")
        if response[0].lower() == 'y':
            subprocess.run(['rm', '-rf', path])
            create_vectordb()
        else:
            print('No Changes Made...')
    else:
        create_vectordb()
