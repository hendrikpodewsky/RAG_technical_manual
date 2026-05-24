import pytest
from qdrant_client import QdrantClient

from wissenssystem.interfaces.vector_store import VectorItem, VectorStore
from wissenssystem.providers.qdrant_store import QdrantVectorStore, _stable_id

NS = "test_namespace"
DIM = 4


@pytest.fixture
def store() -> QdrantVectorStore:
    return QdrantVectorStore(QdrantClient(":memory:"))


def _item(chunk_id: str, vector: list[float] | None = None) -> VectorItem:
    return VectorItem(
        id=chunk_id,
        vector=vector or [0.1, 0.2, 0.3, 0.4],
        payload={"chunk_id": chunk_id, "text": "Beispieltext"},
    )


# --- protocol compliance ---


def test_implements_vector_store_protocol():
    assert isinstance(QdrantVectorStore(QdrantClient(":memory:")), VectorStore)


# --- create / delete ---


def test_create_and_list_namespace(store):
    store.create_namespace(NS, DIM)
    assert NS in store.list_namespaces()


def test_delete_namespace(store):
    store.create_namespace(NS, DIM)
    store.delete_namespace(NS)
    assert NS not in store.list_namespaces()


def test_list_namespaces_empty(store):
    assert store.list_namespaces() == []


# --- upsert / search ---


def test_upsert_and_search(store):
    store.create_namespace(NS, DIM)
    store.upsert(NS, [_item("c1", [1.0, 0.0, 0.0, 0.0])])
    results = store.search(NS, [1.0, 0.0, 0.0, 0.0], top_k=5)
    assert len(results) >= 1
    assert results[0].score > 0.9


def test_search_returns_payload(store):
    store.create_namespace(NS, DIM)
    store.upsert(NS, [_item("c1")])
    results = store.search(NS, [0.1, 0.2, 0.3, 0.4], top_k=1)
    assert results[0].payload["chunk_id"] == "c1"


def test_upsert_is_idempotent(store):
    store.create_namespace(NS, DIM)
    store.upsert(NS, [_item("c1")])
    store.upsert(NS, [_item("c1")])  # same id, should replace
    results = store.search(NS, [0.1, 0.2, 0.3, 0.4], top_k=10)
    assert len(results) == 1


def test_top_k_respected(store):
    store.create_namespace(NS, DIM)
    store.upsert(NS, [_item(f"c{i}", [float(i), 0.0, 0.0, 0.0]) for i in range(10)])
    results = store.search(NS, [1.0, 0.0, 0.0, 0.0], top_k=3)
    assert len(results) == 3


# --- _stable_id ---


def test_stable_id_deterministic():
    assert _stable_id("abc") == _stable_id("abc")


def test_stable_id_non_negative():
    for s in ["", "a", "cfg__bosch__ui800__0001"]:
        assert _stable_id(s) >= 0
