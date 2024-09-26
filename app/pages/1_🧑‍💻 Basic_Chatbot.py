import os

import streamlit as st

import msg_store
import chatbot_api as api

if msg_store.empty():
    msg_store.init()

st.set_page_config(page_title='A Chatbot', page_icon=':8ball:')

st.title('Basic chatbot talking to an :green[LLM]')

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
                        st.markdown(f'**{message['content']}**')

render_chat()

user_prompt = st.chat_input("How can I help you?", key='user-prompt')
if (user_prompt):
    user_prompt = user_prompt.strip()
    msg_store.add_message(msg_store.HUMAN, user_prompt)

    with st.spinner('On it...'):
        response = api.ask( [ (m['type'], m['content']) for m in st.session_state.messages] )
    
    msg_store.add_message(msg_store.AI, response)

    st.rerun()