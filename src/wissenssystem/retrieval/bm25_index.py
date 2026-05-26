"""Persistent per-namespace BM25 index for keyword-based retrieval."""

import pickle
import re
from pathlib import Path

from rank_bm25 import BM25Okapi


def _normalize(word: str) -> str:
    """Strip common German inflection suffixes for light stemming."""
    for suffix in ("en", "er", "em", "es", "e"):
        if word.endswith(suffix) and len(word) > len(suffix) + 2:
            return word[:-len(suffix)]
    return word


def _tokenize(text: str) -> list[str]:
    return [_normalize(w) for w in re.findall(r"\w+", text.lower())]


class BM25Index:
    """BM25Okapi index for a single namespace.

    Build from chunk texts during ingest, save to disk, load lazily at query time.
    """

    def __init__(self) -> None:
        self._bm25: BM25Okapi | None = None
        self._chunk_ids: list[str] = []

    # ── Build & persist ──────────────────────────────────────────────────────

    def build(self, texts: list[str], chunk_ids: list[str]) -> None:
        if len(texts) != len(chunk_ids):
            raise ValueError("texts and chunk_ids must have the same length")
        self._chunk_ids = list(chunk_ids)
        self._bm25 = BM25Okapi([_tokenize(t) for t in texts])

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("wb") as fh:
            pickle.dump({"bm25": self._bm25, "chunk_ids": self._chunk_ids}, fh)

    @classmethod
    def load(cls, path: Path) -> "BM25Index":
        instance = cls()
        with path.open("rb") as fh:
            data = pickle.load(fh)  # noqa: S301
        instance._bm25 = data["bm25"]
        instance._chunk_ids = data["chunk_ids"]
        return instance

    # ── Query ────────────────────────────────────────────────────────────────

    def search(self, query: str, top_k: int = 10) -> list[tuple[str, float]]:
        """Return (chunk_id, bm25_score) pairs, descending by score."""
        if self._bm25 is None or not self._chunk_ids:
            return []
        tokens = _tokenize(query)
        scores = self._bm25.get_scores(tokens)
        ranked = sorted(
            ((self._chunk_ids[i], float(s)) for i, s in enumerate(scores) if s > 0),
            key=lambda x: x[1],
            reverse=True,
        )
        return ranked[:top_k]

    def __len__(self) -> int:
        return len(self._chunk_ids)
