from wissenssystem.interfaces.embedding_provider import EmbeddingProvider


def build_embedder(
    model_name: str, ollama_url: str = "http://localhost:11434"
) -> EmbeddingProvider:
    """Return the right EmbeddingProvider for the given model name.

    Ollama models use 'name:tag' format (e.g. 'bge-m3:latest').
    HuggingFace/sentence-transformers models contain '/' or no ':'.
    """
    if ":" in model_name and "/" not in model_name:
        from wissenssystem.providers.ollama_embeddings import OllamaEmbeddingProvider

        return OllamaEmbeddingProvider(model=model_name, ollama_url=ollama_url)
    from wissenssystem.providers.sentence_transformer_embeddings import (
        SentenceTransformerEmbeddingProvider,
    )

    return SentenceTransformerEmbeddingProvider(model_name)
