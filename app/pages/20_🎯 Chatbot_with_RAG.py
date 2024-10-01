import os
from pathlib import Path
import pandas as pd
import streamlit as st

from chat_history import ChatHistory
from api.rag_orchestrator import RagOrchestrator


st.set_page_config(
    page_title='Specialized Assistant using RAG', page_icon=':dart:')

st.title(':dart: Chatbot powered by :violet[RAG]')


def __initChatMessages():

    # clear chat

    # widget state switch - see docs.streamlit.io/develop/concepts/architecture/widget-behavior#widgets-do-not-persist-when-not-continually-rendered
    new_sys_prompt = st.session_state["_"+SYS_PROMPT_KEY]

    st.session_state[SYS_PROMPT_KEY] = new_sys_prompt
    st.session_state['chatHistory'] = ChatHistory(
        'rag_chat.messages', new_sys_prompt)


def __createModel():
    model_type = st.session_state['_rag_chat.modelType']
    model_temp = st.session_state['_rag_chat.modelTemp']

    st.session_state['rag_chat.orc'] = RagOrchestrator(model_type, model_temp)


def __update_model_spec():
    st.session_state['rag_chat.modelType'] = st.session_state['_rag_chat.modelType']
    st.session_state['rag_chat.modelTemp'] = st.session_state['_rag_chat.modelTemp']
    __createModel()


def _get_orc():
    return st.session_state['rag_chat.orc']


# Prelude

# constants
SYS_PROMPT_KEY = 'rag_chat.system_prompt'
SYS_PROMPT = '''You are an expert analyst who can answer questions on financial statements and investor presentations.

Use the pieces of retrieved context only to answer the question. 
If you don't know the answer, just say that you can respond that it is outside your area of expertise. Do not give any reasons for the same.
Answer in a formal, concise manner and within 200 words '''


if ('globalSetupDone' not in st.session_state):
    GOOG_API_KEY = 'GOOGLE_API_KEY'
    if (GOOG_API_KEY in st.secrets):
        os.environ[GOOG_API_KEY] = st.secrets[GOOG_API_KEY]

    OPENAI_API_KEY = 'OPENAI_API_KEY'
    if (OPENAI_API_KEY in st.secrets):
        os.environ[OPENAI_API_KEY] = st.secrets[OPENAI_API_KEY]

    if (OPENAI_API_KEY not in os.environ):
        st.error('Cannot proceed without an API Key (Open AI)', icon=':material/error:')
        st.stop();
    
    if (GOOG_API_KEY not in os.environ):
        st.error('Cannot proceed without an API Key (Google)', icon=':material/error:')
        st.stop();
        
    st.session_state['globalSetupDone'] = True

if ('pageSetupDone' not in st.session_state):
    st.session_state[SYS_PROMPT_KEY] = SYS_PROMPT
    st.session_state['chatHistory'] = ChatHistory(
        'rag_chat.messages', SYS_PROMPT)

    st.session_state['rag_chat.modelType'] = 'Google Gemini'
    st.session_state['rag_chat.modelTemp'] = 0.3
    st.session_state['pageSetupDone'] = True

st.session_state['_rag_chat.modelType'] = st.session_state['rag_chat.modelType']
st.session_state['_rag_chat.modelTemp'] = st.session_state['rag_chat.modelTemp']
__createModel()


# see docs.streamlit.io/develop/concepts/architecture/widget-behavior#widgets-do-not-persist-when-not-continually-rendered
st.session_state["_" + SYS_PROMPT_KEY] = st.session_state[SYS_PROMPT_KEY]


def model_settings_fragment():
    with st.expander('Model', icon=':material/edit:', expanded=False):
        st.selectbox('Select LLM', ['Google Gemini', 'OpenAI ChatGPT'],
                     key='_rag_chat.modelType',
                     on_change=__update_model_spec)

        st.slider('Temperature', 0.0, 1.0, step=0.1,
                  key='_rag_chat.modelTemp',
                  on_change=__update_model_spec)

        st.text_area('System Prompt', key="_"+SYS_PROMPT_KEY,
                     max_chars=500, on_change=__initChatMessages)


@st.fragment(run_every='3s')
def db_stats_fragment(api):

    col1, col2 = st.columns([1, 1])
    st.session_state['rag_chat.doc_count'] = api.get_documents_count()
    col1.metric('Indexed documents',
                st.session_state['rag_chat.doc_count'], delta=None)

    cleared = col2.button(':red[Clear Database]', key='rag_chat.clear_db')
    if cleared:
        api.clear_embeddings()
        st.toast(':material/delete_sweep: Embeddings cleared')


def dev_tools_section(api):
    with st.expander('Debug', icon=':material/manage_search:', expanded=False):

        _sample_query = st.text_input(
            'Enter sample query', key='_rag_chat.query_for_sim_search')
        if (_sample_query):
            docs = api.similarity_search(_sample_query)
            st.dataframe(pd.DataFrame(docs, columns=['Score', 'Document']))

        # list messages
        st.text('Messages')
        data = st.session_state['chatHistory'].get_message_tuples()
        st.dataframe(pd.DataFrame(data, columns=['Role', 'Message']))


def etl_section(api):
    pdfFile = st.file_uploader('Select private dataset (pdf)',
                               accept_multiple_files=False, key='etl.uploaded_file', type=['pdf'])

    if (pdfFile):

        dest_path = Path(f'./tmp-files/Upload-{pdfFile.name}')
        processed_docs = 0
        try:
            Path('./tmp-files').mkdir(exist_ok=True)

            with st.spinner('Processing...'):
                with open(dest_path.name, mode='wb') as w:
                    w.write(pdfFile.getvalue())

                processed_docs = api.load_pdf(dest_path.name)
            st.session_state['etl.doc_count'] = api.get_documents_count()

        finally:
            if dest_path.is_file():
                dest_path.unlink()

        st.success(f':thumbsup: :green[Ingested {processed_docs} chunks]')


with st.sidebar:
    api = _get_orc()
    with st.expander('ETL', icon=':material/database:', expanded=False):
        db_stats_fragment(api)
        etl_section(api)

    model_settings_fragment()

    dev_tools_section(api)

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

st.caption(f':heavy_check_mark: Creating model {
           st.session_state['_rag_chat.modelType']}  (temp={st.session_state['_rag_chat.modelTemp']})')


def render_chat():
    with st.container():
        for message in st.session_state['chatHistory'].get_messages():

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

    _history = st.session_state['chatHistory']
    _history.add_human_message(user_prompt)

    try:
        with st.spinner('Please wait...'):
            response = _get_orc().ask(_history.get_message_tuples())

    except Exception as ex:
        response = f'Error: {type(ex)}'

    _history.add_ai_message(response)

    st.rerun()
