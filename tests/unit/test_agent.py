from unittest.mock import MagicMock

import pytest
from pydantic import BaseModel

from wissenssystem.agent.answer_generator import _NO_INFO, AnswerGenerator
from wissenssystem.agent.intent_classifier import Intent, IntentClassifier
from wissenssystem.agent.machine_resolver import MachineResolver
from wissenssystem.agent.orchestrator import Orchestrator
from wissenssystem.domain.machine import Machine
from wissenssystem.interfaces.llm_provider import LLMResponse
from wissenssystem.registry.machine_registry import MachineRegistry
from wissenssystem.retrieval.hybrid_search import SearchResult

NS = "cfg__bosch__ui800__nf87-02__de"


# ============================================================
# Fixtures
# ============================================================


@pytest.fixture
def reg() -> MachineRegistry:
    r = MachineRegistry(":memory:")
    from wissenssystem.domain.machine import Configuration

    r.register_configuration(
        Configuration(
            namespace=NS,
            manufacturer="Bosch",
            model_family="UI 800",
            indoor_unit=None,
            outdoor_unit=None,
            software_version="NF87.02",
            country="DE",
        )
    )
    r.register_machine(
        Machine(
            machine_id="m1",
            name="Wärmepumpe Halle 2",
            aliases=["WP Halle 2", "die hintere Pumpe"],
            location="Halle 2",
            responsible="Technik",
            configuration_namespace=NS,
        )
    )
    return r


def _llm_result(**kwargs) -> MagicMock:
    mock = MagicMock()

    class _R(BaseModel):
        intent: str = "howto"
        confidence: float = 0.9
        reasoning: str = "test"
        machine_id: str | None = None
        ranking: list[int] = []

    for k, v in kwargs.items():
        setattr(_R, k, v)

    mock.complete_structured.return_value = _R(**{k: v for k, v in kwargs.items()})
    return mock


# ============================================================
# IntentClassifier
# ============================================================


def test_intent_classifier_howto():
    class _R(BaseModel):
        intent: str = "howto"
        confidence: float = 0.92
        reasoning: str = "Anleitung"

    mock_llm = MagicMock()
    mock_llm.complete_structured.return_value = _R()
    clf = IntentClassifier(mock_llm)
    result = clf.classify("Wie starte ich die Wärmepumpe?")
    assert result.intent == Intent.HOWTO
    assert result.confidence == 0.92


def test_intent_classifier_unknown_intent_maps_to_unclear():
    class _R(BaseModel):
        intent: str = "invented_intent"
        confidence: float = 0.5
        reasoning: str = "?"

    mock_llm = MagicMock()
    mock_llm.complete_structured.return_value = _R()
    clf = IntentClassifier(mock_llm)
    result = clf.classify("blaaa")
    assert result.intent == Intent.UNCLEAR


def test_intent_classifier_confidence_clamped():
    class _R(BaseModel):
        intent: str = "safety"
        confidence: float = 1.5  # out of range
        reasoning: str = ""

    mock_llm = MagicMock()
    mock_llm.complete_structured.return_value = _R()
    result = IntentClassifier(mock_llm).classify("Gefahr?")
    assert result.confidence <= 1.0


# ============================================================
# MachineResolver
# ============================================================


def test_resolver_alias_exact_match(reg):
    resolver = MachineResolver(reg)
    result = resolver.resolve("Was ist mit WP Halle 2 passiert?")
    assert result.machine is not None
    assert result.machine.machine_id == "m1"
    assert result.confidence >= 0.9
    assert not result.ambiguous


def test_resolver_partial_alias_match(reg):
    resolver = MachineResolver(reg)
    result = resolver.resolve("WP Halle kaputt")
    assert result.machine is not None


def test_resolver_no_match_single_machine(reg):
    resolver = MachineResolver(reg)
    result = resolver.resolve("Das Gerät macht komische Geräusche")
    # Only one machine in registry → assume it
    assert result.machine is not None
    assert result.confidence >= 0.5


def test_resolver_ambiguous_when_multiple_candidates():
    r = MachineRegistry(":memory:")
    from wissenssystem.domain.machine import Configuration

    for ns, name in [
        ("cfg__a__x__1__de", "Maschine Alpha"),
        ("cfg__b__y__1__de", "Maschine Beta"),
    ]:
        r.register_configuration(
            Configuration(
                namespace=ns,
                manufacturer="Test",
                model_family="M",
                indoor_unit=None,
                outdoor_unit=None,
                software_version=None,
                country="DE",
            )
        )
        r.register_machine(
            Machine(
                machine_id=ns,
                name=name,
                aliases=["Maschine"],
                location=None,
                responsible=None,
                configuration_namespace=ns,
            )
        )
    resolver = MachineResolver(r, confidence_threshold=0.75)
    result = resolver.resolve("Maschine läuft nicht")
    assert result.ambiguous


def test_resolver_empty_registry():
    r = MachineRegistry(":memory:")
    result = MachineResolver(r).resolve("irgendwas")
    assert result.machine is None
    assert result.confidence == 0.0


def test_resolver_llm_fallback_when_no_keyword(reg):
    class _R(BaseModel):
        machine_id: str | None = "m1"
        confidence: float = 0.8
        reasoning: str = "LLM matched"

    mock_llm = MagicMock()
    mock_llm.complete_structured.return_value = _R()
    resolver = MachineResolver(reg, llm_provider=mock_llm, confidence_threshold=0.75)
    result = resolver.resolve("Das Aggregat funktioniert nicht mehr")
    mock_llm.complete_structured.assert_called_once()
    assert result.machine is not None


# ============================================================
# AnswerGenerator
# ============================================================


def _search_result(chunk_id="c1", score=0.9, text="Sicherheitstext.") -> SearchResult:
    return SearchResult(
        chunk_id=chunk_id,
        score=score,
        payload={"text": text, "source_ref": {"page": 5, "section_path": ["3"]}},
        chunk_type="text",
    )


def test_answer_generator_returns_llm_response():
    mock_llm = MagicMock()
    mock_llm.complete.return_value = LLMResponse(
        content="Die Wärmepumpe startet durch Drücken von OK.",
        model="test",
        input_tokens=10,
        output_tokens=20,
    )
    gen = AnswerGenerator(mock_llm)
    answer = gen.generate("Wie starte ich?", [_search_result()])
    assert "Wärmepumpe" in answer


def test_answer_generator_no_results_returns_no_info():
    gen = AnswerGenerator(MagicMock())
    answer = gen.generate("Was ist X?", [])
    assert answer == _NO_INFO


def test_answer_generator_empty_llm_response_returns_no_info():
    mock_llm = MagicMock()
    mock_llm.complete.return_value = LLMResponse(
        content="   ", model="t", input_tokens=1, output_tokens=1
    )
    gen = AnswerGenerator(mock_llm)
    answer = gen.generate("q", [_search_result()])
    assert answer == _NO_INFO


# ============================================================
# Orchestrator
# ============================================================


def _mock_orchestrator(
    reg: MachineRegistry,
    intent_str: str = "howto",
    answer_text: str = "Hier ist die Antwort.",
) -> tuple[Orchestrator, MagicMock, MagicMock]:
    _intent_val = intent_str

    class _IntentR(BaseModel):
        intent: str = _intent_val
        confidence: float = 0.9
        reasoning: str = "ok"

    class _MachineR(BaseModel):
        machine_id: str | None = "m1"
        confidence: float = 0.85
        reasoning: str = "matched"

    intent_llm = MagicMock()
    intent_llm.complete_structured.return_value = _IntentR()

    answer_llm = MagicMock()
    answer_llm.complete.return_value = LLMResponse(
        content=answer_text, model="t", input_tokens=1, output_tokens=1
    )

    search = MagicMock()
    search.search.return_value = [_search_result()]

    orch = Orchestrator(
        intent_classifier=IntentClassifier(intent_llm),
        machine_resolver=MachineResolver(reg),
        hybrid_search=search,
        answer_generator=AnswerGenerator(answer_llm),
    )
    return orch, intent_llm, answer_llm


def test_orchestrator_happy_path(reg):
    orch, _, _ = _mock_orchestrator(reg)
    result = orch.answer("WP Halle 2 — wie Vorlauftemperatur ändern?")
    assert not result.needs_clarification
    assert result.machine_namespace == NS
    assert result.answer != ""


def test_orchestrator_no_machine_returns_clarification():
    r = MachineRegistry(":memory:")  # empty registry

    class _IntentR(BaseModel):
        intent: str = "howto"
        confidence: float = 0.9
        reasoning: str = ""

    intent_llm = MagicMock()
    intent_llm.complete_structured.return_value = _IntentR()

    orch = Orchestrator(
        intent_classifier=IntentClassifier(intent_llm),
        machine_resolver=MachineResolver(r),
        hybrid_search=MagicMock(),
        answer_generator=MagicMock(),
    )
    result = orch.answer("Das Gerät läuft nicht")
    assert result.needs_clarification or result.answer == "Mir liegt dazu keine Information vor."


def test_orchestrator_result_has_sources(reg):
    orch, _, _ = _mock_orchestrator(reg)
    result = orch.answer("WP Halle 2 — Fehlercode E5?")
    assert len(result.sources) >= 1
