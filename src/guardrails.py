from __future__ import annotations

import re
from dataclasses import dataclass, field

from . import config

CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
CITATION_RE = re.compile(r"\[(\d+)\]")

INJECTION_PATTERNS = [
    r"ignore (all |the |any )*(previous|prior|above|earlier) (instructions|prompts|messages|rules)",
    r"disregard (all |the |any )*(previous|prior|above|earlier)",
    r"forget (all |the |any )*(previous|prior|above|earlier)",
    r"reveal (your |the )*(system )?(prompt|instructions|message)",
    r"print (your |the )*(system )?(prompt|instructions|message)",
    r"(system|developer) (prompt|message|instructions)",
    r"you are now (a |an |the |no longer)",
    r"(enable|enter) (developer|debug|god) mode",
    r"jailbreak",
    r"do anything now",
    r"<\|(im_start|im_end|system|endoftext|assistant)\|>",
    r"\[\s*system\s*\]",
]


@dataclass
class InputGuardResult:
    allowed: bool
    reason: str
    sanitized: str
    notes: list[str] = field(default_factory=list)


@dataclass
class OutputGuardResult:
    text: str
    citations: list[dict]
    references: list[dict]
    notes: list[str]


def scrub_control_chars(text: str) -> str:
    return CONTROL_CHARS.sub("", text or "")


def check_input(query: str) -> InputGuardResult:
    notes: list[str] = []
    original = query or ""
    raw = scrub_control_chars(original)
    if raw != original:
        notes.append("stripped control characters from input")
    sanitized = raw.strip()

    if len(sanitized) < config.MIN_QUERY_LEN:
        return InputGuardResult(False, "query too short", sanitized, notes)
    if len(sanitized) > config.MAX_QUERY_LEN:
        reason = f"query too long ({len(sanitized)} > {config.MAX_QUERY_LEN} chars)"
        return InputGuardResult(False, reason, sanitized, notes)

    lowered = sanitized.lower()
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, lowered):
            note = f"matched injection pattern: {pattern}"
            return InputGuardResult(False, "possible prompt injection", sanitized, notes + [note])

    return InputGuardResult(True, "", sanitized, notes)


def finalize_output(answer: str, references: list[dict], extra_notes=None) -> OutputGuardResult:
    notes: list[str] = list(extra_notes or [])
    text = scrub_control_chars(answer).strip()

    valid_ids = {ref["id"] for ref in references}
    used_ids = sorted({int(match) for match in CITATION_RE.findall(text)})

    citations: list[dict] = []
    for cid in used_ids:
        if cid in valid_ids:
            ref = next(r for r in references if r["id"] == cid)
            citations.append(
                {
                    "id": cid,
                    "title": ref.get("title", ""),
                    "url": ref.get("url", ""),
                    "source": ref.get("source", ""),
                }
            )
        else:
            notes.append(f"citation [{cid}] has no matching reference")

    if references and not citations:
        notes.append("final answer contains no inline citations")

    references_out = [
        {
            "id": ref["id"],
            "title": ref.get("title", ""),
            "url": ref.get("url", ""),
            "source": ref.get("source", ""),
        }
        for ref in references
    ]
    return OutputGuardResult(text=text, citations=citations, references=references_out, notes=notes)
