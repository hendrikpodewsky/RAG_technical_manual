from pathlib import Path

from wissenssystem.interfaces.llm_provider import LLMProvider, LLMResponse, Message
from wissenssystem.retrieval.hybrid_search import SearchResult
from wissenssystem.retrieval.menu_path_search import MenuPathHit

_PROMPT_PATH = Path(__file__).parent.parent.parent.parent / "prompts" / "answer_generation.md"
_NO_INFO = "Mir liegt dazu keine Information vor."


def _load_prompt() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")


def _format_chunks(results: list[SearchResult]) -> str:
    parts = []
    for i, r in enumerate(results, start=1):
        text = r.payload.get("text") or r.payload.get("description", "")
        source = r.payload.get("source_ref", {})
        page = source.get("page", "?") if isinstance(source, dict) else "?"
        parts.append(f"[Passage {i} — Seite {page}]\n{text}")
    return "\n\n---\n\n".join(parts)


def _format_menu_paths(hits: list[MenuPathHit]) -> str:
    if not hits:
        return ""
    lines = [f"- {h.breadcrumb} (Seite {h.page})" for h in hits]
    return "Gefundene Menüpfade:\n" + "\n".join(lines)


class AnswerGenerator:
    """Generates a grounded answer from retrieved passages and menu paths."""

    def __init__(self, llm_provider: LLMProvider) -> None:
        self._llm = llm_provider

    def generate(
        self,
        question: str,
        results: list[SearchResult],
        menu_hits: list[MenuPathHit] | None = None,
    ) -> str:
        if not results and not menu_hits:
            return _NO_INFO

        chunks_text = _format_chunks(results)
        menu_text = _format_menu_paths(menu_hits or [])

        user_content = f"Frage: {question}\n\n"
        if chunks_text:
            user_content += f"Quellpassagen:\n{chunks_text}"
        if menu_text:
            user_content += f"\n\n{menu_text}"

        response: LLMResponse = self._llm.complete(
            system=_load_prompt(),
            messages=[Message(role="user", content=user_content)],
            temperature=0.0,
            max_tokens=1024,
        )
        return response.content.strip() or _NO_INFO
