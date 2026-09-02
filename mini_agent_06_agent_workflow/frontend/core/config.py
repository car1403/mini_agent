import os

from dotenv import load_dotenv


load_dotenv()

PYTHON_AGENT_API_URL = os.getenv(
    "PYTHON_AGENT_API_URL",
    "http://127.0.0.1:8000",
).rstrip("/")
LANGGRAPH_AGENT_API_URL = os.getenv(
    "LANGGRAPH_AGENT_API_URL",
    "http://127.0.0.1:8001",
).rstrip("/")

API_URLS = {
    "Python Agent": PYTHON_AGENT_API_URL,
    "LangGraph Agent": LANGGRAPH_AGENT_API_URL,
}
