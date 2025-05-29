import streamlit as st
import io
import requests
from audio_recorder_streamlit import audio_recorder
import base64
import re

# Replace with your FastAPI backend URL
API_BASE_URL = "http://localhost:8000/"


def speech_to_text(wav_bytes_io):
    response = requests.post(
        f"{API_BASE_URL}/agents/voice-agent/stt",
        files={"file": ("audio.wav", wav_bytes_io)},
        data={"format": "wav"}
    )
    if response.status_code == 200:
        return response.json().get("text", "")

def text_to_speech(text, lang="en"):
    if text == "" or not text:
        return None
    
    clean = re.sub(r"[^\w\s.,?]", "", text)
    response = requests.post(
        f"{API_BASE_URL}/agents/voice-agent/tts",
        data={"text": clean, "lang": lang}
    )
    if response.status_code == 200:
        return response.content
    return None

def say_text(say: str):
    tts_audio = text_to_speech(say)
    if tts_audio:
        play_audio_hidden(tts_audio)


def play_audio_hidden(audio_data):
    b64 = base64.b64encode(audio_data).decode()
    md = f"""
    <audio autoplay style="display:none">
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    """
    st.markdown(md, unsafe_allow_html=True)

def user_input(query):
    response = requests.post(f"{API_BASE_URL}/supervisor", params={"Query": query})
    if response.status_code == 200:
        
        ado = None  # To collect all audio segments
        
        for i in response.json()['messages']:
            print(i)
            print("\n")
            if i['content'] != "" and i['type'] != 'human':
                with st.container():
                    st.markdown(f"**{i['name']}**")
                    st.markdown(i['content'])

                # Text-to-speech
                if i['name'] == 'supervisor':
                    tts_audio = text_to_speech(i['content'])
                    if not ado and tts_audio:
                        ado = tts_audio
                    elif ado and tts_audio:
                        ado += tts_audio

        if ado:
            play_audio_hidden(ado)



def upload_pdf_to_backend(file):
    response = requests.post(
        f"{API_BASE_URL}/data_ingestion/pdf",
        files={"file": (file.name, file, file.type)}
    )
    return response.json()

def upload_url_to_backend(url):
    response = requests.post(
        f"{API_BASE_URL}/data_ingestion/urls",
        params = {"urls": [url]}
    )
    return response.json()

def delete_vector_store():
    response = requests.get(f"{API_BASE_URL}/data_ingestion/delete_vectordb")
    return response.json()



def main():
    # Setup the page
    st.set_page_config("Finance Assistant", initial_sidebar_state='collapsed')
    st.header("Multi-Source Multi-Agent Finance Assistant")

    # Initialize session state
    if 'submitted' not in st.session_state:
        st.session_state['submitted'] = False
    if 'user_question' not in st.session_state:
        st.session_state['user_question'] = ""
    if 'text_input' not in st.session_state:
        st.session_state['text_input'] = ""

    # Layout: Input via text and audio
    col1, col2 = st.columns([8, 1])

    with col1:
        st.session_state.text_input = st.text_input(
            "Ask a Question from the context provided", 
            value=st.session_state.text_input, 
            key="text_input_field"
        )

        if st.session_state.text_input:
            st.session_state.user_question = st.session_state.text_input
            st.session_state.submitted = True
            st.session_state.text_input = ""  # Clear input bar

    with col2:
        st.write("\n" * 2)
        audio = audio_recorder(text="", icon_size="2x")
        if audio:
            wav_bytes_io = io.BytesIO(audio)
            st.session_state.user_question = speech_to_text(wav_bytes_io)
            st.session_state.submitted = True

    # If question is ready, process it
    if st.session_state.submitted and st.session_state.user_question:
        st.write(st.session_state.user_question)
        user_input(st.session_state.user_question)
        # Reset after processing
        st.session_state.submitted = False
        st.session_state.user_question = ""

    with st.sidebar:
        st.title("Menu:")
        if st.button("Clear existing data"):
            result = delete_vector_store()
            st.info("Cleared existing data." if result['success'] else "Error clearing data.")
            say_text("Cleared existing data successfully.")

        link = st.chat_input("Paste the web link here")
        if link:
            with st.spinner("Processing..."):
                result = upload_url_to_backend(link)
                st.success("Done" if result['success'] else "Error")
            say_text("Added the link to the vector store.")

        files = st.file_uploader("Upload your PDF Files or images here:", accept_multiple_files=True)
        if st.button("Submit & Process"):
            with st.spinner("Processing..."):
                for file in files:
                    if file.type == 'application/pdf':
                        result = upload_pdf_to_backend(file)
                        st.success("PDF uploaded successfully" if result['success'] else "Failed to upload PDF")
                    else:
                        st.write("Invalid File Type")
            say_text("Your Files uploaded successfully.")

if __name__ == "__main__":
    main()