from unittest.mock import MagicMock

import pytest

from wissenssystem.domain.safety import SafetyLevel
from wissenssystem.ingestion.safety_detector import (
    SafetyDetector,
    _needs_secondary_check,
    detect_from_text,
)
from wissenssystem.interfaces.document_parser import ParsedBlock


def _block(text: str) -> ParsedBlock:
    return ParsedBlock(
        block_type="text",
        content=text,
        page=1,
        level=None,
        position=None,
        section_path=["4"],
        image_data=None,
        image_media_type=None,
    )


# --- detect_from_text (regex stage) ---


@pytest.mark.parametrize(
    "text,expected_level",
    [
        ("GEFAHR: Lebensgefährliche Spannung.", SafetyLevel.GEFAHR),
        ("WARNUNG! Verbrühungsgefahr durch heißes Wasser.", SafetyLevel.WARNUNG),
        ("VORSICHT: Frostschäden möglich.", SafetyLevel.VORSICHT),
        ("ACHTUNG: Gerät nicht kippen.", SafetyLevel.ACHTUNG),
        ("HINWEIS: Vor Inbetriebnahme lesen.", SafetyLevel.HINWEIS),
        ("gefahr: Stromschlaggefahr.", SafetyLevel.GEFAHR),  # case-insensitive
        ("Warnung vor Überhitzung.", SafetyLevel.WARNUNG),
    ],
)
def test_detect_from_text_explicit_keywords(text, expected_level):
    notice = detect_from_text(text)
    assert notice is not None
    assert notice.level == expected_level
    assert notice.raw_text == text


def test_detect_from_text_no_keyword():
    assert detect_from_text("Das Gerät einschalten und Temperatur prüfen.") is None


def test_detect_from_text_returns_first_keyword():
    notice = detect_from_text("WARNUNG: Gefahr durch Überhitzung.")
    assert notice is not None
    assert notice.level == SafetyLevel.WARNUNG


# --- _needs_secondary_check ---


def test_needs_secondary_check_with_trigger_no_keyword():
    assert _needs_secondary_check("Bei Verbrühung sofort kaltes Wasser auftragen.") is True


def test_needs_secondary_check_with_keyword_and_trigger():
    assert _needs_secondary_check("WARNUNG: Verbrühungsgefahr.") is False


def test_needs_secondary_check_no_trigger():
    assert _needs_secondary_check("Betriebsdruck 3 bar.") is False


# --- SafetyDetector.detect ---


def test_detector_regex_match():
    detector = SafetyDetector()
    notice = detector.detect(_block("WARNUNG: Verbrühungsgefahr durch Warmwasser!"))
    assert notice is not None
    assert notice.level == SafetyLevel.WARNUNG


def test_detector_no_match_no_llm():
    detector = SafetyDetector()
    assert detector.detect(_block("Nennspannung: 230 V")) is None


def test_detector_calls_llm_for_secondary_trigger():
    mock_llm = MagicMock()
    from pydantic import BaseModel

    class LLMResult(BaseModel):
        is_safety: bool
        level: str | None = None

    mock_llm.complete_structured.return_value = LLMResult(is_safety=True, level="VORSICHT")

    detector = SafetyDetector(llm_provider=mock_llm)
    notice = detector.detect(_block("Bei Verbrühung sofort kaltes Wasser."))
    assert notice is not None
    assert notice.level == SafetyLevel.VORSICHT
    mock_llm.complete_structured.assert_called_once()


def test_detector_llm_returns_no_safety():
    mock_llm = MagicMock()
    from pydantic import BaseModel

    class LLMResult(BaseModel):
        is_safety: bool
        level: str | None = None

    mock_llm.complete_structured.return_value = LLMResult(is_safety=False)

    detector = SafetyDetector(llm_provider=mock_llm)
    assert detector.detect(_block("Stromverbrauch: 2,1 kW")) is None


def test_detector_no_llm_skips_secondary():
    detector = SafetyDetector(llm_provider=None)
    result = detector.detect(_block("Verbrühungsgefahr bei Warmwasser."))
    assert result is None


# --- SafetyDetector.detect_all ---


def test_detect_all_returns_only_matches():
    detector = SafetyDetector()
    blocks = [
        _block("Normaler Text."),
        _block("GEFAHR: Hochspannung!"),
        _block("Noch mehr normaler Text."),
        _block("WARNUNG: Verbrühungsgefahr."),
    ]
    results = detector.detect_all(blocks)
    assert len(results) == 2
    assert results[0][1].level == SafetyLevel.GEFAHR
    assert results[1][1].level == SafetyLevel.WARNUNG


# --- Simulated UI 800 Kapitel 4 fixtures ---


UI800_SAFETY_BLOCKS = [
    "WARNUNG! Verbrühungsgefahr. Das Warmwasser kann sehr heiß sein.",
    "VORSICHT: Fußbodenschäden durch Kondenswasser möglich.",
    "GEFAHR: Lebensgefährliche elektrische Spannung im Inneren des Geräts.",
    "ACHTUNG: Gerät nicht mit Hochdruckreiniger reinigen.",
]


@pytest.mark.parametrize("text", UI800_SAFETY_BLOCKS)
def test_ui800_fixture_blocks_detected(text):
    notice = detect_from_text(text)
    assert notice is not None, f"Nicht erkannt: {text!r}"
    assert notice.level in SafetyLevel.__members__.values()
