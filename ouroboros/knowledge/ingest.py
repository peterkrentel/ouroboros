from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Chunk:
    source: str
    text: str


def chunk_text(text: str, source: str, chunk_size: int = 600) -> list[Chunk]:
    """Split text into fixed-size chunks for downstream indexing."""
    stripped = " ".join(text.split())
    if not stripped:
        return []
    return [
        Chunk(source=source, text=stripped[i : i + chunk_size])
        for i in range(0, len(stripped), chunk_size)
    ]
