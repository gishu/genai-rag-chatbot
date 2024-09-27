from langchain_chroma import Chroma
from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings


embedding_model = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

class ChromaWrapper: 
    ''' Wrapper type for Langchain chroma database
        a Vector database to store embeddings and locate relevant docs/chunks
    '''
    def __init__(self):
        self.store = Chroma(
            collection_name="anamika",
            embedding_function=embedding_model,
            persist_directory="./data/chroma_db")  
        
    
    def clear(self):
        self.store.reset_collection()
    
    def document_count(self):
        return self.store.get()['documents']

    def similarity_search(self, query):
        ''' Returns a [(score, document_text)...] of top 3 relevant/similar documents based on score '''

        [(score, doc.page_content[:50]) for doc, score in self.store.similarity_search_with_relevance_scores(query, k=3)]
