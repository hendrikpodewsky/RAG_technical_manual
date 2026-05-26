"""Extract menu navigation paths from PDF pages using Claude Vision."""

import base64
import json
import re
from pathlib import Path

import anthropic
import fitz  # pymupdf

from wissenssystem.domain.menu_path import MenuPath
from wissenssystem.domain.source import SourceRef

_PROMPT_PATH = Path(__file__).parent.parent.parent.parent / "prompts" / "vision_menu_extraction.md"
_PAGE_DPI = 150


def _load_prompt() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")


def _parse_json_response(text: str) -> list[dict]:
    clean = re.sub(r"^```(?:json)?\s*", "", text.strip())
    clean = re.sub(r"\s*```$", "", clean).strip()
    if not clean:
        return []
    try:
        data = json.loads(clean)
        return data.get("paths", []) if isinstance(data, dict) else []
    except json.JSONDecodeError:
        return []


class ClaudeVisionMenuExtractor:
    """Extracts menu navigation paths from PDF pages using Claude Vision.

    Runs as a supplementary pass alongside the text-based MenuPathExtractor.
    Particularly effective for PDFs where Docling doesn't parse bullet lists
    well enough for the heuristic extractor to find menu paths.
    """

    def __init__(self, api_key: str, model: str = "claude-haiku-4-5-20251001") -> None:
        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model
        self._prompt = _load_prompt()

    def extract(self, pdf_path: Path, namespace: str) -> list[MenuPath]:
        """Render each page and ask Claude Vision for menu paths."""
        doc = fitz.open(str(pdf_path))
        matrix = fitz.Matrix(_PAGE_DPI / 72, _PAGE_DPI / 72)
        total = doc.page_count
        all_paths: list[MenuPath] = []
        counter = 0

        for page_num in range(total):
            page = doc[page_num]
            pix = page.get_pixmap(matrix=matrix)
            page_png = pix.tobytes("png")
            print(f"  Vision menu extraction page {page_num + 1}/{total}…", end="\r")

            raw_paths = self._extract_page(page_png)
            for path_data in raw_paths:
                nodes = path_data.get("nodes", [])
                if not nodes or len(nodes) < 2:
                    continue
                counter += 1
                all_paths.append(
                    MenuPath(
                        path_id=f"{namespace}__vmenu__{counter:04d}",
                        nodes=nodes,
                        leaf_description=nodes[-1],
                        source_ref=SourceRef(
                            doc_id="",
                            page=page_num + 1,
                            section_path=[],
                        ),
                        namespace=namespace,
                    )
                )

        doc.close()
        print(f"  Vision menu extraction done — {len(all_paths)} paths found.      ")
        return all_paths

    def _extract_page(self, page_png: bytes) -> list[dict]:
        b64 = base64.standard_b64encode(page_png).decode()
        try:
            response = self._client.messages.create(
                model=self._model,
                max_tokens=1024,
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
                    ],
                }],
            )
        except anthropic.APIError:
            return []

        raw_text = next(
            (b.text for b in response.content if hasattr(b, "text")), ""
        )
        return _parse_json_response(raw_text)
