"""Streamlit UI for the agentic RAG system."""

import base64
import re

import streamlit as st

from wissenssystem.agent.answer_generator import AnswerGenerator
from wissenssystem.agent.intent_classifier import IntentClassifier
from wissenssystem.agent.machine_resolver import MachineResolver
from wissenssystem.agent.orchestrator import AnswerResult, Orchestrator
from wissenssystem.config import get_settings
from wissenssystem.providers.local_blob_store import LocalBlobStore
from wissenssystem.providers.ollama_provider import OllamaLLMProvider
from wissenssystem.providers.qdrant_store import QdrantVectorStore
from wissenssystem.providers.sentence_transformer_embeddings import (
    SentenceTransformerEmbeddingProvider,
)
from wissenssystem.registry.machine_registry import MachineRegistry
from wissenssystem.retrieval.hybrid_search import HybridSearch
from wissenssystem.retrieval.menu_path_search import MenuPathSearch
from wissenssystem.retrieval.reranker import Reranker

# ── Page setup ──────────────────────────────────────────────────────────────


st.set_page_config(
    page_title="Wissenssystem – Maschinen-Anleitung",
    page_icon="⚙️",
    layout="wide",
)


# ── Cached providers (loaded once per session) ───────────────────────────────


@st.cache_resource
def _load_resources():
    cfg = get_settings()

    embedder = SentenceTransformerEmbeddingProvider(cfg.embedding_model)
    llm = OllamaLLMProvider(model=cfg.llm_model, base_url=cfg.ollama_url)
    blob_store = LocalBlobStore(cfg.blobs_dir)

    try:
        from qdrant_client import QdrantClient
        client = QdrantClient(url=cfg.qdrant_url)
        client.get_collections()  # ping
    except Exception:
        from qdrant_client import QdrantClient
        client = QdrantClient(":memory:")

    vector_store = QdrantVectorStore(client)
    registry = MachineRegistry(cfg.registry_db_path)

    orch = Orchestrator(
        intent_classifier=IntentClassifier(llm),
        machine_resolver=MachineResolver(registry, llm_provider=llm),
        hybrid_search=HybridSearch(vector_store, embedder, top_k=cfg.retrieval_top_k),
        answer_generator=AnswerGenerator(llm),
        reranker=Reranker(llm_provider=llm),
        menu_path_search=MenuPathSearch(vector_store, embedder),
        machine_confidence_threshold=cfg.machine_resolution_threshold,
    )
    return orch, blob_store, registry


# ── Helpers ──────────────────────────────────────────────────────────────────


def _render_image_tag(image_id: str, blob_store: LocalBlobStore) -> str:
    try:
        data = blob_store.get(image_id)
        b64 = base64.b64encode(data).decode()
        return f'<img src="data:image/png;base64,{b64}" style="max-width:100%;" />'
    except Exception:
        return f"*[Bild {image_id} nicht verfügbar]*"


def _replace_image_refs(text: str, blob_store: LocalBlobStore) -> str:
    def replace(match):
        return _render_image_tag(match.group(1), blob_store)
    return re.sub(r"\[BILD:([^\]]+)\]", replace, text)


def _render_sources(result: AnswerResult) -> None:
    if not result.sources and not result.menu_hits:
        return
    with st.expander("Quellen", expanded=False):
        for r in result.sources:
            ref = r.payload.get("source_ref", {})
            if isinstance(ref, dict):
                page = ref.get("page", "?")
                section = " › ".join(ref.get("section_path", []))
                st.markdown(f"- Seite **{page}** — {section} *(score: {r.score:.2f})*")
        for h in result.menu_hits:
            st.markdown(f"- Menüpfad: **{h.breadcrumb}** (Seite {h.page})")


# ── Main UI ──────────────────────────────────────────────────────────────────


def main() -> None:
    orch, blob_store, registry = _load_resources()

    st.title("⚙️ Maschinen-Wissenssystem")
    st.caption("Stell Fragen zu deinen Maschinen-Bedienungsanleitungen.")

    # Sidebar: machine info
    machines = registry.list_machines()
    with st.sidebar:
        st.header("Bekannte Maschinen")
        if machines:
            for m in machines:
                st.markdown(f"**{m.name}**")
                if m.aliases:
                    st.caption(", ".join(m.aliases))
        else:
            st.info("Keine Maschinen registriert. Führe `seed_registry` aus.")

    # Session state
    if "history" not in st.session_state:
        st.session_state.history = []
    if "pending_clarification" not in st.session_state:
        st.session_state.pending_clarification = False

    # Render chat history
    for entry in st.session_state.history:
        with st.chat_message(entry["role"]):
            if entry.get("html"):
                st.markdown(entry["content"], unsafe_allow_html=True)
            else:
                st.markdown(entry["content"])

    # Input
    user_input = st.chat_input("Deine Frage…")
    if not user_input:
        return

    st.session_state.history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Suche…"):
            result = orch.answer(user_input)

        if result.needs_clarification:
            st.warning(result.clarification_prompt)
            st.session_state.history.append(
                {"role": "assistant", "content": result.clarification_prompt or ""}
            )
            return

        # Replace [BILD:id] tokens with inline images
        rendered = _replace_image_refs(result.answer, blob_store)
        has_images = "[BILD:" in result.answer

        st.markdown(rendered, unsafe_allow_html=has_images)
        _render_sources(result)

        st.session_state.history.append(
            {"role": "assistant", "content": rendered, "html": has_images}
        )


if __name__ == "__main__":
    main()
