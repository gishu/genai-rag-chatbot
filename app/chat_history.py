import streamlit as st

# message type codes aka langchain
HUMAN = 'human'
AI = 'ai'
SYSTEM = 'system'

class ChatHistory:
    '''
    Maintain a sequence of messages to enable a proper conversation
    Backed by streamlit session_state. Volatile.
    '''

    def __init__(self, key, system_prompt='You are a helpful assistant. Answer in english and in less than 5 sentences'):
        ''' Against the specified key,  Initialize an array with a system prompt as the first message in session state '''

        self.key = key
        if not self.__exists():
            st.session_state[key] = [
                {'role': 'system', 'content': system_prompt}]
        

    def add_human_message(self, content):
        st.session_state[self.key].append({'role': HUMAN, 'content': content})

    def add_ai_message(self, content):
        st.session_state[self.key].append({'role': AI, 'content': content})

    def get_messages(self):
        return st.session_state[self.key]
    
    def get_message_tuples(self):
        return [(m['role'], m['content'])
                                    for m in st.session_state[self.key]]

    def __exists(self):
        return (self.key in st.session_state)
    
    def is_sys_message(message):
        return message['role'] == SYSTEM

    def is_user_message(message):
        return message['role'] == HUMAN
