import streamlit as st

# Streamlit cloud has an incompatible version of Sqlite which breaks ChromaDb
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
# end workaround

st.set_page_config(page_title='Ragnarok', page_icon=':technologist:')

st.title('GenAI Chatbots')

st.markdown('''
### Basic chat

A general chatbot. LLM would answer all queries

            
### RAG Chatbot

A chatbot that would answer questions pertaining to a specific domain. 
The specific dataset has to be uploaded as a pdf beforehand.
            ''')





