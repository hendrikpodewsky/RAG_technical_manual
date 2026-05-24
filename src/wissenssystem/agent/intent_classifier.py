from enum import Enum
from pathlib import Path

from pydantic import BaseModel

from wissenssystem.interfaces.llm_provider import LLMProvider, Message

_PROMPT_PATH = Path(__file__).parent.parent.parent.parent / "prompts" / "intent_classification.md"


def _load_prompt() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")


class Intent(str, Enum):
    TROUBLESHOOT = "troubleshoot"
    HOWTO = "howto"
    LOOKUP = "lookup"
    MENU_NAVIGATION = "menu_navigation"
    SAFETY = "safety"
    UNCLEAR = "unclear"


class IntentResult(BaseModel):
    intent: Intent
    confidence: float
    reasoning: str


class _LLMResult(BaseModel):
    intent: str
    confidence: float
    reasoning: str


class IntentClassifier:
    """Classifies a user question into one of the Intent categories."""

    def __init__(self, llm_provider: LLMProvider) -> None:
        self._llm = llm_provider

    def classify(self, question: str) -> IntentResult:
        result: _LLMResult = self._llm.complete_structured(
            system=_load_prompt(),
            messages=[Message(role="user", content=question)],
            schema=_LLMResult,
        )
        try:
            intent = Intent(result.intent.lower())
        except ValueError:
            intent = Intent.UNCLEAR
        return IntentResult(
            intent=intent,
            confidence=max(0.0, min(1.0, result.confidence)),
            reasoning=result.reasoning,
        )
