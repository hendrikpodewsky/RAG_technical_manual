from typing import Literal

from pydantic import BaseModel, ConfigDict

from wissenssystem.domain.safety import SafetyLevel
from wissenssystem.domain.source import SourceRef


class TextChunk(BaseModel):
    """A semantically coherent text segment with provenance metadata."""

    chunk_id: str
    text: str
    source_ref: SourceRef
    chunk_type: Literal["prose", "table", "list", "safety_notice"]
    safety_level: SafetyLevel | None
    country_restriction: list[str] | None
    related_image_ids: list[str]

    model_config = ConfigDict(frozen=True)


class ImageChunk(BaseModel):
    """An extracted image with a Vision-LLM-generated description."""

    chunk_id: str
    image_id: str
    description: str
    caption: str | None
    source_ref: SourceRef
    related_text_chunk_ids: list[str]

    model_config = ConfigDict(frozen=True)
