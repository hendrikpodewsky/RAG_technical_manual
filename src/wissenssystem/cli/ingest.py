"""Ingest a PDF into the vector store.

Usage:
    python -m wissenssystem.cli.ingest <pdf_path> --namespace <ns> [options]
"""

import argparse
import sys
import time
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest a PDF document")
    parser.add_argument("pdf_path", type=Path, help="Path to the PDF file")
    parser.add_argument("--namespace", required=True, help="Target namespace (cfg__...)")
    parser.add_argument("--db", default="data/registry.db", help="Registry DB path")
    parser.add_argument("--no-vision", action="store_true", help="Skip image description")
    args = parser.parse_args()

    if not args.pdf_path.exists():
        print(f"Error: PDF not found: {args.pdf_path}", file=sys.stderr)
        sys.exit(1)

    # Deferred imports so the CLI starts fast even without all providers loaded
    from wissenssystem.config import get_settings
    from wissenssystem.ingestion.pipeline import IngestionPipeline
    from wissenssystem.providers.docling_parser import DoclingParserAdapter
    from wissenssystem.providers.local_blob_store import LocalBlobStore
    from wissenssystem.providers.ollama_provider import OllamaLLMProvider, OllamaVisionProvider
    from wissenssystem.providers.sentence_transformer_embeddings import (
        SentenceTransformerEmbeddingProvider,
    )

    cfg = get_settings()

    print(f"Loading embedding model: {cfg.embedding_model}")
    embedder = SentenceTransformerEmbeddingProvider(cfg.embedding_model)

    print("Initialising providers…")
    parser_adapter = DoclingParserAdapter()
    blob_store = LocalBlobStore(cfg.blobs_dir)
    llm = OllamaLLMProvider(model=cfg.llm_model, ollama_url=cfg.ollama_url)
    vision = (
        None
        if args.no_vision
        else OllamaVisionProvider(model=cfg.vision_model, ollama_url=cfg.ollama_url)
    )

    # Qdrant vector store — try remote server, fall back to local file-based mode
    from qdrant_client import QdrantClient

    from wissenssystem.providers.qdrant_store import QdrantVectorStore

    try:
        client = QdrantClient(url=cfg.qdrant_url)
        client.get_collections()  # ping — raises if server not reachable
        vector_store = QdrantVectorStore(client)
        print(f"Vector store: Qdrant at {cfg.qdrant_url}")
    except Exception:  # noqa: BLE001
        qdrant_path = cfg.data_dir / "qdrant_storage"
        qdrant_path.mkdir(parents=True, exist_ok=True)
        client = QdrantClient(path=str(qdrant_path))
        vector_store = QdrantVectorStore(client)
        print(f"Vector store: Qdrant local ({qdrant_path})")

    pipeline = IngestionPipeline(
        parser=parser_adapter,
        embedder=embedder,
        vector_store=vector_store,
        blob_store=blob_store,
        vision_provider=vision,
        llm_provider=llm,
    )

    print(f"\nIngesting {args.pdf_path} → {args.namespace}")
    t0 = time.perf_counter()
    report = pipeline.ingest(args.pdf_path, args.namespace)
    elapsed = time.perf_counter() - t0

    print(f"\nIngest complete in {elapsed:.1f}s")
    print(f"  doc_id:          {report.doc_id}")
    print(f"  chunks:          {report.chunks_count}")
    print(f"  images:          {report.images_count}")
    print(f"  menu paths:      {report.menu_paths_count}")
    print(f"  safety notices:  {report.safety_notices_count}")


if __name__ == "__main__":
    main()
