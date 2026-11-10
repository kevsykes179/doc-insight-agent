"""Tests for the API wrapper using a fake Anthropic client (no network)."""

from __future__ import annotations

from types import SimpleNamespace as NS

import anthropic
import pytest

try:  # newer SDK versions use httpx2, older ones httpx
    import httpx2
except ImportError:  # pragma: no cover
    import httpx as httpx2

from docagent.agent import ROUTER_TOOLS
from docagent.insights import INSIGHT_TOOL
from docagent.llm import LLM, parse_json, strict_schema


def text_block(t):
    return NS(type="text", text=t)


def tool_block(name, args):
    return NS(type="tool_use", name=name, input=args)


class FakeMessages:
    def __init__(self, responses):
        self.responses = list(responses)
        self.requests = []

    def create(self, **kwargs):
        self.requests.append(kwargs)
        r = self.responses.pop(0)
        if isinstance(r, Exception):
            raise r
        return r if hasattr(r, "content") else NS(content=r, stop_reason="end_turn")


def make_llm(responses):
    llm = LLM.__new__(LLM)  # skip __init__ (no API key / model listing)
    llm.model, llm.fast_model = "main", "fast"
    llm.client = NS(messages=FakeMessages(responses))
    return llm


def bad_request():
    resp = httpx2.Response(400, request=httpx2.Request("POST", "https://api.anthropic.com/v1/messages"))
    return anthropic.BadRequestError("output_config not supported", response=resp, body=None)


def test_structured_uses_output_config():
    llm = make_llm([[text_block('{"summary": "s", "insights": []}')]])
    out = llm.structured("sys", "prompt", INSIGHT_TOOL, fast=True)
    req = llm.client.messages.requests[0]
    assert out == {"summary": "s", "insights": []}
    assert req["model"] == "fast"
    assert req["output_config"]["format"]["type"] == "json_schema"
    assert "tool_choice" not in req


def test_structured_falls_back_to_tool_call():
    llm = make_llm([bad_request(), [tool_block("record_insights", {"summary": "s", "insights": []})]])
    assert llm.structured("sys", "p", INSIGHT_TOOL)["summary"] == "s"
    assert "tool_choice" not in llm.client.messages.requests[1]


def test_routing_never_forces_tool_choice():
    llm = make_llm([[tool_block("list_documents", {"reason": "r"})]])
    calls = llm.choose_tools("sys", [{"role": "user", "content": "docs?"}], ROUTER_TOOLS)
    assert calls[0].name == "list_documents"
    assert "tool_choice" not in llm.client.messages.requests[0]


def test_plain_text_reply_becomes_direct_response():
    llm = make_llm([[text_block("Hello! I can summarise the documents.")]])
    calls = llm.choose_tools("sys", [{"role": "user", "content": "hi"}], ROUTER_TOOLS)
    assert calls[0].name == "respond_directly"


def test_strict_schema_closes_objects_and_drops_length_limits():
    schema = strict_schema({"type": "object", "properties": {"items": {"type": "array", "maxItems": 5,
                            "items": {"type": "object", "properties": {"a": {"type": "string"}}}}}})
    assert schema["additionalProperties"] is False
    assert "maxItems" not in schema["properties"]["items"]
    assert schema["properties"]["items"]["items"]["additionalProperties"] is False


@pytest.mark.parametrize("raw", ['{"a": 1}', '```json\n{"a": 1}\n```', 'Here you go: {"a": 1}'])
def test_parse_json_tolerates_wrapping(raw):
    assert parse_json(raw) == {"a": 1}


def test_truncated_reply_is_retried_with_higher_limit():
    llm = make_llm([NS(content=[text_block("Bottom line: compet")], stop_reason="max_tokens"),
                    NS(content=[text_block("Bottom line: complete answer.")], stop_reason="end_turn")])
    assert llm.text("sys", "p", max_tokens=100) == "Bottom line: complete answer."
    assert [r["max_tokens"] for r in llm.client.messages.requests] == [100, 300]
