from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()


def get_secret(name: str, default: str = "") -> str:
    """Read a setting from the environment (.env) or Streamlit secrets.

    Local runs use `.env`; Streamlit Community Cloud exposes values set in the
    dashboard through `st.secrets`. Environment variables take precedence.
    """
    value = os.getenv(name)
    if value:
        return value
    try:
        import streamlit as st

        return str(st.secrets[name])
    except Exception:
        return default


GROQ_API_KEY = get_secret("GROQ_API_KEY")
GEMINI_API_KEY = get_secret("GEMINI_API_KEY")
TAVILY_API_KEY = get_secret("TAVILY_API_KEY")

PLANNER_MODEL = get_secret("PLANNER_MODEL", "openai/gpt-oss-120b")
ANALYSIS_MODEL = get_secret("ANALYSIS_MODEL", "openai/gpt-oss-120b")
CRITIC_MODEL = get_secret("CRITIC_MODEL", "gemini-3.8-flash")
SYNTHESIS_MODEL = get_secret("SYNTHESIS_MODEL", "gemini-3.8-flash")

MAX_QUERY_LEN = int(get_secret("MAX_QUERY_LEN", "4000"))
MIN_QUERY_LEN = int(get_secret("MIN_QUERY_LEN", "3"))


def require_keys() -> list[str]:
    keys = {
        "GROQ_API_KEY": GROQ_API_KEY,
        "GEMINI_API_KEY": GEMINI_API_KEY,
        "TAVILY_API_KEY": TAVILY_API_KEY,
    }
    return [name for name, value in keys.items() if not value]
