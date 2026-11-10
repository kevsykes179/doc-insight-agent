"""Command-line interface.

    python -m docagent.cli docs                       # list documents (no API key needed)
    python -m docagent.cli prepare                    # build the insight index (one-off)
    python -m docagent.cli ask "What are the key risks?"
    python -m docagent.cli chat                       # interactive session
"""

from __future__ import annotations

import argparse
import logging
import sys

from .agent import TOOL_LABELS, Agent, AgentResponse
from .config import get_settings
from .ingest import load_folder
from .llm import LLM
from .tools import Toolbox


def _print(resp: AgentResponse) -> None:
    for c in resp.calls:
        print(f"\n> Routed to: {TOOL_LABELS[c.name]} ({c.args.get('reason', '')}) [{resp.routed_by}]")
    print("\n" + resp.markdown)
    if resp.sources:
        print("\nSources:\n" + "\n".join(f"  - {s}" for s in resp.sources))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="docagent", description="AI document insight agent")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("docs", help="List loaded documents")
    sub.add_parser("prepare", help="Extract insights from every document (cached)")
    ask = sub.add_parser("ask", help="Ask a single question")
    ask.add_argument("request", nargs="+")
    sub.add_parser("chat", help="Interactive chat")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING, format="%(message)s")
    settings = get_settings()
    docs = load_folder(settings.data_dir)

    if args.command == "docs":
        print(Toolbox(None, docs, None, settings.cache_dir).list_documents().markdown)  # type: ignore[arg-type]
        return 0

    try:
        llm = LLM(settings.api_key, settings.model, settings.fast_model)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1
    agent = Agent(llm, docs, settings.cache_dir)
    print(f"Models: main={llm.model}, extraction={llm.fast_model}", file=sys.stderr)

    if args.command == "prepare":
        agent.tools.doc_insights(lambda d, t, title: print(f"  [{d}/{t}] {title}", file=sys.stderr))
        print("Insight index ready.")
    elif args.command == "ask":
        _print(agent.run(" ".join(args.request)))
    else:
        print("Ask about the documents. Type 'exit' to quit.")
        while True:
            try:
                request = input("\nYou: ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if request.lower() in {"exit", "quit"}:
                break
            if request:
                _print(agent.run(request))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
