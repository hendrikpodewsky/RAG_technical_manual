from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from wissenssystem.interfaces.embedding_provider import EmbeddingProvider
from wissenssystem.providers.sentence_transformer_embeddings import (
    SentenceTransformerEmbeddingProvider,
)


def _make_provider(dim: int = 384):
    with patch(
        "wissenssystem.providers.sentence_transformer_embeddings.SentenceTransformer"
    ) as mock_cls:
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = dim
        mock_cls.return_value = mock_model
        provider = SentenceTransformerEmbeddingProvider("paraphrase-multilingual-MiniLM-L12-v2")
        provider._model = mock_model
    return provider, mock_model


def test_implements_protocol():
    provider, _ = _make_provider()
    assert isinstance(provider, EmbeddingProvider)


def test_dimension_property():
    provider, _ = _make_provider(dim=384)
    assert provider.dimension == 384


def test_embed_returns_correct_shape():
    provider, mock_model = _make_provider(dim=4)
    mock_model.encode.return_value = np.array([[0.1, 0.2, 0.3, 0.4], [0.5, 0.6, 0.7, 0.8]])

    result = provider.embed(["Hallo", "Welt"])

    assert len(result) == 2
    assert len(result[0]) == 4


def test_embed_one_returns_single_vector():
    provider, mock_model = _make_provider(dim=4)
    mock_model.encode.return_value = np.array([[1.0, 2.0, 3.0, 4.0]])

    result = provider.embed_one("Testtext")

    assert len(result) == 4
    assert result[0] == pytest.approx(1.0)


def test_embed_batches_large_input():
    provider, mock_model = _make_provider(dim=2)
    n_texts = 300
    mock_model.encode.return_value = np.ones((128, 2))

    provider.embed(["text"] * n_texts)

    assert mock_model.encode.call_count == 3  # ceil(300 / 128)


def test_embed_single_batch():
    provider, mock_model = _make_provider(dim=2)
    mock_model.encode.return_value = np.ones((5, 2))

    provider.embed(["a"] * 5)

    assert mock_model.encode.call_count == 1


def test_embed_empty_list():
    provider, mock_model = _make_provider()

    result = provider.embed([])

    assert result == []
    mock_model.encode.assert_not_called()
