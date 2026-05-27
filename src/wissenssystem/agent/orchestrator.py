from dataclasses import dataclass, field

from wissenssystem.agent.answer_generator import AnswerGenerator
from wissenssystem.agent.intent_classifier import Intent, IntentClassifier, IntentResult
from wissenssystem.agent.machine_resolver import MachineResolver
from wissenssystem.retrieval.hybrid_search import HybridSearch, SearchResult
from wissenssystem.retrieval.menu_path_search import MenuPathHit, MenuPathSearch
from wissenssystem.retrieval.reranker import Reranker

# Image chunks whose description matches these substrings are decorative
# (logos, icons, warning symbols) and should not be shown as attachments.
_DECORATIVE_KEYWORDS = (
    "Logo",
    "Markenzeichen",
    "Herstellerlogo",
    "Unternehmenslogo",
    "Wortmarke",
    "Ikonografisches Symbol",
    "Funktionssymbol / Icon",
    "Symboldarstellung",
    "Warnsymbol",
    "Warnschild-Symbol",
    "Informationssymbol",
    "Hinweissymbol",
    "Info-Icon",
)

_MAX_IMAGE_ATTACHMENTS = 3
_TOP_N_FOR_IMAGES = 8  # look at top-N reranked results; image chunks rank below prose


def _extract_image_ids(results: list[SearchResult]) -> list[str]:
    """Return up to _MAX_IMAGE_ATTACHMENTS relevant image IDs from top results.

    Only looks at the top _TOP_N_FOR_IMAGES results, skips decorative images
    (logos, icons, symbols), and deduplicates.
    """
    seen: list[str] = []
    for r in results[:_TOP_N_FOR_IMAGES]:
        img_id = r.payload.get("image_id")
        if not img_id:
            continue
        desc = r.payload.get("description", "")
        if any(kw in desc for kw in _DECORATIVE_KEYWORDS):
            continue
        if img_id not in seen:
            seen.append(img_id)
        if len(seen) >= _MAX_IMAGE_ATTACHMENTS:
            break
    return seen


@dataclass
class AnswerResult:
    answer: str
    intent: IntentResult
    machine_namespace: str | None
    sources: list[SearchResult] = field(default_factory=list)
    menu_hits: list[MenuPathHit] = field(default_factory=list)
    needs_clarification: bool = False
    clarification_prompt: str | None = None
    image_ids: list[str] = field(default_factory=list)


class Orchestrator:
    """Two-stage agent:

    Stage 1 — Resolver:
        IntentClassifier → MachineResolver → confidence check.
        If machine confidence < threshold: return clarification request.

    Stage 2 — Retrieve + Generate:
        HybridSearch + (MenuPathSearch if intent=menu_navigation) →
        Reranker → AnswerGenerator.
    """

    def __init__(
        self,
        intent_classifier: IntentClassifier,
        machine_resolver: MachineResolver,
        hybrid_search: HybridSearch,
        answer_generator: AnswerGenerator,
        reranker: Reranker | None = None,
        menu_path_search: MenuPathSearch | None = None,
        machine_confidence_threshold: float = 0.75,
    ) -> None:
        self._intent = intent_classifier
        self._resolver = machine_resolver
        self._search = hybrid_search
        self._generator = answer_generator
        self._reranker = reranker or Reranker()
        self._menu_search = menu_path_search
        self._threshold = machine_confidence_threshold

    def answer(self, question: str, context: dict | None = None) -> AnswerResult:
        # Stage 1: classify + resolve
        intent_result = self._intent.classify(question)
        resolve_result = self._resolver.resolve(question)

        if resolve_result.ambiguous or (
            resolve_result.machine is None and resolve_result.confidence < self._threshold
        ):
            candidates = ", ".join(m.name for m in resolve_result.candidates[:3])
            return AnswerResult(
                answer="",
                intent=intent_result,
                machine_namespace=None,
                needs_clarification=True,
                clarification_prompt=(
                    f"Welche Maschine meinst du? "
                    f"Mögliche Kandidaten: {candidates or 'keine bekannten Maschinen'}."
                ),
            )

        if resolve_result.machine is None:
            return AnswerResult(
                answer="Mir liegt dazu keine Information vor.",
                intent=intent_result,
                machine_namespace=None,
            )

        namespace = resolve_result.machine.configuration_namespace

        # Stage 2: retrieve
        results = self._search.search(question, namespace)
        results = self._reranker.rerank(question, results)

        menu_hits: list[MenuPathHit] = []
        if intent_result.intent == Intent.MENU_NAVIGATION and self._menu_search:
            menu_hits = self._menu_search.search(question, namespace)

        answer_text = self._generator.generate(question, results, menu_hits)

        image_ids = _extract_image_ids(results)

        return AnswerResult(
            answer=answer_text,
            intent=intent_result,
            machine_namespace=namespace,
            sources=results,
            menu_hits=menu_hits,
            image_ids=image_ids,
        )
