from __future__ import annotations

from operator import add
from typing import Annotated, TypedDict


class GraphState(TypedDict, total=False):
    query: str
    safe_query: str
    blocked: bool
    block_reason: str
    plan: list[str]
    research_tasks: list[str]
    wikipedia: Annotated[list[dict], add]
    web: Annotated[list[dict], add]
    analysis: str
    critique: str
    answer: str
    references: list[dict]
    citations: list[dict]
    guardrail_notes: Annotated[list[str], add]
