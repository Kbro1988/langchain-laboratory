#! /usr/bin/env python3

import os

import streamlit as st
import yaml

from config import Config
from Home import session_state

# import config settings
configs = Config()

# Set logger
logger = configs.logger

custom_prompt_directory = configs.custom_prompt_directory

# Initialize Session State
if "original_prompt" not in st.session_state:
    st.session_state["old_custom_prompt"] = None
if "disable_cprompt_reset" not in st.session_state:
    st.session_state["disable_cprompt_reset"] = True


def load_yaml(custom_prompt):
    with open(custom_prompt_directory.joinpath(custom_prompt), "r") as f:
        prompt = yaml.safe_load(f)
        session_state("old_custom_prompt", prompt)
    return prompt


def str_presenter(dumper, data):
    if len(data.splitlines()) > 1:  # check for multiline string
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)


def list_to_str(prompt):
    _strform = ""
    for _ in prompt["input_variables"]:
        _strform += f"{_}, "
    return _strform[:-2]


def reset():
    st.session_state["promptFormPromptTypeTextInput"] = str(prompt["_type"])
    st.session_state["promptFormInputVariableTextInput"] = _input_variables
    st.session_state["promptFormPromptTemplateTextArea"] = str(prompt["template"])


def reset_callback():
    if prompt == st.session_state["old_custom_prompt"]:
        st.session_state["disable_cprompt_reset"] = False


st.title("Custom Prompt Editor")

st.write("Directions: Under Construction 🚧")

custom_prompt = st.selectbox("Choose the custom prompt filename.", options=[doc for doc in os.listdir(custom_prompt_directory.as_posix()) if doc[-5:] == ".yaml"], index=0,
                             key="promptEditorCustomPromptSelectBox")

try:
    prompt = load_yaml(custom_prompt)
    _input_variables = list_to_str(prompt)
    new_prompt = prompt.copy()
    new_prompt['_type'] = st.text_input("Prompt Type", prompt['_type'], on_change=reset_callback, key="promptFormPromptTypeTextInput")
    _new_input_variables = st.text_input("Prompt Variable", _input_variables, on_change=reset_callback, key="promptFormInputVariableTextInput")
    new_prompt['input_variables'] = [v.strip() for v in _new_input_variables.split(",")]
    new_prompt['template'] = st.text_area("Prompt Template", prompt['template'], height=700, on_change=reset_callback, key="promptFormPromptTemplateTextArea")
    if custom_prompt == "new_template.yaml":
        custom_prompt = st.text_input("Enter Filename")

    if st.button("Reset", disabled=st.session_state["disable_cprompt_reset"], on_click=reset):
        st.session_state["disable_cprompt_reset"] = True
        st.experimental_rerun()

    if st.button("Save Changes?"):
        try:
            if prompt == st.session_state["old_custom_prompt"]:
                with open(custom_prompt_directory.joinpath(custom_prompt), "w") as f:
                    yaml.representer.SafeRepresenter.add_representer(str, str_presenter)
                    yaml.safe_dump(new_prompt, f)
                st.success(f"✅ '{custom_prompt}' updated successfully! ")
                session_state("old_custom_prompt", new_prompt)
            else:
                st.info("⚠️ No changes were made to the template. Be sure you have pressed enter after you enter a value in each box.")
        except FileNotFoundError or TypeError as e:
            st.exception(f"{e}: There is an issue with your file. Please verify.")

except FileNotFoundError as e:
    st.exception(f"{e}: No custom templates found.")
