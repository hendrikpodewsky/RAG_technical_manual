import json
import urllib.request


class OllamaEmbeddingProvider:
    """EmbeddingProvider backed by Ollama's /api/embed endpoint."""

    def __init__(self, model: str, ollama_url: str = "http://localhost:11434") -> None:
        self._model = model
        self._url = f"{ollama_url.rstrip('/')}/api/embed"
        self._dimension: int | None = None

    @property
    def dimension(self) -> int:
        if self._dimension is None:
            self._dimension = len(self.embed_one("warmup"))
        return self._dimension

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        payload = json.dumps({"model": self._model, "input": texts}).encode()
        req = urllib.request.Request(
            self._url, data=payload, headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
        return data["embeddings"]

    def embed_one(self, text: str) -> list[float]:
        return self.embed([text])[0]
