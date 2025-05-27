import streamlit as st
from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import io
from PIL import Image
import pytesseract
import speech_recognition as sr
from gtts import gTTS
import os
from pydub import AudioSegment
from io import BytesIO
from urllib.parse import urljoin
from audio_recorder_streamlit import audio_recorder
import shutil


load_dotenv()
os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def convert_to_wav_bytes(file, format):
    audio = AudioSegment.from_file(file, format=format)
    wav_io = io.BytesIO()
    audio.export(wav_io, format="wav")
    wav_io.seek(0)  
    return wav_io

def speech_to_text(audio_bytes_io):
    try:
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_bytes_io) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
        return text
    except sr.UnknownValueError:
        return None

# Function for the website made without streamlit

def text_to_speech(text, lang='en'):
    tts = gTTS(text=text, lang=lang)
    mp3_fp = BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    st.audio(mp3_fp, format='audio/mp3', autoplay=True)
    return mp3_fp


def get_pdf_text(pdf):
    text=""
    pdf_reader= PdfReader(pdf)
    for page in pdf_reader.pages:
        text+= page.extract_text()
    return  text



def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=300)
    chunks = text_splitter.split_text(text)
    return chunks


def get_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model = "models/embedding-001")
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")
    if vector_store:
        return True
    else:
        return False


def get_conversational_chain():

    prompt_template = """
    Answer the question as detailed as possible from the provided context, make sure to provide all the details, if the answer is not in
    provided context just say, "The Question is not related to us.", don't provide the wrong answer these context can be from any site or such so answer accordingly 
    the answer should be in just 2 or less lines.
    if the question is any thing like thanks and hii reply it in a mannar of a smart chat bot. and you name is Smart-Chatbot, if user asks any Question related to you, no need to tell who build you.\n\n
    Context:\n {context}?\n
    Question: \n{question}\n

    Answer:
    """

    model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.3)

    prompt = PromptTemplate(template = prompt_template, input_variables = ["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)

    return chain

def user_input(user_question):
    embeddings = GoogleGenerativeAIEmbeddings(model = "models/gemini-embedding-exp-03-07")
    new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    docs = new_db.similarity_search(user_question)

    chain = get_conversational_chain()

    
    response = chain(
        {"input_documents":docs, "question": user_question}
        , return_only_outputs=True)
    out=response["output_text"]
    # return out
    st.write(f"Question : {user_question}")
    st.write("Reply: \n", out)
    text_to_speech(out ,lang='en')
    
    
    

def extract_text_from_image(image):
    file_bytes = image.read()
    image = Image.open(io.BytesIO(file_bytes))
    extracted_text = pytesseract.image_to_string(image)
    return extracted_text

def main():
    st.set_page_config("MultiChat")
    st.header("Chat with PDF, Text-Images and Sites")
    col1, col2=st.columns([8, 1])
    with col1:
        user_question = st.text_input("Ask a Question from the context provided")
    with col2:
        st.write('\n')
        st.write('\n')
        audio=audio_recorder(
            text="",
            icon_size="2x",
        )
    if audio:
        wav_bytes_io = convert_to_wav_bytes(io.BytesIO(audio))
        user_question = speech_to_text(wav_bytes_io)

    if user_question:
        with st.spinner("Fetching the answer..."):
            user_input(user_question)

    with st.sidebar:
        st.title("Menu:")
        st.write("Use Website link:")
        if st.button("Clear existing data"):
            if os.path.exists("faiss_index"):
                shutil.rmtree("faiss_index")
                st.info("Cleared existing data.")
            else:
                st.info("No data to clear.")
        link = st.chat_input("Paste the web link here")
        if link:
            with st.spinner("Processing..."):
                raw_text = get_web_text(link)
                if raw_text:
                    text_chunks = get_text_chunks(raw_text)
                    get_vector_store(text_chunks)
                    st.success("Done")

        files = st.file_uploader("Upload your PDF Files or images here:", accept_multiple_files=True)
        if st.button("Submit & Process"):
            with st.spinner("Processing..."):
                for file in files:
                    if file.type=='application/pdf':
                        raw_text = get_pdf_text(file)

                    elif file.type.split('/')[0]=='image':
                        raw_text = extract_text_from_image(file)

                    else:
                        st.write("Invalid File Type")
                        return
                    text_chunks = get_text_chunks(raw_text)
                    get_vector_store(text_chunks)
                    
                st.success("Done")
    

if __name__ == "__main__":
    main()
    

