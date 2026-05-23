import base64
import json
import time
from typing import Any

import ollama as ollama_client

from wissenssystem.interfaces.llm_provider import LLMResponse, Message


class ProviderError(Exception):
    """Raised when a provider call fails after all retries."""


def _with_retry(fn, max_attempts: int = 3, base_delay: float = 1.0):
    """Retry fn with exponential backoff on connection errors."""
    for attempt in range(max_attempts):
        try:
            return fn()
        except (ollama_client.ResponseError, Exception) as exc:
            if attempt == max_attempts - 1:
                msg = f"Provider call failed after {max_attempts} attempts: {exc}"
                raise ProviderError(msg) from exc
            time.sleep(base_delay * (2**attempt))


class OllamaLLMProvider:
    """LLMProvider backed by a local Ollama instance."""

    def __init__(self, model: str, ollama_url: str = "http://localhost:11434") -> None:
        self._model = model
        self._client = ollama_client.Client(host=ollama_url)

    def complete(
        self,
        system: str,
        messages: list[Message],
        *,
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        ollama_messages = [{"role": "system", "content": system}]
        ollama_messages += [{"role": m.role, "content": m.content} for m in messages]

        def _call():
            return self._client.chat(
                model=self._model,
                messages=ollama_messages,
                options={"temperature": temperature, "num_predict": max_tokens},
            )

        response = _with_retry(_call)
        return LLMResponse(
            content=response.message.content,
            model=self._model,
            input_tokens=response.prompt_eval_count or 0,
            output_tokens=response.eval_count or 0,
        )

    def complete_structured(
        self,
        system: str,
        messages: list[Message],
        schema: type[Any],
        *,
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ) -> Any:
        json_instruction = (
            f"\n\nRespond with valid JSON matching this schema: {schema.model_json_schema()}"
        )
        ollama_messages = [{"role": "system", "content": system + json_instruction}]
        ollama_messages += [{"role": m.role, "content": m.content} for m in messages]

        def _call():
            return self._client.chat(
                model=self._model,
                messages=ollama_messages,
                format="json",
                options={"temperature": temperature, "num_predict": max_tokens},
            )

        response = _with_retry(_call)
        data = json.loads(response.message.content)
        return schema.model_validate(data)


class OllamaVisionProvider:
    """VisionProvider backed by a local Ollama vision model."""

    def __init__(self, model: str, ollama_url: str = "http://localhost:11434") -> None:
        self._model = model
        self._client = ollama_client.Client(host=ollama_url)

    def describe_image(
        self,
        image: bytes,
        media_type: str,
        context: str,
        prompt: str,
    ) -> str:
        image_b64 = base64.b64encode(image).decode()
        full_prompt = f"{prompt}\n\nContext from surrounding manual text:\n{context}"

        def _call():
            return self._client.chat(
                model=self._model,
                messages=[
                    {
                        "role": "user",
                        "content": full_prompt,
                        "images": [image_b64],
                    }
                ],
            )

        response = _with_retry(_call)
        return response.message.content


