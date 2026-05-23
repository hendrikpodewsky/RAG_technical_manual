import re
from pathlib import Path

from pydantic import BaseModel

from wissenssystem.domain.safety import SafetyLevel, SafetyNotice
from wissenssystem.interfaces.document_parser import ParsedBlock
from wissenssystem.interfaces.llm_provider import LLMProvider, Message

_KEYWORD_RE = re.compile(
    r"(?<!\w)(GEFAHR|WARNUNG|VORSICHT|ACHTUNG|HINWEIS)(?!\w)",
    re.IGNORECASE,
)

_LEVEL_MAP: dict[str, SafetyLevel] = {
    "GEFAHR": SafetyLevel.GEFAHR,
    "WARNUNG": SafetyLevel.WARNUNG,
    "VORSICHT": SafetyLevel.VORSICHT,
    "ACHTUNG": SafetyLevel.ACHTUNG,
    "HINWEIS": SafetyLevel.HINWEIS,
}

_SECONDARY_TRIGGERS = re.compile(
    r"(Verbrühung|Verbrennung|Stromschlag|Elektroschlag|Explosion|Brand"
    r"|Vergiftung|Erstickung|Lebensgefahr|tödlich|Verletzung"
    r"|Überdruck|Frostschaden|Kurzschluss)",
    re.IGNORECASE,
)

_PROMPT_PATH = Path(__file__).parent.parent.parent.parent / "prompts" / "safety_check.md"


def _load_prompt() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")


class _LLMResult(BaseModel):
    is_safety: bool
    level: str | None = None


def detect_from_text(text: str) -> SafetyNotice | None:
    """First-pass regex detection of explicit safety keywords."""
    match = _KEYWORD_RE.search(text)
    if not match:
        return None
    level = _LEVEL_MAP[match.group(1).upper()]
    return SafetyNotice(level=level, raw_text=text)


def _needs_secondary_check(text: str) -> bool:
    """True if text has secondary safety triggers but no explicit keyword."""
    has_keyword = bool(_KEYWORD_RE.search(text))
    has_trigger = bool(_SECONDARY_TRIGGERS.search(text))
    return has_trigger and not has_keyword


def _llm_check(text: str, llm: LLMProvider) -> SafetyNotice | None:
    """Second-pass LLM check for ambiguous blocks."""
    prompt = _load_prompt()
    response = llm.complete_structured(
        system=prompt,
        messages=[Message(role="user", content=text)],
        schema=_LLMResult,
    )
    if not response.is_safety or not response.level:
        return None
    level = _LEVEL_MAP.get(response.level.upper())
    if not level:
        return None
    return SafetyNotice(level=level, raw_text=text)


class SafetyDetector:
    """Detects safety notices in parsed document blocks.

    Stage 1: regex match on GEFAHR/WARNUNG/VORSICHT/ACHTUNG/HINWEIS.
    Stage 2: optional LLM check for blocks with safety-relevant vocabulary
             but no explicit keyword.
    """

    def __init__(self, llm_provider: LLMProvider | None = None) -> None:
        self._llm = llm_provider

    def detect(self, block: ParsedBlock) -> SafetyNotice | None:
        text = block.content
        notice = detect_from_text(text)
        if notice:
            return notice
        if self._llm and _needs_secondary_check(text):
            return _llm_check(text, self._llm)
        return None

    def detect_all(self, blocks: list[ParsedBlock]) -> list[tuple[ParsedBlock, SafetyNotice]]:
        """Return (block, notice) pairs for all blocks with safety content."""
        results = []
        for block in blocks:
            notice = self.detect(block)
            if notice:
                results.append((block, notice))
        return results
