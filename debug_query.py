"""Debug tool: trace a single query through the full RAG pipeline.

Shows intermediate results at every stage in readable tables and
writes a JSON-Lines log to data/debug_logs/.

Usage:
    python debug_query.py "your question"
    python debug_query.py "your question" --namespace cfg__bosch__ui800__nf87-02__de
    python debug_query.py "your question" --db data/registry.db --top-k 20
"""

import argparse
import json
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent / "src"))

from qdrant_client import QdrantClient

from wissenssystem.agent.intent_classifier import IntentClassifier
from wissenssystem.agent.machine_resolver import MachineResolver
from wissenssystem.config import get_settings
from wissenssystem.interfaces.llm_provider import LLMProvider, LLMResponse, Message
from wissenssystem.providers.ollama_provider import OllamaLLMProvider
from wissenssystem.providers.qdrant_store import QdrantVectorStore, _stable_id
from wissenssystem.providers.sentence_transformer_embeddings import (
    SentenceTransformerEmbeddingProvider,
)
from wissenssystem.registry.machine_registry import MachineRegistry
from wissenssystem.retrieval.bm25_index import BM25Index
from wissenssystem.retrieval.hybrid_search import _rrf

# ── Helpers ───────────────────────────────────────────────────────────────────

_W = 120  # terminal width


def _hr(char="═"):
    print(char * _W)


def _section(title: str):
    print()
    _hr("─")
    print(f"  {title}")
    _hr("─")


def _table(headers: list[str], rows: list[list[str]], col_widths: list[int]) -> None:
    def _row(cells, sep="│"):
        parts = [str(c)[:w].ljust(w) for c, w in zip(cells, col_widths)]
        print(sep + sep.join(parts) + sep)

    divider = "├" + "┼".join("─" * w for w in col_widths) + "┤"
    top = "┌" + "┬".join("─" * w for w in col_widths) + "┐"
    bot = "└" + "┴".join("─" * w for w in col_widths) + "┘"

    print(top)
    _row(headers)
    print(divider)
    for r in rows:
        _row(r)
    print(bot)


def _t(seconds: float) -> str:
    return f"{seconds*1000:.0f}ms"


def _preview(payload: dict, length: int = 180) -> str:
    text = payload.get("text") or payload.get("description") or payload.get("leaf_description", "")
    text = text.replace("\n", " ").strip()
    return text[:length] + ("…" if len(text) > length else "")


def _page(payload: dict) -> str:
    ref = payload.get("source_ref", {})
    if isinstance(ref, dict):
        p = ref.get("page", "?")
        sec = " › ".join(str(s) for s in ref.get("section_path", []))
        return f"{p} [{sec}]" if sec else str(p)
    return "?"


# ── Capturing LLM wrapper ─────────────────────────────────────────────────────


@dataclass
class LLMCall:
    stage: str
    system: str
    messages: list[dict]
    response: str
    latency_s: float


class CapturingLLMProvider(LLMProvider):
    """Wraps OllamaLLMProvider and records every call made."""

    def __init__(self, inner: OllamaLLMProvider) -> None:
        self._inner = inner
        self.calls: list[LLMCall] = []
        self._current_stage = "unknown"

    def set_stage(self, stage: str) -> None:
        self._current_stage = stage

    def complete(self, system, messages, *, temperature=0.0, max_tokens=1024) -> LLMResponse:
        t0 = time.perf_counter()
        resp = self._inner.complete(system, messages, temperature=temperature, max_tokens=max_tokens)
        self.calls.append(
            LLMCall(
                stage=self._current_stage,
                system=system,
                messages=[{"role": m.role, "content": m.content} for m in messages],
                response=resp.content,
                latency_s=time.perf_counter() - t0,
            )
        )
        return resp

    def complete_structured(self, system, messages, schema, *, temperature=0.0, max_tokens=1024):
        t0 = time.perf_counter()
        result = self._inner.complete_structured(
            system, messages, schema, temperature=temperature, max_tokens=max_tokens
        )
        self.calls.append(
            LLMCall(
                stage=self._current_stage,
                system=system,
                messages=[{"role": m.role, "content": m.content} for m in messages],
                response=result.model_dump_json() if hasattr(result, "model_dump_json") else str(result),
                latency_s=time.perf_counter() - t0,
            )
        )
        return result


# ── Main trace ────────────────────────────────────────────────────────────────


def run_trace(question: str, namespace: str, db_path: str, top_k: int, bypass_resolver: bool = False) -> dict:
    cfg = get_settings()
    log: dict[str, Any] = {
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "namespace": namespace,
    }

    # ── Providers ─────────────────────────────────────────────────────────────
    print("\nLoading providers…")
    embedder = SentenceTransformerEmbeddingProvider(cfg.embedding_model)
    inner_llm = OllamaLLMProvider(model=cfg.llm_model, ollama_url=cfg.ollama_url)
    llm = CapturingLLMProvider(inner_llm)
    registry = MachineRegistry(db_path)

    try:
        client = QdrantClient(url=cfg.qdrant_url)
        client.get_collections()
    except Exception:
        qdrant_path = cfg.data_dir / "qdrant_storage"
        client = QdrantClient(path=str(qdrant_path))

    vector_store = QdrantVectorStore(client)

    bm25_path = cfg.data_dir / "bm25" / f"{namespace}.pkl"
    bm25: BM25Index | None = None
    if bm25_path.exists():
        bm25 = BM25Index.load(bm25_path)
        print(f"  BM25 index: {len(bm25)} chunks  ({bm25_path})")
    else:
        print(f"  BM25 index: NOT FOUND at {bm25_path}")

    # ── Header ────────────────────────────────────────────────────────────────
    print()
    _hr()
    print(f"  QUERY TRACE  |  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Question: {question!r}")
    print(f"  Namespace: {namespace}  |  top_k={top_k}")
    _hr()

    # ── Stage 1: Intent ───────────────────────────────────────────────────────
    _section("STAGE 1 — INTENT CLASSIFICATION")
    llm.set_stage("intent")
    t0 = time.perf_counter()
    intent_result = IntentClassifier(llm).classify(question)
    intent_latency = time.perf_counter() - t0

    print(f"  intent:     {intent_result.intent.value}")
    print(f"  confidence: {intent_result.confidence:.2f}")
    print(f"  reasoning:  {intent_result.reasoning}")
    print(f"  latency:    {_t(intent_latency)}")
    log["intent"] = {
        "intent": intent_result.intent.value,
        "confidence": intent_result.confidence,
        "reasoning": intent_result.reasoning,
        "latency_s": intent_latency,
    }

    # ── Stage 2: Machine resolution ────────────────────────────────────────────
    _section("STAGE 2 — MACHINE RESOLUTION")
    llm.set_stage("machine_resolver")
    t0 = time.perf_counter()
    resolve_result = MachineResolver(registry, llm_provider=llm).resolve(question)
    resolve_latency = time.perf_counter() - t0

    if resolve_result.machine:
        print(f"  machine:    {resolve_result.machine.name}")
        print(f"  namespace:  {resolve_result.machine.configuration_namespace}")
        print(f"  confidence: {resolve_result.confidence:.2f}")
        # Use machine namespace if not overridden on CLI
        if namespace == "cfg__bosch__ui800__nf87-02__de":
            namespace = resolve_result.machine.configuration_namespace
    else:
        print(f"  machine:    NOT RESOLVED  (ambiguous={resolve_result.ambiguous})")
        print(f"  candidates: {[m.name for m in resolve_result.candidates]}")
    print(f"  latency:    {_t(resolve_latency)}")
    log["machine_resolution"] = {
        "machine": resolve_result.machine.name if resolve_result.machine else None,
        "namespace": resolve_result.machine.configuration_namespace if resolve_result.machine else None,
        "confidence": resolve_result.confidence,
        "latency_s": resolve_latency,
    }

    if resolve_result.machine is None:
        if bypass_resolver:
            print(f"\n  ⚠  Machine not resolved — using --bypass-resolver, continuing with namespace: {namespace}")
        else:
            print("\n  ⚠  Machine not resolved — cannot retrieve. Aborting trace.")
            print("     Tip: use --bypass-resolver to skip machine resolution and use the namespace directly.")
            return log

    # ── Stage 3: Embedding ────────────────────────────────────────────────────
    _section("STAGE 3 — EMBEDDING")
    t0 = time.perf_counter()
    query_vector = embedder.embed_one(question)
    embed_latency = time.perf_counter() - t0
    print(f"  dim:     {len(query_vector)}")
    print(f"  latency: {_t(embed_latency)}")
    log["embedding"] = {"dim": len(query_vector), "latency_s": embed_latency}

    # ── Stage 4: Vector search ─────────────────────────────────────────────────
    _section("STAGE 4 — VECTOR SEARCH")
    namespaces_in_store = set(vector_store.list_namespaces())
    image_ns = f"{namespace}__images"

    t0 = time.perf_counter()
    raw_vector_hits: dict[str, Any] = {}

    if namespace in namespaces_in_store:
        for h in vector_store.search(namespace, query_vector, top_k=top_k * 2):
            key = h.payload.get("chunk_id", h.id)
            raw_vector_hits[key] = h
        print(f"  text namespace '{namespace}': {len(raw_vector_hits)} hits")
    else:
        print(f"  ⚠  text namespace NOT FOUND in store (available: {sorted(namespaces_in_store)})")

    if image_ns in namespaces_in_store:
        before = len(raw_vector_hits)
        for h in vector_store.search(image_ns, query_vector, top_k=top_k):
            key = h.payload.get("chunk_id", h.id)
            if key not in raw_vector_hits or h.score > raw_vector_hits[key].score:
                raw_vector_hits[key] = h
        added = len(raw_vector_hits) - before
        print(f"  image namespace '{image_ns}': {added} additional hits")

    vector_latency = time.perf_counter() - t0
    print(f"  total: {len(raw_vector_hits)} unique hits  |  latency: {_t(vector_latency)}")

    sorted_vector = sorted(raw_vector_hits.items(), key=lambda x: x[1].score, reverse=True)
    rows = []
    for rank, (cid, h) in enumerate(sorted_vector):
        rows.append([
            str(rank + 1),
            cid[:22],
            f"{h.score:.4f}",
            _page(h.payload)[:14],
            _preview(h.payload, 55),
        ])
    _table(
        ["#", "chunk_id", "score", "page[sec]", "preview (55 chars)"],
        rows,
        [3, 23, 7, 15, 56],
    )
    log["vector_search"] = {
        "count": len(sorted_vector),
        "latency_s": vector_latency,
        "hits": [
            {
                "rank": i + 1,
                "chunk_id": cid,
                "score": h.score,
                "page": _page(h.payload),
                "preview": _preview(h.payload, 200),
            }
            for i, (cid, h) in enumerate(sorted_vector)
        ],
    }

    # ── Stage 5: BM25 search ───────────────────────────────────────────────────
    _section("STAGE 5 — BM25 SEARCH")
    t0 = time.perf_counter()
    bm25_ranked: list[tuple[str, float]] = []
    if bm25 is not None:
        bm25_ranked = bm25.search(question, top_k=top_k * 2)
    bm25_latency = time.perf_counter() - t0
    print(f"  hits with score > 0: {len(bm25_ranked)}  |  latency: {_t(bm25_latency)}")

    vector_ids = set(raw_vector_hits.keys())
    bm25_only = [(cid, s) for cid, s in bm25_ranked if cid not in vector_ids]

    bm25_rows = []
    for rank, (cid, score) in enumerate(bm25_ranked):
        status = "vector+BM25" if cid in vector_ids else "⚠ BM25-only"
        # Try to get payload for BM25-only hits from Qdrant directly
        preview = ""
        if cid in vector_ids:
            preview = _preview(raw_vector_hits[cid].payload, 50)
        else:
            try:
                from qdrant_client.models import FieldCondition, Filter, MatchValue
                pts = client.scroll(
                    collection_name=namespace,
                    scroll_filter=Filter(must=[FieldCondition(key="chunk_id", match=MatchValue(value=cid))]),
                    limit=1,
                    with_payload=True,
                    with_vectors=False,
                )[0]
                if pts:
                    preview = _preview(pts[0].payload or {}, 50)
                else:
                    preview = "(not in Qdrant)"
            except Exception as e:
                preview = f"(lookup error: {e})"
        bm25_rows.append([str(rank + 1), cid[:22], f"{score:.4f}", status, preview])

    _table(
        ["#", "chunk_id", "BM25score", "status", "preview (50 chars)"],
        bm25_rows or [["—", "—", "—", "no BM25 results", ""]],
        [3, 23, 10, 12, 51],
    )

    if bm25_only:
        print(f"\n  ⚠  {len(bm25_only)} BM25-only hit(s) — no vector score → WILL BE DROPPED in RRF:")
        from qdrant_client.models import FieldCondition, Filter, MatchValue
        for cid, score in bm25_only:
            print(f"     score={score:.4f}  id={cid}")
            try:
                result_scroll = client.scroll(
                    collection_name=namespace,
                    scroll_filter=Filter(must=[FieldCondition(key="chunk_id", match=MatchValue(value=cid))]),
                    limit=1,
                    with_payload=True,
                    with_vectors=False,
                )
                pts = result_scroll[0]
                if pts:
                    print(f"       payload preview: {_preview(pts[0].payload or {}, 120)}")
                else:
                    print("       NOT FOUND in Qdrant → chunk missing from vector store")
            except Exception as e:
                print(f"       (lookup failed: {e})")

    log["bm25_search"] = {
        "count": len(bm25_ranked),
        "bm25_only_count": len(bm25_only),
        "latency_s": bm25_latency,
        "hits": [{"rank": i + 1, "chunk_id": cid, "score": s} for i, (cid, s) in enumerate(bm25_ranked)],
        "bm25_only": [{"chunk_id": cid, "score": s} for cid, s in bm25_only],
    }

    # ── Stage 6: RRF fusion ────────────────────────────────────────────────────
    _section("STAGE 6 — RRF FUSION  (k=60)")
    t0 = time.perf_counter()
    rrf_scores: dict[str, float] = {}
    rrf_vector_contrib: dict[str, float] = {}
    rrf_bm25_contrib: dict[str, float] = {}

    for rank, (chunk_key, h) in enumerate(sorted_vector):
        contrib = _rrf(rank)
        rrf_scores[chunk_key] = rrf_scores.get(chunk_key, 0.0) + contrib
        rrf_vector_contrib[chunk_key] = contrib

    for rank, (cid, _) in enumerate(bm25_ranked):
        contrib = _rrf(rank)
        rrf_scores[cid] = rrf_scores.get(cid, 0.0) + contrib
        rrf_bm25_contrib[cid] = contrib

    fused = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
    # Keep only those with vector payloads
    fused_with_payload = [(cid, s) for cid, s in fused if cid in vector_ids]
    rrf_latency = time.perf_counter() - t0

    print(f"  {len(fused)} unique chunk_ids in RRF pool")
    print(f"  {len(fused) - len(fused_with_payload)} dropped (BM25-only, no vector payload)")
    print(f"  {len(fused_with_payload)} carry into next stage  |  latency: {_t(rrf_latency)}")
    print()

    rrf_rows = []
    for rank, (cid, score) in enumerate(fused_with_payload[:top_k]):
        v_rank = next((i + 1 for i, (k, _) in enumerate(sorted_vector) if k == cid), "—")
        b_rank = next((i + 1 for i, (c, _) in enumerate(bm25_ranked) if c == cid), "—")
        v_c = f"{rrf_vector_contrib.get(cid, 0):.5f}"
        b_c = f"{rrf_bm25_contrib.get(cid, 0):.5f}"
        h = raw_vector_hits[cid]
        rrf_rows.append([
            str(rank + 1), cid[:22], f"{score:.5f}",
            str(v_rank), v_c, str(b_rank), b_c,
            _preview(h.payload, 35),
        ])
    _table(
        ["#", "chunk_id", "RRF", "v_rank", "v_contrib", "b_rank", "b_contrib", "preview"],
        rrf_rows or [["—", "—", "—", "—", "—", "—", "—", "no results"]],
        [3, 23, 8, 7, 10, 7, 10, 36],
    )
    log["rrf_fusion"] = {
        "total_pool": len(fused),
        "dropped_bm25_only": len(fused) - len(fused_with_payload),
        "latency_s": rrf_latency,
        "top_results": [
            {
                "rank": i + 1,
                "chunk_id": cid,
                "rrf_score": score,
                "vector_rank": next((j + 1 for j, (k, _) in enumerate(sorted_vector) if k == cid), None),
                "bm25_rank": next((j + 1 for j, (c, _) in enumerate(bm25_ranked) if c == cid), None),
                "vector_contrib": rrf_vector_contrib.get(cid, 0),
                "bm25_contrib": rrf_bm25_contrib.get(cid, 0),
                "preview": _preview(raw_vector_hits[cid].payload, 200),
            }
            for i, (cid, score) in enumerate(fused_with_payload[:top_k])
        ],
    }

    # ── Stage 7: Reranker ──────────────────────────────────────────────────────
    from wissenssystem.retrieval.hybrid_search import SearchResult, _infer_type
    from wissenssystem.retrieval.reranker import Reranker

    pre_rerank = [
        SearchResult(
            chunk_id=cid,
            score=score,
            payload=raw_vector_hits[cid].payload,
            chunk_type=_infer_type(raw_vector_hits[cid].payload),
        )
        for cid, score in fused_with_payload[:top_k]
    ]

    _section("STAGE 7 — RERANKER  (LLM-based)")
    print(f"  input: {len(pre_rerank)} results")
    llm.set_stage("reranker")
    reranker = Reranker(llm_provider=llm)
    t0 = time.perf_counter()
    reranked = reranker.rerank(question, pre_rerank)
    rerank_latency = time.perf_counter() - t0
    print(f"  latency: {_t(rerank_latency)}")

    rerank_rows = []
    pre_ids = [r.chunk_id for r in pre_rerank]
    for out_rank, r in enumerate(reranked):
        in_rank = pre_ids.index(r.chunk_id) + 1 if r.chunk_id in pre_ids else "?"
        move = out_rank + 1 - (in_rank if isinstance(in_rank, int) else out_rank + 1)
        arrow = f"↑{-move}" if move < 0 else (f"↓{move}" if move > 0 else "=")
        rerank_rows.append([
            str(out_rank + 1), str(in_rank), arrow, r.chunk_id[:22],
            f"{r.score:.5f}", _preview(r.payload, 45),
        ])
    _table(
        ["out#", "in#", "Δ", "chunk_id", "score", "preview"],
        rerank_rows or [["—", "—", "—", "—", "—", "no results"]],
        [5, 4, 4, 23, 8, 46],
    )
    log["reranker"] = {
        "input_count": len(pre_rerank),
        "latency_s": rerank_latency,
        "output": [{"rank": i + 1, "chunk_id": r.chunk_id, "rrf_score": r.score} for i, r in enumerate(reranked)],
    }

    # ── Stage 8: Answer generation ─────────────────────────────────────────────
    from wissenssystem.agent.answer_generator import AnswerGenerator
    from wissenssystem.retrieval.menu_path_search import MenuPathSearch

    _section("STAGE 8 — ANSWER GENERATION")
    llm.set_stage("answer_generator")
    menu_hits = []
    if intent_result.intent.value == "menu_navigation":
        menu_search = MenuPathSearch(vector_store, embedder)
        menu_hits = menu_search.search(question, namespace)
        print(f"  menu hits: {len(menu_hits)}")

    answer_gen = AnswerGenerator(llm)
    t0 = time.perf_counter()
    answer = answer_gen.generate(question, reranked, menu_hits)
    answer_latency = time.perf_counter() - t0
    print(f"  latency: {_t(answer_latency)}")

    # Show the full prompt that was sent to LLM
    gen_call = next((c for c in reversed(llm.calls) if c.stage == "answer_generator"), None)
    if gen_call:
        print()
        print("  ── System prompt ──────────────────────────────────────────────────")
        for line in gen_call.system.splitlines():
            print(f"  {line}")
        print()
        print("  ── User message (passages + question) ─────────────────────────────")
        user_msg = gen_call.messages[0]["content"] if gen_call.messages else ""
        for line in user_msg.splitlines():
            print(f"  {line}")

    log["answer_generation"] = {
        "latency_s": answer_latency,
        "system_prompt": gen_call.system if gen_call else None,
        "user_message": gen_call.messages[0]["content"] if gen_call and gen_call.messages else None,
        "answer": answer,
    }

    # ── Stage 9: Final answer ──────────────────────────────────────────────────
    _section("STAGE 9 — FINAL ANSWER")
    print()
    for line in answer.splitlines():
        print(f"  {line}")

    # ── Summary ───────────────────────────────────────────────────────────────
    total_llm = sum(c.latency_s for c in llm.calls)
    total = sum([
        intent_latency, resolve_latency, embed_latency,
        vector_latency, bm25_latency, rrf_latency, rerank_latency, answer_latency,
    ])
    _section("TIMING SUMMARY")
    timings = [
        ("Intent classification", intent_latency),
        ("Machine resolution", resolve_latency),
        ("Embedding", embed_latency),
        ("Vector search", vector_latency),
        ("BM25 search", bm25_latency),
        ("RRF fusion", rrf_latency),
        ("Reranker", rerank_latency),
        ("Answer generation", answer_latency),
    ]
    for name, t in timings:
        bar = "█" * int(t / total * 40)
        print(f"  {name:<25} {_t(t):>7}  {bar}")
    print()
    print(f"  {'TOTAL':<25} {_t(total):>7}  (LLM calls: {_t(total_llm)})")

    log["timing"] = {s: t for s, t in timings}
    log["llm_calls"] = [
        {"stage": c.stage, "latency_s": c.latency_s} for c in llm.calls
    ]

    return log


def main():
    parser = argparse.ArgumentParser(description="Debug RAG pipeline for a single query")
    parser.add_argument("question", help="The question to trace")
    parser.add_argument(
        "--namespace",
        default="cfg__bosch__ui800__nf87-02__de",
        help="Namespace to search (default: cfg__bosch__ui800__nf87-02__de)",
    )
    parser.add_argument("--db", default="data/registry.db", help="Registry DB path")
    parser.add_argument("--top-k", type=int, default=10, help="Top-K for retrieval (default: 10)")
    parser.add_argument("--log-dir", default="data/debug_logs", help="Directory for JSON-Lines logs")
    parser.add_argument(
        "--bypass-resolver",
        action="store_true",
        help="Skip machine resolution and use --namespace directly (for debugging retrieval)",
    )
    args = parser.parse_args()

    log = run_trace(args.question, args.namespace, args.db, args.top_k, bypass_resolver=args.bypass_resolver)

    log_dir = Path(args.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    safe_q = "".join(c if c.isalnum() else "_" for c in args.question[:40])
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = log_dir / f"{ts}_{safe_q}.jsonl"
    with log_path.open("w", encoding="utf-8") as f:
        f.write(json.dumps(log, ensure_ascii=False, default=str) + "\n")

    print()
    _hr()
    print(f"  Log written to: {log_path}")
    _hr()


if __name__ == "__main__":
    main()
