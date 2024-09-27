
from langchain_community.document_loaders import PyPDFLoader, PDFMinerLoader

from langchain_text_splitters import RecursiveCharacterTextSplitter

# config
CHUNK_SIZE=500

def parse_to_chunks(file):
    loader = PDFMinerLoader(file, concatenate_pages=False)
    docs =loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=20, length_function=len)
    
    chunks = text_splitter.split_documents(docs)
    return chunks