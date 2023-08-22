import streamlit as st

st.header("Session State")
st.json(st.session_state)

st.button("Re-run", key="session_state_page_refresh")
