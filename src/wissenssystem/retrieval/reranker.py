from pathlib import Path

from pydantic import BaseModel

from wissenssystem.interfaces.llm_provider import LLMProvider, Message
from wissenssystem.retrieval.hybrid_search import SearchResult

_PROMPT_PATH = Path(__file__).parent.parent.parent.parent / "prompts" / "reranker.md"
_MAX_CHARS_PER_CHUNK = 800


def _load_prompt() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")


class _RankResult(BaseModel):
    ranking: list[int]


class Reranker:
    """LLM-based reranker for retrieval results.

    Falls back to the original score order when no LLM is available or the
    LLM returns an invalid ranking.
    """

    def __init__(self, llm_provider: LLMProvider | None = None) -> None:
        self._llm = llm_provider

    def rerank(self, query: str, results: list[SearchResult]) -> list[SearchResult]:
        """Return results sorted by relevance to query.

        If LLM is not available, returns results sorted by original score.
        """
        if not results:
            return results
        if self._llm is None or len(results) == 1:
            return sorted(results, key=lambda r: r.score, reverse=True)
        try:
            return self._llm_rerank(query, results)
        except Exception:  # noqa: BLE001
            return sorted(results, key=lambda r: r.score, reverse=True)

    def _llm_rerank(self, query: str, results: list[SearchResult]) -> list[SearchResult]:
        passages = "\n\n".join(
            f"[{i}] {_excerpt(r)}" for i, r in enumerate(results)
        )
        user_message = f"Frage: {query}\n\nPassagen:\n{passages}"

        response: _RankResult = self._llm.complete_structured(
            system=_load_prompt(),
            messages=[Message(role="user", content=user_message)],
            schema=_RankResult,
        )

        ranking = response.ranking
        # Validate: must be a permutation of 0..n-1
        if sorted(ranking) != list(range(len(results))):
            return sorted(results, key=lambda r: r.score, reverse=True)

        return [results[i] for i in ranking]


def _excerpt(result: SearchResult) -> str:
    text = result.payload.get("text") or result.payload.get("description", "")
    return text[:_MAX_CHARS_PER_CHUNK]
