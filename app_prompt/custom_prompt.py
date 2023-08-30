from pathlib import Path
from textwrap import dedent

from langchain.prompts import (ChatPromptTemplate, HumanMessagePromptTemplate,
                               SystemMessagePromptTemplate, load_prompt)

from config import Config

configs = Config()

logger = configs.logger

custom_prompt_directory = configs.custom_prompt_directory


def load_custom_prompt(file_name):
    try:
        if Path(file_name).suffix == ".yaml":
            print(custom_prompt_directory.joinpath(file_name).as_posix())
            system_prompt = load_prompt(custom_prompt_directory.joinpath(file_name).as_posix())
            print(system_prompt)
            return system_prompt
        else:
            raise ValueError(f"Expected file with 'yaml' suffix. Got {Path(file_name).suffix}")
    except FileNotFoundError as e:
        logger.warn(f"{e}: File {file_name} not found.")


def get_custom_prompt(file_name):
    human_template = dedent("""\
                            I would like you to answers the following: {question}
                            """)
    CUSTOM_PROMPT = ChatPromptTemplate.from_messages(
        [SystemMessagePromptTemplate(prompt=load_custom_prompt(file_name)),
         HumanMessagePromptTemplate.from_template(human_template)])
    return CUSTOM_PROMPT
