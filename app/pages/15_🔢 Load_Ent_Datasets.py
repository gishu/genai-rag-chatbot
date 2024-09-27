from pathlib import Path

import streamlit as st

from api.rag_orchestrator import RagOrchestrator


st.set_page_config(page_title='Load Ent. Datasets', page_icon=':material/database:')
st.title('Load Ent. Datasets :material/database:')

_the_conductor = RagOrchestrator()


@st.fragment(run_every='3s')
def sidebar_fragment():
    
    st.session_state['etl.doc_count'] = _the_conductor.get_documents_count()
    st.metric('Indexed documents', st.session_state['etl.doc_count'], delta=None)

    cleared = st.button(':red[Clear Database]', key='etl.clear_db')
    if cleared:
        _the_conductor.clear_embeddings();
        st.toast(':material/delete_sweep: Embeddings cleared')

with st.sidebar:
    sidebar_fragment()


pdfFile = st.file_uploader('Select private dataset (pdf)', accept_multiple_files=False, key='etl.uploaded_file', type= ['pdf'])
if (pdfFile):
    
    dest_path = Path(f'./tmp-files/Upload-{pdfFile.name}')
    processed_docs = 0
    try:
        Path('./tmp-files').mkdir(exist_ok=True)

        with st.spinner('Processing...'):
            with open(dest_path.name, mode='wb') as w:
                w.write(pdfFile.getvalue())

            processed_docs = _the_conductor.load_pdf(dest_path.name)
        st.session_state['etl.doc_count'] = _the_conductor.get_documents_count()
    
    finally:        
        if dest_path.is_file():
            dest_path.unlink()
        
    st.success(f':thumbsup: :green[Ingested {processed_docs} chunks]')


