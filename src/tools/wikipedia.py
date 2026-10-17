from __future__ import annotations

import requests

WIKI_API = "https://en.wikipedia.org/w/api.php"
REST_SUMMARY = "https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
HEADERS = {"User-Agent": "MultiAgentResearch/1.0 (educational; contact: local)"}


def _summary(title: str) -> dict | None:
    url = REST_SUMMARY.format(title=requests.utils.quote(title, safe=""))
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
    except requests.RequestException:
        return None
    if resp.status_code != 200:
        return None
    data = resp.json()
    extract = (data.get("extract") or "").strip()
    if not extract:
        return None
    page = (
        data.get("content_urls", {})
        .get("desktop", {})
        .get("page", f"https://en.wikipedia.org/wiki/{requests.utils.quote(title)}")
    )
    return {
        "source": "wikipedia",
        "title": data.get("title", title),
        "url": page,
        "content": extract,
    }


def search(query: str, limit: int = 2) -> list[dict]:
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json",
        "srlimit": max(1, limit),
    }
    try:
        resp = requests.get(WIKI_API, params=params, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except requests.RequestException:
        return []

    hits = resp.json().get("query", {}).get("search", [])
    results: list[dict] = []
    for hit in hits:
        summary = _summary(hit["title"])
        if summary:
            results.append(summary)
    return results
