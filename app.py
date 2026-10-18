from __future__ import annotations

import streamlit as st

from src.config import (
    ANALYSIS_MODEL,
    CRITIC_MODEL,
    PLANNER_MODEL,
    SYNTHESIS_MODEL,
    require_keys,
)
from src.graph import build_graph

NODE_LABELS = {
    "input_guardrails": "Input guardrails",
    "planner": "Planner",
    "wikipedia": "Wikipedia agent",
    "web_search": "Web search agent",
    "analysis": "Analysis agent",
    "critic": "Critic agent",
    "synthesis": "Synthesis agent",
    "output_guardrails": "Output guardrails",
}


def initial_state(query: str) -> dict:
    return {
        "query": query,
        "wikipedia": [],
        "web": [],
        "guardrail_notes": [],
        "plan": [],
        "research_tasks": [],
        "references": [],
    }


st.set_page_config(page_title="Multi-Agent Research", page_icon="🔎", layout="wide")

st.markdown(
    """
    <style>
    :root {
        --bg: #0b1020;
        --panel: #131a30;
        --accent: #7c5cff;
        --accent2: #00d4ff;
        --text: #e6e9f5;
        --muted: #9aa3c0;
    }
    .stApp {
        background:
            radial-gradient(1000px 600px at 90% -10%, rgba(124, 92, 255, 0.22), transparent 60%),
            radial-gradient(900px 500px at -10% 110%, rgba(0, 212, 255, 0.14), transparent 60%),
            var(--bg);
        color: var(--text);
    }
    #MainMenu, footer { visibility: hidden; }

    h1, h2, h3, .stApp .markdown-text-container { color: var(--text); }
    h1 {
        background: linear-gradient(90deg, #fff 0%, #b9a4ff 55%, #79e8ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    .stApp .stCaption, .stApp [data-testid="stMarkdownContainer"] p { color: var(--text); }

    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #131a30 0%, #0d1330 100%);
        border-right: 1px solid rgba(124, 92, 255, 0.25);
    }
    div[data-testid="stSidebar"] * { color: var(--text) !important; }

    .stTextArea textarea, .stTextInput input {
        background-color: var(--panel) !important;
        color: var(--text) !important;
        border: 1px solid rgba(124, 92, 255, 0.35) !important;
        border-radius: 12px !important;
    }
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 2px rgba(124, 92, 255, 0.25) !important;
    }

    .stButton > button {
        background: linear-gradient(90deg, var(--accent) 0%, #5a8bff 60%, var(--accent2) 130%);
        color: #fff;
        border: none;
        border-radius: 12px;
        font-weight: 600;
        padding: 0.55rem 1.5rem;
        transition: filter 0.15s ease, transform 0.05s ease;
    }
    .stButton > button:hover { filter: brightness(1.12); }
    .stButton > button:active { transform: translateY(1px); }
    .stButton > button:disabled {
        background: rgba(124, 92, 255, 0.25);
        color: rgba(255,255,255,0.5);
    }

    div[data-testid="stStatusWidget"],
    [data-testid="stStatus"] {
        background-color: var(--panel) !important;
        border: 1px solid rgba(124, 92, 255, 0.25);
        border-radius: 12px;
    }
    div[data-testid="stExpander"] {
        background-color: var(--panel);
        border: 1px solid rgba(124, 92, 255, 0.2);
        border-radius: 12px;
    }
    .stDivider > div { border-color: rgba(124, 92, 255, 0.3) !important; }

    .stAlert { border-radius: 12px; border: none; }

    .badge-pipeline {
        display: inline-flex; gap: 6px; flex-wrap: wrap; margin: 4px 0 14px 0;
    }
    .badge-pipeline span {
        background: linear-gradient(90deg, rgba(124,92,255,0.25), rgba(0,212,255,0.18));
        border: 1px solid rgba(124,92,255,0.4);
        color: #d8d3ff;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 0.8rem;
    }
    .hero-card {
        background: var(--panel);
        border: 1px solid rgba(124,92,255,0.25);
        border-radius: 16px;
        padding: 18px 22px;
        margin-bottom: 18px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Multi-Agent Research Assistant")
st.caption(
    "Planner → Wikipedia + Web search → Analysis → Critic → Synthesis, "
    "with input/output guardrails and citations."
)
st.markdown(
    '<div class="badge-pipeline">'
    "<span>🧭 Planner</span><span>📚 Wikipedia</span><span>🌐 Web search</span>"
    "<span>🔬 Analysis</span><span>🧐 Critic</span><span>✍️ Synthesis</span>"
    "<span>🛡️ Guardrails</span></div>",
    unsafe_allow_html=True,
)

missing = require_keys()
if missing:
    st.error("Missing API keys. Set them in `.env` (local) or in Streamlit secrets (Cloud): " + ", ".join(missing))
    st.stop()

with st.sidebar:
    st.subheader("🤖 Models")
    st.markdown(
        f'<div class="hero-card">'
        f"<b style='color:#b9a4ff'>Planner</b><br><code>{PLANNER_MODEL}</code><br>"
        f"<b style='color:#b9a4ff'>Analysis</b><br><code>{ANALYSIS_MODEL}</code><br>"
        f"<b style='color:#b9a4ff'>Critic</b><br><code>{CRITIC_MODEL}</code><br>"
        f"<b style='color:#b9a4ff'>Synthesis</b><br><code>{SYNTHESIS_MODEL}</code>"
        f"</div>",
        unsafe_allow_html=True,
    )
    st.info("Set overrides in `.env` (local) or Streamlit secrets (Cloud).")

query = st.text_area(
    "Research question",
    height=100,
    placeholder="e.g. What are the security risks of prompt injection in LLM agents?",
)
run = st.button("🚀 Run research", type="primary", disabled=not query.strip())

if run:
    app = build_graph()
    state = initial_state(query.strip())

    with st.status("Running agent pipeline...", expanded=True) as status:
        try:
            for chunk in app.stream(state, stream_mode="updates"):
                for node, update in chunk.items():
                    st.write(f"✓ {NODE_LABELS.get(node, node)}")
                    if isinstance(update, dict):
                        state.update(update)
            status.update(label="Complete", state="complete", expanded=False)
        except Exception as exc:
            status.update(label="Failed", state="error")
            st.exception(exc)
            st.stop()

    st.divider()
    st.subheader("Answer")
    st.markdown(state.get("answer") or "_(no answer produced)_")

    plan = state.get("plan") or []
    if plan:
        st.subheader("Plan")
        for index, step in enumerate(plan, 1):
            st.markdown(f"{index}. {step}")

    references = state.get("references") or []
    citations = state.get("citations") or []
    if references:
        st.subheader("References")
        for ref in references:
            st.markdown(f"**[{ref['id']}]** [{ref['title']}]({ref['url']}) — _{ref['source']}_")
    if citations:
        ids = ", ".join(f"[{cite['id']}]" for cite in citations)
        st.caption(f"Cited: {ids}")

    notes = state.get("guardrail_notes") or []
    if notes:
        st.subheader("Guardrail notes")
        for note in notes:
            st.warning(note)
