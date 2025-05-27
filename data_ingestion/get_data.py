from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from pypdf import PdfReader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os

def get_pdf_text(pdf):
    text=""
    pdf_reader= PdfReader(pdf)
    for page in pdf_reader.pages:
        text+= page.extract_text()
    return  text


def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=50)
    chunks = text_splitter.split_text(text)
    return chunks



def create_vector_store(text:str = "Hello world!"):
    chunks = get_text_chunks(text)
    embeddings = GoogleGenerativeAIEmbeddings(model = "models/gemini-embedding-exp-03-07")
    vector_store = FAISS.from_texts(chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")
    return vector_store
    
def get_vector_store():
    embeddings = GoogleGenerativeAIEmbeddings(model = "models/gemini-embedding-exp-03-07")
    if not os.path.exists("faiss_index"):
        return create_vector_store()
    vectorstore = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    return vectorstore