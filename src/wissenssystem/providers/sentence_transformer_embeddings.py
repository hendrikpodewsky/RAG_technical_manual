from sentence_transformers import SentenceTransformer

from wissenssystem.interfaces.embedding_provider import EmbeddingProvider

_BATCH_SIZE = 128


class SentenceTransformerEmbeddingProvider:
    """EmbeddingProvider using a local sentence-transformers model."""

    def __init__(self, model_name: str) -> None:
        self._model = SentenceTransformer(model_name)
        self._dimension = self._model.get_sentence_embedding_dimension()

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed(self, texts: list[str]) -> list[list[float]]:
        results: list[list[float]] = []
        for i in range(0, len(texts), _BATCH_SIZE):
            batch = texts[i : i + _BATCH_SIZE]
            vectors = self._model.encode(batch, convert_to_numpy=True)
            results.extend(v.tolist() for v in vectors)
        return results

    def embed_one(self, text: str) -> list[float]:
        return self.embed([text])[0]


def _assert_protocol() -> None:
    assert issubclass(SentenceTransformerEmbeddingProvider, type(EmbeddingProvider))
