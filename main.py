from __future__ import annotations

import sys

from src.config import require_keys
from src.graph import build_graph


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


def render(result: dict) -> None:
    print("=" * 72)
    print((result.get("answer") or "").strip())
    print("=" * 72)

    plan = result.get("plan") or []
    if plan:
        print("\nPlan:")
        for index, step in enumerate(plan, 1):
            print(f"  {index}. {step}")

    references = result.get("references") or []
    if references:
        print("\nReferences:")
        for ref in references:
            print(f"  [{ref['id']}] {ref['title']} - {ref['url']}")

    citations = result.get("citations") or []
    if citations:
        ids = ", ".join(f"[{cite['id']}]" for cite in citations)
        print(f"\nCited: {ids}")

    notes = result.get("guardrail_notes") or []
    if notes:
        print("\nGuardrail notes:")
        for note in notes:
            print(f"  - {note}")


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    query = " ".join(sys.argv[1:]).strip()
    if not query:
        query = input("Enter your research question: ").strip()

    missing = require_keys()
    if missing:
        print("Missing API keys in .env: " + ", ".join(missing))
        print("Add them, then re-run.")
        return 1

    app = build_graph()
    result = app.invoke(initial_state(query))
    render(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
