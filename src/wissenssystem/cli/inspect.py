"""Inspect and filter chunks in a Qdrant namespace.

Usage:
    python -m wissenssystem.cli.inspect [options]

Options:
    --namespace NS      Target namespace (default: first available)
    --type TYPE         Filter by chunk_type (prose|table|safety_notice|list|image)
    --section SEC       Filter by section_id prefix (e.g. "4" matches 4, 4.1, 4.2 ...)
    --search TEXT       Case-insensitive text search within chunk content
    --hyde              Show HyDE questions for matching chunks
    --full              Print complete chunk text (default: 120-char preview)
    --stats             Print aggregate statistics and exit
    --limit N           Max chunks to print (default: 50, 0 = all)
    --page P            Filter by page number
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


def _tokens(text: str) -> int:
    return max(1, len(text) // 4)


def _preview(text: str, width: int = 120) -> str:
    return text.replace("\n", " ").replace("\t", " ")[:width]


def _load_all_points(client, namespace: str) -> list:
    points = []
    offset = None
    while True:
        batch, offset = client.scroll(
            collection_name=namespace,
            limit=200,
            offset=offset,
            with_payload=True,
            with_vectors=False,
        )
        points.extend(batch)
        if offset is None:
            break
    return points


def _hyde_map(client, hyde_ns: str) -> dict[str, list[str]]:
    """Return {source_chunk_id: [question, ...]} from the HyDE namespace."""
    mapping: dict[str, list[str]] = {}
    try:
        points = _load_all_points(client, hyde_ns)
        for p in points:
            src = p.payload.get("source_chunk_id", "")
            q = p.payload.get("text", "")
            if src and q:
                mapping.setdefault(src, []).append(q)
    except Exception:
        pass
    return mapping


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Inspect chunks in a Qdrant namespace",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--namespace", default="", help="Target namespace (default: auto-detect)")
    parser.add_argument(
        "--type",
        dest="chunk_type",
        default="",
        help="Filter by chunk_type (prose|table|safety_notice|list|image)",
    )
    parser.add_argument("--section", default="", help="Filter by section_id prefix")
    parser.add_argument("--search", default="", help="Case-insensitive text search")
    parser.add_argument("--hyde", action="store_true", help="Show HyDE questions per chunk")
    parser.add_argument("--full", action="store_true", help="Print complete chunk text")
    parser.add_argument("--stats", action="store_true", help="Print statistics and exit")
    parser.add_argument("--limit", type=int, default=50, help="Max results (0 = all)")
    parser.add_argument("--page", type=int, default=0, help="Filter by page number (0 = all)")
    args = parser.parse_args()

    from qdrant_client import QdrantClient

    from wissenssystem.config import get_settings

    cfg = get_settings()
    qdrant_path = cfg.data_dir / "qdrant_storage"
    try:
        client = QdrantClient(path=str(qdrant_path))
    except RuntimeError as exc:
        if "already accessed" in str(exc):
            print(
                "ERROR: Qdrant storage is locked by another process (e.g. Streamlit).\n"
                "Stop it first:  pkill -f streamlit\n"
                "Then re-run this command.",
                file=sys.stderr,
            )
            sys.exit(1)
        raise

    all_ns = [c.name for c in client.get_collections().collections]
    # Main namespaces only (exclude sub-namespaces like __hyde, __menupaths)
    _sub = ("__hyde", "__menupaths", "__images")
    main_ns = [n for n in all_ns if not any(n.endswith(s) for s in _sub)]

    if not main_ns:
        print("No namespaces found in the vector store.")
        sys.exit(1)

    namespace = args.namespace or main_ns[0]
    if namespace not in all_ns:
        print(f"Namespace '{namespace}' not found.")
        print(f"Available: {main_ns}")
        sys.exit(1)

    points = _load_all_points(client, namespace)
    # Sort by chunk_id for stable output
    points.sort(key=lambda p: p.payload.get("chunk_id", str(p.id)))

    # ── Stats mode ───────────────────────────────────────────────────────────
    if args.stats:
        from collections import Counter

        types: Counter = Counter()
        sections: Counter = Counter()
        total_tokens = 0
        for p in points:
            pay = p.payload or {}
            ctype = pay.get("chunk_type") or ("image" if "image_id" in pay else "unknown")
            types[ctype] += 1
            sid = pay.get("section_id") or ""
            stitle = pay.get("section_title") or ""
            label = f"{sid}  {stitle}".strip() if sid else "(no section)"
            sections[label] += 1
            total_tokens += _tokens(pay.get("text", "") or pay.get("description", ""))

        hyde_ns = f"{namespace}__hyde"
        hyde_count = client.count(hyde_ns).count if hyde_ns in all_ns else 0

        print(f"\nChunk Statistics — {namespace}")
        print("═" * 60)
        print(f"Total points:   {len(points)}")
        print(f"Total tokens:   {total_tokens:,}")
        if hyde_count:
            print(f"HyDE questions: {hyde_count}")
        print()
        print("By type:")
        for ctype, cnt in types.most_common():
            pct = cnt / len(points) * 100
            print(f"  {ctype:<18} {cnt:>4}  ({pct:.1f}%)")
        print()
        print("By section (top 20):")
        for label, cnt in sections.most_common(20):
            print(f"  {cnt:>4}  {label}")
        return

    # ── Filtering ────────────────────────────────────────────────────────────
    filtered = []
    search_lower = args.search.lower()
    for p in points:
        pay = p.payload or {}
        ctype = pay.get("chunk_type") or ("image" if "image_id" in pay else "unknown")
        text = pay.get("text") or pay.get("description", "")
        section_id = pay.get("section_id") or ""
        source_ref = pay.get("source_ref") or {}
        page = source_ref.get("page", 0) or 0

        if args.chunk_type and ctype != args.chunk_type:
            continue
        if args.section and not section_id.startswith(args.section):
            continue
        if args.page and page != args.page:
            continue
        if search_lower and search_lower not in text.lower():
            continue
        filtered.append((p, ctype, text, section_id, page))

    limit = args.limit if args.limit > 0 else len(filtered)

    # ── Load HyDE if requested ────────────────────────────────────────────────
    hyde_data: dict[str, list[str]] = {}
    if args.hyde:
        hyde_ns = f"{namespace}__hyde"
        if hyde_ns in all_ns:
            hyde_data = _hyde_map(client, hyde_ns)
        else:
            print(f"(no HyDE namespace found: {hyde_ns})")

    # ── Header ───────────────────────────────────────────────────────────────
    filters = []
    if args.chunk_type:
        filters.append(f"type={args.chunk_type}")
    if args.section:
        filters.append(f"section={args.section}")
    if args.search:
        filters.append(f"search='{args.search}'")
    if args.page:
        filters.append(f"page={args.page}")
    filter_str = "  filter: " + ", ".join(filters) if filters else ""

    print(f"\nNamespace: {namespace}{filter_str}")
    print(f"Showing {min(limit, len(filtered))} of {len(filtered)} matching chunks\n")

    col_w = 38
    cols = f"{'#':>4}  {'chunk_id':<{col_w}}  {'type':<15}  {'sec':>6}  {'pg':>3}  {'toks':>5}"
    print(f"{cols}  preview")
    print("─" * 130)

    for i, (p, ctype, text, section_id, page) in enumerate(filtered[:limit]):
        pay = p.payload or {}
        chunk_id = pay.get("chunk_id", str(p.id))
        short_id = chunk_id.split("__")[-1] if "__" in chunk_id else chunk_id
        toks = _tokens(text)
        sec = section_id or "—"
        meta = f"{i + 1:>4}  {short_id:<{col_w}}  {ctype:<15}  {sec:>6}  {str(page):>3}  {toks:>5}"
        print(f"{meta}  {_preview(text)}")

        if args.full:
            print()
            print(text)
            print()
        elif text and not args.full:
            pass  # preview already shown inline

        if args.hyde:
            questions = hyde_data.get(chunk_id, [])
            for q in questions:
                print(f"       ❓ {q}")
            if not questions:
                print("       (no HyDE questions)")
            print()

    print("─" * 130)
    if len(filtered) > limit:
        print(f"(+{len(filtered) - limit} more — use --limit 0 to show all)")


if __name__ == "__main__":
    main()
