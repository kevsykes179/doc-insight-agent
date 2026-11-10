"""Document ingestion: load PDFs and HTML pages, clean them, split into chunks.

Design notes
- File type is detected from the file's *content*, not its extension. The sample
  dataset contains "AI_Playbook_for_UK_Government.pdf", which is actually a saved
  HTML web page; trusting the extension would crash the PDF parser.
- HTML pages from GOV.UK and similar sites are mostly navigation, cookie banners
  and footers. We keep only the <main> content area and drop the clutter.
- PDFs keep their page numbers so answers can cite "Document, p.12".
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from bs4 import BeautifulSoup
from pypdf import PdfReader

SUPPORTED_SUFFIXES = {".pdf", ".html", ".htm", ".txt", ".md"}

# Elements that never contain document content.
_HTML_NOISE_TAGS = ["script", "style", "noscript", "nav", "header", "footer", "aside", "form", "svg", "button"]
# GOV.UK-style components that sit inside <main> but are not content.
_HTML_NOISE_SELECTORS = [
    ".govuk-breadcrumbs",
    ".gem-c-cookie-banner",
    ".gem-c-feedback",
    ".gem-c-contextual-sidebar",
    ".gem-c-related-navigation",
    ".gem-c-print-link",
    ".gem-c-share-links",
    ".gem-c-single-page-notification-button",
    ".govuk-skip-link",
    "[role=complementary]",
]


@dataclass
class Page:
    number: int | None  # PDF page number; None for web pages
    text: str


@dataclass
class Document:
    doc_id: str  # short stable id, e.g. "AI_Safety_Institute"
    title: str
    source_file: str
    file_type: str  # "pdf" | "html" | "text"
    pages: list[Page] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)  # ingestion warnings worth surfacing
    page_title: str = ""  # title embedded in the file itself, for reference

    @property
    def text(self) -> str:
        return "\n\n".join(p.text for p in self.pages if p.text)

    @property
    def word_count(self) -> int:
        return len(self.text.split())


@dataclass
class Chunk:
    chunk_id: str
    doc_id: str
    title: str
    page: int | None
    text: str

    @property
    def citation(self) -> str:
        return f"{self.title}, p.{self.page}" if self.page else self.title


# --------------------------------------------------------------------------- #
# Loading
# --------------------------------------------------------------------------- #

def detect_type(path: Path) -> str:
    """Sniff the first bytes of the file rather than trusting the extension."""
    head = path.read_bytes()[:2048]
    if head.startswith(b"%PDF"):
        return "pdf"
    lowered = head.lower()
    if b"<html" in lowered or b"<!doctype html" in lowered:
        return "html"
    return "text"


def _clean_whitespace(text: str) -> str:
    text = text.replace(" ", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip()


def _load_pdf(path: Path) -> tuple[str, list[Page]]:
    reader = PdfReader(str(path))
    pages = [Page(i + 1, _clean_whitespace(p.extract_text() or "")) for i, p in enumerate(reader.pages)]
    title = ""
    if reader.metadata and reader.metadata.title:
        title = str(reader.metadata.title).strip()
    return title, pages


def _load_html(path: Path) -> tuple[str, list[Page]]:
    soup = BeautifulSoup(path.read_text(encoding="utf-8", errors="ignore"), "lxml")

    title = ""
    h1 = soup.find("h1")
    if h1:
        title = h1.get_text(" ", strip=True)
    if not title and soup.title:
        title = soup.title.get_text(strip=True)

    mains = soup.find_all("main")
    root = mains[0] if mains else (soup.body or soup)
    for tag in root.find_all(_HTML_NOISE_TAGS):
        tag.decompose()
    for selector in _HTML_NOISE_SELECTORS:
        for tag in root.select(selector):
            tag.decompose()

    # Put block elements on their own lines so paragraphs survive.
    for block in root.find_all(["p", "li", "h1", "h2", "h3", "h4", "h5", "h6", "tr", "div", "br"]):
        block.insert_after("\n")
    text = _clean_whitespace(root.get_text(" "))
    text = "\n".join(line.strip() for line in text.split("\n"))
    return title, [Page(None, _clean_whitespace(text))]


def _pretty_title(path: Path) -> str:
    return path.stem.replace("_", " ").strip()


def load_document(path: Path) -> Document:
    file_type = detect_type(path)
    notes: list[str] = []
    if file_type == "pdf":
        title, pages = _load_pdf(path)
    elif file_type == "html":
        title, pages = _load_html(path)
    else:
        title, pages = "", [Page(None, _clean_whitespace(path.read_text(encoding="utf-8", errors="ignore")))]

    if path.suffix.lower() == ".pdf" and file_type != "pdf":
        notes.append(f"File has a .pdf extension but is actually {file_type.upper()}; parsed as {file_type}.")

    # Embedded titles are unreliable ("Full report", "AI", two pages both titled
    # "AI Opportunities Action Plan"), so the file name is used as the display title.
    doc = Document(path.stem, _pretty_title(path), path.name, file_type, pages, notes, page_title=title)
    if doc.word_count < 600:
        doc.notes.append(
            f"Short page (~{doc.word_count} words after cleaning): likely a landing or index page, not the full document."
        )
    return doc


def load_folder(folder: str | Path) -> list[Document]:
    folder = Path(folder)
    docs = []
    for path in sorted(folder.iterdir()):
        if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES:
            docs.append(load_document(path))
    if not docs:
        raise FileNotFoundError(f"No supported documents found in {folder}")
    return docs


# --------------------------------------------------------------------------- #
# Chunking
# --------------------------------------------------------------------------- #

def chunk_document(doc: Document, target_words: int = 350, overlap_words: int = 50) -> list[Chunk]:
    """Split a document into ~350-word chunks with a small overlap.

    Chunks never span PDF pages, so each chunk carries one page number for citation.
    """
    chunks: list[Chunk] = []
    for page in doc.pages:
        words = page.text.split()
        if not words:
            continue
        start = 0
        while start < len(words):
            end = min(start + target_words, len(words))
            text = " ".join(words[start:end])
            chunks.append(Chunk(f"{doc.doc_id}#{len(chunks)}", doc.doc_id, doc.title, page.number, text))
            if end == len(words):
                break
            start = end - overlap_words
    return chunks


def chunk_documents(docs: list[Document], **kwargs) -> list[Chunk]:
    return [c for d in docs for c in chunk_document(d, **kwargs)]
