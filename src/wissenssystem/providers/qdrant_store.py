from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, FieldCondition, Filter, MatchValue, PointStruct, VectorParams

from wissenssystem.interfaces.vector_store import VectorHit, VectorItem


class QdrantVectorStore:
    """Qdrant-backed vector store.

    Works with both a real Qdrant server and the in-memory client
    (QdrantClient(':memory:')).
    """

    def __init__(self, client: QdrantClient) -> None:
        self._client = client

    def create_namespace(self, namespace: str, dimension: int) -> None:
        self._client.create_collection(
            collection_name=namespace,
            vectors_config=VectorParams(size=dimension, distance=Distance.COSINE),
        )

    def upsert(self, namespace: str, items: list[VectorItem]) -> None:
        points = [
            PointStruct(id=_stable_id(item.id), vector=item.vector, payload=item.payload)
            for item in items
        ]
        self._client.upsert(collection_name=namespace, points=points)

    def search(
        self,
        namespace: str,
        query_vector: list[float],
        top_k: int = 10,
        filter: dict[str, Any] | None = None,
    ) -> list[VectorHit]:
        results = self._client.query_points(
            collection_name=namespace,
            query=query_vector,
            limit=top_k,
            with_payload=True,
        ).points
        return [
            VectorHit(id=str(r.id), score=r.score, payload=r.payload or {})
            for r in results
        ]

    def fetch_by_ids(self, namespace: str, ids: list[str]) -> list[VectorHit]:
        int_ids = [_stable_id(i) for i in ids]
        results = self._client.retrieve(
            collection_name=namespace,
            ids=int_ids,
            with_payload=True,
        )
        id_to_str = {_stable_id(i): i for i in ids}
        return [
            VectorHit(id=id_to_str.get(r.id, str(r.id)), score=0.0, payload=r.payload or {})
            for r in results
        ]

    def fetch_by_parent_id(self, namespace: str, parent_id: str) -> list[VectorHit]:
        results, _ = self._client.scroll(
            collection_name=namespace,
            scroll_filter=Filter(must=[
                FieldCondition(key="parent_chunk_id", match=MatchValue(value=parent_id))
            ]),
            with_payload=True,
            with_vectors=False,
            limit=50,
        )
        return [
            VectorHit(id=r.payload.get("chunk_id", str(r.id)), score=0.0, payload=r.payload or {})
            for r in results
        ]

    def delete_namespace(self, namespace: str) -> None:
        self._client.delete_collection(namespace)

    def list_namespaces(self) -> list[str]:
        return [c.name for c in self._client.get_collections().collections]


def _stable_id(chunk_id: str) -> int:
    """Map a string chunk_id to a stable integer for Qdrant point IDs."""
    return abs(hash(chunk_id)) % (2**63)
