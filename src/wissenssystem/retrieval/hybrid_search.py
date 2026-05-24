from dataclasses import dataclass
from pathlib import Path
from typing import Any

from wissenssystem.interfaces.embedding_provider import EmbeddingProvider
from wissenssystem.interfaces.vector_store import VectorHit, VectorStore
from wissenssystem.retrieval.bm25_index import BM25Index

_RRF_K = 60  # standard constant for Reciprocal Rank Fusion


@dataclass(frozen=True)
class SearchResult:
    """A ranked retrieval result from the hybrid search."""

    chunk_id: str
    score: float
    payload: dict[str, Any]
    chunk_type: str  # "text" | "image"


class HybridSearch:
    """True hybrid search: dense vector + BM25 keyword, fused with RRF.

    Vector search covers semantic similarity; BM25 covers exact terms
    (error codes, model numbers, section headings). Results from both
    legs are merged via Reciprocal Rank Fusion so neither dominates.

    BM25 indices are loaded lazily per namespace from *bm25_dir* (a
    directory containing ``<namespace>.pkl`` files written by the
    IngestionPipeline).  If no BM25 index exists for a namespace the
    search degrades gracefully to vector-only.
    """

    def __init__(
        self,
        vector_store: VectorStore,
        embedder: EmbeddingProvider,
        top_k: int = 10,
        bm25_dir: Path | None = None,
    ) -> None:
        self._store = vector_store
        self._embedder = embedder
        self._top_k = top_k
        self._bm25_dir = bm25_dir
        self._bm25_cache: dict[str, BM25Index] = {}

    # ── Public API ────────────────────────────────────────────────────────────

    def search(self, query: str, namespace: str) -> list[SearchResult]:
        """Return up to top_k results fused from vector and BM25 searches."""
        vector = self._embedder.embed_one(query)
        existing = set(self._store.list_namespaces())

        # ── Vector leg ───────────────────────────────────────────────────────
        vector_hits: dict[str, VectorHit] = {}
        if namespace in existing:
            for h in self._store.search(namespace, vector, top_k=self._top_k * 2):
                vector_hits[h.id] = h

        image_ns = f"{namespace}__images"
        if image_ns in existing:
            for h in self._store.search(image_ns, vector, top_k=self._top_k):
                if h.id not in vector_hits or h.score > vector_hits[h.id].score:
                    vector_hits[h.id] = h

        # ── BM25 leg ─────────────────────────────────────────────────────────
        bm25_ranked: list[tuple[str, float]] = []
        bm25 = self._load_bm25(namespace)
        if bm25 is not None:
            bm25_ranked = bm25.search(query, top_k=self._top_k * 2)

        # ── RRF fusion ───────────────────────────────────────────────────────
        rrf_scores: dict[str, float] = {}

        for rank, (chunk_id, _) in enumerate(
            sorted(vector_hits.items(), key=lambda x: x[1].score, reverse=True)
        ):
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0.0) + _rrf(rank)

        for rank, (chunk_id, _) in enumerate(bm25_ranked):
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0.0) + _rrf(rank)

        # ── Build results ────────────────────────────────────────────────────
        # Payload comes from vector hits; BM25-only hits are skipped (no payload).
        results: list[SearchResult] = []
        for chunk_id, score in sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True):
            if chunk_id not in vector_hits:
                continue  # BM25-only hit: no payload available
            h = vector_hits[chunk_id]
            results.append(
                SearchResult(
                    chunk_id=chunk_id,
                    score=score,
                    payload=h.payload,
                    chunk_type=_infer_type(h.payload),
                )
            )

        return results[: self._top_k]

    # ── Internals ────────────────────────────────────────────────────────────

    def _load_bm25(self, namespace: str) -> BM25Index | None:
        if namespace in self._bm25_cache:
            return self._bm25_cache[namespace]
        if self._bm25_dir is None:
            return None
        path = self._bm25_dir / f"{namespace}.pkl"
        if not path.exists():
            return None
        index = BM25Index.load(path)
        self._bm25_cache[namespace] = index
        return index


def _rrf(rank: int, k: int = _RRF_K) -> float:
    return 1.0 / (k + rank + 1)


def _infer_type(payload: dict[str, Any]) -> str:
    return "image" if "image_id" in payload else "text"
