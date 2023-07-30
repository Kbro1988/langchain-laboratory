import os
from textwrap import dedent
from ai_api import get_query, AVAILABLE_PROMPTS, MODELS
import streamlit as st
from vectorstore import (
    DOC_DIRECTORY,
    list_collections,
    create_collection,
    create_vectordb,
    delete_collection,)

st.set_page_config(page_title="QA",
                   page_icon="",
                   layout="wide")

chromadash = st.container()

chromadash.title("Chroma Vector Store Dashboard")
chromadash_col1, chromadash_col2, chromadash_col3 = chromadash.columns([1, 1, 1])
with chromadash_col1:
    st.header("Current Vectore Store Collections")
    for coll in list_collections():
        st.divider()
        st.write(f"📚 name: {coll.name:} | 💫 vectors: {coll.count()}")

with chromadash_col2:
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
    with st.empty():
        if submitted:
            response = get_query(model,
                                 query,
                                 collection_name,
                                 prompt,
                                 k_value,
                                 )
            st.write(response)


with chromadash_col3:
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
        st.write("Load a Document")
        filename = st.selectbox("Choose Document",
                                [doc for doc in os.listdir(DOC_DIRECTORY)])
        collection_name = st.selectbox("Choose a Collection",
                                       options=[coll.name for coll in list_collections()])
        submitted = st.form_submit_button("Load Document")
    if submitted:
        create_vectordb(filename, collection_name)
        st.experimental_rerun()
