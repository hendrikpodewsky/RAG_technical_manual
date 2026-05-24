from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

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

    def delete_namespace(self, namespace: str) -> None:
        self._client.delete_collection(namespace)

    def list_namespaces(self) -> list[str]:
        return [c.name for c in self._client.get_collections().collections]


def _stable_id(chunk_id: str) -> int:
    """Map a string chunk_id to a stable integer for Qdrant point IDs."""
    return abs(hash(chunk_id)) % (2**63)
