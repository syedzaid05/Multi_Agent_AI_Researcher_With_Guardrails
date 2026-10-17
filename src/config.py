from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

PLANNER_MODEL = os.getenv("PLANNER_MODEL", "openai/gpt-oss-120b")
ANALYSIS_MODEL = os.getenv("ANALYSIS_MODEL", "openai/gpt-oss-120b")
CRITIC_MODEL = os.getenv("CRITIC_MODEL", "gemini-3.8-flash")
SYNTHESIS_MODEL = os.getenv("SYNTHESIS_MODEL", "gemini-3.8-flash")

MAX_QUERY_LEN = int(os.getenv("MAX_QUERY_LEN", "4000"))
MIN_QUERY_LEN = int(os.getenv("MIN_QUERY_LEN", "3"))


def require_keys() -> list[str]:
    keys = {
        "GROQ_API_KEY": GROQ_API_KEY,
        "GEMINI_API_KEY": GEMINI_API_KEY,
        "TAVILY_API_KEY": TAVILY_API_KEY,
    }
    return [name for name, value in keys.items() if not value]
