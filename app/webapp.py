import streamlit as st
import chatbot_api as api
import messages as msg_store

st.set_page_config(page_title='Ragnarok', page_icon=':8ball:')

st.title('AI Chatbot :green[powered by RAG]')

if msg_store.empty():
    msg_store.init()

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
        response = api.ask(user_prompt)
    
    msg_store.add_message(msg_store.AI, response)

    st.rerun()
