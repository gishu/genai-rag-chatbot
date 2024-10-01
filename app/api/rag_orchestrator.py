import api.pdf_parser as pdf_parser
from api.chroma_wrapper import ChromaWrapper

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings


class RagOrchestrator:
    '''
    Orchestrates various components for RAG
    '''

    def __init__(self, model_type, model_temp):

        if model_type.startswith('Google'):
            self.vector_db = ChromaWrapper(GoogleGenerativeAIEmbeddings(
                model="models/text-embedding-004"))

            self.llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash", temperature=model_temp)
        else:
            self.vector_db = ChromaWrapper(OpenAIEmbeddings(model="text-embedding-3-small"))
            self.llm = ChatOpenAI(model='gpt-4o-mini', temperature=model_temp)

    def load_pdf(self, data_file):
        '''
        Parse and vectorize the specified PDF file
        Load the pdf, split it into chunks. Convert to embeddings and store in database
        '''
        chunks = pdf_parser.parse_to_chunks(data_file)

        items = self.vector_db.add(chunks)
        return len(items)

    def clear_embeddings(self):
        self.vector_db.clear()

    def get_documents_count(self):
        ''' Returns the count of vectors/embeddings in the DB'''
        return self.vector_db.document_count()

    def ask(self, messages):
        '''
        Ask a query to the LLM (last message) with the chat history.
        Expects a sequence of messages of format ([role], [content])
            where role is human/ai/system (see also: langchain message) 
            & content is message text
        '''

        # Need to format the query to have a question and context placeholder
        m = messages[:]
        last_msg = m.pop()
        m.append(RagOrchestrator.__format_as_question_with_context(last_msg))

        user_query = last_msg[1]

        prompt_template = ChatPromptTemplate.from_messages(m)
        rag_chain = ({"context": self.vector_db.store.as_retriever() | RagOrchestrator.__context_formatter, "question": RunnablePassthrough()}
                     | prompt_template
                     | self.llm
                     | StrOutputParser())

        return rag_chain.invoke(user_query)

    def similarity_search(self, query):
        return self.vector_db.similarity_search(query)

    def __context_formatter(relevant_docs):
        ''' 
        INTERNAL method for concatenating the documents relevant to the user's query '''
        return "\n\n".join([doc.page_content for doc in relevant_docs])

    def __format_as_question_with_context(user_message):
        ''' Creates a message with content = prompt template with placeholders e.g.q, context '''
        return (user_message[0], '''
                Question: {question}

                Context: {context}

                Answer: 
                ''')
