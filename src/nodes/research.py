from __future__ import annotations

from ..tools import web_search as web_tool
from ..tools import wikipedia as wiki_tool

MAX_TASKS = 4


def _tasks(state) -> list[str]:
    tasks = state.get("research_tasks") or [state.get("safe_query", "")]
    return [task for task in tasks if task][:MAX_TASKS]


def wikipedia_node(state):
    items: list[dict] = []
    for task in _tasks(state):
        items.extend(wiki_tool.search(task, limit=2))
    return {"wikipedia": items}


def web_search_node(state):
    items: list[dict] = []
    for task in _tasks(state):
        items.extend(web_tool.search(task, max_results=3))
    return {"web": items}
