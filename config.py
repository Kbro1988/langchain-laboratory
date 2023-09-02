import os
from pathlib import Path

from dotenv import load_dotenv
from streamlit.logger import get_logger


class Config:
    """
     Config used to instiate environment varilables from .env by defualt

     Note all file paths are relative to the root directory of application
    """

    logger = get_logger(__name__)  # Streamlit internal logger

    def __init__(self, custom_env_location: str = None,
                 doc_directory: str = None,
                 weaviate_path: str = "./weaviate/templates/",
                 logger=logger, **kwargs, ):
        if custom_env_location:
            load_dotenv(dotenv_path=custom_env_location)
        else:
            load_dotenv()
        if doc_directory:
            self.doc_directory = Path(doc_directory)
        else:
            self.doc_directory = Path(os.getenv("DOC_DIRECTORY", "./document_repo"))
        self.doc_directory_str = self.doc_directory.as_posix()
        self.weaviate_path = weaviate_path
        self.logger = logger
        self.OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
        self.TOKENIZERS_PARALLELISM = os.environ.get("TOKENIZERS_PARALLELISM")
        self.WEAVIATE_URL = os.environ.get("WEAVIATE_URL")
        self.CHROMA_DB_URL = os.environ.get("CHROMA_DB_URL")
        self.SERPAPI_KEY = os.environ.get("SERPAPI_KEY")
        self._custom_prompt_directory = None
        #  Process **kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def custom_prompt_directory(self):
        if self._custom_prompt_directory is None:
            self._custom_prompt_directory = self.doc_directory.joinpath('custom_prompts')
        return self._custom_prompt_directory
