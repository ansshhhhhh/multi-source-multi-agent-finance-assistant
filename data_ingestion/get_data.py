from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from pypdf import PdfReader
from langchain_community.document_loaders import WebBaseLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os
import shutil
from dotenv import load_dotenv
import google.generativeai as genai


load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

vectorstore_path = "data_ingestion/faiss_index"
embeddings = GoogleGenerativeAIEmbeddings(model = "models/gemini-embedding-exp-03-07")
# embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def get_pdf_text(pdf):
    text=""
    pdf_reader= PdfReader(pdf)
    for page in pdf_reader.pages:
        text += page.extract_text()
    return  text

def add_web_docs(urls:list[str]):
    docs = [WebBaseLoader(url).load() for url in urls]
    docs_list = [item for sublist in docs for item in sublist]
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=1024, chunk_overlap=64)
    doc_splits = text_splitter.split_documents(docs_list)
    if not os.path.exists(vectorstore_path):
        return create_vector_store()
    vectorstore = FAISS.load_local(vectorstore_path, embeddings, allow_dangerous_deserialization=True)
    vectorstore.aadd_documents(doc_splits)
    return True

def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=64)
    chunks = text_splitter.split_text(text)
    return chunks

def add_to_vectore_store(text: str):
    chunks = get_text_chunks(text)
    if not os.path.exists(vectorstore_path):
        return create_vector_store(chunks)
    vector_store = FAISS.load_local(vectorstore_path, embeddings, allow_dangerous_deserialization=True)
    vector_store.add_texts(chunks)
    return True

def delete_vector_store():
    if os.path.exists(vectorstore_path):
        shutil.rmtree(vectorstore_path)
    return True

def create_vector_store(chunks: list[str] = ["Hello world!"]):
    vector_store = FAISS.from_texts(chunks, embedding=embeddings)
    vector_store.save_local(vectorstore_path)
    return vector_store
    
def get_vector_store():
    if not os.path.exists(vectorstore_path):
        return create_vector_store()
    vectorstore = FAISS.load_local(vectorstore_path, embeddings, allow_dangerous_deserialization=True)
    return vectorstore