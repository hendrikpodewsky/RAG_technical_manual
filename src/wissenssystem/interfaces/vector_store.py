from typing import Any, Protocol, runtime_checkable

from pydantic import BaseModel


class VectorItem(BaseModel):
    """An item to be stored in the vector store."""

    id: str
    vector: list[float]
    payload: dict[str, Any]


class VectorHit(BaseModel):
    """A single search result from the vector store."""

    id: str
    score: float
    payload: dict[str, Any]


@runtime_checkable
class VectorStore(Protocol):
    """Namespace-isolated vector storage and similarity search."""

    def create_namespace(self, namespace: str, dimension: int) -> None: ...

    def upsert(self, namespace: str, items: list[VectorItem]) -> None: ...

    def search(
        self,
        namespace: str,
        query_vector: list[float],
        top_k: int = 10,
        filter: dict[str, Any] | None = None,
    ) -> list[VectorHit]: ...

    def delete_namespace(self, namespace: str) -> None: ...

    def list_namespaces(self) -> list[str]: ...
