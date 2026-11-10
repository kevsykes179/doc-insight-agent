"""Streamlit web app: chat with the document collection.

Run with:  streamlit run app.py
"""

from __future__ import annotations

import logging

import streamlit as st

from docagent.agent import TOOL_LABELS, Agent
from docagent.config import get_settings
from docagent.ingest import load_folder
from docagent.insights import is_prepared
from docagent.llm import LLM

logging.basicConfig(level=logging.INFO)
st.set_page_config(page_title="Document Insight Agent", layout="wide")

EXAMPLES = [
    "Summarise the documents for a senior audience",
    "What are the key risks?",
    "List the actions and who owns them",
    "What deadlines or milestones are mentioned?",
    "What is the AI Safety Institute's mission?",
    "What does the CMA say about competition in foundation models?",
]

settings = get_settings()
if not settings.api_key:
    st.error("No API key found. Copy `.env.example` to `.env`, add your `ANTHROPIC_API_KEY`, then restart the app.")
    st.stop()


@st.cache_resource(show_spinner="Loading documents...")
def load_resources():
    llm = LLM(settings.api_key, settings.model, settings.fast_model)
    docs = load_folder(settings.data_dir)
    return llm, docs


try:
    llm, docs = load_resources()
except ValueError as exc:  # bad API key or empty data folder
    st.error(str(exc))
    st.stop()
if "agent" not in st.session_state:
    st.session_state.agent = Agent(llm, docs, settings.cache_dir)
    st.session_state.messages = []
agent: Agent = st.session_state.agent

# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.header("Documents")
    st.caption(f"{len(docs)} documents · ~{sum(d.word_count for d in docs):,} words")
    for d in docs:
        label = f"{d.title}" + ("  (!)" if d.notes else "")
        with st.expander(label):
            st.write(f"{d.file_type.upper()} · {d.word_count:,} words")
            for n in d.notes:
                st.warning(n)

    st.divider()
    prepared = is_prepared(llm.fast_model, docs, settings.cache_dir)
    st.write("Insight index: " + ("ready" if prepared else "not built yet"))
    if not prepared and st.button("Build insight index now"):
        bar = st.progress(0.0, text="Reading documents...")
        agent.tools.doc_insights(lambda done, total, title: bar.progress(done / total, text=f"Read {title}"))
        st.rerun()
    st.caption(f"Main model: `{llm.model}`  \nExtraction model: `{llm.fast_model}`")
    if st.button("Clear conversation"):
        st.session_state.agent = Agent(llm, docs, settings.cache_dir)
        st.session_state.messages = []
        st.rerun()

# ---------------------------------------------------------------- main
st.title("Document Insight Agent")
st.caption("Ask for a summary, risks, actions, deadlines, stakeholders, or any question about the documents.")


def show_assistant(msg: dict) -> None:
    for call in msg["calls"]:
        reason = call["args"].get("reason", "")
        st.caption(f"Routed to **{TOOL_LABELS[call['name']]}** · {reason} · _{msg['routed_by']}_")
    st.markdown(msg["markdown"])
    if msg["sources"]:
        with st.expander(f"Sources ({len(msg['sources'])})"):
            for s in msg["sources"]:
                st.write(f"- {s}")


for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        show_assistant(msg) if msg["role"] == "assistant" else st.markdown(msg["content"])

clicked = None
if not st.session_state.messages:
    cols = st.columns(3)
    for i, example in enumerate(EXAMPLES):
        if cols[i % 3].button(example, use_container_width=True):
            clicked = example

request = st.chat_input("Ask about the documents...") or clicked
if request:
    st.session_state.messages.append({"role": "user", "content": request})
    with st.chat_message("user"):
        st.markdown(request)
    with st.chat_message("assistant"):
        status = st.empty()
        bar_holder = st.empty()

        def progress(done, total, title):
            bar_holder.progress(done / total, text=f"First run only: reading documents ({done}/{total}) {title}")

        agent.tools.progress = progress
        with st.spinner("Thinking..."):
            resp = agent.run(request)
        bar_holder.empty()
        status.empty()
        msg = {
            "role": "assistant",
            "calls": [{"name": c.name, "args": c.args} for c in resp.calls],
            "routed_by": resp.routed_by,
            "markdown": resp.markdown,
            "sources": resp.sources,
        }
        show_assistant(msg)
    st.session_state.messages.append(msg)
