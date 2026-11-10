"""Per-document insight extraction (the "map" step), cached to disk.

Each document is read once by the cheaper/faster model, which returns structured
JSON: a short summary plus risks, opportunities, actions, deadlines and stakeholders,
each with a page reference. Results are cached, so this cost is paid once per
document; the user-facing tools then work from these small structured records
instead of re-reading ~84,000 words for every request.

Large documents are split into sections of ~12,000 words, which keeps each request
below the per-minute token limits of a new API account.
"""

from __future__ import annotations

import hashlib
import json
import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Callable

from .ingest import Document
from .llm import LLM

log = logging.getLogger(__name__)

PROMPT_VERSION = "v2"  # bump to invalidate the cache when the prompt or schema changes
SECTION_WORDS = 12_000
CATEGORIES = ["risk", "opportunity", "action", "deadline", "stakeholder"]

INSIGHT_TOOL = {
    "name": "record_insights",
    "description": "Record the summary and structured insights extracted from a document section.",
    "input_schema": {
        "type": "object",
        "properties": {
            "summary": {
                "type": "string",
                "description": "Neutral summary of this section in at most 120 words: purpose, key findings, recommendations.",
            },
            "insights": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "category": {"type": "string", "enum": CATEGORIES},
                        "title": {"type": "string", "description": "Short label, max 12 words."},
                        "detail": {"type": "string", "description": "One or two sentences of specifics."},
                        "owner": {
                            "type": "string",
                            "description": "Who is responsible or affected (organisation/role). Empty string if not stated.",
                        },
                        "date": {
                            "type": "string",
                            "description": "Deadline or timing exactly as stated in the text. Empty string if none.",
                        },
                        "page": {"anyOf": [{"type": "integer"}, {"type": "null"}], "description": "Page number from the [p.N] markers, or null."},
                        "importance": {"type": "string", "enum": ["high", "medium", "low"]},
                    },
                    "required": ["category", "title", "detail", "owner", "date", "page", "importance"],
                },
            },
        },
        "required": ["summary", "insights"],
    },
}

SYSTEM = """You are a senior analyst extracting decision-relevant intelligence from UK government AI policy documents for a consulting team.
Rules:
- Only record what the text actually states. Never infer owners or dates that are not written down; use an empty string instead.
- risk = something that could go wrong or cause harm; opportunity = potential benefit or growth area;
  action = a recommendation, commitment or required step; deadline = any dated milestone or time-bound commitment;
  stakeholder = an organisation, body or group with a defined role or interest.
- Prefer fewer, substantive items over many trivial ones (roughly 5-25 per section). Skip navigation text, contact details and boilerplate.
- importance reflects relevance to a senior decision-maker."""


def _sections(doc: Document) -> list[str]:
    """Split document text into ~12k-word sections on page boundaries, with [p.N] markers."""
    sections, current, count = [], [], 0
    for page in doc.pages:
        if not page.text:
            continue
        block = f"[p.{page.number}]\n{page.text}" if page.number else page.text
        words = len(page.text.split())
        if current and count + words > SECTION_WORDS:
            sections.append("\n\n".join(current))
            current, count = [], 0
        current.append(block)
        count += words
    if current:
        sections.append("\n\n".join(current))
    return sections


def _cache_path(cache_dir: Path, doc: Document, model: str) -> Path:
    digest = hashlib.sha256(f"{PROMPT_VERSION}|{model}|{doc.text}".encode()).hexdigest()[:16]
    return cache_dir / "insights" / f"{doc.doc_id}.{digest}.json"


def _normalise(record: dict, doc: Document) -> dict:
    """Web pages have no page numbers, so drop any the model supplied for them."""
    if doc.file_type != "pdf":
        for item in record["insights"]:
            item["page"] = None
    return record


def extract_document(llm: LLM, doc: Document, cache_dir: Path) -> dict:
    path = _cache_path(cache_dir, doc, llm.fast_model)
    if path.exists():
        return _normalise(json.loads(path.read_text(encoding="utf-8")), doc)

    summaries, insights = [], []
    sections = _sections(doc)
    for i, section in enumerate(sections, 1):
        log.info("Extracting %s (section %d/%d)", doc.doc_id, i, len(sections))
        prompt = (
            f"Document: {doc.title}\nSection {i} of {len(sections)}\n"
            + ("".join(f"Ingestion note: {n}\n" for n in doc.notes))
            + f"\n<document>\n{section}\n</document>"
        )
        result = llm.structured(SYSTEM, prompt, INSIGHT_TOOL, fast=True)
        summaries.append(result.get("summary", ""))
        insights.extend(result.get("insights", []))

    for item in insights:
        item["doc_id"] = doc.doc_id
        item["doc_title"] = doc.title
    insights = _normalise({"insights": insights}, doc)["insights"]

    record = {"doc_id": doc.doc_id, "title": doc.title, "summary": " ".join(summaries), "insights": insights}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
    return record


def extract_all(
    llm: LLM, docs: list[Document], cache_dir: Path, progress: Callable[[int, int, str], None] | None = None
) -> list[dict]:
    """Extract insights for every document (cached ones return instantly). Two at a time to respect rate limits."""
    results: dict[str, dict] = {}
    done = 0
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = {pool.submit(extract_document, llm, d, cache_dir): d for d in docs}
        for fut, doc in futures.items():
            results[doc.doc_id] = fut.result()
            done += 1
            if progress:
                progress(done, len(docs), doc.title)
    return [results[d.doc_id] for d in docs]


def is_prepared(llm_fast_model: str, docs: list[Document], cache_dir: Path) -> bool:
    return all(_cache_path(cache_dir, d, llm_fast_model).exists() for d in docs)
