from __future__ import annotations

import json
import re


def message_text(msg) -> str:
    content = getattr(msg, "content", msg)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for part in content:
            if isinstance(part, str):
                parts.append(part)
            elif isinstance(part, dict):
                text = part.get("text") or part.get("text_delta")
                if text:
                    parts.append(text)
        return "\n".join(parts)
    return str(content)


def parse_json(text) -> dict:
    raw = text if isinstance(text, str) else message_text(text)
    if not raw:
        return {}
    fenced = re.search(r"```(?:json)?\s*(.*?)```", raw, re.S)
    if fenced:
        raw = fenced.group(1)
    start, end = raw.find("{"), raw.rfind("}")
    if start != -1 and end != -1 and end > start:
        raw = raw[start:end + 1]
    try:
        data = json.loads(raw)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def number_sources(sources) -> list[dict]:
    refs: list[dict] = []
    seen: set[str] = set()
    for source in sources or []:
        url = (source.get("url") or "").strip()
        if not url or url in seen:
            continue
        seen.add(url)
        refs.append(
            {
                "id": len(refs) + 1,
                "title": source.get("title", ""),
                "url": url,
                "source": source.get("source", ""),
                "content": source.get("content", ""),
            }
        )
    return refs


def fence_untrusted(refs) -> str:
    if not refs:
        return "<untrusted-data>\n(no sources retrieved)\n</untrusted-data>"
    blocks = [
        f"[{ref['id']}] {ref['title']} <{ref['url']}>\n{ref.get('content', '')}"
        for ref in refs
    ]
    return "<untrusted-data>\n" + "\n\n".join(blocks) + "\n</untrusted-data>"


def references_block(refs) -> str:
    if not refs:
        return "(none)"
    return "\n".join(f"[{ref['id']}] {ref['title']} - {ref['url']}" for ref in refs)
