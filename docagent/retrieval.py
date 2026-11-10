"""Keyword search over chunks using BM25 (the ranking method classic search engines use).

Why BM25 rather than embeddings/vector search?
- No extra service or API key needed (Anthropic does not offer an embeddings API).
- Runs instantly on ~370 chunks, fully offline, easy to explain and debug.
- Policy documents use consistent terminology, so keyword matching works well.
Trade-off: it misses synonyms ("hazards" vs "risks"). The router mitigates this by
rewriting the user's question into a keyword-rich search query. See README "Improvements".
"""

from __future__ import annotations

import re

from rank_bm25 import BM25Okapi

from .ingest import Chunk

_STOPWORDS = set(
    """a an and are as at be by for from has have how i in is it its of on or that the this to was were what when
    where which who why will with do does did can could should would about into than then there these those our we
    you your they them their not no yes any all also more most other some such only own same so very just""".split()
)


def tokenize(text: str) -> list[str]:
    return [t for t in re.findall(r"[a-z0-9£]+", text.lower()) if t not in _STOPWORDS and len(t) > 1]


class SearchIndex:
    def __init__(self, chunks: list[Chunk]):
        self.chunks = chunks
        self._bm25 = BM25Okapi([tokenize(c.text + " " + c.title) for c in chunks])

    def search(self, query: str, k: int = 8, doc_ids: list[str] | None = None) -> list[tuple[Chunk, float]]:
        tokens = tokenize(query)
        if not tokens:
            return []
        scores = self._bm25.get_scores(tokens)
        ranked = sorted(zip(self.chunks, scores), key=lambda x: x[1], reverse=True)
        if doc_ids:
            ranked = [(c, s) for c, s in ranked if c.doc_id in doc_ids]
        return [(c, float(s)) for c, s in ranked[:k] if s > 0]
