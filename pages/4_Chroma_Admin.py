import streamlit as st

from config import Config
from data.chroma_db import (create_collection, delete_collection,
                            list_collections)

# Load config settings
configs = Config()

# Set Logging
logger = configs.logger

col1, col2 = st.columns(2)
with col1:

    # Create & Modify Vectorstores

    st.header("Create & Modify Vectorstores")
    with st.expander("Expand for Chroma Settings 👇", expanded=True):
        st.header("Create Collection - ChromaDB only")
        st.write("Note: See Weaviate tab for class creation")
        collection_name = st.text_input("Collection Name", help="Name for Collection. Must not have spaces")
        if st.button("Create"):
            create_collection(collection_name)
            st.experimental_rerun()

        st.header("Delete a Chroma Collection")
        collection_name = st.selectbox("Choose a Collection", options=[coll.name for coll in list_collections()], key="deleteVectorstore")
        if st.button("Delete"):
            delete_collection(collection_name)
            st.experimental_rerun()


with col2:

    st.header("Current Vectore Store Collections")
    for coll in list_collections():
        st.divider()
        st.write(f"📚 name: {coll.name:} | 💫 item count: {coll.count()}")
