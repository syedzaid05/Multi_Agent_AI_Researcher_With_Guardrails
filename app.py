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

st.title("Multi-Agent Research Assistant")
st.caption(
    "Planner → Wikipedia + Web search → Analysis → Critic → Synthesis, "
    "with input/output guardrails and citations."
)

missing = require_keys()
if missing:
    st.error("Missing API keys. Set them in `.env` (local) or in Streamlit secrets (Cloud): " + ", ".join(missing))
    st.stop()

with st.sidebar:
    st.subheader("Models")
    st.write(f"Planner: `{PLANNER_MODEL}`")
    st.write(f"Analysis: `{ANALYSIS_MODEL}`")
    st.write(f"Critic: `{CRITIC_MODEL}`")
    st.write(f"Synthesis: `{SYNTHESIS_MODEL}`")
    st.divider()
    st.write("Set overrides in `.env` (local) or Streamlit secrets (Cloud).")

query = st.text_area(
    "Research question",
    height=100,
    placeholder="e.g. What are the security risks of prompt injection in LLM agents?",
)
run = st.button("Run", type="primary", disabled=not query.strip())

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
