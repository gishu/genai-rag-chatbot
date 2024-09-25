import streamlit as st

HUMAN='human'
AI='ai'
SYSTEM='system'

def empty():
    return ('messages' not in st.session_state) or (len(st.session_state['messages']) == 0)

def init():
    st.session_state.messages = [
        {'type': 'system', 'content': 'You are a helpful assistant. Use only the provided context to answer any queries in less than 5 sentences'}
    ]

def add_message(type, content):
    st.session_state.messages.append({'type': type, 'content': content})