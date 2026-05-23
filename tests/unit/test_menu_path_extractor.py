import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pydantic import BaseModel

from wissenssystem.ingestion.menu_path_extractor import MenuPathExtractor, _parse_item
from wissenssystem.interfaces.document_parser import ParsedBlock

NS = "cfg__test__model__1__de"

_SNAPSHOT_PATH = Path(__file__).parent / "fixtures" / "expected_menu_paths.json"


def _block(
    content: str,
    block_type: str = "text",
    page: int = 1,
    level: int | None = None,
    section_path: list[str] | None = None,
) -> ParsedBlock:
    return ParsedBlock(
        block_type=block_type,
        content=content,
        page=page,
        level=level,
        position=None,
        section_path=section_path or ["8"],
        image_data=None,
        image_media_type=None,
    )


# --- _parse_item ---


@pytest.mark.parametrize(
    "line,expected",
    [
        ("- Service", (0, "Service")),
        ("– Service", (0, "Service")),
        ("• Item", (0, "Item")),
        ("  – Anlageneinstellungen", (1, "Anlageneinstellungen")),
        ("    – Wärmepumpe", (2, "Wärmepumpe")),
        ("1. Erster Punkt", (0, "Erster Punkt")),
        ("1) Erster Punkt", (0, "Erster Punkt")),
    ],
)
def test_parse_item_detects_bullets(line, expected):
    assert _parse_item(line) == expected


def test_parse_item_returns_none_for_plain_text():
    assert _parse_item("Normaler Text ohne Bullet") is None


def test_parse_item_returns_none_for_empty():
    assert _parse_item("") is None


# --- flat list → single-level paths ---


def test_flat_list_produces_depth0_paths():
    extractor = MenuPathExtractor()
    blocks = [
        _block("- Alpha\n- Beta\n- Gamma"),
    ]
    paths = extractor.extract(blocks, NS)
    assert len(paths) == 3
    labels = [p.nodes[-1] for p in paths]
    assert labels == ["Alpha", "Beta", "Gamma"]
    assert all(len(p.nodes) == 1 for p in paths)


# --- nested list → correct ancestor chain ---


def test_nested_list_builds_ancestor_chain():
    extractor = MenuPathExtractor()
    blocks = [
        _block(
            "- Service\n"
            "  – Anlageneinstellungen\n"
            "    – Wärmepumpe\n"
            "      – Geräuscharmer Betrieb\n"
        )
    ]
    paths = extractor.extract(blocks, NS)
    leaf = next(p for p in paths if p.leaf_description == "Geräuscharmer Betrieb")
    assert leaf.nodes == ["Service", "Anlageneinstellungen", "Wärmepumpe", "Geräuscharmer Betrieb"]


def test_sibling_resets_stack_correctly():
    extractor = MenuPathExtractor()
    blocks = [
        _block(
            "- Service\n"
            "  – Untermenü A\n"
            "  – Untermenü B\n"
        )
    ]
    paths = extractor.extract(blocks, NS)
    b_path = next(p for p in paths if p.leaf_description == "Untermenü B")
    assert b_path.nodes == ["Service", "Untermenü B"]


# --- level field overrides heuristic depth ---


def test_level_field_overrides_heuristic():
    extractor = MenuPathExtractor()
    blocks = [
        _block("- Service", level=0),
        _block("- Anlageneinstellungen", level=1),
        _block("- Heizkreis", level=2),
    ]
    paths = extractor.extract(blocks, NS)
    deepest = next(p for p in paths if p.leaf_description == "Heizkreis")
    assert deepest.nodes == ["Service", "Anlageneinstellungen", "Heizkreis"]


# --- empty blocks → no paths ---


def test_empty_blocks_return_no_paths():
    extractor = MenuPathExtractor()
    assert extractor.extract([], NS) == []


def test_no_bullets_no_paths_without_llm():
    extractor = MenuPathExtractor()
    blocks = [_block("Das ist normaler Text ohne Listenpunkte.")]
    assert extractor.extract(blocks, NS) == []


# --- path IDs are unique ---


def test_path_ids_are_unique():
    extractor = MenuPathExtractor()
    blocks = [_block("- A\n- B\n- C\n  - D\n  - E")]
    paths = extractor.extract(blocks, NS)
    ids = [p.path_id for p in paths]
    assert len(ids) == len(set(ids))


# --- namespace is set on all paths ---


def test_namespace_on_all_paths():
    extractor = MenuPathExtractor()
    blocks = [_block("- X\n- Y")]
    paths = extractor.extract(blocks, NS)
    assert all(p.namespace == NS for p in paths)


# --- source_ref page is set ---


def test_source_ref_page():
    extractor = MenuPathExtractor()
    blocks = [_block("- Item", page=42)]
    paths = extractor.extract(blocks, NS)
    assert paths[0].source_ref.page == 42


# --- LLM fallback ---


def test_llm_called_when_no_heuristic_match():
    mock_llm = MagicMock()

    class _LLMPath(BaseModel):
        nodes: list[str]

    class _LLMResult(BaseModel):
        paths: list[_LLMPath]

    mock_llm.complete_structured.return_value = _LLMResult(
        paths=[
            _LLMPath(nodes=["Service", "Anlageneinstellungen", "Geräuscharmer Betrieb"])
        ]
    )

    extractor = MenuPathExtractor(llm_provider=mock_llm)
    blocks = [_block("Service  Anlageneinstellungen  Geräuscharmer Betrieb")]
    paths = extractor.extract(blocks, NS)
    mock_llm.complete_structured.assert_called_once()
    assert len(paths) == 1
    assert paths[0].nodes == ["Service", "Anlageneinstellungen", "Geräuscharmer Betrieb"]


def test_llm_not_called_when_heuristic_succeeds():
    mock_llm = MagicMock()
    extractor = MenuPathExtractor(llm_provider=mock_llm)
    blocks = [_block("- Service\n  – Einstellung")]
    extractor.extract(blocks, NS)
    mock_llm.complete_structured.assert_not_called()


# --- snapshot test ---


def _build_snapshot_blocks() -> list[ParsedBlock]:
    """Synthetic fixture that mirrors the UI-800 service menu structure."""
    content = (
        "- Service\n"
        "  – Anlageneinstellungen\n"
        "    – Wärmepumpe\n"
        "      – Geräuscharmer Betrieb\n"
        "      – Mindestlaufzeit Verdichter\n"
        "      – Abtauzyklus\n"
        "    – Heizkreis\n"
        "      – Heizkurve\n"
        "      – Raumtemperatur Soll\n"
        "  – Fehlerliste\n"
        "    – Aktuelle Fehler\n"
        "    – Fehlerhistorie\n"
    )
    return [_block(content, page=45, section_path=["8"])]


def test_snapshot(tmp_path):
    extractor = MenuPathExtractor()
    blocks = _build_snapshot_blocks()
    paths = extractor.extract(blocks, NS)

    snapshot_data = [{"path_id": p.path_id, "nodes": p.nodes} for p in paths]

    if not _SNAPSHOT_PATH.exists():
        _SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
        _SNAPSHOT_PATH.write_text(json.dumps(snapshot_data, ensure_ascii=False, indent=2))
        pytest.skip("Snapshot created — re-run to verify")

    expected = json.loads(_SNAPSHOT_PATH.read_text())
    assert snapshot_data == expected


def test_geraeuscharm_path_matches_spec():
    """Acceptance criterion: path to Geräuscharmer Betrieb matches TASKS.md spec."""
    extractor = MenuPathExtractor()
    blocks = _build_snapshot_blocks()
    paths = extractor.extract(blocks, NS)
    match = next((p for p in paths if p.leaf_description == "Geräuscharmer Betrieb"), None)
    assert match is not None
    assert match.nodes == [
        "Service",
        "Anlageneinstellungen",
        "Wärmepumpe",
        "Geräuscharmer Betrieb",
    ]
