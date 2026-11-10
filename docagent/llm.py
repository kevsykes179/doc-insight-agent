"""Thin wrapper around the Anthropic API.

Everything that talks to the model goes through this class, so the rest of the code
(and the tests) can swap in a fake.
"""

from __future__ import annotations

import copy
import json
import logging
import re
from dataclasses import dataclass
from typing import Any

import anthropic

log = logging.getLogger(__name__)

# Used only if auto-detection fails and nothing is set in .env.
FALLBACK_MODEL = "claude-sonnet-4-5"
FALLBACK_FAST_MODEL = "claude-haiku-4-5"


@dataclass
class ToolCall:
    name: str
    args: dict[str, Any]


class LLM:
    def __init__(self, api_key: str, model: str | None = None, fast_model: str | None = None):
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is not set. Copy .env.example to .env and add your key.")
        # Generous retries: new API accounts have low per-minute token limits, and the
        # SDK backs off automatically when it gets a rate-limit response.
        self.client = anthropic.Anthropic(api_key=api_key, max_retries=6, timeout=300)
        self.model = model or self._newest("sonnet", FALLBACK_MODEL)
        self.fast_model = fast_model or self._newest("haiku", FALLBACK_FAST_MODEL)

    def _newest(self, family: str, fallback: str) -> str:
        """Pick the newest available model in a family, so the code doesn't go stale."""
        try:
            for m in self.client.models.list(limit=100):  # API returns newest first
                if family in m.id:
                    return m.id
        except anthropic.AuthenticationError as exc:
            raise ValueError("Your ANTHROPIC_API_KEY was rejected. Check the key in your .env file.") from exc
        except Exception as exc:  # noqa: BLE001 - any other failure just means "use the fallback"
            log.warning("Could not list models (%s); using %s", exc, fallback)
        return fallback

    # ------------------------------------------------------------------ #

    def text(self, system: str, prompt: str, *, fast: bool = False, max_tokens: int = 4000) -> str:
        """Plain text completion.

        If the reply is cut off by the token limit (newer models can spend part of the
        allowance on internal reasoning), retry once with a larger limit rather than
        returning a half-finished answer.
        """
        for limit in (max_tokens, max_tokens * 3):
            resp = self.client.messages.create(
                model=self.fast_model if fast else self.model,
                max_tokens=limit,
                system=system,
                messages=[{"role": "user", "content": prompt}],
            )
            text = "".join(b.text for b in resp.content if b.type == "text").strip()
            if getattr(resp, "stop_reason", None) != "max_tokens":
                return text
            log.warning("Reply truncated at %d tokens; retrying with a higher limit", limit)
        return text + "\n\n*[Answer truncated: token limit reached]*"

    def structured(self, system: str, prompt: str, tool: dict, *, fast: bool = False, max_tokens: int = 8000) -> dict:
        """Return JSON matching the tool's input_schema.

        Preferred: the API's structured-outputs feature (output_config json_schema), which
        guarantees valid JSON. Fallback for models/accounts without it: offer the schema as a
        tool and read the model's tool call.
        """
        model = self.fast_model if fast else self.model
        try:
            resp = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": prompt}],
                output_config={"format": {"type": "json_schema", "schema": strict_schema(tool["input_schema"])}},
            )
            return parse_json("".join(b.text for b in resp.content if b.type == "text"))
        except anthropic.BadRequestError as exc:
            log.info("Structured outputs unavailable (%s); falling back to tool call", exc)

        resp = self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system + f"\n\nRespond ONLY by calling the {tool['name']} tool.",
            tools=[tool],
            messages=[{"role": "user", "content": prompt}],
        )
        for block in resp.content:
            if block.type == "tool_use":
                return dict(block.input)
        return parse_json("".join(b.text for b in resp.content if b.type == "text"))

    def choose_tools(self, system: str, messages: list[dict], tools: list[dict]) -> list[ToolCall]:
        """Routing step: the model picks one (or more) of the given tools.

        Newer models don't accept a *forced* tool choice, so the system prompt instructs the
        model to always call a tool. If it replies in plain text anyway, that reply is
        treated as a direct response rather than an error.
        """
        resp = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            system=system + "\n\nAlways respond by calling one or more of the tools. Never reply in plain text.",
            tools=tools,
            messages=messages,
        )
        calls = [ToolCall(b.name, dict(b.input)) for b in resp.content if b.type == "tool_use"]
        if not calls:
            text = "".join(b.text for b in resp.content if b.type == "text").strip()
            if text:
                calls = [ToolCall("respond_directly", {"message": text, "reason": "model replied without a tool"})]
        return calls


def strict_schema(schema: dict) -> dict:
    """Adapt a JSON schema for structured outputs: closed objects, no length keywords
    (length limits are enforced in our own code instead)."""
    schema = copy.deepcopy(schema)

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            for key in ("maxItems", "minItems", "maxLength", "minLength"):
                node.pop(key, None)
            if node.get("type") == "object":
                node["additionalProperties"] = False
                node.setdefault("required", list(node.get("properties", {})))
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(schema)
    return schema


def parse_json(text: str) -> dict:
    """Parse JSON from model text, tolerating code fences or stray prose around it."""
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.S)
        if match:
            return json.loads(match.group(0))
        raise RuntimeError("Model did not return valid JSON") from None
