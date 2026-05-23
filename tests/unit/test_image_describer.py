from unittest.mock import MagicMock

from wissenssystem.ingestion.image_describer import ImageDescriber, _ext, _extract_caption
from wissenssystem.interfaces.document_parser import ParsedBlock

_PNG = b"\x89PNG\r\n\x1a\n"  # minimal PNG header
_MEDIA = "image/png"
DOC = "doc1"


def _block(
    block_type: str = "text",
    content: str = "Text.",
    page: int = 1,
    image_data: bytes | None = None,
    image_media_type: str | None = None,
    section_path: list[str] | None = None,
) -> ParsedBlock:
    return ParsedBlock(
        block_type=block_type,
        content=content,
        page=page,
        level=None,
        position=None,
        section_path=section_path or ["3"],
        image_data=image_data,
        image_media_type=image_media_type,
    )


def _img(content: str = "", page: int = 1) -> ParsedBlock:
    return _block("image", content=content, page=page, image_data=_PNG, image_media_type=_MEDIA)


def _mock_store() -> MagicMock:
    store = MagicMock()
    store.put.return_value = "abc123"
    return store


# --- _ext ---


def test_ext_jpeg():
    assert _ext("image/jpeg") == "jpg"


def test_ext_png():
    assert _ext("image/png") == "png"


def test_ext_unknown():
    assert _ext("application/octet-stream") == "bin"


# --- _extract_caption ---


def test_extract_caption_multiline():
    block = _img(content="some content\nMy Caption")
    assert _extract_caption(block) == "My Caption"


def test_extract_caption_singleline():
    block = _img(content="no newline here")
    assert _extract_caption(block) is None


def test_extract_caption_trailing_blank():
    block = _img(content="content\n   ")
    assert _extract_caption(block) is None


# --- describe_all ---


def test_describe_all_skips_non_image_blocks():
    vision = MagicMock()
    describer = ImageDescriber(vision, DOC)
    blocks = [_block("text"), _block("table", content="| A |"), _block("heading", content="§")]
    chunks = describer.describe_all(blocks, _mock_store())
    assert chunks == []
    vision.describe_image.assert_not_called()


def test_describe_all_skips_image_without_data():
    vision = MagicMock()
    describer = ImageDescriber(vision, DOC)
    block = _block("image", image_data=None, image_media_type=None)
    chunks = describer.describe_all([block], _mock_store())
    assert chunks == []


def test_describe_all_produces_one_chunk_per_image():
    vision = MagicMock()
    vision.describe_image.return_value = "Beschreibung."
    describer = ImageDescriber(vision, DOC)
    blocks = [_img(), _img()]
    chunks = describer.describe_all(blocks, _mock_store())
    assert len(chunks) == 2


def test_describe_all_calls_store_put():
    vision = MagicMock()
    vision.describe_image.return_value = "desc"
    store = _mock_store()
    describer = ImageDescriber(vision, DOC)
    describer.describe_all([_img()], store)
    store.put.assert_called_once_with(_PNG, "png")


def test_describe_all_chunk_ids_are_unique():
    vision = MagicMock()
    vision.describe_image.return_value = "d"
    describer = ImageDescriber(vision, DOC)
    blocks = [_img(), _img(), _img()]
    chunks = describer.describe_all(blocks, _mock_store())
    ids = [c.chunk_id for c in chunks]
    assert len(ids) == len(set(ids))


def test_describe_all_source_ref_page():
    vision = MagicMock()
    vision.describe_image.return_value = "d"
    describer = ImageDescriber(vision, DOC)
    chunks = describer.describe_all([_img(page=7)], _mock_store())
    assert chunks[0].source_ref.page == 7


def test_describe_all_description_stored():
    vision = MagicMock()
    vision.describe_image.return_value = "Kältekreis-Schema mit Kompressor."
    describer = ImageDescriber(vision, DOC)
    chunks = describer.describe_all([_img()], _mock_store())
    assert chunks[0].description == "Kältekreis-Schema mit Kompressor."


def test_describe_all_caption_from_content():
    vision = MagicMock()
    vision.describe_image.return_value = "d"
    describer = ImageDescriber(vision, DOC)
    block = _img(content="img\nAbb. 10 – Kältekreislauf")
    chunks = describer.describe_all([block], _mock_store())
    assert chunks[0].caption == "Abb. 10 – Kältekreislauf"


# --- context window ---


def test_context_before_and_after_passed_to_vision():
    vision = MagicMock()
    vision.describe_image.return_value = "d"
    describer = ImageDescriber(vision, DOC, context_window=1)
    blocks = [
        _block(content="Vorheriger Absatz."),
        _img(),
        _block(content="Nachfolgender Absatz."),
    ]
    describer.describe_all(blocks, _mock_store())
    call_kwargs = vision.describe_image.call_args
    context_arg = call_kwargs[1]["context"] if call_kwargs[1] else call_kwargs[0][2]
    assert "Vorheriger Absatz." in context_arg
    assert "Nachfolgender Absatz." in context_arg


def test_no_context_when_isolated():
    vision = MagicMock()
    vision.describe_image.return_value = "d"
    describer = ImageDescriber(vision, DOC, context_window=2)
    describer.describe_all([_img()], _mock_store())
    call_kwargs = vision.describe_image.call_args
    context_arg = call_kwargs[1]["context"] if call_kwargs[1] else call_kwargs[0][2]
    assert context_arg == ""
