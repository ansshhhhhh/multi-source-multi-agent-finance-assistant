import sys, os
top_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(top_dir)

from langgraph_supervisor import create_supervisor
from agents.retriever_agent import get_retriever_agent
from agents.scraping_agent import get_scraping_agent
from agents.api_agent import get_api_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import google.generativeai as genai


load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def get_supervisor():
    retriever_agent = get_retriever_agent()
    scraping_agent = get_scraping_agent()
    api_agent = get_api_agent()
    return create_supervisor(
        model = ChatGoogleGenerativeAI(model="gemini-2.0-flash"),
        agents=[scraping_agent, retriever_agent, api_agent],
        prompt=(
            "You are a supervisor managing three agents:\n"
            "- a scraping agent. Assign scraping-related tasks to this agent\n"
            "- a retriever agent. Provide the link or path to  fetch any documment and it will help you with it's content\n"
            "- a api agent. Assign finance-related tasks to this agent\n"
            "Assign work to one agent at a time, do not call agents in parallel.\n"
            "Do not do any work yourself."
        ),
        add_handoff_back_messages=True,
        output_mode="full_history",
    ).compile()

# supervisor = get_supervisor()

# result = supervisor.invoke({"messages": ["Latest news about Apple?"]})

# for i in result["messages"]:
#     i.pretty_print()