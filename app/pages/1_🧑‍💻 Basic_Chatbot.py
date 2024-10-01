import os

import streamlit as st

from chat_history import ChatHistory
import chatbot_api as api


st.set_page_config(page_title='A Chatbot', page_icon=':8ball:')

st.title('Basic chatbot talking to an :green[LLM]')

GOOG_API_KEY = 'GOOGLE_API_KEY'

# Prelude
if ('globalSetupDone' not in st.session_state):
    
    if (GOOG_API_KEY in st.secrets):
        os.environ[GOOG_API_KEY] = st.secrets[GOOG_API_KEY]
    
    OPENAI_API_KEY = 'OPENAI_API_KEY'
    if (OPENAI_API_KEY in st.secrets):
        os.environ[OPENAI_API_KEY] = st.secrets[OPENAI_API_KEY]

    if (GOOG_API_KEY not in os.environ):
        st.error('Cannot proceed without an API Key (Google)', icon=':material/error:')
        st.stop();
    st.session_state['globalSetupDone'] = True

if ('basic_chat.pageSetupDone' not in st.session_state):
    st.session_state['basic_chat.history'] = ChatHistory(
        'rag_chat.messages')

    st.session_state['basic_chat.pageSetupDone'] = True




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
        for message in st.session_state['basic_chat.history'].get_messages():

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
    _history = st.session_state['basic_chat.history']
    _history.add_human_message(user_prompt)

    try:
        with st.spinner('On it...'):
            response = api.ask(_history.get_message_tuples())
    
    except Exception as ex:
        response = f'Error: {type(ex)}'

    _history.add_ai_message(response)

    st.rerun()
