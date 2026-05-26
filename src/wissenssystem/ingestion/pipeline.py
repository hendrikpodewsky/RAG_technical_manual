from pathlib import Path

from wissenssystem.domain.chunk import ImageChunk
from wissenssystem.domain.menu_path import MenuPath
from wissenssystem.ingestion.chunker import Chunker
from wissenssystem.ingestion.image_describer import ImageDescriber
from wissenssystem.ingestion.menu_path_extractor import MenuPathExtractor
from wissenssystem.ingestion.metadata import IngestReport
from wissenssystem.interfaces.blob_store import BlobStore
from wissenssystem.interfaces.document_parser import DocumentParser
from wissenssystem.interfaces.embedding_provider import EmbeddingProvider
from wissenssystem.interfaces.llm_provider import LLMProvider
from wissenssystem.interfaces.vector_store import VectorItem, VectorStore
from wissenssystem.interfaces.vision_provider import VisionProvider
from wissenssystem.retrieval.bm25_index import BM25Index


class IngestionPipeline:
    """Orchestrates PDF → chunks → embeddings → vector store.

    Steps:
    1. Parse PDF into structured blocks.
    2. Chunk text/table blocks.
    3. Extract menu navigation paths.
    4. Describe images (optional, requires VisionProvider).
    5. Embed all chunks.
    6. Idempotent upsert: delete existing namespace, then write fresh.
    7. Return IngestReport with per-type counts.
    """

    def __init__(
        self,
        parser: DocumentParser,
        embedder: EmbeddingProvider,
        vector_store: VectorStore,
        blob_store: BlobStore,
        vision_provider: VisionProvider | None = None,
        llm_provider: LLMProvider | None = None,
        bm25_dir: Path | None = None,
        vision_menu_extractor: object | None = None,
    ) -> None:
        self._parser = parser
        self._embedder = embedder
        self._vector_store = vector_store
        self._blob_store = blob_store
        self._vision = vision_provider
        self._llm = llm_provider
        self._bm25_dir = bm25_dir
        self._vision_menu_extractor = vision_menu_extractor

    def ingest(self, pdf_path: Path, namespace: str) -> IngestReport:
        doc_id = f"{namespace}__{pdf_path.stem}"

        blocks = self._parser.parse(pdf_path)

        chunker = Chunker(doc_id)
        text_chunks = chunker.chunk(blocks)

        menu_extractor = MenuPathExtractor(self._llm)
        menu_paths: list[MenuPath] = menu_extractor.extract(blocks, namespace)

        # Supplement with Vision-based menu path extraction when available.
        if self._vision_menu_extractor is not None:
            vision_paths = self._vision_menu_extractor.extract(pdf_path, namespace)
            # Deduplicate by node sequence (Vision may repeat paths found by heuristic).
            existing_node_keys = {tuple(p.nodes) for p in menu_paths}
            for vp in vision_paths:
                if tuple(vp.nodes) not in existing_node_keys:
                    menu_paths.append(vp)
                    existing_node_keys.add(tuple(vp.nodes))

        image_chunks: list[ImageChunk] = []
        if self._vision:
            describer = ImageDescriber(self._vision, doc_id)
            image_chunks = describer.describe_all(blocks, self._blob_store)

        safety_count = sum(1 for c in text_chunks if c.safety_level is not None)

        # Section chunks are hierarchy anchors; child chunks already carry the
        # heading as a text prefix, so section chunks add no retrieval signal
        # and only dilute the vector space.
        indexable_chunks = [c for c in text_chunks if c.chunk_type != "section"]

        def _embed_text(chunk: object) -> str:
            if getattr(chunk, "chunk_type", None) == "table" and getattr(chunk, "section_title", None):
                return f"{chunk.section_title}: {chunk.text}"  # type: ignore[attr-defined]
            return chunk.text  # type: ignore[attr-defined]

        # Embed text chunks and image descriptions
        text_vectors = self._embedder.embed([_embed_text(c) for c in indexable_chunks]) if indexable_chunks else []
        image_vectors = (
            self._embedder.embed([c.description for c in image_chunks]) if image_chunks else []
        )

        # Build vector items
        items: list[VectorItem] = [
            VectorItem(id=chunk.chunk_id, vector=vec, payload=chunk.model_dump())
            for chunk, vec in zip(indexable_chunks, text_vectors)
        ]
        items += [
            VectorItem(id=chunk.chunk_id, vector=vec, payload=chunk.model_dump())
            for chunk, vec in zip(image_chunks, image_vectors)
        ]

        # Store menu paths in a dedicated sub-namespace
        menu_items: list[VectorItem] = []
        if menu_paths:
            menu_ns = f"{namespace}__menupaths"
            menu_texts = [" > ".join(p.nodes) for p in menu_paths]
            menu_vectors = self._embedder.embed(menu_texts)
            menu_items = [
                VectorItem(id=p.path_id, vector=vec, payload=p.model_dump())
                for p, vec in zip(menu_paths, menu_vectors)
            ]

        # Idempotent upsert: clear stale data before writing
        existing = self._vector_store.list_namespaces()
        for ns in (namespace, f"{namespace}__menupaths"):
            if ns in existing:
                self._vector_store.delete_namespace(ns)

        dim = self._embedder.dimension
        if items:
            self._vector_store.create_namespace(namespace, dim)
            self._vector_store.upsert(namespace, items)

        if menu_items:
            menu_ns = f"{namespace}__menupaths"
            self._vector_store.create_namespace(menu_ns, dim)
            self._vector_store.upsert(menu_ns, menu_items)

        # Build and persist BM25 index for keyword retrieval
        if self._bm25_dir is not None and indexable_chunks:
            bm25 = BM25Index()
            bm25.build(
                texts=[c.text for c in indexable_chunks],
                chunk_ids=[c.chunk_id for c in indexable_chunks],
            )
            bm25.save(self._bm25_dir / f"{namespace}.pkl")

        return IngestReport(
            doc_id=doc_id,
            namespace=namespace,
            chunks_count=len(text_chunks),
            images_count=len(image_chunks),
            menu_paths_count=len(menu_paths),
            safety_notices_count=safety_count,
        )
