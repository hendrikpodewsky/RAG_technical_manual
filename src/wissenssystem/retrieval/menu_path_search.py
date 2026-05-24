from dataclasses import dataclass

from wissenssystem.interfaces.embedding_provider import EmbeddingProvider
from wissenssystem.interfaces.vector_store import VectorStore


@dataclass(frozen=True)
class MenuPathHit:
    """A single menu path search result."""

    path_id: str
    nodes: list[str]
    leaf_description: str
    breadcrumb: str  # e.g. "Service > Anlageneinstellungen > Wärmepumpe > ..."
    score: float
    page: int


class MenuPathSearch:
    """Searches the menu path sub-namespace for navigation queries.

    The menu path index lives in <namespace>__menupaths.
    """

    def __init__(
        self,
        vector_store: VectorStore,
        embedder: EmbeddingProvider,
        top_k: int = 3,
    ) -> None:
        self._store = vector_store
        self._embedder = embedder
        self._top_k = top_k

    def search(self, query: str, namespace: str) -> list[MenuPathHit]:
        """Return top_k menu path hits for the query."""
        menu_ns = f"{namespace}__menupaths"
        if menu_ns not in self._store.list_namespaces():
            return []

        vector = self._embedder.embed_one(query)
        hits = self._store.search(menu_ns, vector, top_k=self._top_k)
        return [_hit_to_result(h) for h in hits]


def _hit_to_result(hit) -> MenuPathHit:
    nodes: list[str] = hit.payload.get("nodes", [])
    source = hit.payload.get("source_ref", {})
    return MenuPathHit(
        path_id=hit.payload.get("path_id", hit.id),
        nodes=nodes,
        leaf_description=hit.payload.get("leaf_description", nodes[-1] if nodes else ""),
        breadcrumb=" > ".join(nodes),
        score=hit.score,
        page=source.get("page", 0) if isinstance(source, dict) else 0,
    )
