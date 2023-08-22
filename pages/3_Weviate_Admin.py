import os
import traceback

import streamlit as st

from config import Config
from weaviate import exceptions
from data.weaviate_db import (create_class_obj, CLIENT,
                              weaviate_create_schema,
                              weaviate_get_batch_with_cursor,
                              weaviate_get_classes, weaviate_get_schema, weaviate_delete_class, weaviate_delete_id)

# Load config settings
configs = Config()

# Set Logging
logger = configs.logger

if "wv_schema_preview" not in st.session_state:
    st.session_state["wv_schema_preview"] = False
if "wv_schema_preview_existing" not in st.session_state:
    st.session_state["wv_schema_preview_existing"] = False


def expand_schema_preview_existing():
    st.session_state["wv_schema_preview_existing"] = True


weaviate_col1, weaviate_col2 = st.columns(2)
with weaviate_col1:
    with st.expander("Create Weaviate Class"):
        j2_file = st.file_uploader(label="Upload j2 File", type=["j2"], accept_multiple_files=False, key="weaviateJ2Uploader", )
        if j2_file is not None:
            fp = (f"{configs.weaviate_path}{j2_file.name}")
            with open(fp, "wb") as f:
                f.write(j2_file.getbuffer())
                logger.info("%s uploaded", j2_file.name)
                st.success(f"Uploaded {j2_file.name} to {configs.weaviate_path}")

        with st.form("create class"):
            with open('./weaviate/templates/base_schema_value_example.json', 'r') as f:
                example_values = f.read()
            schema_values = st.text_area("Update JSON of Schema values.", example_values, height=200)
            schema_template = st.selectbox("Select Schema Template", [file for file in os.listdir(configs.weaviate_path) if file.endswith(".j2")], key="schemaTemplate")
            create_template = st.form_submit_button("Create Template", type="primary")
            build = st.form_submit_button("Build Class from Temalate", type="secondary", disabled=not st.session_state["FormSubmitter:create class-Create Template"])
            template = None
            if create_template:
                template = create_class_obj(schema_template, schema_values)
                st.session_state["template"] = template
                st.session_state["wv_schema_preview"] = True
            if build:
                with st.spinner("Building Schema..."):
                    weaviate_create_schema(st.session_state["template"])
                    st.success("Class Successfully created")
                    st.session_state["template"] = None

with weaviate_col2:
    with st.expander("Schema Preview", expanded=st.session_state["wv_schema_preview"]):
        clear_preview = st.button("Clear Preview")
        if clear_preview:
            template = None
            st.session_state["wv_schema_preview"] = False
        template_preview_container = st.container()
        if template is not None:
            template_preview_container.json(template)
        else:
            template_preview_container.json("{\"Null\": \"Null\"}")
            st.session_state["wv_schema_preview"] = False

    with st.expander("View Existing Schemas", expanded=st.session_state["wv_schema_preview_existing"]):
        show_schema = st.selectbox("Select Class", options=[cn for cn in weaviate_get_classes()], key="weaviate_schema")
        if st.button("Display", on_click=expand_schema_preview_existing):
            st.json(weaviate_get_schema(show_schema))

st.header("Details")
wcn = st.selectbox("Select Class", options=[wcn for wcn in weaviate_get_classes()], key="weaviate_detail")
count: dict = CLIENT.query.aggregate(wcn).with_meta_count().do()
st.write("Chunk Data:")
st.write(f"📚 name: {wcn} | 💫 item count: {count['data']['Aggregate'][wcn][0]['meta']['count']}")
delete_class = st.checkbox("Activate Delete?", value=False, key="deleteClassActivateCheckbox")
if st.button("Delete Class", disabled=not st.session_state["deleteClassActivateCheckbox"], key="weaviateDeleteButton"):
    weaviate_delete_class(wcn)
    st.experimental_rerun()

# Object Retrieval
st.divider()
st.subheader("Object Retrieval")

input1, input2, input3 = st.columns([1, 1, 1])
total_properties = len(weaviate_get_schema(wcn)["properties"])
class_properties = input1.selectbox("Class Property", 
                                    options=[weaviate_get_schema(wcn)["properties"][prop]["name"] for prop in range(total_properties)], key="weaviateAdminClassProp")
batch_size = int(input2.text_input("Batch Size", value="20", help="Interger Only"))
cursor = input3.text_input("Cursor", value=None)

st.write("Delete by UID. Seperate by 1 sapce")
dl1, dl2 = st.columns(2)
ids = dl1.text_input("Null", label_visibility="hidden",
                     disabled=not st.session_state["deleteClassActivateCheckbox"], key="weaviatDeleteIdText").strip()
ids = ids.replace(" ", ",").split(",")
if dl2.button("Delete IDs", disabled=not st.session_state["deleteClassActivateCheckbox"], key="weaviateDeleteIdButton"):
    try:
        weaviate_delete_id(ids=ids, index_name=wcn, text_key=class_properties)
    except exceptions.UnexpectedStatusCodeException as e:
        logger.warning(traceback.format_exc(), e)
        st.exception(e)

if st.button("Get Batch"):
    with st.spinner("Processing..."):
        st.json(weaviate_get_batch_with_cursor(class_name=wcn, class_properties=class_properties, batch_size=batch_size, cursor=cursor))

# List classes
st.divider()
with st.expander("Expand for Weaviate Classes 👇"):
    for cn in weaviate_get_classes():
        st.divider()
        count: dict = CLIENT.query.aggregate(cn).with_meta_count().do()
        st.write(f"📚 name: {cn} | 💫 item count: {count['data']['Aggregate'][cn][0]['meta']['count']}")
