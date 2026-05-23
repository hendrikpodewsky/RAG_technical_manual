from typing import Any, Protocol, runtime_checkable

from pydantic import BaseModel


class Message(BaseModel):
    """A single message in an LLM conversation."""

    role: str
    content: str


class LLMResponse(BaseModel):
    """Raw response from an LLM completion call."""

    content: str
    model: str
    input_tokens: int
    output_tokens: int


@runtime_checkable
class LLMProvider(Protocol):
    """Generates text completions from a prompt."""

    def complete(
        self,
        system: str,
        messages: list[Message],
        *,
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ) -> LLMResponse: ...

    def complete_structured(
        self,
        system: str,
        messages: list[Message],
        schema: type[BaseModel],
        *,
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ) -> Any: ...
