from dataclasses import dataclass
from pathlib import Path
from typing import Any

from wissenssystem.interfaces.embedding_provider import EmbeddingProvider
from wissenssystem.interfaces.llm_provider import LLMProvider, Message
from wissenssystem.interfaces.vector_store import VectorHit, VectorStore
from wissenssystem.retrieval.bm25_index import BM25Index

_HYDE_PROMPT_PATH = Path(__file__).parent.parent.parent.parent / "prompts" / "hyde_answer.md"


def _load_hyde_prompt() -> str:
    return _HYDE_PROMPT_PATH.read_text(encoding="utf-8")

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
        llm_provider: LLMProvider | None = None,
    ) -> None:
        self._store = vector_store
        self._embedder = embedder
        self._top_k = top_k
        self._bm25_dir = bm25_dir
        self._bm25_cache: dict[str, BM25Index] = {}
        self._llm = llm_provider

    # ── Public API ────────────────────────────────────────────────────────────

    def search(self, query: str, namespace: str) -> list[SearchResult]:
        """Return up to top_k results fused from vector and BM25 searches."""
        embed_text = self._hyde_expand(query) if self._llm else query
        vector = self._embedder.embed_one(embed_text)
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
        # Fetch payloads for chunks that BM25 found but vector search missed.
        bm25_only_ids = [cid for cid in rrf_scores if cid not in vector_hits]
        bm25_payloads: dict[str, VectorHit] = {}
        if bm25_only_ids and namespace in existing:
            for h in self._store.fetch_by_ids(namespace, bm25_only_ids):
                bm25_payloads[h.id] = h

        results: list[SearchResult] = []
        for chunk_id, score in sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True):
            if chunk_id in vector_hits:
                h = vector_hits[chunk_id]
            elif chunk_id in bm25_payloads:
                h = bm25_payloads[chunk_id]
            else:
                continue
            results.append(
                SearchResult(
                    chunk_id=chunk_id,
                    score=score,
                    payload=h.payload,
                    chunk_type=_infer_type(h.payload),
                )
            )

        return self._expand_to_parents(results[:self._top_k], namespace)

    # ── Internals ────────────────────────────────────────────────────────────

    def _expand_to_parents(
        self, results: list[SearchResult], namespace: str
    ) -> list[SearchResult]:
        """Replace child chunks with their parent when a parent_chunk_id exists.

        Multiple children of the same parent collapse into one parent entry,
        keeping the highest child score. Children without a parent pass through.
        """
        parent_ids_needed: dict[str, float] = {}  # parent_id → best child score
        passthrough: list[SearchResult] = []

        for r in results:
            pid = r.payload.get("parent_chunk_id")
            if pid:
                if pid not in parent_ids_needed or r.score > parent_ids_needed[pid]:
                    parent_ids_needed[pid] = r.score
            else:
                passthrough.append(r)

        if not parent_ids_needed:
            return results

        parent_hits = self._store.fetch_by_ids(namespace, list(parent_ids_needed.keys()))
        parent_map = {h.id: h for h in parent_hits}

        expanded: list[SearchResult] = list(passthrough)
        seen_parents: set[str] = set()
        seen_chunk_ids: set[str] = {r.chunk_id for r in results}
        for r in results:
            pid = r.payload.get("parent_chunk_id")
            if not pid:
                continue
            if pid in parent_map:
                # Parent found: collapse all children into one parent entry.
                if pid in seen_parents:
                    continue
                seen_parents.add(pid)
                ph = parent_map[pid]
                expanded.append(SearchResult(
                    chunk_id=pid,
                    score=parent_ids_needed[pid],
                    payload=ph.payload,
                    chunk_type=_infer_type(ph.payload),
                ))
            else:
                # Parent not indexed: keep this child and pull in any table
                # siblings that were not independently retrieved.
                expanded.append(r)
                if pid not in seen_parents:
                    seen_parents.add(pid)
                    for sibling in self._store.fetch_by_parent_id(namespace, pid):
                        if (
                            sibling.id not in seen_chunk_ids
                            and sibling.payload.get("chunk_type") == "table"
                        ):
                            seen_chunk_ids.add(sibling.id)
                            expanded.append(SearchResult(
                                chunk_id=sibling.id,
                                score=r.score,
                                payload=sibling.payload,
                                chunk_type="table",
                            ))

        return sorted(expanded, key=lambda x: x.score, reverse=True)[:self._top_k]

    def _hyde_expand(self, query: str) -> str:
        """Generate a hypothetical document passage for HyDE embedding."""
        try:
            response = self._llm.complete(
                system=_load_hyde_prompt(),
                messages=[Message(role="user", content=query)],
                temperature=0.0,
                max_tokens=256,
            )
            return response.content.strip() or query
        except Exception:  # noqa: BLE001
            return query

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
