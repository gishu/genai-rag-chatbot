import streamlit as st

import msg_store
import os

GOOG_API_KEY = 'GOOGLE_API_KEY'
if (GOOG_API_KEY in st.secrets):
    os.environ[GOOG_API_KEY] = st.secrets[GOOG_API_KEY]

st.set_page_config(page_title='Ragnarok', page_icon=':technologist:')

st.title('Chatbot demo app')

st.info('Under Construction')




