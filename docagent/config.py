"""Configuration. Secrets come from environment variables or a local .env file (never committed)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


@dataclass
class Settings:
    api_key: str | None
    model: str | None  # main model (routing, answers, summaries); None = auto-detect newest Sonnet
    fast_model: str | None  # cheap model for bulk per-document extraction; None = auto-detect newest Haiku
    data_dir: Path
    cache_dir: Path


def get_settings() -> Settings:
    return Settings(
        api_key=os.getenv("ANTHROPIC_API_KEY") or None,
        model=os.getenv("ANTHROPIC_MODEL") or None,
        fast_model=os.getenv("ANTHROPIC_FAST_MODEL") or None,
        data_dir=Path(os.getenv("DATA_DIR") or PROJECT_ROOT / "data"),
        cache_dir=Path(os.getenv("CACHE_DIR") or PROJECT_ROOT / ".cache"),
    )
