"""Small, local, file-based memory layer."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MEMORY = ROOT / "memory"


def _slug(value: str) -> str:
    value = re.sub(r"[^\w\-ก-๙ ]+", "", value, flags=re.UNICODE).strip().lower()
    return re.sub(r"\s+", "-", value)[:60] or "note"


def save_note(content: str, kind: str = "raw", title: str = "note") -> Path:
    if kind not in {"raw", "wiki", "outputs"}:
        raise ValueError("kind must be raw, wiki, or outputs")
    directory = MEMORY / kind
    directory.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    path = directory / f"{timestamp}-{_slug(title)}.md"
    text = f"# {title}\n\n_created: {datetime.now(timezone.utc).isoformat()}_\n\n{content.rstrip()}\n"
    path.write_text(text, encoding="utf-8")
    return path
