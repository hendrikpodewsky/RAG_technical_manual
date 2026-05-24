from dataclasses import dataclass
from typing import Any

from wissenssystem.interfaces.embedding_provider import EmbeddingProvider
from wissenssystem.interfaces.vector_store import VectorHit, VectorStore


@dataclass(frozen=True)
class SearchResult:
    """A ranked retrieval result from the vector store."""

    chunk_id: str
    score: float
    payload: dict[str, Any]
    chunk_type: str  # "text" | "image"


class HybridSearch:
    """Searches text chunks and image descriptions in a namespace.

    Both searches use the same query embedding. Results are merged and
    de-duplicated by chunk_id, keeping the higher score per id.
    If the namespace has an image sub-collection (<ns>__images), it is
    searched in parallel and results interleaved by score.
    """

    def __init__(
        self,
        vector_store: VectorStore,
        embedder: EmbeddingProvider,
        top_k: int = 10,
    ) -> None:
        self._store = vector_store
        self._embedder = embedder
        self._top_k = top_k

    def search(self, query: str, namespace: str) -> list[SearchResult]:
        """Return up to top_k results merged from text and image collections."""
        vector = self._embedder.embed_one(query)
        existing = set(self._store.list_namespaces())

        hits: dict[str, VectorHit] = {}

        # Text / main namespace
        if namespace in existing:
            for h in self._store.search(namespace, vector, top_k=self._top_k):
                hits[h.id] = h

        # Image descriptions sub-namespace (optional)
        image_ns = f"{namespace}__images"
        if image_ns in existing:
            for h in self._store.search(image_ns, vector, top_k=self._top_k):
                if h.id not in hits or h.score > hits[h.id].score:
                    hits[h.id] = h

        return sorted(
            [
                SearchResult(
                    chunk_id=h.id,
                    score=h.score,
                    payload=h.payload,
                    chunk_type=_infer_type(h.payload),
                )
                for h in hits.values()
            ],
            key=lambda r: r.score,
            reverse=True,
        )[: self._top_k]


def _infer_type(payload: dict[str, Any]) -> str:
    if "image_id" in payload:
        return "image"
    return "text"
