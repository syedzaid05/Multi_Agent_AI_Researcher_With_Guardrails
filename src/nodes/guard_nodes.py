from __future__ import annotations

from ..guardrails import check_input, finalize_output


def input_guard_node(state):
    result = check_input(state.get("query", ""))
    update = {"safe_query": result.sanitized, "guardrail_notes": result.notes}
    if not result.allowed:
        update["blocked"] = True
        update["block_reason"] = result.reason
        update["answer"] = f"Request blocked by input guardrails: {result.reason}"
        update["guardrail_notes"] = result.notes + [f"blocked: {result.reason}"]
    return update


def route_after_input(state):
    return "blocked" if state.get("blocked") else "continue"


def output_guard_node(state):
    references = state.get("references") or []
    result = finalize_output(state.get("answer", ""), references)
    return {
        "answer": result.text,
        "citations": result.citations,
        "references": result.references,
        "guardrail_notes": result.notes,
    }
