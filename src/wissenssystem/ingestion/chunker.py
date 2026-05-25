import re

from wissenssystem.domain.chunk import TextChunk
from wissenssystem.domain.safety import SafetyLevel
from wissenssystem.domain.source import SourceRef
from wissenssystem.interfaces.document_parser import ParsedBlock

_MAX_TOKENS = 1500
_MIN_TOKENS = 100
_MAX_LIST_TOKENS = 1000

_CHARS_PER_TOKEN = 4
_SECTION_HEADING_RE = re.compile(r"^(\d+(?:\.\d+)*)\s+(.*)")


def _token_estimate(text: str) -> int:
    return max(1, len(text) // _CHARS_PER_TOKEN)


def _parse_section_heading(text: str) -> tuple[str | None, str | None]:
    m = _SECTION_HEADING_RE.match(text.strip())
    if m:
        return m.group(1), m.group(2).strip()
    return None, text.strip() or None


def _make_chunk(
    chunk_id: str,
    text: str,
    source_ref: SourceRef,
    chunk_type: str,
    safety_level: SafetyLevel | None = None,
    country_restriction: list[str] | None = None,
    parent_chunk_id: str | None = None,
    section_id: str | None = None,
    section_title: str | None = None,
) -> TextChunk:
    return TextChunk(
        chunk_id=chunk_id,
        text=text,
        source_ref=source_ref,
        chunk_type=chunk_type,  # type: ignore[arg-type]
        safety_level=safety_level,
        country_restriction=country_restriction,
        related_image_ids=[],
        parent_chunk_id=parent_chunk_id,
        section_id=section_id,
        section_title=section_title,
    )


def _source_ref(block: ParsedBlock, doc_id: str) -> SourceRef:
    return SourceRef(doc_id=doc_id, page=block.page, section_path=block.section_path)


class Chunker:
    """Hierarchical chunker: section headings become parent chunks, content
    within sections becomes child chunks.

    Rules:
    - Heading → parent chunk (chunk_type="section"), text = heading only.
    - Content within a section → child chunks with parent_chunk_id set.
      Child chunk text is prefixed with the section heading for better
      embedding quality.
    - Tables → single child chunk, never split.
    - Short child chunks (< _MIN_TOKENS) merged into preceding child of the
      same section; cross-section merges and merges into table/safety_notice
      chunks are forbidden.
    - Max child chunk size: _MAX_TOKENS tokens.
    """

    def __init__(self, doc_id: str) -> None:
        self._doc_id = doc_id
        self._counter = 0

    def _next_id(self) -> str:
        self._counter += 1
        return f"{self._doc_id}_{self._counter:04d}"

    def chunk(self, blocks: list[ParsedBlock]) -> list[TextChunk]:
        from wissenssystem.ingestion.safety_detector import detect_from_text

        chunks: list[TextChunk] = []
        current_parent_id: str | None = None
        current_section_id: str | None = None
        current_section_title: str | None = None
        current_heading: str | None = None

        pending_text: list[str] = []
        pending_ref: SourceRef | None = None
        pending_safety: SafetyLevel | None = None

        def flush_pending() -> None:
            nonlocal pending_text, pending_ref, pending_safety
            if not pending_text or pending_ref is None:
                return
            combined = "\n\n".join(pending_text)
            # Prefix with section heading so the embedding captures section context.
            full_text = f"{current_heading}\n\n{combined}" if current_heading else combined

            if (
                _token_estimate(combined) < _MIN_TOKENS
                and pending_safety is None
                and chunks
                and chunks[-1].chunk_type in ("prose", "list")
                and chunks[-1].parent_chunk_id == current_parent_id
            ):
                # Merge raw content into preceding child of the same section.
                last = chunks[-1]
                chunks[-1] = _make_chunk(
                    last.chunk_id,
                    last.text + "\n\n" + combined,
                    last.source_ref,
                    last.chunk_type,
                    last.safety_level,
                    last.country_restriction,
                    parent_chunk_id=last.parent_chunk_id,
                    section_id=last.section_id,
                    section_title=last.section_title,
                )
            else:
                chunk_type = "safety_notice" if pending_safety else "prose"
                chunks.append(
                    _make_chunk(
                        self._next_id(),
                        full_text,
                        pending_ref,
                        chunk_type,
                        pending_safety,
                        parent_chunk_id=current_parent_id,
                        section_id=current_section_id,
                        section_title=current_section_title,
                    )
                )
            pending_text = []
            pending_ref = None
            pending_safety = None

        for block in blocks:
            ref = _source_ref(block, self._doc_id)

            if block.block_type == "heading":
                flush_pending()
                heading_text = block.content.strip()
                section_id, section_title = _parse_section_heading(heading_text)
                parent = _make_chunk(
                    self._next_id(),
                    heading_text,
                    ref,
                    "section",
                    section_id=section_id,
                    section_title=section_title,
                )
                chunks.append(parent)
                current_parent_id = parent.chunk_id
                current_section_id = section_id
                current_section_title = section_title
                current_heading = heading_text
                continue

            if block.block_type == "table":
                flush_pending()
                chunks.append(
                    _make_chunk(
                        self._next_id(),
                        block.content,
                        ref,
                        "table",
                        parent_chunk_id=current_parent_id,
                        section_id=current_section_id,
                        section_title=current_section_title,
                    )
                )
                continue

            if block.block_type == "image":
                flush_pending()
                continue

            text = block.content.strip()
            if not text:
                continue

            safety_notice = detect_from_text(text)
            block_safety = safety_notice.level if safety_notice else None

            if pending_ref is None:
                pending_ref = ref

            if block_safety and pending_text:
                flush_pending()
                pending_ref = ref

            heading_tokens = _token_estimate(current_heading) if current_heading else 0
            if _token_estimate(text) + heading_tokens >= _MAX_TOKENS:
                flush_pending()
                full_text = f"{current_heading}\n\n{text}" if current_heading else text
                chunks.append(
                    _make_chunk(
                        self._next_id(),
                        full_text,
                        ref,
                        "safety_notice" if block_safety else "prose",
                        block_safety,
                        parent_chunk_id=current_parent_id,
                        section_id=current_section_id,
                        section_title=current_section_title,
                    )
                )
                continue

            would_be = "\n\n".join([*pending_text, text])
            if pending_text and _token_estimate(would_be) + heading_tokens > _MAX_TOKENS:
                flush_pending()
                pending_ref = ref

            pending_text.append(text)
            if block_safety and pending_safety is None:
                pending_safety = block_safety

        flush_pending()
        return chunks

    def chunk_list_blocks(self, blocks: list[ParsedBlock]) -> list[TextChunk]:
        """Chunk a sequence of list items: keep together if total < 1000 tokens."""
        combined = "\n".join(b.content.strip() for b in blocks if b.content.strip())
        if not combined or not blocks:
            return []
        ref = _source_ref(blocks[0], self._doc_id)
        if _token_estimate(combined) < _MAX_LIST_TOKENS:
            return [_make_chunk(self._next_id(), combined, ref, "list")]
        chunks = []
        current: list[str] = []
        current_ref = ref
        for block in blocks:
            text = block.content.strip()
            if not text:
                continue
            candidate = "\n".join([*current, text])
            if current and _token_estimate(candidate) > _MAX_LIST_TOKENS:
                chunks.append(
                    _make_chunk(
                        self._next_id(),
                        "\n".join(current),
                        current_ref,
                        "list",
                    )
                )
                current = []
                current_ref = _source_ref(block, self._doc_id)
            current.append(text)
        if current:
            chunks.append(_make_chunk(self._next_id(), "\n".join(current), current_ref, "list"))
        return chunks
