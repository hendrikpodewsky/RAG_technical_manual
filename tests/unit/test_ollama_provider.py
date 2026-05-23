from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from wissenssystem.interfaces.llm_provider import LLMProvider, Message
from wissenssystem.interfaces.vision_provider import VisionProvider
from wissenssystem.providers.ollama_provider import (
    OllamaLLMProvider,
    OllamaVisionProvider,
    ProviderError,
)


def _make_chat_response(content: str, prompt_tokens: int = 10, eval_tokens: int = 20):
    return SimpleNamespace(
        message=SimpleNamespace(content=content),
        prompt_eval_count=prompt_tokens,
        eval_count=eval_tokens,
    )


# --- Protocol compliance ---


def test_llm_provider_implements_protocol():
    provider = OllamaLLMProvider("qwen2.5:3b")
    assert isinstance(provider, LLMProvider)


def test_vision_provider_implements_protocol():
    provider = OllamaVisionProvider("moondream2")
    assert isinstance(provider, VisionProvider)


# --- OllamaLLMProvider.complete ---


@patch("wissenssystem.providers.ollama_provider.ollama_client.Client")
def test_complete_sends_correct_messages(mock_client_cls):
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client
    mock_client.chat.return_value = _make_chat_response("Antwort des Modells")

    provider = OllamaLLMProvider("qwen2.5:3b", ollama_url="http://localhost:11434")
    response = provider.complete(
        system="Du bist ein Assistent.",
        messages=[Message(role="user", content="Wie geht es?")],
    )

    assert response.content == "Antwort des Modells"
    assert response.model == "qwen2.5:3b"
    assert response.input_tokens == 10
    assert response.output_tokens == 20

    call_args = mock_client.chat.call_args
    sent_messages = call_args.kwargs["messages"]
    assert sent_messages[0]["role"] == "system"
    assert sent_messages[1]["role"] == "user"
    assert sent_messages[1]["content"] == "Wie geht es?"


@patch("wissenssystem.providers.ollama_provider.ollama_client.Client")
def test_complete_passes_temperature(mock_client_cls):
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client
    mock_client.chat.return_value = _make_chat_response("ok")

    provider = OllamaLLMProvider("qwen2.5:3b")
    provider.complete(
        system="sys",
        messages=[Message(role="user", content="hi")],
        temperature=0.5,
        max_tokens=512,
    )

    options = mock_client.chat.call_args.kwargs["options"]
    assert options["temperature"] == 0.5
    assert options["num_predict"] == 512


# --- OllamaLLMProvider.complete_structured ---


@patch("wissenssystem.providers.ollama_provider.ollama_client.Client")
def test_complete_structured_parses_json(mock_client_cls):
    from pydantic import BaseModel

    class Intent(BaseModel):
        intent: str
        confidence: float

    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client
    mock_client.chat.return_value = _make_chat_response(
        '{"intent": "troubleshoot", "confidence": 0.9}'
    )

    provider = OllamaLLMProvider("qwen2.5:3b")
    result = provider.complete_structured(
        system="Classify intent.",
        messages=[Message(role="user", content="Pumpe läuft nicht.")],
        schema=Intent,
    )

    assert isinstance(result, Intent)
    assert result.intent == "troubleshoot"
    assert result.confidence == 0.9


@patch("wissenssystem.providers.ollama_provider.ollama_client.Client")
def test_complete_structured_uses_json_format(mock_client_cls):
    from pydantic import BaseModel

    class Simple(BaseModel):
        value: str

    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client
    mock_client.chat.return_value = _make_chat_response('{"value": "test"}')

    provider = OllamaLLMProvider("qwen2.5:3b")
    provider.complete_structured(
        system="sys", messages=[Message(role="user", content="hi")], schema=Simple
    )

    assert mock_client.chat.call_args.kwargs["format"] == "json"


# --- OllamaVisionProvider.describe_image ---


@patch("wissenssystem.providers.ollama_provider.ollama_client.Client")
def test_describe_image_sends_image(mock_client_cls):
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client
    mock_client.chat.return_value = _make_chat_response("Schaltplan mit Kompressor.")

    provider = OllamaVisionProvider("moondream2")
    result = provider.describe_image(
        image=b"\x89PNG\r\n",
        media_type="image/png",
        context="Kältekreisdiagramm auf Seite 10.",
        prompt="Beschreibe dieses technische Bild.",
    )

    assert result == "Schaltplan mit Kompressor."
    call_messages = mock_client.chat.call_args.kwargs["messages"]
    assert len(call_messages[0]["images"]) == 1


@patch("wissenssystem.providers.ollama_provider.ollama_client.Client")
def test_describe_image_includes_context_in_prompt(mock_client_cls):
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client
    mock_client.chat.return_value = _make_chat_response("Beschreibung")

    provider = OllamaVisionProvider("moondream2")
    provider.describe_image(
        image=b"data",
        media_type="image/jpeg",
        context="Umgebender Text: Kältekreis",
        prompt="Beschreibe.",
    )

    content = mock_client.chat.call_args.kwargs["messages"][0]["content"]
    assert "Kältekreis" in content


# --- Retry behaviour ---


@patch("wissenssystem.providers.ollama_provider.time.sleep")
@patch("wissenssystem.providers.ollama_provider.ollama_client.Client")
def test_retries_on_failure_then_succeeds(mock_client_cls, mock_sleep):
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client
    mock_client.chat.side_effect = [
        Exception("connection refused"),
        _make_chat_response("ok"),
    ]

    provider = OllamaLLMProvider("qwen2.5:3b")
    response = provider.complete(
        system="sys", messages=[Message(role="user", content="hi")]
    )

    assert response.content == "ok"
    assert mock_sleep.call_count == 1


@patch("wissenssystem.providers.ollama_provider.time.sleep")
@patch("wissenssystem.providers.ollama_provider.ollama_client.Client")
def test_raises_provider_error_after_max_retries(mock_client_cls, mock_sleep):
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client
    mock_client.chat.side_effect = Exception("connection refused")

    provider = OllamaLLMProvider("qwen2.5:3b")
    with pytest.raises(ProviderError):
        provider.complete(system="sys", messages=[Message(role="user", content="hi")])

    assert mock_sleep.call_count == 2
