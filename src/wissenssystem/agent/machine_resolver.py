from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel

from wissenssystem.domain.machine import Machine
from wissenssystem.interfaces.llm_provider import LLMProvider, Message
from wissenssystem.registry.machine_registry import MachineRegistry

_PROMPT_PATH = Path(__file__).parent.parent.parent.parent / "prompts" / "machine_resolution.md"


def _load_prompt() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")


@dataclass(frozen=True)
class ResolveResult:
    machine: Machine | None
    confidence: float
    ambiguous: bool
    candidates: list[Machine]


class _LLMResult(BaseModel):
    machine_id: str | None
    confidence: float
    reasoning: str


class MachineResolver:
    """Resolves a user question to a specific machine.

    Three-stage resolution:
    1. Exact / prefix alias match in registry.
    2. Partial name match.
    3. LLM-based inference from question context (if provider given).

    Returns ResolveResult with ambiguous=True when multiple candidates exist
    and confidence stays below threshold.
    """

    def __init__(
        self,
        registry: MachineRegistry,
        llm_provider: LLMProvider | None = None,
        confidence_threshold: float = 0.75,
    ) -> None:
        self._registry = registry
        self._llm = llm_provider
        self._threshold = confidence_threshold

    def resolve(self, question: str) -> ResolveResult:
        machines = self._registry.list_machines()
        if not machines:
            return ResolveResult(machine=None, confidence=0.0, ambiguous=False, candidates=[])

        # Stage 1: alias prefix match
        words = question.lower().split()
        for length in range(min(5, len(words)), 0, -1):
            for start in range(len(words) - length + 1):
                phrase = " ".join(words[start : start + length])
                hits = self._registry.find_by_alias(phrase)
                if len(hits) == 1:
                    return ResolveResult(
                        machine=hits[0], confidence=0.95, ambiguous=False, candidates=hits
                    )
                if len(hits) > 1:
                    return ResolveResult(
                        machine=None, confidence=0.5, ambiguous=True, candidates=hits
                    )

        # Stage 2: partial name match
        for word in words:
            if len(word) < 3:
                continue
            hits = self._registry.find_by_name(word)
            if len(hits) == 1:
                return ResolveResult(
                    machine=hits[0], confidence=0.8, ambiguous=False, candidates=hits
                )

        # Stage 3: LLM inference
        if self._llm and len(machines) <= 5:
            return self._llm_resolve(question, machines)

        # Single machine in registry → assume it
        if len(machines) == 1:
            return ResolveResult(
                machine=machines[0], confidence=0.6, ambiguous=False, candidates=machines
            )

        return ResolveResult(machine=None, confidence=0.0, ambiguous=True, candidates=machines)

    def _llm_resolve(self, question: str, machines: list[Machine]) -> ResolveResult:
        machine_list = "\n".join(
            f"- id={m.machine_id} name={m.name!r} aliases={m.aliases}" for m in machines
        )
        user_content = f"Frage: {question}\n\nBekannte Maschinen:\n{machine_list}"

        result: _LLMResult = self._llm.complete_structured(
            system=_load_prompt(),
            messages=[Message(role="user", content=user_content)],
            schema=_LLMResult,
        )
        if result.machine_id is None:
            return ResolveResult(
                machine=None, confidence=result.confidence, ambiguous=True, candidates=machines
            )
        matched = next((m for m in machines if m.machine_id == result.machine_id), None)
        return ResolveResult(
            machine=matched,
            confidence=result.confidence,
            ambiguous=matched is None,
            candidates=machines,
        )
