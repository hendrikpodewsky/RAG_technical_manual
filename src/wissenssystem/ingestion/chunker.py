from wissenssystem.domain.chunk import TextChunk
from wissenssystem.domain.safety import SafetyLevel
from wissenssystem.domain.source import SourceRef
from wissenssystem.interfaces.document_parser import ParsedBlock

_MAX_TOKENS = 1500
_MIN_TOKENS = 100
_MAX_LIST_TOKENS = 1000

_CHARS_PER_TOKEN = 4


def _token_estimate(text: str) -> int:
    return max(1, len(text) // _CHARS_PER_TOKEN)


def _make_chunk(
    chunk_id: str,
    text: str,
    source_ref: SourceRef,
    chunk_type: str,
    safety_level: SafetyLevel | None = None,
    country_restriction: list[str] | None = None,
) -> TextChunk:
    return TextChunk(
        chunk_id=chunk_id,
        text=text,
        source_ref=source_ref,
        chunk_type=chunk_type,  # type: ignore[arg-type]
        safety_level=safety_level,
        country_restriction=country_restriction,
        related_image_ids=[],
    )


def _source_ref(block: ParsedBlock, doc_id: str) -> SourceRef:
    return SourceRef(doc_id=doc_id, page=block.page, section_path=block.section_path)


class Chunker:
    """Converts parsed document blocks into semantically coherent TextChunks.

    Rules:
    - Tables are always one chunk, never split.
    - Lists are kept together when < 1000 tokens; split on section boundary otherwise.
    - Prose is split at heading boundaries; max 1500 tokens, min 100 tokens.
    - Short chunks (< 100 tokens) are merged into the preceding chunk.
    """

    def __init__(self, doc_id: str) -> None:
        self._doc_id = doc_id
        self._counter = 0

    def _next_id(self) -> str:
        self._counter += 1
        return f"{self._doc_id}_{self._counter:04d}"

    def chunk(self, blocks: list[ParsedBlock]) -> list[TextChunk]:
        chunks: list[TextChunk] = []
        pending_text: list[str] = []
        pending_ref: SourceRef | None = None
        pending_safety: SafetyLevel | None = None

        def flush_pending() -> None:
            nonlocal pending_text, pending_ref, pending_safety
            if not pending_text or pending_ref is None:
                return
            combined = "\n\n".join(pending_text)
            if _token_estimate(combined) < _MIN_TOKENS and chunks and pending_safety is None:
                last = chunks[-1]
                merged_text = last.text + "\n\n" + combined
                chunks[-1] = _make_chunk(
                    last.chunk_id,
                    merged_text,
                    last.source_ref,
                    last.chunk_type,
                    last.safety_level or pending_safety,
                    last.country_restriction,
                )
            else:
                chunk_type = "safety_notice" if pending_safety else "prose"
                chunks.append(
                    _make_chunk(
                        self._next_id(),
                        combined,
                        pending_ref,
                        chunk_type,
                        pending_safety,
                    )
                )
            pending_text = []
            pending_ref = None
            pending_safety = None

        for block in blocks:
            ref = _source_ref(block, self._doc_id)

            if block.block_type == "table":
                flush_pending()
                chunks.append(
                    _make_chunk(self._next_id(), block.content, ref, "table")
                )
                continue

            if block.block_type == "heading":
                flush_pending()
                continue

            if block.block_type == "image":
                flush_pending()
                continue

            # text block
            text = block.content.strip()
            if not text:
                continue

            from wissenssystem.ingestion.safety_detector import detect_from_text

            safety_notice = detect_from_text(text)
            block_safety = safety_notice.level if safety_notice else None

            if pending_ref is None:
                pending_ref = ref

            if block_safety and pending_text:
                flush_pending()
                pending_ref = ref

            if _token_estimate(text) >= _MAX_TOKENS:
                flush_pending()
                chunks.append(
                    _make_chunk(
                        self._next_id(),
                        text,
                        ref,
                        "safety_notice" if block_safety else "prose",
                        block_safety,
                    )
                )
                continue

            would_be = "\n\n".join([*pending_text, text])
            if pending_text and _token_estimate(would_be) > _MAX_TOKENS:
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
            chunks.append(
                _make_chunk(self._next_id(), "\n".join(current), current_ref, "list")
            )
        return chunks
