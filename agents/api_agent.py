from langchain_community.tools.yahoo_finance_news import YahooFinanceNewsTool
from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_api_agent():
    return create_react_agent(
        model=ChatGoogleGenerativeAI(model="gemini-2.0-flash"),
        tools=[YahooFinanceNewsTool()],
        prompt=(
            "You are a Financial agent.\n\n"
            "INSTRUCTIONS:\n"
            "- You polls real-time & historical market data.\n"
            "- You use the YahooFinanceNewsTool to get the latest finanical news update.\n"
            "- After you're done with your tasks, respond to the supervisor directly\n"
            "- Respond ONLY with the results of your work, do NOT include ANY other text.\n"
            "- You can use the tools provided to you to get the data."
        ),
        name="Financial_agent",
    )

# api_agent = get_api_agent()

# result = api_agent.invoke({"messages": ["Latest news about Apple?"]})

# for i in result["messages"]:
#     i.pretty_print()