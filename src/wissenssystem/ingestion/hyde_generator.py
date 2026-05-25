from pathlib import Path

from wissenssystem.interfaces.llm_provider import LLMProvider, Message

_PROMPT_PATH = Path(__file__).parent.parent.parent.parent / "prompts" / "hyde_generation.md"


class HydeGenerator:
    """Generates hypothetical questions for a text chunk at ingest time.

    At search time, the query embedding is compared against these question
    embeddings, which often matches user phrasing better than raw manual text.
    """

    def __init__(self, llm: LLMProvider, n_questions: int = 3) -> None:
        self._llm = llm
        self._n = n_questions

    def generate(self, text: str) -> list[str]:
        """Return up to n_questions German questions answerable by *text*."""
        if not text.strip():
            return []
        try:
            prompt = _PROMPT_PATH.read_text(encoding="utf-8")
            response = self._llm.complete(
                system=prompt,
                messages=[Message(role="user", content=text[:2000])],
                temperature=0.3,
                max_tokens=256,
            )
            lines = [ln.strip() for ln in response.content.splitlines()]
            questions = [ln for ln in lines if ln.endswith("?")]
            return questions[: self._n]
        except Exception:
            return []
