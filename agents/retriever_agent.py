from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools.retriever import create_retriever_tool
from data_ingestion.get_data import get_vector_store
from dotenv import load_dotenv
import google.generativeai as genai
import os

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def get_retriever_agent():
    vectorstore = get_vector_store()
    return create_react_agent(
    model=ChatGoogleGenerativeAI(model="gemini-2.0-flash"),
    tools=[create_retriever_tool(vectorstore.as_retriever(), "financial_data_retriever", "Search and return information about the company data or the information you are asked for",)],
    prompt=(
        "You are a retriever agent.\n\n"
        "INSTRUCTIONS:\n"
        "- Get the data from the vector store.\n"
        "- if retrieval confidence < threshold, prompt user clarification.\n"
        "- After you're done with your tasks, respond to the supervisor directly\n"
    ),
    name="retriever_agent",
)

# retriever_agent = get_retriever_agent()

# result = retriever_agent.invoke({"messages": ["Latest news about Apple?"]})

# for i in result["messages"]:
#     i.pretty_print()