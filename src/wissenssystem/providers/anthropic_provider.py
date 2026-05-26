import json
import re
import time
from typing import Any

import anthropic

from wissenssystem.interfaces.llm_provider import LLMResponse, Message


class ProviderError(Exception):
    """Raised when a provider call fails after all retries."""


def _with_retry(fn, max_attempts: int = 3, base_delay: float = 1.0):
    for attempt in range(max_attempts):
        try:
            return fn()
        except anthropic.RateLimitError as exc:
            if attempt == max_attempts - 1:
                raise ProviderError(f"Rate limit after {max_attempts} attempts: {exc}") from exc
            time.sleep(base_delay * (2**attempt))
        except anthropic.APIConnectionError as exc:
            if attempt == max_attempts - 1:
                raise ProviderError(f"Connection failed after {max_attempts} attempts: {exc}") from exc
            time.sleep(base_delay * (2**attempt))


class AnthropicVisionProvider:
    """VisionProvider backed by Claude's vision capabilities."""

    def __init__(self, model: str, api_key: str) -> None:
        self._model = model
        self._client = anthropic.Anthropic(api_key=api_key)

    def describe_image(
        self,
        image: bytes,
        media_type: str,
        context: str,
        prompt: str,
    ) -> str:
        import base64
        image_b64 = base64.standard_b64encode(image).decode()
        full_prompt = f"{prompt}\n\nKontext aus dem umgebenden Handbuchtext:\n{context}"

        def _call():
            return self._client.messages.create(
                model=self._model,
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_b64,
                            },
                        },
                        {"type": "text", "text": full_prompt},
                    ],
                }],
            )

        response = _with_retry(_call)
        return next((b.text for b in response.content if hasattr(b, "text")), "")


class AnthropicLLMProvider:
    """LLMProvider backed by the Anthropic API."""

    def __init__(self, model: str, api_key: str) -> None:
        self._model = model
        self._client = anthropic.Anthropic(api_key=api_key)

    def complete(
        self,
        system: str,
        messages: list[Message],
        *,
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        api_messages = [{"role": m.role, "content": m.content} for m in messages]

        def _call():
            return self._client.messages.create(
                model=self._model,
                system=system,
                messages=api_messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        response = _with_retry(_call)
        content = response.content[0].text if response.content else ""
        return LLMResponse(
            content=content,
            model=self._model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
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
        api_messages = [{"role": m.role, "content": m.content} for m in messages]

        def _call():
            return self._client.messages.create(
                model=self._model,
                system=system + json_instruction,
                messages=api_messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        response = _with_retry(_call)
        raw = next((b.text for b in response.content if hasattr(b, "text")), "") or "{}"
        # Strip markdown code fences that Sonnet sometimes adds
        clean = re.sub(r"^```(?:json)?\s*", "", raw.strip())
        clean = re.sub(r"\s*```$", "", clean).strip() or "{}"
        data = json.loads(clean)
        return schema.model_validate(data)
