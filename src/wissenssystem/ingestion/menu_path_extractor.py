import re
from pathlib import Path

from pydantic import BaseModel

from wissenssystem.domain.menu_path import MenuPath
from wissenssystem.domain.source import SourceRef
from wissenssystem.interfaces.document_parser import ParsedBlock
from wissenssystem.interfaces.llm_provider import LLMProvider, Message

_BULLET_RE = re.compile(r"^(\s*)([-–—•*]|\d+[.\)])\s+(.*)")
_INDENT_UNIT = 2

_PROMPT_PATH = Path(__file__).parent.parent.parent.parent / "prompts" / "menu_path_extraction.md"


def _load_prompt() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")


class _LLMPath(BaseModel):
    nodes: list[str]


class _LLMResult(BaseModel):
    paths: list[_LLMPath]


def _parse_item(line: str) -> tuple[int, str] | None:
    """Returns (indent_depth, label) for a bullet/numbered list line, else None."""
    m = _BULLET_RE.match(line)
    if not m:
        return None
    label = m.group(3).strip()
    if not label:
        return None
    depth = len(m.group(1)) // _INDENT_UNIT
    return depth, label


class MenuPathExtractor:
    """Extracts hierarchical menu paths from parsed document blocks.

    Stage 1: heuristic bullet/indent detection.
    Stage 2: optional LLM fallback when heuristic yields no results.
    """

    def __init__(self, llm_provider: LLMProvider | None = None) -> None:
        self._llm = llm_provider

    def extract(self, blocks: list[ParsedBlock], namespace: str) -> list[MenuPath]:
        """Return all menu paths found in blocks, associated with namespace."""
        raw_items = self._collect_items(blocks)
        if raw_items:
            return self._build_paths(raw_items, namespace)
        if self._llm:
            return self._extract_with_llm(blocks, namespace)
        return []

    # --- heuristic stage ---

    def _collect_items(
        self, blocks: list[ParsedBlock]
    ) -> list[tuple[int, str, SourceRef]]:
        """Parse all blocks into (depth, label, source_ref) tuples."""
        items: list[tuple[int, str, SourceRef]] = []
        for block in blocks:
            if block.block_type not in ("text", "heading"):
                continue
            ref = SourceRef(
                doc_id="",
                page=block.page,
                section_path=block.section_path,
            )
            lines = block.content.splitlines()
            for line in lines:
                parsed = _parse_item(line)
                if parsed is None:
                    continue
                heuristic_depth, label = parsed
                # Level field (set by docling for structured lists) takes precedence
                depth = block.level if block.level is not None else heuristic_depth
                items.append((depth, label, ref))
        return items

    def _build_paths(
        self,
        items: list[tuple[int, str, SourceRef]],
        namespace: str,
    ) -> list[MenuPath]:
        paths: list[MenuPath] = []
        counter = 0
        # stack holds (depth, label) for the current ancestor chain
        stack: list[tuple[int, str]] = []

        for depth, label, ref in items:
            while stack and stack[-1][0] >= depth:
                stack.pop()
            stack.append((depth, label))

            nodes = [s[1] for s in stack]
            counter += 1
            paths.append(
                MenuPath(
                    path_id=f"{namespace}__menu__{counter:04d}",
                    nodes=nodes,
                    leaf_description=label,
                    source_ref=ref,
                    namespace=namespace,
                )
            )

        return paths

    # --- LLM stage ---

    def _extract_with_llm(
        self, blocks: list[ParsedBlock], namespace: str
    ) -> list[MenuPath]:
        text = "\n".join(b.content for b in blocks if b.content.strip())
        if not text:
            return []
        ref = SourceRef(
            doc_id="",
            page=blocks[0].page if blocks else 1,
            section_path=blocks[0].section_path if blocks else [],
        )
        prompt = _load_prompt()
        result: _LLMResult = self._llm.complete_structured(  # type: ignore[union-attr]
            system=prompt,
            messages=[Message(role="user", content=text)],
            schema=_LLMResult,
        )
        paths = []
        for i, path in enumerate(result.paths, start=1):
            if not path.nodes:
                continue
            paths.append(
                MenuPath(
                    path_id=f"{namespace}__menu__{i:04d}",
                    nodes=path.nodes,
                    leaf_description=path.nodes[-1],
                    source_ref=ref,
                    namespace=namespace,
                )
            )
        return paths
