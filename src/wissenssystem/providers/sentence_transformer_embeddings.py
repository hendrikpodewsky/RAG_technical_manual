from sentence_transformers import SentenceTransformer

from wissenssystem.interfaces.embedding_provider import EmbeddingProvider

_BATCH_SIZE = 128

# Models that require explicit query/passage prefixes for correct retrieval.
# "embed" (indexing) uses "passage: ", "embed_one" (query) uses "query: ".
_PREFIX_MODELS = ("e5",)


def _detect_prefixes(model_name: str) -> tuple[str, str]:
    """Return (query_prefix, passage_prefix) for the given model name."""
    lower = model_name.lower()
    if any(k in lower for k in _PREFIX_MODELS):
        return "query: ", "passage: "
    return "", ""


class SentenceTransformerEmbeddingProvider:
    """EmbeddingProvider using a local sentence-transformers model.

    E5-family models need "query: " / "passage: " prefixes — applied automatically.
    """

    def __init__(self, model_name: str) -> None:
        self._model = SentenceTransformer(model_name)
        self._dimension = self._model.get_embedding_dimension()
        self._query_prefix, self._passage_prefix = _detect_prefixes(model_name)

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Embed document passages (uses passage prefix for e5 models)."""
        results: list[list[float]] = []
        for i in range(0, len(texts), _BATCH_SIZE):
            batch = [f"{self._passage_prefix}{t}" for t in texts[i : i + _BATCH_SIZE]]
            vectors = self._model.encode(batch, convert_to_numpy=True)
            results.extend(v.tolist() for v in vectors)
        return results

    def embed_one(self, text: str) -> list[float]:
        """Embed a search query (uses query prefix for e5 models)."""
        prefixed = f"{self._query_prefix}{text}"
        return self._model.encode([prefixed], convert_to_numpy=True)[0].tolist()


def _assert_protocol() -> None:
    assert issubclass(SentenceTransformerEmbeddingProvider, type(EmbeddingProvider))
