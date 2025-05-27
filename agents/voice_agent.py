import speech_recognition as sr
from gtts import gTTS
from io import BytesIO
from pydub import AudioSegment


def convert_to_wav_bytes(file, format):
    audio = AudioSegment.from_file(file, format=format)
    wav_io = BytesIO()
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

def text_to_speech(text, lang='en'):
    tts = gTTS(text=text, lang=lang)
    mp3_fp = BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    return mp3_fp