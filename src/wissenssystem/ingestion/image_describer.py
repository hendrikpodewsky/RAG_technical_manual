from pathlib import Path

from wissenssystem.domain.chunk import ImageChunk
from wissenssystem.domain.source import SourceRef
from wissenssystem.interfaces.document_parser import ParsedBlock
from wissenssystem.interfaces.vision_provider import VisionProvider

_PROMPT_PATH = Path(__file__).parent.parent.parent.parent / "prompts" / "image_description.md"


def _load_prompt() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")


def _build_context(preceding: list[str], following: list[str]) -> str:
    parts = []
    if preceding:
        parts.append("Vorheriger Text:\n" + "\n".join(preceding))
    if following:
        parts.append("Nachfolgender Text:\n" + "\n".join(following))
    return "\n\n".join(parts)


class ImageDescriber:
    """Generates searchable descriptions for document images using a VisionProvider.

    For each image block, surrounding text (up to context_window paragraphs before
    and after) is passed as context so the model can ground its description.
    """

    def __init__(
        self,
        vision_provider: VisionProvider,
        doc_id: str,
        context_window: int = 2,
    ) -> None:
        self._vision = vision_provider
        self._doc_id = doc_id
        self._context_window = context_window
        self._counter = 0

    def describe_all(
        self,
        blocks: list[ParsedBlock],
        image_store: "BlobStoreProtocol",
    ) -> list[ImageChunk]:
        """Describe every image block, storing raw bytes in image_store."""
        chunks: list[ImageChunk] = []

        for i, block in enumerate(blocks):
            if block.block_type != "image":
                continue
            if not block.image_data or not block.image_media_type:
                continue

            image_id = image_store.put(block.image_data, _ext(block.image_media_type))

            # Gather surrounding prose for context
            text_before = self._surrounding_text(blocks, i, before=True)
            text_after = self._surrounding_text(blocks, i, before=False)
            context = _build_context(text_before, text_after)

            prompt = _load_prompt()
            if context:
                prompt = f"{prompt}\n\nKontext:\n{context}"

            description = self._vision.describe_image(
                image=block.image_data,
                media_type=block.image_media_type,
                context=context,
                prompt=prompt,
            )

            self._counter += 1
            ref = SourceRef(
                doc_id=self._doc_id,
                page=block.page,
                section_path=block.section_path,
            )
            chunks.append(
                ImageChunk(
                    chunk_id=f"{self._doc_id}_img_{self._counter:04d}",
                    image_id=image_id,
                    description=description,
                    caption=_extract_caption(block),
                    source_ref=ref,
                    related_text_chunk_ids=[],
                )
            )

        return chunks

    def _surrounding_text(
        self, blocks: list[ParsedBlock], image_idx: int, *, before: bool
    ) -> list[str]:
        results: list[str] = []
        indices = (
            range(image_idx - 1, max(-1, image_idx - 1 - self._context_window), -1)
            if before
            else range(image_idx + 1, min(len(blocks), image_idx + 1 + self._context_window))
        )
        for idx in indices:
            b = blocks[idx]
            if b.block_type == "text" and b.content.strip():
                results.append(b.content.strip())
        if before:
            results.reverse()
        return results


def _ext(media_type: str) -> str:
    """Map MIME type to file extension."""
    return {
        "image/jpeg": "jpg",
        "image/png": "png",
        "image/gif": "gif",
        "image/webp": "webp",
    }.get(media_type, "bin")


def _extract_caption(block: ParsedBlock) -> str | None:
    """Return caption text if embedded in content after a newline, else None."""
    lines = block.content.strip().splitlines()
    if len(lines) > 1:
        return lines[-1].strip() or None
    return None


# Type alias for BlobStore protocol (avoid circular import)
class BlobStoreProtocol:
    def put(self, data: bytes, extension: str) -> str: ...
    def get(self, image_id: str) -> bytes: ...
