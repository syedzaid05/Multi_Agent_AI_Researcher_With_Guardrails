from __future__ import annotations

from ..config import ANALYSIS_MODEL, SYNTHESIS_MODEL
from ..llm import deep_invoke
from ..utils import message_text, references_block

SYSTEM = """You are the Synthesis agent. Produce the final answer to the user's question.
Use the analysis and resolve every issue the critic raised.
Cite supporting sources inline with bracketed ids that match the provided references, e.g. [1][2].
Only cite ids that appear in the reference list. Never invent sources.
If uncertainty remains, add a final line beginning with "Limitations:".
"""


def synthesis_node(state):
    references = state.get("references") or []
    human = (
        f"Question:\n{state.get('safe_query', '')}\n\n"
        f"Analysis:\n{state.get('analysis', '')}\n\n"
        f"Critique:\n{state.get('critique', '')}\n\n"
        f"References:\n{references_block(references)}\n\n"
        "Write the final answer now."
    )
    response = deep_invoke(
        SYNTHESIS_MODEL,
        [("system", SYSTEM), ("human", human)],
        temperature=0.3,
        fallback_model=ANALYSIS_MODEL,
    )
    return {"answer": message_text(response)}
