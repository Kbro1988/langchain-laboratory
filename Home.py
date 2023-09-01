#! /usr/bin/env python3

import os
import re
from textwrap import dedent

import streamlit as st

st.set_page_config(page_title="LangChain-Laboratory", page_icon="🔬", layout="wide")  # This must be placed before data files are imported

from config import Config
from data.ai_api import Query
from data.chroma_db import list_collections
from data.weaviate_db import weaviate_get_classes, weaviate_get_schema

# Load config settings
configs = Config()

# Set Logging
logger = configs.logger

# Instantiate
query_session = Query()

# Set the directory for custom prompts
custom_prompt_directory = configs.custom_prompt_directory


def session_state(key: any, value: any) -> None:
    """
    session_state Create and update the Streamlit Session State

    Args:
        key (any): Required. Dictionary Key
        value (any): Required. Dictionary Value
    """
    if key not in st.session_state:
        st.session_state[key] = value
        logger.debug("Session State: %s added.", key)
    elif key in st.session_state:
        st.session_state[key] = value
        logger.debug("Session State: %s updated", key)


def doc_loader_select(vectordb_docload):
    if vectordb_docload == "ChromaDB":
        collection = [coll.name for coll in list_collections()]
        return collection
    elif vectordb_docload == "Weaviate":
        collection = [cn for cn in weaviate_get_classes()]
        return collection


st.title("LangChain Laboratory 🧪")
main_tab, docsearch_output = st.tabs(["Main 🏠",  "Vector Store Content Chunks 📚"])

# Main Page Start

with main_tab:
    with st.expander("Query Settings", expanded=True):
        model = st.selectbox("Choose LLM", options=query_session.MODELS, index=0,
                             help=dedent("""\
                                        Choose the LMM model you wish to use. Earlier models will
                                        provide faster performance, but may yeild less quality responses
                                        compared to newer models. Also some models will handle more than
                                        4096 tokens, but their is more cost associated with them."""), key="selectModel")
        if "vectordb_choice" not in st.session_state:
            st.session_state['vectordb_choice'] = "ChromaDB"
        radio_default = 1 if st.session_state["vectordb_choice"] == "Weaviate" else 0
        vectordb_choice = st.radio("Choose the vector store", ("ChromaDB", "Weaviate",), index=radio_default, key="vectordb_choice", horizontal=True)
        collection_name = st.selectbox("Choose a Collection", options=doc_loader_select(st.session_state["vectordb_choice"]),
                                       help=dedent("""\
                                                   Choose the Chroma Vector Store collection that will
                                                   will be queried. This collection will be used by the
                                                   vectordb object to use the 'similiarity_search()' methdod.
                                                   This is part of the LangChain Chroma Class. See
                                                   https://python.langchain.com/docs/integrations/vectorstores/chroma
                                                   for more information"""), key="queryVDB")
        if "Weaviate" in st.session_state["vectordb_choice"]:
            total_properties = len(weaviate_get_schema(collection_name)["properties"])
            text_key = st.selectbox("Choose Class Property Name",
                                    options=[weaviate_get_schema(collection_name)["properties"][prop]["name"] for prop in range(total_properties)],
                                    help="Class Property Name, also known as, text_tag",
                                    key="queryWvClProp", disabled="Weaviate" not in st.session_state["vectordb_choice"])
        else:
            text_key = None
        prompt = st.selectbox("Choose Prompt Template", options=query_session.AVAILABLE_PROMPTS, key="homePromptSelectBox")
        if prompt == "CUSTOM PROMPT":
            query_session.custom_prompt_filename = st.selectbox("Choose the custom prompt filename.",
                                                                options=[doc for doc in os.listdir(custom_prompt_directory.as_posix()) if doc[-5:] == ".yaml"],
                                                                disabled=st.session_state['homePromptSelectBox'] != "CUSTOM PROMPT",
                                                                key="homeCustomPromptFilenameSelectBox")
        search_name = st.radio("Search Type", ("Similarity", "MMR", "Similarity and Display Score", "Similarity with Score Threshold", "Filter"),
                               index=0, key="querySearchType", horizontal=True, help=dedent("""\
                                - Activate an MMR document search. Increases Document Diversity
                                - Set Relvance Score"""))
        k_value = st.select_slider("Select K-value for Doc Query", options=[k_val for k_val in range(1, 8)], value=4, format_func=int,
                                   help=dedent("""\
                                               Choose the K Value (1 through 8. Default: 4.)
                                               for the simlarity search. This will determine how many
                                               chuncks you will retrieve from the Vector Store."""))
        kwargs_text = st.text_input("Search Keys", placeholder="None", key="homeSearchKeysTextInput")
        if kwargs_text != "None":
            kwargs = dict(re.findall(r'(\w+)\s*=\s*(\w+)', kwargs_text))
            if "lambda_mult" in kwargs.keys():
                kwargs["lambda_mult"] = float(kwargs["lambda_mult"])
            if "fetch_k" in kwargs.keys():
                kwargs["fetch_k"] = int(kwargs["fetch_k"])
            if "score_threshold" in kwargs.keys():
                kwargs["score_threshold"] = float(kwargs["score_threshold"])

    # Query Settings
    st.header("Query Document 🙋‍♂️")
    chain_type = st.radio("Choose QA Chain", options=("stuff", "map_reduce", "refine", "map_rerank"), index=0, key="homeChainTypeRadio", horizontal=True,
                          help="Choose Chain Type. Please note that history is not stored or custom promps used for any chain other than stuff")
    query = st.text_input("Query")

    with st.expander("Memory"):
        st.json(query_session.load_memory())
        if st.button("Reset Memory"):
            query_session.clear_memory()
            st.experimental_rerun()

    # Query Response

    st.subheader("Reponse:")
    response_box = st.empty()
    with response_box.container():
        if st.button("Submit"):
            with st.spinner("Processing..."):
                output = query_session.get_query(model, query, vectordb_choice, collection_name, text_key, prompt, chain_type, search_name, k_value, **kwargs)
            if search_name == "Similarity and Display Score":
                st.markdown(output[0])
            else:
                st.markdown(output["result"])

with docsearch_output:
    st.header("Docs retrieved from the Vector Store Database")
    try:
        if search_name == "Similarity and Display Score":
            for docnum, line in enumerate(output[1]):
                st.write(f"Doc Number: {docnum + 1}")
                st.code(f"Page Content:\n{line[0].page_content}")
                st.code(f"Metadata:\n{line[0].metadata}")
                st.code(f"Score: {line[1]}")
        else:
            for docnum, line in enumerate(output["source_documents"]):
                if line.metadata:
                    source_info = line.metadata["page"]
                else:
                    source_info = "Null"
                st.write(f"Doc Number: {docnum + 1} - Source Page: {source_info}")
                st.code(f"Page Content:\n{line.page_content}")
                st.code(f"Metadata:\n{line.metadata}")
    except (NameError, TypeError):
        st.write("Null")
