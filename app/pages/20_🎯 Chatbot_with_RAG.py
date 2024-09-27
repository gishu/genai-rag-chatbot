import os
import pandas as pd
import streamlit as st

from chat_history import ChatHistory
from api.rag_orchestrator import RagOrchestrator


st.set_page_config(
    page_title='Specialized Assistant using RAG', page_icon=':dart:')

st.title(':dart: Chatbot powered by :violet[RAG]')

# Prelude
_api = RagOrchestrator()
_history = ChatHistory('rag_chat.messages')

GOOG_API_KEY = 'GOOGLE_API_KEY'
if (GOOG_API_KEY in st.secrets):
    os.environ[GOOG_API_KEY] = st.secrets[GOOG_API_KEY]


def __initChatMessages():
    _history = ChatHistory('rag_chat.messages')

with st.sidebar:

    with st.expander('Advanced', icon=':material/manage_search:'):

        # if metric is 0, store is empty
        st.metric('Indexed documents', _api.get_documents_count(), delta=None)

        st.text_area('System Prompt', key='system_prompt',
                     max_chars=500, on_change=__initChatMessages)

        # list messages
        st.text('History')
        data = _history.get_message_tuples()
        st.dataframe(pd.DataFrame(data, columns=['Role', 'Message']))


st.info("You type in a query. Wait for a few seconds for your answer.")
# Tweak to right align user's messages
st.html(
    """
<style>
    .stChatMessage:has(.is-user) {
        flex-direction: row-reverse;
        text-align: right;
    }
</style>
"""
)


def render_chat():
    with st.container():
        for message in _history.get_messages():

            if (not ChatHistory.is_sys_message(message)):
                if (ChatHistory.is_user_message(message)):
                    with st.chat_message('user'):
                        st.html(f"<span class='is-user'></span>")
                        st.write(message['content'])
                else:
                    with st.chat_message('ai'):
                        if (message['content'].startswith('Error:')):
                            st.error(f':anger: :red[{message['content']}]')
                        else:
                            st.markdown(
                                f':violet[ {message['content']} ] :sparkles:')

render_chat()

user_prompt = st.chat_input("How can I help you?", key='user-prompt')
if (user_prompt):
    user_prompt = user_prompt.strip()
    _history.add_human_message(user_prompt)

    try:
        with st.spinner('On it...'):
            if (GOOG_API_KEY not in os.environ):
                response = 'Error: Not authorized without a key'
            else:
                response = _api.ask(_history.get_message_tuples())
                st.toast(response)

    except Exception as ex:
        response = f'Error: {type(ex)}'

    _history.add_ai_message(response)

    st.rerun()
