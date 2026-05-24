"""Unit tests for BM25Index."""

import pytest

from wissenssystem.retrieval.bm25_index import BM25Index

TEXTS = [
    "GEFAHR Hochspannung beim Öffnen des Geräts",
    "Warmwasser Solltemperatur einstellen im Menü",
    "Kältemittel R410A maximaler Betriebsdruck 42 bar",
    "Geräuscharmer Betrieb Service Anlageneinstellungen Wärmepumpe",
    "Frostschutz Außeneinheit Winterbetrieb",
]
IDS = [f"chunk_{i}" for i in range(len(TEXTS))]


@pytest.fixture
def index() -> BM25Index:
    idx = BM25Index()
    idx.build(TEXTS, IDS)
    return idx


def test_build_and_len(index):
    assert len(index) == 5


def test_exact_keyword_top_hit(index):
    results = index.search("Hochspannung", top_k=3)
    assert results, "expected at least one result"
    assert results[0][0] == "chunk_0"


def test_error_code_lookup(index):
    results = index.search("42 bar Druck", top_k=3)
    top_ids = [r[0] for r in results]
    assert "chunk_2" in top_ids


def test_no_match_returns_empty(index):
    results = index.search("WLAN Verbindung App", top_k=5)
    assert results == []


def test_top_k_respected(index):
    results = index.search("Betrieb", top_k=2)
    assert len(results) <= 2


def test_scores_descending(index):
    results = index.search("Wärmepumpe", top_k=5)
    scores = [s for _, s in results]
    assert scores == sorted(scores, reverse=True)


def test_save_and_load_roundtrip(index, tmp_path):
    path = tmp_path / "test_ns.pkl"
    index.save(path)

    loaded = BM25Index.load(path)
    assert len(loaded) == len(index)

    original = index.search("Hochspannung", top_k=1)
    restored = loaded.search("Hochspannung", top_k=1)
    assert original == restored


def test_build_mismatched_lengths_raises():
    idx = BM25Index()
    with pytest.raises(ValueError, match="same length"):
        idx.build(["text1", "text2"], ["id1"])


def test_search_on_empty_index_returns_empty():
    idx = BM25Index()
    assert idx.search("anything") == []
