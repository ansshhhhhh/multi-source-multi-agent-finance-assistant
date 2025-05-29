from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import StreamingResponse, JSONResponse
from orchestrator.supervisor import get_supervisor
from agents.api_agent import get_api_agent
from agents.retriever_agent import get_retriever_agent
from agents.scraping_agent import get_scraping_agent
from agents.voice_agent import *
from data_ingestion.get_data import *


app = FastAPI()

@app.post('/supervisor')
def supervisor(Query: str):
    supervisor = get_supervisor()
    result = supervisor.invoke({'messages':[Query]})
    for i in result['messages']:
        i.pretty_print()
    return result

@app.post('/agents/api_agent')
def api_agent(Query: str):
    api_agent = get_api_agent()
    result = api_agent.invoke({'messages':[Query]})
    return result

@app.post('/agents/retriever_agent')
def retriever_agent(Query: str):
    retriever_agent = get_retriever_agent()
    result = retriever_agent.invoke({'messages':[Query]})
    return result

@app.post('/agents/scraping_agent')
def scraping_agent(Query: str):
    scraping_agent = get_scraping_agent()
    result = scraping_agent.invoke({'messages':[Query]})
    return result

@app.post("/agents/voice-agent/stt")
def speech_to_text_api(file: UploadFile = File(...), format: str = Form(...)):
    content = file.read()
    wav_bytes = convert_to_wav_bytes(BytesIO(content), format)
    text = speech_to_text(wav_bytes)
    if text is None:
        return JSONResponse(status_code=400, content={"error": "Could not recognize speech"})
    return {"text": text}

@app.post("/agents/voice-agent/tts")
def text_to_speech_api(text: str = Form(...), lang: str = Form(default='en')):
    mp3_bytes = text_to_speech(text, lang)
    return StreamingResponse(mp3_bytes, media_type="audio/mpeg")

@app.post("/data_ingestion/pdf")
def upload_pdf(file: UploadFile):
    if file.filename.split('.')[-1]=='pdf':
        raw_text = get_pdf_text(file.file)
    else:
        return {'error':'Unsupported file type'}
    status = add_to_vectore_store(raw_text)
    return {'success':status}
    
@app.post("/data_ingestion/urls")
def add_web_docs(urls: list[str]):
    add_web_docs(urls)
    return {'success':True}


@app.get("/data_ingestion/delete_vectordb")
def delete_vectordb():
    delete_vector_store()
    return {'success' : True}

@app.get('/')
async def home():
    return {
        "message" : "Welcome to the Multi-Source Multi-Agent Finance Assistant"
        } 