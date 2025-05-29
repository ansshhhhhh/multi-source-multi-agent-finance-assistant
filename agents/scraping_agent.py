from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain_community.document_loaders import WebBaseLoader, PyPDFLoader
from langchain_community.document_loaders.csv_loader import CSVLoader
from dotenv import load_dotenv
import google.generativeai as genai
import os

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

@tool
def web_loader(url: str) -> str:
    """Provides the docs of the web of the url provided."""
    doc = WebBaseLoader(url).load()
    s = ''
    for i in doc:
        s += '\n' + i.page_content.strip()
    return s

@tool
def pdf_loader(file_path: str) -> str:
    """Provides the pdf docs of the file_path provided."""
    doc = PyPDFLoader(file_path).load()
    s = ''
    for i in doc:
        s += '\n' + i.page_content.strip()
    return s

@tool
def csv_loader(file_path: str) -> str:
    """Provides the csv docs of the file_path provided."""
    doc = CSVLoader(file_path).load()
    s = ''
    for i in doc:
        s += '\n' + i.page_content.strip()
    return s

def get_scraping_agent():
    return create_react_agent(
    model=ChatGoogleGenerativeAI(model="gemini-2.0-flash"),
    tools=[web_loader, pdf_loader, csv_loader],
    prompt=(
        "You are a scraping agent.\n\n"
        "INSTRUCTIONS:\n"
        "- Use the provided links and file paths to scratch data from the file.\n"
        "- Get the data from the web, pdf, csv\n"
        "- After you're done with your tasks, respond to the supervisor directly"
    ),
    name="scraping_agent",
)