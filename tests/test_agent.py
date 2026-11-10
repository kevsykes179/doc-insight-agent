"""Offline tests: no API key needed. The model is replaced by a FakeLLM."""

from __future__ import annotations

from pathlib import Path

import pytest

from docagent.agent import Agent, keyword_route
from docagent.ingest import chunk_documents, detect_type, load_document, load_folder
from docagent.llm import ToolCall
from docagent.retrieval import SearchIndex
from docagent.tools import SUMMARY_WORD_LIMIT, trim_to_words, word_count

DATA = Path(__file__).resolve().parent.parent / "data"


@pytest.fixture(scope="session")
def docs():
    return load_folder(DATA)


class FakeLLM:
    model = "fake-main"
    fast_model = "fake-fast"

    def __init__(self, route: list[ToolCall] | None = None, fail_routing: bool = False, long_summary: bool = False):
        self.route = route or []
        self.fail_routing = fail_routing
        self.long_summary = long_summary
        self.calls: list[str] = []

    def choose_tools(self, system, messages, tools):
        self.calls.append("route")
        if self.fail_routing:
            raise ConnectionError("simulated outage")
        return self.route

    def text(self, system, prompt, fast=False, max_tokens=1500):
        self.calls.append("text")
        if "executive summaries" in system:
            return "word " * (450 if self.long_summary else 120)
        return "The mission is to minimise surprise from AI advances [S1]."

    def structured(self, system, prompt, tool, fast=False, max_tokens=8000):
        self.calls.append(f"structured:{tool['name']}")
        if tool["name"] == "record_insights":
            return {
                "summary": "A summary.",
                "insights": [
                    {"category": "risk", "title": "Market concentration", "detail": "Few firms dominate.", "owner": "CMA",
                     "date": "", "page": 3, "importance": "high"},
                    {"category": "action", "title": "Publish guidance", "detail": "Issue guidance.", "owner": "GDS",
                     "date": "2025", "page": None, "importance": "medium"},
                ],
            }
        return {"items": [{"title": "Market concentration", "detail": "Few firms dominate.", "owner": "CMA", "date": "",
                           "importance": "high", "sources": ["AI Foundation Models Short Report, p.3"]}]}


# ------------------------------------------------------------------ ingestion

def test_mislabelled_pdf_is_detected_as_html():
    path = DATA / "AI_Playbook_for_UK_Government.pdf"
    assert detect_type(path) == "html"
    doc = load_document(path)
    assert doc.file_type == "html"
    assert any("actually HTML" in n for n in doc.notes)


def test_all_documents_load_with_content(docs):
    assert len(docs) == 11
    assert all(d.word_count > 100 for d in docs)


def test_html_clutter_removed(docs):
    text = next(d for d in docs if d.doc_id == "AI_Safety_Institute").text.lower()
    assert "cookies on gov.uk" not in text
    assert "mission" in text


def test_pdf_chunks_keep_page_numbers(docs):
    report = next(d for d in docs if d.doc_id == "AI_Foundation_Models_Short_Report")
    chunks = chunk_documents([report])
    assert all(c.page is not None for c in chunks)
    assert chunks[0].citation.startswith("AI Foundation Models Short Report, p.")


# ------------------------------------------------------------------ retrieval

def test_search_finds_relevant_document(docs):
    index = SearchIndex(chunk_documents(docs))
    top = index.search("AI Safety Institute mission minimise surprise", k=3)
    assert top and top[0][0].doc_id == "AI_Safety_Institute"


def test_search_empty_query_returns_nothing(docs):
    assert SearchIndex(chunk_documents(docs)).search("the and of") == []


# ------------------------------------------------------------------ routing

@pytest.mark.parametrize("request_text,expected", [
    ("Summarise the documents", "executive_summary"),
    ("Identify the key risks", "extract_insights"),
    ("List actions and owners", "extract_insights"),
    ("What is the AI Safety Institute?", "answer_question"),
    ("Which documents are loaded?", "list_documents"),
])
def test_keyword_fallback_router(request_text, expected):
    assert keyword_route(request_text).name == expected


def test_model_routing_dispatches_to_chosen_tool(docs, tmp_path):
    llm = FakeLLM(route=[ToolCall("answer_question", {"question": "Mission?", "search_query": "AI Safety Institute mission", "reason": "factual"})])
    resp = Agent(llm, docs, tmp_path).run("What is the AISI's mission?")
    assert resp.routed_by == "model"
    assert [c.name for c in resp.calls] == ["answer_question"]
    assert "[S1]" in resp.markdown and resp.sources


def test_multi_intent_runs_both_tools(docs, tmp_path):
    llm = FakeLLM(route=[ToolCall("executive_summary", {"reason": "a"}), ToolCall("extract_insights", {"categories": ["risk"], "reason": "b"})])
    resp = Agent(llm, docs, tmp_path).run("Summarise and list risks")
    assert len(resp.results) == 2
    assert "Market concentration" in resp.markdown


def test_routing_failure_uses_fallback(docs, tmp_path):
    resp = Agent(FakeLLM(fail_routing=True), docs, tmp_path).run("Which documents are loaded?")
    assert resp.routed_by == "keyword-fallback"
    assert "11 documents" in resp.markdown


def test_history_is_kept_for_follow_ups(docs, tmp_path):
    agent = Agent(FakeLLM(route=[ToolCall("list_documents", {"reason": "x"})]), docs, tmp_path)
    agent.run("Which documents?")
    agent.run("And which are short?")
    assert len(agent.history) == 4


# ------------------------------------------------------------------ insights & summary

def test_insights_are_cached(docs, tmp_path):
    llm = FakeLLM(route=[ToolCall("extract_insights", {"categories": ["risk"], "reason": "x"})])
    Agent(llm, docs, tmp_path).run("risks")
    first = llm.calls.count("structured:record_insights")
    llm2 = FakeLLM(route=llm.route)
    Agent(llm2, docs, tmp_path).run("risks")
    assert first >= len(docs)  # big documents are split into several sections
    assert llm2.calls.count("structured:record_insights") == 0


def test_summary_word_limit_enforced(docs, tmp_path):
    llm = FakeLLM(route=[ToolCall("executive_summary", {"reason": "x"})], long_summary=True)
    resp = Agent(llm, docs, tmp_path).run("summarise")
    assert resp.results[0].data["word_count"] <= SUMMARY_WORD_LIMIT


def test_trim_to_words_cuts_on_sentence():
    text = "One two three. Four five six. Seven eight nine."
    assert trim_to_words(text, 7) == "One two three. Four five six."
    assert word_count(trim_to_words("word " * 500, 300)) <= 300


def test_web_pages_never_get_page_numbers(docs, tmp_path):
    from docagent.insights import extract_document
    html_doc = next(d for d in docs if d.file_type == "html")
    record = extract_document(FakeLLM(), html_doc, tmp_path)  # FakeLLM returns page=3 for one item
    assert all(i["page"] is None for i in record["insights"])
