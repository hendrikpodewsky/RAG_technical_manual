"""PDF parser that uses Claude Vision to extract structured blocks page by page."""

import base64
import json
import re
from pathlib import Path

import anthropic
import fitz  # pymupdf

from wissenssystem.interfaces.document_parser import ParsedBlock

_PROMPT_PATH = Path(__file__).parent.parent.parent.parent / "prompts" / "vision_parser.md"
_PAGE_DPI = 150  # sufficient for Claude Vision, keeps token count low


def _load_prompt() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")


def _pdf_to_page_images(pdf_path: Path) -> list[bytes]:
    """Render each PDF page to PNG bytes."""
    doc = fitz.open(str(pdf_path))
    matrix = fitz.Matrix(_PAGE_DPI / 72, _PAGE_DPI / 72)
    pages = []
    for page in doc:
        pix = page.get_pixmap(matrix=matrix)
        pages.append(pix.tobytes("png"))
    doc.close()
    return pages


def _parse_json_response(text: str) -> list[dict]:
    clean = re.sub(r"^```(?:json)?\s*", "", text.strip())
    clean = re.sub(r"\s*```$", "", clean).strip()
    if not clean or clean == "[]":
        return []
    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        return []


class ClaudeVisionParserAdapter:
    """DocumentParser that sends each PDF page to Claude Vision for extraction."""

    def __init__(self, api_key: str, model: str = "claude-haiku-4-5-20251001") -> None:
        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model
        self._prompt = _load_prompt()

    def parse(self, pdf_path: Path) -> list[ParsedBlock]:
        pages = _pdf_to_page_images(pdf_path)
        total = len(pages)
        blocks: list[ParsedBlock] = []
        current_section: list[str] = []

        for page_num, page_png in enumerate(pages, start=1):
            print(f"  Vision parsing page {page_num}/{total}…", end="\r")
            page_blocks = self._parse_page(page_png, page_num, current_section)
            # Track section path from headings
            for b in page_blocks:
                if b.block_type == "heading":
                    current_section = [b.content.strip()]
            blocks.extend(page_blocks)

        print(f"  Vision parsing done — {len(blocks)} blocks extracted.      ")
        return blocks

    def _parse_page(
        self, page_png: bytes, page_num: int, section_path: list[str]
    ) -> list[ParsedBlock]:
        b64 = base64.standard_b64encode(page_png).decode()
        try:
            response = self._client.messages.create(
                model=self._model,
                max_tokens=2048,
                system=self._prompt,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": b64,
                            },
                        },
                        {"type": "text", "text": f"Seite {page_num}"},
                    ],
                }],
            )
        except anthropic.APIError:
            return []

        raw_text = next(
            (b.text for b in response.content if hasattr(b, "text")), ""
        )
        raw_blocks = _parse_json_response(raw_text)

        result = []
        for item in raw_blocks:
            block_type = item.get("block_type", "text")
            content = item.get("content", "").strip()
            section_title = item.get("section_title")
            if not content:
                continue

            sp = list(section_path)
            if section_title and section_title not in sp:
                sp = [section_title]

            result.append(ParsedBlock(
                block_type="table" if block_type == "table" else
                           "heading" if block_type == "heading" else "text",
                content=content,
                page=page_num,
                level=1 if block_type == "heading" else None,
                position=None,
                section_path=sp,
                image_data=None,
                image_media_type=None,
            ))
        return result
