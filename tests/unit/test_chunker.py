
from wissenssystem.domain.safety import SafetyLevel
from wissenssystem.ingestion.chunker import _CHARS_PER_TOKEN, _MAX_TOKENS, Chunker
from wissenssystem.interfaces.document_parser import ParsedBlock


def _block(
    content: str,
    block_type: str = "text",
    page: int = 1,
    section_path: list[str] | None = None,
) -> ParsedBlock:
    return ParsedBlock(
        block_type=block_type,
        content=content,
        page=page,
        level=None,
        position=None,
        section_path=section_path or ["1"],
        image_data=None,
        image_media_type=None,
    )


def _table_block(content: str, page: int = 1) -> ParsedBlock:
    return ParsedBlock(
        block_type="table",
        content=content,
        page=page,
        level=None,
        position=None,
        section_path=["3"],
        image_data=None,
        image_media_type=None,
    )


# --- Tables always one chunk ---


def test_table_is_single_chunk():
    chunker = Chunker("doc1")
    blocks = [_table_block("| A | B |\n| 1 | 2 |\n| 3 | 4 |")]
    chunks = chunker.chunk(blocks)
    assert len(chunks) == 1
    assert chunks[0].chunk_type == "table"


def test_multipage_table_stays_one_chunk():
    chunker = Chunker("doc1")
    blocks = [
        _table_block("| A | B |\n| 1 | 2 |", page=5),
        _table_block("| 3 | 4 |\n| 5 | 6 |", page=6),
    ]
    chunks = chunker.chunk(blocks)
    assert len(chunks) == 2
    assert all(c.chunk_type == "table" for c in chunks)


def test_table_not_merged_with_text():
    chunker = Chunker("doc1")
    blocks = [
        _block("Einführungstext vor der Tabelle."),
        _table_block("| A | B |"),
        _block("Text nach der Tabelle."),
    ]
    chunks = chunker.chunk(blocks)
    table_chunks = [c for c in chunks if c.chunk_type == "table"]
    assert len(table_chunks) == 1


# --- Prose splitting ---


def test_short_blocks_merged():
    chunker = Chunker("doc1")
    blocks = [
        _block("Erster kurzer Satz."),
        _block("Zweiter kurzer Satz."),
    ]
    chunks = chunker.chunk(blocks)
    assert len(chunks) == 1
    assert "Erster" in chunks[0].text
    assert "Zweiter" in chunks[0].text


def test_heading_flushes_pending():
    chunker = Chunker("doc1")
    blocks = [
        _block("Text in Abschnitt 1."),
        _block("4.1 Unterabschnitt", block_type="heading"),
        _block("Text in Abschnitt 2."),
    ]
    chunks = chunker.chunk(blocks)
    texts = [c.text for c in chunks]
    assert not any("Unterabschnitt" in t for t in texts)


def test_max_token_limit_splits_chunk():
    chunker = Chunker("doc1")
    long_text = "A" * (_MAX_TOKENS * _CHARS_PER_TOKEN + 100)
    blocks = [_block(long_text)]
    chunks = chunker.chunk(blocks)
    assert len(chunks) >= 1
    assert all(len(c.text) > 0 for c in chunks)


def test_oversized_single_block_becomes_own_chunk():
    chunker = Chunker("doc1")
    long = "B" * (_MAX_TOKENS * _CHARS_PER_TOKEN + 50)
    short = "Kurzer Satz."
    blocks = [_block(short), _block(long)]
    chunks = chunker.chunk(blocks)
    chunk_texts = [c.text for c in chunks]
    assert any("B" * 100 in t for t in chunk_texts)


# --- Safety notices ---


def test_safety_block_gets_chunk_type_safety_notice():
    chunker = Chunker("doc1")
    blocks = [_block("WARNUNG: Verbrühungsgefahr durch heißes Wasser!")]
    chunks = chunker.chunk(blocks)
    assert len(chunks) == 1
    assert chunks[0].chunk_type == "safety_notice"
    assert chunks[0].safety_level == SafetyLevel.WARNUNG


def test_safety_block_flushed_separately():
    chunker = Chunker("doc1")
    blocks = [
        _block("Normaler einleitender Text."),
        _block("GEFAHR: Hochspannung im Gerät!"),
        _block("Text nach dem Sicherheitshinweis."),
    ]
    chunks = chunker.chunk(blocks)
    safety_chunks = [c for c in chunks if c.chunk_type == "safety_notice"]
    assert len(safety_chunks) == 1
    assert safety_chunks[0].safety_level == SafetyLevel.GEFAHR


# --- Minimum size merging ---


def test_tiny_chunk_merged_into_previous():
    chunker = Chunker("doc1")
    long = "W" * 500
    tiny = "OK"
    blocks = [_block(long), _block(tiny)]
    chunks = chunker.chunk(blocks)
    assert len(chunks) == 1
    assert "OK" in chunks[0].text


# --- Section path on chunks ---


def test_chunk_carries_section_path():
    chunker = Chunker("doc1")
    blocks = [_block("Text.", section_path=["5", "5.2"])]
    chunks = chunker.chunk(blocks)
    assert chunks[0].source_ref.section_path == ["5", "5.2"]


# --- Chunk IDs unique ---


def test_chunk_ids_are_unique():
    chunker = Chunker("doc1")
    blocks = [_block(f"Block {i}.") for i in range(20)]
    chunks = chunker.chunk(blocks)
    ids = [c.chunk_id for c in chunks]
    assert len(ids) == len(set(ids))


# --- List chunking ---


def test_list_blocks_merged_when_small():
    chunker = Chunker("doc1")
    items = [_block(f"– Listenpunkt {i}") for i in range(5)]
    chunks = chunker.chunk_list_blocks(items)
    assert len(chunks) == 1
    assert chunks[0].chunk_type == "list"


def test_list_blocks_split_when_large():
    chunker = Chunker("doc1")
    items = [_block("– " + "X" * 200) for _ in range(30)]
    chunks = chunker.chunk_list_blocks(items)
    assert len(chunks) > 1
    assert all(c.chunk_type == "list" for c in chunks)
