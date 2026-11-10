"""The agent: decides which tool should handle a request, then runs it.

Pattern: "router + executor".
1. ROUTE   - Claude sees the request (plus recent conversation) and a menu of tools,
             and must pick one or more tools and fill in their arguments
             (Anthropic tool use / function calling, with tool_choice="any").
2. EXECUTE - our code runs the chosen tool(s). Each tool is ordinary Python that may
             make its own focused model call.
3. FALLBACK- if the routing call fails (network, rate limit), a simple keyword
             router picks a tool so the user still gets an answer.

Why not a free-running loop where the model calls tools repeatedly? For this task
every request maps to one or two tools, so a single routing decision is cheaper,
faster, predictable and easy to audit. The trade-off is documented in the README.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

from .ingest import Document, chunk_documents, load_folder
from .insights import CATEGORIES
from .llm import LLM, ToolCall
from .retrieval import SearchIndex
from .tools import ToolResult, Toolbox

log = logging.getLogger(__name__)

ROUTER_SYSTEM = """You are the routing layer of a document-analysis assistant used by consultants.
The loaded documents are UK government publications about AI policy, safety, security and adoption.
Choose the tool(s) that best fulfil the user's request and fill in their arguments.
- Factual or specific questions -> answer_question. Write a keyword-rich search_query (add synonyms and key terms).
- Requests for risks, opportunities, actions, owners, deadlines, timelines or stakeholders -> extract_insights with the right categories.
- Requests for an overview, summary, briefing or "what do these say" -> executive_summary.
- Questions about which documents are loaded, their size or quality -> list_documents.
- Greetings, thanks, or requests unrelated to the documents -> respond_directly (briefly explain what you can do).
If a request clearly asks for two different things (e.g. "summarise and list the risks"), call both tools.
Use the conversation history to resolve follow-ups such as "what about deadlines?"."""

ROUTER_TOOLS = [
    {
        "name": "answer_question",
        "description": "Search the documents and answer a specific factual question with citations.",
        "input_schema": {
            "type": "object",
            "properties": {
                "question": {"type": "string", "description": "The user's question, self-contained (resolve follow-ups)."},
                "search_query": {"type": "string", "description": "Keyword-rich query for the search index, including synonyms."},
                "reason": {"type": "string", "description": "One short sentence: why this tool."},
            },
            "required": ["question", "search_query", "reason"],
        },
    },
    {
        "name": "extract_insights",
        "description": "Produce structured tables of risks, opportunities, actions (with owners), deadlines and/or stakeholders across all documents.",
        "input_schema": {
            "type": "object",
            "properties": {
                "categories": {"type": "array", "items": {"type": "string", "enum": CATEGORIES}},
                "topic": {"type": "string", "description": "Optional focus area, e.g. 'security' or 'procurement'. Empty for all."},
                "max_items": {"type": "integer", "description": "Items per category, 3-20. Default 10."},
                "reason": {"type": "string", "description": "One short sentence: why this tool."},
            },
            "required": ["categories", "reason"],
        },
    },
    {
        "name": "executive_summary",
        "description": "Write a concise executive summary (max 300 words) of all documents for senior stakeholders.",
        "input_schema": {
            "type": "object",
            "properties": {
                "focus": {"type": "string", "description": "Optional angle or audience, e.g. 'for a defence client'. Empty for general."},
                "reason": {"type": "string", "description": "One short sentence: why this tool."},
            },
            "required": ["reason"],
        },
    },
    {
        "name": "list_documents",
        "description": "List the loaded documents with type, size and any data-quality notes.",
        "input_schema": {
            "type": "object",
            "properties": {"reason": {"type": "string", "description": "One short sentence: why this tool."}},
            "required": ["reason"],
        },
    },
    {
        "name": "respond_directly",
        "description": "Reply without using the documents: greetings, thanks, out-of-scope requests or asking the user to clarify.",
        "input_schema": {
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "The reply to show the user."},
                "reason": {"type": "string", "description": "One short sentence: why this tool."},
            },
            "required": ["message", "reason"],
        },
    },
]

TOOL_LABELS = {
    "answer_question": "Question answering (search + cited answer)",
    "extract_insights": "Insight extraction",
    "executive_summary": "Executive summary",
    "list_documents": "Document catalogue",
    "respond_directly": "Direct reply",
}


def keyword_route(request: str) -> ToolCall:
    """Fallback router used only if the model-based router is unavailable."""
    r = request.lower()
    cats = [c for c, pat in {
        "risk": r"\brisk|threat|danger|concern|harm",
        "opportunity": r"opportunit|benefit|growth|potential",
        "action": r"\baction|owner|recommend|next step|to.?do",
        "deadline": r"deadline|date|timeline|milestone|when\b|by \d{4}",
        "stakeholder": r"stakeholder|who is involved|organisation|bodies|parties",
    }.items() if re.search(pat, r)]
    if re.search(r"summar|overview|brief|exec|tl;?dr|key points", r):
        return ToolCall("executive_summary", {"reason": "keyword fallback: summary words"})
    if cats and not r.rstrip().endswith("?"):
        return ToolCall("extract_insights", {"categories": cats, "reason": "keyword fallback: insight words"})
    if re.search(r"which documents|what documents|list (the )?documents|what files", r):
        return ToolCall("list_documents", {"reason": "keyword fallback: document listing"})
    return ToolCall("answer_question", {"question": request, "search_query": request, "reason": "keyword fallback: default"})


@dataclass
class AgentResponse:
    request: str
    calls: list[ToolCall]
    results: list[ToolResult]
    routed_by: str  # "model" or "keyword-fallback"

    @property
    def markdown(self) -> str:
        return "\n\n---\n\n".join(r.markdown for r in self.results)

    @property
    def sources(self) -> list[str]:
        seen: list[str] = []
        for r in self.results:
            seen.extend(s for s in r.sources if s not in seen)
        return seen


@dataclass
class Agent:
    llm: LLM
    docs: list[Document]
    cache_dir: Path
    history: list[dict] = field(default_factory=list)

    def __post_init__(self):
        self.index = SearchIndex(chunk_documents(self.docs))
        self.tools = Toolbox(self.llm, self.docs, self.index, self.cache_dir)

    @classmethod
    def from_folder(cls, llm: LLM, data_dir: Path, cache_dir: Path) -> "Agent":
        return cls(llm, load_folder(data_dir), cache_dir)

    def route(self, request: str) -> tuple[list[ToolCall], str]:
        messages = self.history[-6:] + [{"role": "user", "content": request}]
        try:
            calls = self.llm.choose_tools(ROUTER_SYSTEM, messages, ROUTER_TOOLS)
            valid = [c for c in calls if c.name in TOOL_LABELS]
            if valid:
                return valid[:3], "model"
        except Exception as exc:  # noqa: BLE001
            log.warning("Model routing failed (%s); using keyword fallback", exc)
        return [keyword_route(request)], "keyword-fallback"

    def run(self, request: str) -> AgentResponse:
        calls, routed_by = self.route(request)
        results = []
        for call in calls:
            handler = getattr(self.tools, call.name)
            try:
                results.append(handler(**call.args))
            except Exception as exc:  # noqa: BLE001 - show the error rather than crash the UI
                log.exception("Tool %s failed", call.name)
                results.append(ToolResult(f"**{TOOL_LABELS[call.name]} failed:** {exc}"))

        response = AgentResponse(request, calls, results, routed_by)
        # Keep a compact history so follow-up questions can be resolved.
        self.history += [
            {"role": "user", "content": request},
            {"role": "assistant", "content": f"[{', '.join(c.name for c in calls)}] {response.markdown[:600]}"},
        ]
        return response
