"""Run a fixed set of example requests and save the outputs to examples/EXAMPLES.md.

    python scripts/generate_examples.py

These outputs are what the README links to as evidence of each capability.
"""

from __future__ import annotations

import sys
import time
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from docagent.agent import Agent  # noqa: E402
from docagent.config import get_settings  # noqa: E402
from docagent.ingest import load_folder  # noqa: E402
from docagent.llm import LLM  # noqa: E402

EXAMPLES = [
    ("Executive summary", "Summarise the documents for a senior audience"),
    ("Risk extraction", "What are the key risks?"),
    ("Action extraction", "List the actions and who owns them"),
    ("Deadlines", "What deadlines or milestones are mentioned?"),
    ("Stakeholders", "Who are the main stakeholders?"),
    ("Factual question", "What is the AI Safety Institute's mission?"),
    ("Factual question", "What concerns does the CMA raise about competition in foundation models?"),
    ("Factual question", "What does the GCS policy say about using generative AI to create images?"),
    ("Follow-up (uses conversation history)", "Which of those relate to procurement?"),
    ("Multi-intent request", "Give me a short summary and the top 5 opportunities"),
    ("Out of scope", "What's the weather in London?"),
    ("Data-quality awareness", "Which documents are loaded, and are there any problems with them?"),
]


def main() -> None:
    settings = get_settings()
    llm = LLM(settings.api_key, settings.model, settings.fast_model)
    agent = Agent(llm, load_folder(settings.data_dir), settings.cache_dir)
    print("Building insight index (first run takes a few minutes)...")
    agent.tools.doc_insights(lambda d, t, title: print(f"  [{d}/{t}] {title}"))

    out = [
        "# Example outputs",
        "",
        f"Generated {date.today():%d %B %Y} by `scripts/generate_examples.py` using `{llm.model}` "
        f"(routing, answers, summaries) and `{llm.fast_model}` (per-document extraction).",
        "",
    ]
    for label, request in EXAMPLES:
        print(f"- {request}")
        start = time.time()
        resp = agent.run(request)
        routes = "; ".join(f"`{c.name}` ({c.args.get('reason', '')})" for c in resp.calls)
        out += [
            f"## {label}",
            "",
            f"**Request:** {request}",
            "",
            f"**Routed to:** {routes} · routed by {resp.routed_by} · {time.time() - start:.1f}s",
            "",
            resp.markdown,
            "",
        ]
        if resp.sources:
            out += ["<details><summary>Sources</summary>", ""] + [f"- {s}" for s in resp.sources] + ["", "</details>", ""]
        out += ["---", ""]

    path = ROOT / "examples" / "EXAMPLES.md"
    path.parent.mkdir(exist_ok=True)
    path.write_text("\n".join(out), encoding="utf-8")
    print(f"Saved {path}")


if __name__ == "__main__":
    main()
