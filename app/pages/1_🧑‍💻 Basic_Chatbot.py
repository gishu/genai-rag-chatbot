import os

import streamlit as st

import msg_store
import chatbot_api as api


st.set_page_config(page_title='A Chatbot', page_icon=':8ball:')

st.title('Basic chatbot talking to an :green[LLM]')

#Prelude
if msg_store.empty():
    msg_store.init()

GOOG_API_KEY = 'GOOGLE_API_KEY'
if (GOOG_API_KEY in st.secrets):
    os.environ[GOOG_API_KEY] = st.secrets[GOOG_API_KEY]

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
        for message in st.session_state['messages']:
            msg_type = message['type']
            if (msg_type != msg_store.SYSTEM):
                with st.chat_message(msg_type):
                    if (msg_type == msg_store.HUMAN):
                        st.html(f"<span class='is-user'></span>")
                        st.write(message['content'])
                    else:
                        if (message['content'].startswith('Error:')):
                            st.error(f':anger: :red[{message['content']}]')
                        else:
                            st.markdown(f'**{message['content']}**')


render_chat()

user_prompt = st.chat_input("How can I help you?", key='user-prompt')
if (user_prompt):
    user_prompt = user_prompt.strip()
    msg_store.add_message(msg_store.HUMAN, user_prompt)

    try:
        with st.spinner('On it...'):
            if (GOOG_API_KEY not in os.environ):
                response = 'Error: Not authorized without a key'
            else:
                response = api.ask([(m['type'], m['content'])
                                    for m in st.session_state.messages])
    except Exception as ex:
        response = f'Error: {type(ex)}'

    msg_store.add_message(msg_store.AI, response)

    st.rerun()
