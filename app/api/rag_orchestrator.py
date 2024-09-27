import api.pdf_parser as pdf_parser
from api.chroma_wrapper import ChromaWrapper

from langchain_google_genai import ChatGoogleGenerativeAI


class RagOrchestrator:
    '''
    Orchestrates various components for RAG
    '''

    def __init__(self):
        self.vector_db = ChromaWrapper()
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")


    def load_pdf(self, data_file):
        '''
        Parse and vectorize the specified PDF file
        Load the pdf, split it into chunks. Convert to embeddings and store in database
        '''
        chunks = pdf_parser.parse_to_chunks(data_file)

        ids = ["Page%s/%s" % (chunk.metadata['page'], index)
                              for index, chunk in enumerate(chunks)]

        items = self.vector_db.store.add_documents(documents=chunks, ids=ids)
        return len(items)

    def clear_embeddings(self):
        self.vector_db.clear()

    def get_documents_count(self):
        ''' TEST Function'''
        return len(self.vector_db.document_count())
    
    
    
