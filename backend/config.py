import os
from pathlib import Path
from dotenv import load_dotenv

# Ensure .env is loaded from project root regardless of CWD
PROJECT_ROOT = Path(__file__).resolve().parent.parent
env_file = PROJECT_ROOT / ".env"
if env_file.exists():
    load_dotenv(dotenv_path=env_file)
else:
    load_dotenv()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "").strip()
GROQ_MODEL = os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b").strip()
RAG_TOP_K = int(os.environ.get("RAG_TOP_K", 5))
RAG_MAX_CHUNK_CHARS = int(os.environ.get("RAG_MAX_CHUNK_CHARS", 3000))
LLM_MAX_TOKENS = int(os.environ.get("LLM_MAX_TOKENS", 2500))
LLM_TEMPERATURE = float(os.environ.get("LLM_TEMPERATURE", 0.1))

# Web Search
WEB_SEARCH_MAX_RESULTS = int(os.environ.get("WEB_SEARCH_MAX_RESULTS", 5))
WEB_SEARCH_TIMEOUT = int(os.environ.get("WEB_SEARCH_TIMEOUT", 10))
WEB_SEARCH_RECENCY_DAYS = int(os.environ.get("WEB_SEARCH_RECENCY_DAYS", 3650))

