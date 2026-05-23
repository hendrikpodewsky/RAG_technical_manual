import pytest

from wissenssystem.domain import (
    Configuration,
    ImageChunk,
    Machine,
    MenuNode,
    MenuPath,
    SafetyLevel,
    SafetyNotice,
    SourceDocument,
    SourceRef,
    TextChunk,
)

# --- SourceRef / SourceDocument ---


def test_source_ref_construction():
    ref = SourceRef(doc_id="abc", page=5, section_path=["5", "5.1"])
    assert ref.doc_id == "abc"
    assert ref.page == 5
    assert ref.section_path == ["5", "5.1"]


def test_source_document_construction(tmp_path):
    pdf = tmp_path / "manual.pdf"
    doc = SourceDocument(
        doc_id="d1",
        title="UI 800",
        publisher="Bosch",
        document_number="6721108192",
        edition="2026/02",
        software_version="NF87.02",
        country_codes=["DE", "AT"],
        pdf_path=pdf,
        config_namespace="cfg__bosch__ui800__nf87-02__de",
    )
    assert doc.publisher == "Bosch"
    assert "DE" in doc.country_codes


def test_source_document_optional_sw_version(tmp_path):
    pdf = tmp_path / "manual.pdf"
    doc = SourceDocument(
        doc_id="d2",
        title="Manual",
        publisher="X",
        document_number="123",
        edition="2026/01",
        software_version=None,
        country_codes=["DE"],
        pdf_path=pdf,
        config_namespace="cfg__x__model__none__de",
    )
    assert doc.software_version is None


# --- SafetyLevel / SafetyNotice ---


def test_safety_level_values():
    assert SafetyLevel.GEFAHR == "GEFAHR"
    assert SafetyLevel.WARNUNG == "WARNUNG"
    assert SafetyLevel.VORSICHT == "VORSICHT"
    assert SafetyLevel.ACHTUNG == "ACHTUNG"
    assert SafetyLevel.HINWEIS == "HINWEIS"


def test_safety_notice_construction():
    notice = SafetyNotice(level=SafetyLevel.WARNUNG, raw_text="Verbrühungsgefahr!")
    assert notice.level == SafetyLevel.WARNUNG
    assert "Verbrühung" in notice.raw_text


# --- TextChunk / ImageChunk ---


@pytest.fixture
def source_ref():
    return SourceRef(doc_id="d1", page=3, section_path=["4", "4.1"])


def test_text_chunk_construction(source_ref):
    chunk = TextChunk(
        chunk_id="c1",
        text="Wärmepumpe einschalten.",
        source_ref=source_ref,
        chunk_type="prose",
        safety_level=None,
        country_restriction=None,
        related_image_ids=[],
    )
    assert chunk.chunk_type == "prose"
    assert chunk.safety_level is None


def test_text_chunk_safety(source_ref):
    chunk = TextChunk(
        chunk_id="c2",
        text="WARNUNG: Verbrühungsgefahr.",
        source_ref=source_ref,
        chunk_type="safety_notice",
        safety_level=SafetyLevel.WARNUNG,
        country_restriction=None,
        related_image_ids=["img1"],
    )
    assert chunk.safety_level == SafetyLevel.WARNUNG
    assert "img1" in chunk.related_image_ids


def test_image_chunk_construction(source_ref):
    chunk = ImageChunk(
        chunk_id="ic1",
        image_id="sha256abc",
        description="Schaltplan des Kältekreises mit Kompressor und Verflüssiger.",
        caption="Bild 10  Übersicht Kältekreis",
        source_ref=source_ref,
        related_text_chunk_ids=["c1"],
    )
    assert chunk.image_id == "sha256abc"
    assert chunk.caption is not None


# --- Configuration / Machine ---


def test_configuration_construction():
    cfg = Configuration(
        namespace="cfg__bosch__ui800-9kw-r290__nf87-02__de",
        manufacturer="Bosch",
        model_family="UI 800",
        indoor_unit="UI800",
        outdoor_unit="OS9",
        software_version="NF87.02",
        country="DE",
    )
    assert cfg.country == "DE"
    assert cfg.namespace.startswith("cfg__")


def test_machine_construction():
    m = Machine(
        machine_id="m1",
        name="Wärmepumpe Halle 2",
        aliases=["WP Halle 2", "die hintere Pumpe"],
        location="Halle 2",
        responsible="Technik",
        configuration_namespace="cfg__bosch__ui800-9kw-r290__nf87-02__de",
    )
    assert "WP Halle 2" in m.aliases


# --- MenuPath / MenuNode ---


def test_menu_path_construction(source_ref):
    path = MenuPath(
        path_id="mp1",
        nodes=["Service", "Anlageneinstellungen", "Wärmepumpe", "Geräuscharmer Betrieb"],
        leaf_description="Aktiviert den geräuscharmen Nachtbetrieb.",
        source_ref=source_ref,
        namespace="cfg__bosch__ui800-9kw-r290__nf87-02__de",
    )
    assert path.nodes[-1] == "Geräuscharmer Betrieb"
    assert len(path.nodes) == 4


def test_menu_node_construction():
    node = MenuNode(label="Service", children=[MenuNode(label="Anlageneinstellungen")])
    assert node.label == "Service"
    assert node.children[0].label == "Anlageneinstellungen"


# --- Immutability ---


def test_source_ref_is_immutable():
    ref = SourceRef(doc_id="x", page=1, section_path=[])
    with pytest.raises(Exception):
        ref.page = 99  # type: ignore[misc]


def test_text_chunk_is_immutable(source_ref):
    chunk = TextChunk(
        chunk_id="c3",
        text="Test",
        source_ref=source_ref,
        chunk_type="prose",
        safety_level=None,
        country_restriction=None,
        related_image_ids=[],
    )
    with pytest.raises(Exception):
        chunk.text = "geändert"  # type: ignore[misc]


# --- Serialization ---


def test_source_ref_serialization():
    ref = SourceRef(doc_id="d1", page=2, section_path=["1", "1.1"])
    data = ref.model_dump()
    assert data["doc_id"] == "d1"
    assert data["page"] == 2


def test_text_chunk_json_roundtrip(source_ref):
    chunk = TextChunk(
        chunk_id="c4",
        text="Testtext",
        source_ref=source_ref,
        chunk_type="table",
        safety_level=SafetyLevel.HINWEIS,
        country_restriction=["DE"],
        related_image_ids=[],
    )
    json_str = chunk.model_dump_json()
    restored = TextChunk.model_validate_json(json_str)
    assert restored == chunk
