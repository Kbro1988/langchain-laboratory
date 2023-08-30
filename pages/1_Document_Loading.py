import os

import streamlit as st

from config import Config
from data.chroma_db import chroma_create_vectordb, list_collections
from data.weaviate_db import (weaviate_add_doc_to_class, weaviate_get_classes,
                              weaviate_get_schema)
from Home import session_state

# Load config settings
configs = Config()

# Set looger
logger = configs.logger

#Custom Prompot Director
custom_prompt_directory = configs.doc_directory.joinpath("custom_prompts")

# Initialize Session State for docs_hide, csv_hide. Used when there are no files.
if "docs_hide" not in st.session_state:
    st.session_state["docs_hide"] = True
if "csv_hide" not in st.session_state:
    st.session_state["csv_hide"] = True

#Initialize Session state for Weviate upload ("uploadWeaviateHide")
if "uploadWeaviateHide" not in st.session_state:
    st.session_state["uploadWeaviateHide"] = True


def doc_loader_select(vectordb_docload):
    if vectordb_docload == "ChromaDB":
        collection = [coll.name for coll in list_collections()]
        return collection
    elif vectordb_docload == "Weaviate":
        collection = [cn for cn in weaviate_get_classes()]
        return collection


st.header("Loading Documents to Vector Store")

# Document Loader

# Uploade File
with st.expander("Expand to load a document to 'document_repo' directory."):
    uploaded_files = st.file_uploader(label="Upload Document", type=["pdf", "txt", "docx"], accept_multiple_files=True, key="FileUploader", )
    if uploaded_files is not None:
        for uploaded_file in uploaded_files:
            fp = configs.doc_directory.joinpath(f"{uploaded_file.name}")
            with open(fp.as_posix(), "wb") as f:
                f.write(uploaded_file.getbuffer())
                logger.info("%s uploaded", uploaded_file.name)
                st.success(f"Uploaded {uploaded_file.name} to {configs.doc_directory_str}")

# Load a file to Vector Store
st.write("Load a Document from the 'document_repo' directory to vector store collection.")
vectordb_docload = st.radio("Choose the vector store", ("ChromaDB", "Weaviate",), key="vectordb_docload", horizontal=True)
if configs.doc_directory.exists():
    session_state("docs_hide", False)
    filename = st.selectbox("Choose Document", [doc for doc in os.listdir(configs.doc_directory_str) if doc[-4:] != ".csv"],
                            help="Documents in the Document Repo", key="selectDocFile")
else:
    session_state("docs_hide", True)
    st.warning("The 'docs' file doesn't exist. Please be sure a directory name 'docs' is in your root directory of the app. ")
collection_name = st.selectbox("Choose a Collection | Weviate Class", options=doc_loader_select(vectordb_docload),
                               help="Chroma Collection Name or Weaviate Class Name", key="docUploadcn")
if collection_name is None or filename is None:
    session_state("docs_hide", True)
    st.warning("No documents / No collections available. Please add the missing items. ")

if vectordb_docload == "Weaviate":
    session_state("uploadWeaviateHide", False)
    total_properties = len(weaviate_get_schema(collection_name)["properties"])
    text_tag = st.selectbox("Choose Class Property Name",
                            options=[weaviate_get_schema(collection_name)["properties"][prop]["name"] for prop in range(total_properties)],
                            help="Class Property Name, also known as, text_tag",
                            key="docLoadingWvClProp")

if st.button("Submitted", disabled=st.session_state["docs_hide"], help="This will create a new Chroma Colllection or add Weaviate Class"):
    with st.spinner('Processing...'):
        if vectordb_docload == "ChromaDB":
            chroma_create_vectordb(filename, collection_name)
        elif vectordb_docload == "Weaviate":
            weaviate_add_doc_to_class(filename, collection_name, text_tag)
        st.experimental_rerun()

# CSV LOADER SECTION

st.divider()

with st.expander("Expand to load CSV to 'document_repo' directory."):
    csv_file = st.file_uploader(label="Upload CSV File", type=["csv"], accept_multiple_files=False, key="CSVUploader", )
    if csv_file is not None:
        fp = configs.doc_directory.joinpath(f"{csv_file.name}")
        with open(fp.as_posix(), "wb") as f:
            f.write(csv_file.getbuffer())
            logger.info("%s uploaded", csv_file.name)
            st.success(f"Uploaded {csv_file.name} to {configs.doc_directory_str}")

# CSV Loader

st.subheader("Upload CSV to Doc Repo")
st.write("Expand to load CSV File from the 'document_repo' directory to vector store collection.")
if configs.doc_directory.exists() or csv_file:
    session_state("csv_hide", False)
    csv_file = st.selectbox("Choose Document", [doc for doc in os.listdir(configs.doc_directory_str) if doc[-4:] == ".csv"], key='csv_filename', )
else:
    session_state("csv_hide", True)
    st.warning("Please be sure a 'csv' file is in your 'docs' directory of the app.")
collection_name = st.selectbox("Choose a Collection", options=[coll.name for coll in list_collections()], key="docLoadSelectCollection")
if collection_name is None or csv_file is None:
    session_state('csv_hide', True)
    st.warning("No 'csv' / No collections available. Please add the missing items. ")

if st.button("Submit", disabled=st.session_state["csv_hide"], key="docLoadSubmitButton"):
    with st.spinner('Processing...'):
        chroma_create_vectordb(csv_file, collection_name)
        st.experimental_rerun()

# Upload a Custom Prompt

st.subheader("Upload a Custom Prompt to Doc Repo/Custom_Prompts")
yaml_file = st.file_uploader(label="Upload CSV File", type=["yaml"], accept_multiple_files=False, key="uploaderCustomPromptYaml", )
if yaml_file is not None:
    fp = custom_prompt_directory.joinpath(f"{yaml_file.name}")
    with open(fp.as_posix(), "wb") as f:
        f.write(yaml_file.getbuffer())
        logger.info("%s uploaded", yaml_file.name)
        st.success(f"Uploaded {yaml_file.name} to {custom_prompt_directory.as_posix()}")
