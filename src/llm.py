from __future__ import annotations

import sys
from functools import lru_cache

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

from . import config

_warned = False


@lru_cache(maxsize=16)
def groq_llm(model: str, temperature: float = 0.2):
    return ChatGroq(model=model, temperature=temperature, api_key=config.GROQ_API_KEY)


@lru_cache(maxsize=16)
def gemini_llm(model: str, temperature: float = 0.2):
    return ChatGoogleGenerativeAI(
        model=model,
        temperature=temperature,
        google_api_key=config.GEMINI_API_KEY,
    )


def deep_invoke(model: str, messages, temperature: float = 0.2, fallback_model: str | None = None):
    global _warned
    if config.GEMINI_API_KEY:
        try:
            return gemini_llm(model, temperature).invoke(messages)
        except Exception as exc:
            if not _warned:
                print(f"[warn] Gemini unavailable ({exc}); using Groq fallback.", file=sys.stderr)
                _warned = True
    return groq_llm(fallback_model or config.ANALYSIS_MODEL, temperature).invoke(messages)
