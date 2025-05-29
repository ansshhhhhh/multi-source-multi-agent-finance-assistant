# AI Tool Usage Documentation

## Overview
This document details the AI tools, models, and configurations used in the Multi-Source Multi-Agent Finance Assistant project.

## Model Configuration

### Base Model
- **Provider**: Google AI (Gemini)
- **Model Version**: gemini-2.0-flash
- **Configuration**: 
  - API Key: Required (via GOOGLE_API_KEY environment variable)
  - Model Type: ChatGoogleGenerativeAI

### Embeddings
- **Model**: models/gemini-embedding-exp-03-07
- **Provider**: Google AI
- **Usage**: Document embedding for vector store

## Agent Configurations

### 1. Supervisor Agent
```python
Model: ChatGoogleGenerativeAI(model="gemini-2.0-flash")
Prompt Template:
"""
You are a supervisor managing three agents:
- a scraping_agent. Provide the link or path of any documment to it and it will help you with it's content
- a retriever_agent. retrive the data from vector store and if retrieval confidence < threshold, prompt user clarification.
Assign work to one agent at a time, do not call agents in parallel.
Analyse the result of each agent and after that provide what user want if you didn't get answer from one agent use another.
"""
```

### 2. Retriever Agent
```python
Model: ChatGoogleGenerativeAI(model="gemini-2.0-flash")
Tools: 
- create_retriever_tool(vectorstore.as_retriever())
Prompt Template:
"""
You are a retriever agent.

INSTRUCTIONS:
- Get the data from the vector store.
- if retrieval confidence < threshold, prompt user clarification.
- After you're done with your tasks, respond to the supervisor directly
"""
```

### 3. API Agent
```python
Model: ChatGoogleGenerativeAI(model="gemini-2.0-flash")
Tools:
- YahooFinanceNewsTool()
Prompt Template:
"""
You are a Financial agent.

INSTRUCTIONS:
- You polls real-time & historical market data.
- You use the YahooFinanceNewsTool to get the latest finanical news update.
- After you're done with your tasks, respond to the supervisor directly
- Respond ONLY with the results of your work, do NOT include ANY other text.
- You can use the tools provided to you to get the data.
"""
```

### 4. Scraping Agent
```python
Model: ChatGoogleGenerativeAI(model="gemini-2.0-flash")
Tools:
- web_loader: WebBaseLoader for URL content extraction
- pdf_loader: PyPDFLoader for PDF content extraction
- csv_loader: CSVLoader for CSV file processing
Prompt Template:
"""
You are a scraping agent.

INSTRUCTIONS:
- Use the provided links and file paths to scratch data from the file.
- Get the data from the web, pdf, csv
- After you're done with your tasks, respond to the supervisor directly
"""
```

## Vector Store Configuration

### FAISS Vector Store
- **Type**: FAISS (Facebook AI Similarity Search)
- **Embedding Model**: GoogleGenerativeAIEmbeddings
- **Chunk Size**: 1024
- **Chunk Overlap**: 64
- **Storage Path**: data_ingestion/faiss_index

## Voice Processing

### Speech-to-Text
- **Tool**: SpeechRecognition
- **Input Format**: WAV
- **API Endpoint**: /agents/voice-agent/stt

### Text-to-Speech
- **Tool**: gTTS (Google Text-to-Speech)
- **Output Format**: MP3
- **Supported Languages**: Multiple (default: 'en')
- **API Endpoint**: /agents/voice-agent/tts

## Code Generation Steps

1. **Agent Initialization**
   - Load environment variables
   - Configure Google AI API
   - Initialize model instances
   - Set up agent tools and prompts

2. **Vector Store Setup**
   - Initialize embeddings
   - Create/load FAISS index
   - Configure text splitting parameters
   - Set up document processing pipeline

3. **API Integration**
   - Set up FastAPI endpoints
   - Configure request/response handling
   - Implement streaming responses for audio
   - Handle file uploads and processing

4. **Frontend Integration**
   - Implement Streamlit interface
   - Set up audio recording and playback
   - Configure real-time communication with backend
   - Handle user input processing

## Model Parameters

### Text Processing
- **Chunk Size**: 1024 tokens
- **Chunk Overlap**: 64 tokens
- **Text Splitter**: RecursiveCharacterTextSplitter

### Vector Store
- **Similarity Search**: FAISS
- **Index Type**: L2 distance
- **Allow Dangerous Deserialization**: True (for local storage)

### Voice Processing
- **Audio Format**: WAV (input), MP3 (output)
- **Sample Rate**: Default system settings
- **Language Support**: Multiple languages (configurable)

