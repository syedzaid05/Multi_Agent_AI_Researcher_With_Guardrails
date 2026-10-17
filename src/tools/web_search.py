from __future__ import annotations

from .. import config


def _tavily(query: str, max_results: int) -> list[dict]:
    if not config.TAVILY_API_KEY:
        return []
    try:
        from tavily import TavilyClient

        client = TavilyClient(api_key=config.TAVILY_API_KEY)
        response = client.search(query=query, max_results=max_results, search_depth="advanced")
    except Exception:
        return []

    results: list[dict] = []
    for item in response.get("results", []):
        results.append(
            {
                "source": "tavily",
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "content": item.get("content", ""),
            }
        )
    return results


def _duckduckgo(query: str, max_results: int) -> list[dict]:
    try:
        try:
            from ddgs import DDGS
        except ImportError:
            from duckduckgo_search import DDGS
    except ImportError:
        return []

    results: list[dict] = []
    try:
        with DDGS() as ddgs:
            for item in ddgs.text(query, max_results=max_results):
                results.append(
                    {
                        "source": "duckduckgo",
                        "title": item.get("title", ""),
                        "url": item.get("href", ""),
                        "content": item.get("body", ""),
                    }
                )
    except Exception:
        return []
    return results


def search(query: str, max_results: int = 3) -> list[dict]:
    results = _tavily(query, max_results)
    if not results:
        results = _duckduckgo(query, max_results)
    return results
