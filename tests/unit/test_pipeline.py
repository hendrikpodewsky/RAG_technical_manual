from pathlib import Path
from unittest.mock import MagicMock, patch

from wissenssystem.domain.chunk import ImageChunk, TextChunk
from wissenssystem.domain.safety import SafetyLevel
from wissenssystem.domain.source import SourceRef
from wissenssystem.ingestion.pipeline import IngestionPipeline
from wissenssystem.interfaces.document_parser import ParsedBlock

NS = "cfg__test__model__1__de"
PDF = Path("data/sources/dummy.pdf")


def _make_text_chunk(chunk_id: str, text: str = "Text.", safety_level=None) -> TextChunk:
    return TextChunk(
        chunk_id=chunk_id,
        text=text,
        source_ref=SourceRef(doc_id="doc1", page=1, section_path=["1"]),
        chunk_type="prose",
        safety_level=safety_level,
        country_restriction=None,
        related_image_ids=[],
    )


def _make_image_chunk(chunk_id: str) -> ImageChunk:
    return ImageChunk(
        chunk_id=chunk_id,
        image_id="sha256abc",
        description="Kältekreis mit Kompressor.",
        caption=None,
        source_ref=SourceRef(doc_id="doc1", page=2, section_path=["2"]),
        related_text_chunk_ids=[],
    )


def _mock_parser(blocks=None) -> MagicMock:
    parser = MagicMock()
    parser.parse.return_value = blocks or []
    return parser


def _mock_embedder(dim: int = 4) -> MagicMock:
    embedder = MagicMock()
    embedder.dimension = dim
    embedder.embed.side_effect = lambda texts: [[0.1] * dim for _ in texts]
    return embedder


def _mock_vector_store(existing=None) -> MagicMock:
    vs = MagicMock()
    vs.list_namespaces.return_value = existing or []
    return vs


def _build_pipeline(
    blocks=None,
    existing_ns=None,
    dim=4,
    vision=False,
) -> tuple[IngestionPipeline, MagicMock, MagicMock]:
    parser = _mock_parser(blocks)
    embedder = _mock_embedder(dim)
    vs = _mock_vector_store(existing_ns)
    blob = MagicMock()
    blob.put.return_value = "img_sha"
    vision_prov = MagicMock() if vision else None
    if vision_prov:
        vision_prov.describe_image.return_value = "Schema."
    pipe = IngestionPipeline(parser, embedder, vs, blob, vision_provider=vision_prov)
    return pipe, vs, parser


# --- basic happy-path ---


def test_ingest_returns_report():
    pipe, vs, _ = _build_pipeline()
    with patch("wissenssystem.ingestion.pipeline.Chunker") as mock_chunker_cls:
        mock_chunker = MagicMock()
        mock_chunker.chunk.return_value = [_make_text_chunk("c1")]
        mock_chunker_cls.return_value = mock_chunker
        report = pipe.ingest(PDF, NS)
    assert report.namespace == NS
    assert report.chunks_count == 1


def test_ingest_doc_id_contains_namespace_and_stem():
    pipe, vs, _ = _build_pipeline()
    with patch("wissenssystem.ingestion.pipeline.Chunker") as mock_chunker_cls:
        mock_chunker = MagicMock()
        mock_chunker.chunk.return_value = []
        mock_chunker_cls.return_value = mock_chunker
        report = pipe.ingest(PDF, NS)
    assert NS in report.doc_id
    assert "dummy" in report.doc_id


# --- idempotency ---


def test_existing_namespace_is_deleted_before_ingest():
    pipe, vs, _ = _build_pipeline(existing_ns=[NS])
    with patch("wissenssystem.ingestion.pipeline.Chunker") as mock_chunker_cls:
        mock_chunker = MagicMock()
        mock_chunker.chunk.return_value = [_make_text_chunk("c1")]
        mock_chunker_cls.return_value = mock_chunker
        pipe.ingest(PDF, NS)
    vs.delete_namespace.assert_any_call(NS)


def test_namespace_created_with_correct_dimension():
    dim = 8
    pipe, vs, _ = _build_pipeline(dim=dim)
    with patch("wissenssystem.ingestion.pipeline.Chunker") as mock_chunker_cls:
        mock_chunker = MagicMock()
        mock_chunker.chunk.return_value = [_make_text_chunk("c1")]
        mock_chunker_cls.return_value = mock_chunker
        pipe.ingest(PDF, NS)
    vs.create_namespace.assert_any_call(NS, dim)


def test_no_namespace_created_when_no_chunks():
    pipe, vs, _ = _build_pipeline()
    with patch("wissenssystem.ingestion.pipeline.Chunker") as mock_chunker_cls:
        mock_chunker = MagicMock()
        mock_chunker.chunk.return_value = []
        mock_chunker_cls.return_value = mock_chunker
        with patch("wissenssystem.ingestion.pipeline.MenuPathExtractor") as mock_mpe:
            mock_mpe.return_value.extract.return_value = []
            pipe.ingest(PDF, NS)
    vs.create_namespace.assert_not_called()


# --- safety count ---


def test_safety_count_in_report():
    pipe, vs, _ = _build_pipeline()
    chunks = [
        _make_text_chunk("c1", safety_level=SafetyLevel.GEFAHR),
        _make_text_chunk("c2", safety_level=SafetyLevel.WARNUNG),
        _make_text_chunk("c3"),
    ]
    with patch("wissenssystem.ingestion.pipeline.Chunker") as mock_chunker_cls:
        mock_chunker = MagicMock()
        mock_chunker.chunk.return_value = chunks
        mock_chunker_cls.return_value = mock_chunker
        report = pipe.ingest(PDF, NS)
    assert report.safety_notices_count == 2


# --- menu path count ---


def test_menu_paths_stored_in_sub_namespace():
    from wissenssystem.domain.menu_path import MenuPath
    from wissenssystem.domain.source import SourceRef

    menu_path = MenuPath(
        path_id=f"{NS}__menu__0001",
        nodes=["Service", "Einstellung"],
        leaf_description="Einstellung",
        source_ref=SourceRef(doc_id="", page=1, section_path=["8"]),
        namespace=NS,
    )
    pipe, vs, _ = _build_pipeline()
    with patch("wissenssystem.ingestion.pipeline.Chunker") as mock_chunker_cls:
        mock_chunker = MagicMock()
        mock_chunker.chunk.return_value = [_make_text_chunk("c1")]
        mock_chunker_cls.return_value = mock_chunker
        with patch("wissenssystem.ingestion.pipeline.MenuPathExtractor") as mock_mpe:
            mock_mpe.return_value.extract.return_value = [menu_path]
            report = pipe.ingest(PDF, NS)
    assert report.menu_paths_count == 1
    vs.create_namespace.assert_any_call(f"{NS}__menupaths", 4)


# --- image count with vision provider ---


def test_images_counted_when_vision_provider_present():
    _PNG = b"\x89PNG\r\n\x1a\n"
    image_block = ParsedBlock(
        block_type="image",
        content="",
        page=3,
        level=None,
        position=None,
        section_path=["2"],
        image_data=_PNG,
        image_media_type="image/png",
    )
    pipe, vs, parser = _build_pipeline(blocks=[image_block], vision=True)
    parser.parse.return_value = [image_block]
    with patch("wissenssystem.ingestion.pipeline.Chunker") as mock_chunker_cls:
        mock_chunker = MagicMock()
        mock_chunker.chunk.return_value = []
        mock_chunker_cls.return_value = mock_chunker
        with patch("wissenssystem.ingestion.pipeline.MenuPathExtractor") as mock_mpe:
            mock_mpe.return_value.extract.return_value = []
            report = pipe.ingest(PDF, NS)
    assert report.images_count == 1


def test_no_images_without_vision_provider():
    _PNG = b"\x89PNG\r\n\x1a\n"
    image_block = ParsedBlock(
        block_type="image",
        content="",
        page=3,
        level=None,
        position=None,
        section_path=["2"],
        image_data=_PNG,
        image_media_type="image/png",
    )
    pipe, vs, parser = _build_pipeline(blocks=[image_block], vision=False)
    with patch("wissenssystem.ingestion.pipeline.Chunker") as mock_chunker_cls:
        mock_chunker = MagicMock()
        mock_chunker.chunk.return_value = []
        mock_chunker_cls.return_value = mock_chunker
        with patch("wissenssystem.ingestion.pipeline.MenuPathExtractor") as mock_mpe:
            mock_mpe.return_value.extract.return_value = []
            report = pipe.ingest(PDF, NS)
    assert report.images_count == 0
