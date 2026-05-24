"""Eval runner for the agentic RAG system.

Usage:
    python eval/run_eval.py [--questions PATH] [--db PATH] [--output PATH]
"""

import argparse
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from wissenssystem.agent.answer_generator import AnswerGenerator
from wissenssystem.agent.intent_classifier import IntentClassifier
from wissenssystem.agent.machine_resolver import MachineResolver
from wissenssystem.agent.orchestrator import AnswerResult, Orchestrator
from wissenssystem.config import get_settings
from wissenssystem.providers.ollama_provider import OllamaLLMProvider
from wissenssystem.providers.qdrant_store import QdrantVectorStore
from wissenssystem.providers.sentence_transformer_embeddings import (
    SentenceTransformerEmbeddingProvider,
)
from wissenssystem.registry.machine_registry import MachineRegistry
from wissenssystem.retrieval.hybrid_search import HybridSearch
from wissenssystem.retrieval.menu_path_search import MenuPathSearch
from wissenssystem.retrieval.reranker import Reranker


@dataclass
class EvalResult:
    question_id: str
    question: str
    answer: str
    passed: bool
    failures: list[str] = field(default_factory=list)
    latency_s: float = 0.0


def _check(result: AnswerResult, question: dict) -> tuple[bool, list[str]]:
    answer = result.answer.lower()
    failures = []

    should_be_answerable = question.get("should_be_answerable", True)
    no_info_response = "mir liegt dazu keine information vor"

    if should_be_answerable and no_info_response in answer:
        failures.append("should be answerable but got no-info response")

    if not should_be_answerable and no_info_response not in answer:
        failures.append("should be unanswerable but got a real answer")

    for topic in question.get("expected_topics") or []:
        if topic.lower() not in answer:
            failures.append(f"missing topic: {topic!r}")

    safety_quote = question.get("expected_safety_quote")
    if safety_quote and safety_quote.upper() not in result.answer.upper():
        failures.append(f"missing safety keyword: {safety_quote!r}")

    expected_path = question.get("expected_menu_path")
    if expected_path:
        found = any(h.nodes == expected_path for h in result.menu_hits)
        if not found:
            failures.append(f"missing menu path: {expected_path}")

    return len(failures) == 0, failures


def _build_orchestrator(cfg, registry) -> Orchestrator:
    embedder = SentenceTransformerEmbeddingProvider(cfg.embedding_model)
    llm = OllamaLLMProvider(model=cfg.llm_model, ollama_url=cfg.ollama_url)

    from qdrant_client import QdrantClient

    try:
        client = QdrantClient(url=cfg.qdrant_url)
        client.get_collections()
    except Exception:
        qdrant_path = cfg.data_dir / "qdrant_storage"
        qdrant_path.mkdir(parents=True, exist_ok=True)
        client = QdrantClient(path=str(qdrant_path))

    vector_store = QdrantVectorStore(client)

    return Orchestrator(
        intent_classifier=IntentClassifier(llm),
        machine_resolver=MachineResolver(registry, llm_provider=llm),
        hybrid_search=HybridSearch(
            vector_store, embedder,
            top_k=cfg.retrieval_top_k,
            bm25_dir=cfg.data_dir / "bm25",
        ),
        answer_generator=AnswerGenerator(llm),
        reranker=Reranker(llm_provider=llm),
        menu_path_search=MenuPathSearch(vector_store, embedder),
        machine_confidence_threshold=cfg.machine_resolution_threshold,
    )


def _md_report(results: list[EvalResult]) -> str:
    passed = sum(1 for r in results if r.passed)
    total = len(results)
    score = passed / total * 100 if total else 0

    lines = [
        "# Eval-Report\n",
        f"**Score: {passed}/{total} ({score:.0f}%)**\n",
        "",
        "| ID | Frage | Pass | Latenz | Fehler |",
        "|----|-------|------|--------|--------|",
    ]
    for r in results:
        status = "✅" if r.passed else "❌"
        failures = "; ".join(r.failures) if r.failures else "—"
        q = r.question[:60] + "…" if len(r.question) > 60 else r.question
        lines.append(f"| {r.question_id} | {q} | {status} | {r.latency_s:.1f}s | {failures} |")

    lines += [
        "",
        "## Antworten\n",
    ]
    for r in results:
        lines.append(f"### {r.question_id}: {r.question}\n")
        lines.append(f"**Pass:** {'✅' if r.passed else '❌'}\n")
        lines.append(r.answer)
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--questions", default="eval/questions.yaml")
    parser.add_argument("--db", default="data/registry.db")
    parser.add_argument("--output", default="eval/report.md")
    args = parser.parse_args()

    questions_path = Path(args.questions)
    if not questions_path.exists():
        print(f"Questions file not found: {questions_path}", file=sys.stderr)
        sys.exit(1)

    data = yaml.safe_load(questions_path.read_text(encoding="utf-8"))
    questions = data.get("questions", [])

    cfg = get_settings()
    registry = MachineRegistry(args.db)
    orch = _build_orchestrator(cfg, registry)

    print(f"Running {len(questions)} questions…\n")
    results: list[EvalResult] = []

    for q in questions:
        t0 = time.perf_counter()
        try:
            result = orch.answer(q["question"])
        except Exception as exc:
            result = type(
                "R",
                (),
                {
                    "answer": f"[ERROR: {exc}]",
                    "menu_hits": [],
                    "needs_clarification": False,
                },
            )()  # type: ignore[assignment]
        latency = time.perf_counter() - t0

        passed, failures = _check(result, q)  # type: ignore[arg-type]
        icon = "✅" if passed else "❌"
        print(f"{icon} {q['id']}: {q['question'][:60]}")
        if failures:
            for f in failures:
                print(f"     → {f}")

        results.append(
            EvalResult(
                question_id=q["id"],
                question=q["question"],
                answer=result.answer,
                passed=passed,
                failures=failures,
                latency_s=latency,
            )
        )

    passed_count = sum(1 for r in results if r.passed)
    print(f"\nScore: {passed_count}/{len(results)} ({passed_count / len(results) * 100:.0f}%)")

    report = _md_report(results)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    print(f"Report written to {output_path}")


if __name__ == "__main__":
    main()
