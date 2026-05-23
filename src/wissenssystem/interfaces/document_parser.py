from pathlib import Path
from typing import Any, Literal, Protocol, runtime_checkable

from pydantic import BaseModel


class ParsedBlock(BaseModel):
    """A single structured block extracted from a parsed document."""

    block_type: Literal["text", "table", "image", "heading"]
    content: str
    page: int
    level: int | None
    position: dict[str, Any] | None
    section_path: list[str]
    image_data: bytes | None
    image_media_type: str | None

    model_config = {"frozen": True}


@runtime_checkable
class DocumentParser(Protocol):
    """Parses a PDF into structured blocks with positional metadata."""

    def parse(self, pdf_path: Path) -> list[ParsedBlock]: ...
