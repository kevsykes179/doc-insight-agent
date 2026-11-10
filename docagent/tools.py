"""The tools the agent can route a request to.

Each tool returns a ToolResult: markdown for display, the sources it used, and raw
structured data (useful for testing or exporting).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from .ingest import Document
from .insights import CATEGORIES, extract_all
from .llm import LLM
from .retrieval import SearchIndex, tokenize

SUMMARY_WORD_LIMIT = 300
_IMPORTANCE_RANK = {"high": 0, "medium": 1, "low": 2}
_CATEGORY_LABELS = {
    "risk": "Risks",
    "opportunity": "Opportunities",
    "action": "Actions and owners",
    "deadline": "Deadlines and milestones",
    "stakeholder": "Stakeholders",
}


@dataclass
class ToolResult:
    markdown: str
    sources: list[str] = field(default_factory=list)
    data: dict = field(default_factory=dict)


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'£%.-]+\b", text))


def trim_to_words(text: str, limit: int) -> str:
    """Last-resort hard cap: cut at the last full sentence that fits within the limit."""
    if word_count(text) <= limit:
        return text
    sentences = re.split(r"(?<=[.!?])\s+", text)
    kept: list[str] = []
    for s in sentences:
        if word_count(" ".join(kept + [s])) > limit:
            break
        kept.append(s)
    return " ".join(kept) if kept else " ".join(text.split()[:limit])


class Toolbox:
    def __init__(self, llm: LLM, docs: list[Document], index: SearchIndex, cache_dir: Path):
        self.llm = llm
        self.docs = docs
        self.index = index
        self.cache_dir = cache_dir
        self._doc_insights: list[dict] | None = None
        self.progress = None  # optional callback(done, total, title) for UIs

    # ------------------------------------------------------------------ #
    # Shared helpers
    # ------------------------------------------------------------------ #

    def doc_insights(self, progress=None) -> list[dict]:
        if self._doc_insights is None:
            self._doc_insights = extract_all(self.llm, self.docs, self.cache_dir, progress or self.progress)
        return self._doc_insights

    def _catalogue(self) -> str:
        lines = []
        for d in self.docs:
            note = f" [Note: {' '.join(d.notes)}]" if d.notes else ""
            lines.append(f"- {d.title} ({d.file_type}, ~{d.word_count:,} words){note}")
        return "\n".join(lines)

    @staticmethod
    def _source(item: dict) -> str:
        return f"{item['doc_title']}, p.{item['page']}" if item.get("page") else item["doc_title"]

    # ------------------------------------------------------------------ #
    # Tool 1: question answering (retrieval + grounded answer)
    # ------------------------------------------------------------------ #

    def answer_question(self, question: str, search_query: str = "", **_) -> ToolResult:
        hits = self.index.search(search_query or question, k=8)
        if not hits:
            return ToolResult("I couldn't find anything in the documents that matches that question.")

        context = "\n\n".join(f"[S{i}] ({c.citation})\n{c.text}" for i, (c, _) in enumerate(hits, 1))
        system = (
            "You answer questions for consultants using ONLY the provided excerpts from UK government AI documents. "
            "Cite every claim with its excerpt marker, e.g. [S2]. If the excerpts do not contain the answer, say so plainly "
            "and say what the documents do cover instead. Never use outside knowledge. Be concise: under 200 words unless "
            "the question needs more. Use British English."
        )
        prompt = (
            f"Documents available:\n{self._catalogue()}\n\nExcerpts:\n{context}\n\nQuestion: {question}"
        )
        answer = self.llm.text(system, prompt)

        cited = sorted({int(n) for n in re.findall(r"\[S(\d+)\]", answer) if 0 < int(n) <= len(hits)})
        sources = [f"[S{n}] {hits[n - 1][0].citation}" for n in cited]
        return ToolResult(answer, sources, {"retrieved": [c.chunk_id for c, _ in hits]})

    # ------------------------------------------------------------------ #
    # Tool 2: structured insight extraction
    # ------------------------------------------------------------------ #

    def extract_insights(self, categories: list[str] | None = None, topic: str = "", max_items: int = 10, **_) -> ToolResult:
        categories = [c for c in (categories or CATEGORIES) if c in CATEGORIES] or CATEGORIES
        max_items = max(3, min(int(max_items or 10), 20))
        all_items = [i for d in self.doc_insights() for i in d["insights"]]

        sections, data, sources = [], {}, set()
        for cat in categories:
            items = [i for i in all_items if i.get("category") == cat]
            if topic:
                words = set(tokenize(topic))
                matched = [i for i in items if words & set(tokenize(f"{i['title']} {i['detail']} {i['owner']}"))]
                items = matched if len(matched) >= 3 else items  # fall back if the topic filter is too strict
            # Keep the most important items per document so one long report can't crowd out the rest.
            items.sort(key=lambda i: _IMPORTANCE_RANK.get(i.get("importance"), 3))
            per_doc: dict[str, int] = {}
            shortlist = []
            for i in items:
                if per_doc.get(i["doc_id"], 0) < 8:
                    shortlist.append(i)
                    per_doc[i["doc_id"]] = per_doc.get(i["doc_id"], 0) + 1
            if not shortlist:
                continue

            merged = self._consolidate(cat, shortlist, topic, max_items)
            data[cat] = merged
            sources.update(s for m in merged for s in m["sources"])
            sections.append(self._render_table(cat, merged))

        if not sections:
            return ToolResult("No matching insights were found in the documents.")
        heading = f"**Focus:** {topic}\n\n" if topic else ""
        return ToolResult(heading + "\n\n".join(sections), sorted(sources), data)

    def _consolidate(self, category: str, items: list[dict], topic: str, max_items: int) -> list[dict]:
        """Ask the model to merge duplicates across documents and rank for a senior audience."""
        listing = "\n".join(
            f"{n}. [{i['importance']}] {i['title']}: {i['detail']} | owner: {i['owner'] or '-'} | date: {i['date'] or '-'} | source: {self._source(i)}"
            for n, i in enumerate(items, 1)
        )
        tool = {
            "name": "ranked_insights",
            "description": f"The consolidated, ranked list of {category} items.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "maxItems": max_items,
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "detail": {"type": "string", "description": "Max 35 words."},
                                "owner": {"type": "string"},
                                "date": {"type": "string"},
                                "importance": {"type": "string", "enum": ["high", "medium", "low"]},
                                "sources": {"type": "array", "items": {"type": "string"}},
                            },
                            "required": ["title", "detail", "owner", "date", "importance", "sources"],
                        },
                    }
                },
                "required": ["items"],
            },
        }
        system = (
            "You consolidate extracted insights for a senior consulting audience. Merge items that describe the same thing "
            "(combine their sources), drop trivial ones, and rank the rest by importance. Keep owners, dates and source "
            "strings exactly as given; do not invent new facts. Use British English."
        )
        focus = f"Focus on items relevant to: {topic}\n" if topic else ""
        prompt = f"Category: {category}\n{focus}Return at most {max_items} items.\n\n{listing}"
        return self.llm.structured(system, prompt, tool, max_tokens=4000).get("items", [])[:max_items]

    @staticmethod
    def _render_table(category: str, items: list[dict]) -> str:
        def cell(s: str) -> str:
            return (s or "-").replace("|", "/").replace("\n", " ")

        rows = [f"### {_CATEGORY_LABELS[category]}", "", "| # | Item | Detail | Owner | Date | Priority | Source |", "|---|---|---|---|---|---|---|"]
        for n, i in enumerate(items, 1):
            rows.append(
                f"| {n} | **{cell(i['title'])}** | {cell(i['detail'])} | {cell(i['owner'])} | {cell(i['date'])} | "
                f"{cell(i['importance']).capitalize()} | {cell('; '.join(i['sources']))} |"
            )
        return "\n".join(rows)

    # ------------------------------------------------------------------ #
    # Tool 3: executive summary (max 300 words, enforced in code)
    # ------------------------------------------------------------------ #

    def executive_summary(self, focus: str = "", **_) -> ToolResult:
        records = self.doc_insights()
        summaries = "\n\n".join(f"## {r['title']}\n{r['summary']}" for r in records)
        key_items = sorted(
            (i for r in records for i in r["insights"] if i.get("importance") == "high"),
            key=lambda i: CATEGORIES.index(i["category"]) if i["category"] in CATEGORIES else 9,
        )[:40]
        highlights = "\n".join(f"- ({i['category']}) {i['title']}: {i['detail']} [{self._source(i)}]" for i in key_items)

        system = (
            "You write executive summaries for senior stakeholders (directors, partners, permanent secretaries). "
            f"HARD LIMIT: {SUMMARY_WORD_LIMIT} words including headings. Structure: a one-sentence bottom line; "
            "'Key messages' (3-4 bullets); 'Main risks' (2-3 bullets); 'Opportunities' (2-3 bullets); "
            "'Recommended next steps' (2-3 bullets). Plain British English, no jargon, no preamble. "
            "Only use facts from the material provided."
        )
        focus_line = f"Tailor the summary to this focus: {focus}\n\n" if focus else ""
        prompt = f"{focus_line}Document summaries:\n{summaries}\n\nHigh-importance extracted items:\n{highlights}"
        text = self.llm.text(system, prompt, max_tokens=4000)

        if word_count(text) > SUMMARY_WORD_LIMIT:  # one retry, then hard cap
            text = self.llm.text(
                system, f"Shorten this to under {SUMMARY_WORD_LIMIT - 20} words, keeping the structure:\n\n{text}", max_tokens=4000
            )
            text = trim_to_words(text, SUMMARY_WORD_LIMIT)

        words = word_count(text)
        sources = [r["title"] for r in records]
        return ToolResult(f"{text}\n\n*{words} words · based on {len(records)} documents*", sources, {"word_count": words})

    # ------------------------------------------------------------------ #
    # Tool 4: list documents (no AI call)
    # ------------------------------------------------------------------ #

    def list_documents(self, **_) -> ToolResult:
        rows = ["| Document | Type | Pages | Words | Notes |", "|---|---|---|---|---|"]
        for d in self.docs:
            pages = len(d.pages) if d.file_type == "pdf" else "web page"
            rows.append(f"| {d.title} | {d.file_type.upper()} | {pages} | {d.word_count:,} | {' '.join(d.notes) or '-'} |")
        total = sum(d.word_count for d in self.docs)
        return ToolResult(f"{len(self.docs)} documents loaded (~{total:,} words).\n\n" + "\n".join(rows))

    # ------------------------------------------------------------------ #
    # Tool 5: respond directly (greetings, out-of-scope, clarification)
    # ------------------------------------------------------------------ #

    def respond_directly(self, message: str = "", **_) -> ToolResult:
        return ToolResult(message or "How can I help with the documents?")
