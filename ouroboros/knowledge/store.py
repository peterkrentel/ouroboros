from __future__ import annotations

from dataclasses import dataclass

from ouroboros.knowledge.ingest import Chunk


@dataclass
class RetrievedChunk:
    source: str
    text: str
    score: int


class InMemoryKnowledgeStore:
    """Simple lexical retrieval store used as a local development default."""

    def __init__(self) -> None:
        self._chunks: list[Chunk] = []

    def add_chunks(self, chunks: list[Chunk]) -> int:
        self._chunks.extend(chunks)
        return len(chunks)

    def retrieve(self, query: str, top_k: int = 3) -> list[RetrievedChunk]:
        terms = [term for term in query.lower().split() if term]
        if not terms:
            return []

        ranked: list[RetrievedChunk] = []
        for chunk in self._chunks:
            score = sum(chunk.text.lower().count(term) for term in terms)
            if score > 0:
                ranked.append(RetrievedChunk(source=chunk.source, text=chunk.text, score=score))

        ranked.sort(key=lambda item: item.score, reverse=True)
        return ranked[:top_k]

    def size(self) -> int:
        return len(self._chunks)
