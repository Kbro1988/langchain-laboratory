import os
from textwrap import dedent

import streamlit as st
from streamlit.logger import get_logger

from ai_api import AVAILABLE_PROMPTS, MODELS, get_query
from vectorstore import (DOC_DIRECTORY, create_collection, create_vectordb,
                         delete_collection, list_collections)

st.set_page_config(page_title="QA",
                   page_icon="",
                   layout="wide")

# Set Logging
logger = get_logger(__name__)


def session_state(key, value):
    if key not in st.session_state:
        st.session_state[key] = value
        logger.info(f"Session State: {key} added.")
    elif key in st.session_state:
        st.session_state[key] = value
        logger.info(f"Session State: {key} updated")


labdash = st.container()

labdash.title("LangChain Laboratory 🧪")

labdash_col1, labdash_col2, labdash_col3 = labdash.columns([1, 1, 1])
with labdash_col1:
    st.header("Query Document 🙋‍♂️")
    with st.form("query"):
        model = st.selectbox("Choose LLM",
                             options=[llm for llm in MODELS],
                             index=0,
                             help=dedent("""Choose the LMM model you wish to use. Earlier models will
                                         provide faster performance, but may yeild less quality responses
                                         compared to newer models. Also some models will handle more than
                                         4096 tokens, but their is more cost associated with them."""))
        collection_name = st.selectbox("Choose a Collection",
                                       options=[coll.name for coll in list_collections()],
                                       help=dedent("""Choose the Chroma Vector Store collection that will
                                                   will be queried. This collection will be used by the
                                                   vectordb object to use the 'similiarity_search()' methdod.
                                                   This is part of the LangChain Chroma Class. See
                                                   https://python.langchain.com/docs/integrations/vectorstores/chroma
                                                   for more information"""))
        prompt = st.selectbox("Choose Prompt Template",
                              options=[prompt for prompt in AVAILABLE_PROMPTS])
        k_value = st.select_slider("Select K-value for Doc Query",
                                   options=[k_val for k_val in range(1, 8)],
                                   value=4,
                                   format_func=int,
                                   help=dedent("""Choose the K Value (1 through 8. Default: 4.)
                                               for the simlarity search. This will determine how many
                                               chuncks you will retrieve from the Vector Store."""))
        query = st.text_input("Query")
        submitted = st.form_submit_button("Query")
    st.subheader("Reponse:")
    with st.empty():
        if submitted:
            with st.spinner("Processing..."):
                response = get_query(model,
                                     query,
                                     collection_name,
                                     prompt,
                                     k_value,
                                     )
            st.markdown(response)


with labdash_col2:
    st.header("Current Vectore Store Collections")
    for coll in list_collections():
        st.divider()
        st.write(f"📚 name: {coll.name:} | 💫 vectors: {coll.count()}")

with labdash_col3:
    with st.expander("Expand for Vector Store Settings 👇"):
        st.header("Create & Modify Collections")
        with st.form("create_collection"):
            st.write("Create a new Collection")
            collection_name = st.text_input("Collection Name")
            submitted = st.form_submit_button("Create")
        if submitted:
            create_collection(collection_name)
            st.experimental_rerun()

        st.header("Delete a Collection")
        with st.form("delete_collection"):
            st.write("Delete a Collection")
            collection_name = st.selectbox("Choose a Collection",
                                        options=[coll.name for coll in list_collections()]
                                        )
            submitted = st.form_submit_button("Delete")
        if submitted:
            delete_collection(collection_name)
            st.experimental_rerun()

        st.header("Load a Document")
        with st.form("load_document"):
            st.write("Load a Document from the 'docs' directory.")
            if DOC_DIRECTORY.exists():
                session_state('docs_exists', False)
                filename = st.selectbox("Choose Document",
                                        [doc for doc in os.listdir(DOC_DIRECTORY)],
                                        key='document_filename', )
            else:
                session_state('docs_exists', True)
                st.warning("The 'docs' file doesn't exist. Please be sure a directory name 'docs' is in your root directory of the app. ")
            collection_name = st.selectbox("Choose a Collection",
                                        options=[coll.name for coll in list_collections()])
            if collection_name is None or filename is None:
                session_state('docs_exists', True)
                st.warning("No documents / No collections available. Please add the missing items. ")

            submitted = st.form_submit_button("Load Document", disabled=st.session_state.docs_exists)
        if submitted:
            with st.spinner('Processing...'):
                create_vectordb(filename, collection_name)
            st.experimental_rerun()
