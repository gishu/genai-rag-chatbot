from langchain_chroma import Chroma
from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings

embedding_model = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004")


class ChromaWrapper:
    ''' Wrapper type for Langchain chroma database
        a Vector database to store embeddings and locate relevant docs/chunks
    '''

    def __init__(self):
        self.store = Chroma(
            collection_name="anamika",
            embedding_function=embedding_model,
            persist_directory="./data/chroma_db")

    def add(self, documents):
        ids = ["Page%s/%s" % (chunk.metadata['page'], index)
               for index, chunk in enumerate(documents)]

        return self.store.add_documents(documents=documents, ids=ids)

    def clear(self):
        self.store.reset_collection()

    def document_count(self):
        try:
            return len(self.store.get()['documents'])
        except:
            return 0

    def similarity_search(self, query):
        ''' Returns a [(score, document_text)...] of top 3 relevant/similar documents based on score '''
        return [(round(score, 3), doc.page_content[:250]) for doc,
                score in self.store.similarity_search_with_relevance_scores(query, k=5)]
