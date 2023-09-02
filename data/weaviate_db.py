import json

from jinja2 import Environment, FileSystemLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Weaviate

import weaviate
from config import Config
from document_handling import DocumentHandling

# Load config settings
configs = Config()

# Set Logging
logger = configs.logger

WEAVIATE_URL = configs.WEAVIATE_URL

CLIENT = weaviate.Client(WEAVIATE_URL)

embedding_function = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2")

# Set Document Handling
handler = DocumentHandling()

# @cache_resource  # Speeds up app
# def weaviate_client():
#     client = weaviate.Client(WEAVIATE_URL)
#     return client


def weaviate_vectordb(index_name: str, text_key: str = "text") -> Weaviate:
    db = Weaviate(CLIENT, index_name=index_name, text_key=text_key, embedding=embedding_function, by_text=False)
    return db


def weaviate_create_vectordb(file: str, index_name: str = None) -> Weaviate:
    docs = handler.get_loader(file)
    db = Weaviate.from_documents(docs, embedding=embedding_function, weaviate_url=WEAVIATE_URL, index_name=index_name,
                                 by_text=False)
    logger.info("Creating Weaviate Class %s", index_name)
    return db


def weaviate_get_schema(class_name: str = None) -> dict:
    if class_name is None:
        return CLIENT.schema.get()
    else:
        return CLIENT.schema.get(class_name)


def weaviate_create_schema(class_obj: dict) -> None:
    CLIENT.schema.create_class(class_obj)
    return weaviate_get_schema(class_obj["class"])


def weaviate_get_classes():
    db_schema = weaviate_get_schema()
    for _ in range(len(db_schema["classes"])):
        yield db_schema["classes"][_]["class"]


def weaviate_add_doc_to_class(file: str, index_name: str, text_tag: str) -> list[str]:
    docs = handler.get_loader(file)
    db = weaviate_vectordb(index_name, text_tag)
    db.add_documents(docs)


def create_class_obj(schema_template: str, schema_values: str) -> dict:
    """
    create_class_obj Creates a class object from a Jinja template and values from JSON file or dict.
                     this is used with the weaviate_create_schema.
    """
    schema_values = json.loads(schema_values)
    jinja_env = Environment(loader=FileSystemLoader('./weaviate/templates/'),
                            trim_blocks=True,
                            lstrip_blocks=True,
                            keep_trailing_newline=False)
    template = jinja_env.get_template(schema_template)
    rendered = template.render(schema_values)
    class_obj = json.loads(rendered)
    return class_obj


def weaviate_delete_class(class_name: str) -> None:
    CLIENT.schema.delete_class(class_name)


def weaviate_delete_id(ids: list[str], index_name: str, text_key: str) -> None:
    db = weaviate_vectordb(index_name, text_key)
    db.delete(ids=ids, class_name=index_name)  # Note must add in LangChain Library to Weaviate.delete() the class_name attribute
    logger.info("ids %s deleted from Class %s Name %s", ids, index_name, text_key)


def weaviate_get_batch_with_cursor(client=CLIENT, class_name=None, class_properties=None, batch_size=20, cursor="None"):
    query = (client.query.get(class_name, class_properties)
             # Optionally retrieve the vector embedding by adding `vector` to the _additional fields
             .with_additional(["id vector"])
             .with_limit(batch_size))

    if cursor != "None":
        return query.with_after(cursor).do()
    else:
        return query.do()


if __name__ == "__main__":
    index_name = input("Class name: ")
    db = weaviate_vectordb(index_name)
    db_schema = weaviate_get_schema()
    print(json.dumps(db_schema, indent=4))
    with open('./weaviate/templates/base_schema_value_example.json', 'r') as f:
        schema_values = json.load(f)
    schema_template = "document_schema.j2"
