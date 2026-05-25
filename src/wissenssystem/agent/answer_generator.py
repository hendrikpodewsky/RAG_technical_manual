from pathlib import Path

from wissenssystem.interfaces.llm_provider import LLMProvider, LLMResponse, Message
from wissenssystem.retrieval.hybrid_search import SearchResult
from wissenssystem.retrieval.menu_path_search import MenuPathHit

_PROMPT_PATH = Path(__file__).parent.parent.parent.parent / "prompts" / "answer_generation.md"
_NO_INFO = "Mir liegt dazu keine Information vor."
_NO_INFO_LOWER = _NO_INFO.lower()

# Phrases small models use when admitting they lack the information but still
# generating surrounding text — treat the whole answer as no-info.
_ADMISSION_PHRASES = (
    "keine spezifischen anweisungen",
    "nicht erwähnt, wie",
    "nicht beschrieben, wie",
    "empfehle ich, sich an den hersteller",
    "wenden sie sich an den hersteller",
    "wenden sie sich direkt an",
    "empfehlenswert, sich direkt an",
)


def _strip_trailing_no_info(answer: str) -> str:
    """Remove trailing no-info disclaimers that small models append after real content."""
    stripped = answer.strip()
    lower = stripped.lower()
    # If the model admits it lacks the info but wraps it in filler text, collapse to no-info
    if any(phrase in lower for phrase in _ADMISSION_PHRASES):
        return _NO_INFO
    idx = lower.rfind(_NO_INFO_LOWER)
    if idx <= 0:
        return stripped
    # Only strip if there is substantive content before the phrase
    prefix = stripped[:idx].strip()
    return prefix if prefix else stripped


def _load_prompt() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")


def _format_chunks(results: list[SearchResult]) -> str:
    parts = []
    for i, r in enumerate(results, start=1):
        text = r.payload.get("text") or r.payload.get("description", "")
        source = r.payload.get("source_ref", {})
        page = source.get("page", "?") if isinstance(source, dict) else "?"
        section_title = r.payload.get("section_title")
        header = f"Passage {i} — Seite {page}"
        if section_title:
            header += f" — Abschnitt: {section_title}"
        parts.append(f"[{header}]\n{text}")
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
        answer = response.content.strip() or _NO_INFO
        return _strip_trailing_no_info(answer)
