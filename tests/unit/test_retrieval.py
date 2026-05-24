from unittest.mock import MagicMock

from pydantic import BaseModel

from wissenssystem.interfaces.vector_store import VectorHit
from wissenssystem.retrieval.hybrid_search import HybridSearch, SearchResult, _infer_type
from wissenssystem.retrieval.menu_path_search import MenuPathSearch
from wissenssystem.retrieval.reranker import Reranker

NS = "cfg__test__model__1__de"
DIM = 4


def _hit(id: str, score: float, payload: dict | None = None) -> VectorHit:
    return VectorHit(id=id, score=score, payload=payload or {"text": f"text for {id}"})


def _mock_store(namespaces=None, search_results=None) -> MagicMock:
    store = MagicMock()
    store.list_namespaces.return_value = namespaces or [NS]
    store.search.return_value = search_results or []
    return store


def _mock_embedder() -> MagicMock:
    emb = MagicMock()
    emb.embed_one.return_value = [0.1, 0.2, 0.3, 0.4]
    return emb


# ============================================================
# HybridSearch
# ============================================================


def test_hybrid_search_returns_results():
    store = _mock_store(search_results=[_hit("c1", 0.9), _hit("c2", 0.7)])
    hs = HybridSearch(store, _mock_embedder(), top_k=5)
    results = hs.search("Verbrühungsgefahr", NS)
    assert len(results) == 2
    assert results[0].score == 0.9


def test_hybrid_search_deduplicates_by_id():
    # Same id returned from both namespaces
    store = _mock_store(
        namespaces=[NS, f"{NS}__images"],
        search_results=[_hit("c1", 0.9)],
    )
    hs = HybridSearch(store, _mock_embedder(), top_k=10)
    results = hs.search("query", NS)
    ids = [r.chunk_id for r in results]
    assert len(ids) == len(set(ids))


def test_hybrid_search_keeps_higher_score_on_dedup():
    text_hit = _hit("c1", 0.6, {"text": "A"})
    img_hit = _hit("c1", 0.95, {"image_id": "sha1", "description": "B"})

    call_count = [0]

    def _search(ns, vec, top_k):
        call_count[0] += 1
        if "__images" in ns:
            return [img_hit]
        return [text_hit]

    store = MagicMock()
    store.list_namespaces.return_value = [NS, f"{NS}__images"]
    store.search.side_effect = _search

    hs = HybridSearch(store, _mock_embedder(), top_k=10)
    results = hs.search("query", NS)
    assert len(results) == 1
    assert results[0].score == 0.95


def test_hybrid_search_missing_namespace_returns_empty():
    store = _mock_store(namespaces=["other"])
    hs = HybridSearch(store, _mock_embedder())
    assert hs.search("query", NS) == []


def test_hybrid_search_top_k_truncates():
    store = _mock_store(
        search_results=[_hit(f"c{i}", float(i) / 10) for i in range(20)]
    )
    hs = HybridSearch(store, _mock_embedder(), top_k=5)
    results = hs.search("query", NS)
    assert len(results) == 5


def test_infer_type_image():
    assert _infer_type({"image_id": "abc", "description": "X"}) == "image"


def test_infer_type_text():
    assert _infer_type({"text": "foo"}) == "text"


# ============================================================
# MenuPathSearch
# ============================================================


def test_menu_path_search_returns_hits():
    menu_ns = f"{NS}__menupaths"
    store = _mock_store(
        namespaces=[menu_ns],
        search_results=[
            _hit(
                "p1",
                0.88,
                {
                    "path_id": "p1",
                    "nodes": ["Service", "Geräuscharmer Betrieb"],
                    "leaf_description": "Geräuscharmer Betrieb",
                    "source_ref": {"page": 45, "section_path": ["8"]},
                },
            )
        ],
    )
    mps = MenuPathSearch(store, _mock_embedder(), top_k=3)
    hits = mps.search("geräuscharmer Betrieb einstellen", NS)
    assert len(hits) == 1
    assert hits[0].breadcrumb == "Service > Geräuscharmer Betrieb"
    assert hits[0].page == 45


def test_menu_path_search_missing_namespace_returns_empty():
    store = _mock_store(namespaces=[NS])
    mps = MenuPathSearch(store, _mock_embedder())
    assert mps.search("query", NS) == []


# ============================================================
# Reranker
# ============================================================


def _result(chunk_id: str, score: float, text: str = "Text.") -> SearchResult:
    return SearchResult(
        chunk_id=chunk_id,
        score=score,
        payload={"text": text},
        chunk_type="text",
    )


def test_reranker_no_llm_sorts_by_score():
    reranker = Reranker()
    results = [_result("c1", 0.5), _result("c2", 0.9), _result("c3", 0.7)]
    ranked = reranker.rerank("query", results)
    assert [r.chunk_id for r in ranked] == ["c2", "c3", "c1"]


def test_reranker_empty_input():
    assert Reranker().rerank("q", []) == []


def test_reranker_single_result_no_llm_call():
    mock_llm = MagicMock()
    reranker = Reranker(llm_provider=mock_llm)
    result = [_result("c1", 0.9)]
    reranker.rerank("q", result)
    mock_llm.complete_structured.assert_not_called()


def test_reranker_llm_reorders():
    class _RankResult(BaseModel):
        ranking: list[int]

    mock_llm = MagicMock()
    mock_llm.complete_structured.return_value = _RankResult(ranking=[2, 0, 1])

    reranker = Reranker(llm_provider=mock_llm)
    results = [_result("c1", 0.9), _result("c2", 0.7), _result("c3", 0.5)]
    ranked = reranker.rerank("safety question", results)
    assert [r.chunk_id for r in ranked] == ["c3", "c1", "c2"]


def test_reranker_llm_invalid_ranking_falls_back():
    class _RankResult(BaseModel):
        ranking: list[int]

    mock_llm = MagicMock()
    mock_llm.complete_structured.return_value = _RankResult(ranking=[0, 1])  # wrong length

    reranker = Reranker(llm_provider=mock_llm)
    results = [_result("c1", 0.9), _result("c2", 0.7), _result("c3", 0.5)]
    ranked = reranker.rerank("q", results)
    assert ranked[0].chunk_id == "c1"  # fallback to score order


def test_reranker_llm_exception_falls_back():
    mock_llm = MagicMock()
    mock_llm.complete_structured.side_effect = RuntimeError("LLM down")

    reranker = Reranker(llm_provider=mock_llm)
    results = [_result("c1", 0.5), _result("c2", 0.9)]
    ranked = reranker.rerank("q", results)
    assert ranked[0].chunk_id == "c2"
