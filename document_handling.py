from pathlib import Path

from langchain.document_loaders import (CSVLoader, Docx2txtLoader,
                                        PyMuPDFLoader, ReadTheDocsLoader,
                                        TextLoader)
from langchain.text_splitter import RecursiveCharacterTextSplitter

from config import Config


class DocumentHandling:
    logger = Config().logger

    def __init__(self, directory: Path = None, chunk_size: int = 1000, chunk_overlap: int = 100,):
        if directory is None:
            # Load config settings
            configs = Config()
            self.doc_directory = configs.doc_directory
        else:
            self.doc_directory = Path(directory)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def readthedocs_loader(self, file: str) -> list[str]:
        loader = ReadTheDocsLoader(
            file=file,
            features="html.parser",
            custom_html_tag=("article", {"role": "main"})
            )
        raw_docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,)
        docs = text_splitter.split_documents(raw_docs)
        return docs

    def worddoc_loader(self, file: str) -> list[str]:
        loader = Docx2txtLoader(file)
        raw_docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter()
        docs = text_splitter.split_documents(raw_docs)
        return docs

    def pdf_loader(self, file: str) -> list[str]:
        docs = PyMuPDFLoader(file).load_and_split(RecursiveCharacterTextSplitter())
        return docs

    def text_loader(self, file: str) -> list[str]:
        loader = TextLoader(file)
        raw_docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,)
        docs = text_splitter.split_documents(raw_docs)
        return docs

    def csv_loader(self, file: str) -> list[str]:
        loader = CSVLoader(file)
        data = loader.load()
        return data

    def get_loader(self, file: str) -> list[str]:
        file_path = self.doc_directory.joinpath(file)
        doc_extension = file_path.suffix
        method_mapping = {".docx": self.worddoc_loader,
                          ".pdf": self.pdf_loader,
                          ".rtdocs": self.readthedocs_loader,
                          ".txt": self.text_loader,
                          ".csv": self.csv_loader, }

        if doc_extension in method_mapping:
            method_to_call = method_mapping[doc_extension]
            docs = method_to_call(file_path.as_posix())
            return docs
        else:
            # Handle the case when the object's value is not in the dictionary
            raise NameError("No method defined for this object's value.")
