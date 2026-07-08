# ARCHITECTURE.md — Technische Architektur

> Lies dies **nach** `PROJECT.md`. Diese Datei legt Module, Interfaces und
> Datenmodelle fest. Code muss diesen Vorgaben folgen.

## 1 · Verzeichnisstruktur (verbindlich)

```
wissenssystem/
├── PROJECT.md
├── ARCHITECTURE.md
├── TASKS.md
├── README.md
├── CLAUDE.md
├── pyproject.toml
├── .env.example
├── .gitignore
├── debug_query.py                # Trace-Tool: eine Query durch alle Pipeline-Stufen
│
├── src/wissenssystem/
│   ├── __init__.py
│   ├── config.py                 # pydantic-settings, lädt .env
│   ├── logging_setup.py          # structlog-Konfiguration
│   │
│   ├── domain/                   # reine Datenklassen, keine I/O
│   │   ├── chunk.py              # TextChunk, ImageChunk
│   │   ├── machine.py            # Machine, Configuration
│   │   ├── menu_path.py          # MenuPath, MenuNode
│   │   ├── namespace.py          # build_namespace / parse_namespace
│   │   ├── source.py             # SourceDocument, SourceRef
│   │   └── safety.py             # SafetyLevel, SafetyNotice
│   │
│   ├── interfaces/               # Protocols (austauschbare Adapter)
│   │   ├── document_parser.py
│   │   ├── llm_provider.py
│   │   ├── vision_provider.py
│   │   ├── embedding_provider.py
│   │   ├── vector_store.py
│   │   └── blob_store.py
│   │
│   ├── providers/                # konkrete Implementierungen
│   │   ├── docling_parser.py             # Default-Parser (ADR-002)
│   │   ├── claude_vision_parser.py       # optionaler Seiten-Parser via Claude Vision
│   │   ├── claude_vision_menu_extractor.py  # Menüpfade aus Seiten-Screenshots
│   │   ├── anthropic_provider.py         # LLM + Vision, Default (ADR-006)
│   │   ├── ollama_provider.py            # LLM + Vision, Fallback (ADR-005)
│   │   ├── llm_factory.py                # Auswahl über LLM_PROVIDER
│   │   ├── sentence_transformer_embeddings.py
│   │   ├── ollama_embeddings.py
│   │   ├── embedder_factory.py           # Auswahl über Modellnamen
│   │   ├── qdrant_store.py
│   │   └── local_blob_store.py
│   │
│   ├── ingestion/
│   │   ├── pipeline.py           # orchestriert die Ingest-Schritte
│   │   ├── chunker.py            # hierarchisches Parent-Child-Chunking
│   │   ├── image_describer.py    # Vision-LLM Beschreibungen
│   │   ├── safety_detector.py    # erkennt GEFAHR/WARNUNG/etc.
│   │   ├── menu_path_extractor.py
│   │   ├── hyde_generator.py     # HyDE-Fragen fürs Retrieval
│   │   └── metadata.py
│   │
│   ├── registry/
│   │   ├── machine_registry.py   # SQLite im PoC
│   │   └── schema.sql
│   │
│   ├── retrieval/
│   │   ├── hybrid_search.py      # Dense + BM25, RRF-Fusion
│   │   ├── bm25_index.py         # Keyword-Index mit Light-Stemming (Deutsch)
│   │   ├── menu_path_search.py   # strukturierte Suche
│   │   └── reranker.py
│   │
│   ├── agent/
│   │   ├── intent_classifier.py
│   │   ├── machine_resolver.py
│   │   ├── answer_generator.py
│   │   └── orchestrator.py       # zweistufiger Ablauf
│   │
│   ├── ui/
│   │   └── streamlit_app.py
│   │
│   └── cli/
│       ├── ingest.py             # `python -m wissenssystem.cli.ingest`
│       ├── inspect.py            # Chunks eines Namespace inspizieren
│       └── seed_registry.py      # Registry aus data/machines.yaml befüllen
│
├── prompts/                      # versionierte Prompts (keine Hardcodings!)
│                                 # ein .md pro LLM-Aufgabe: Intent, Antwort, HyDE,
│                                 # Reranker, Vision-Parsing, Menüpfad-Extraktion, …
│
├── data/
│   ├── machines.yaml             # Registry-Seed (committet)
│   ├── sources/                  # Original-PDFs (nicht im Repo)
│   ├── blobs/                    # extrahierte Bilder (nicht im Repo)
│   ├── bm25/                     # BM25-Indizes (nicht im Repo)
│   └── registry.db               # SQLite (nicht im Repo)
│
├── eval/
│   ├── questions*.yaml           # Fragensets: Basis, Attachments, Kannegiesser
│   ├── run_eval.py
│   ├── report*.md                # aktuelle Ergebnisse (report.md: 20/20)
│   └── archive/                  # überholte Zwischenstände
│
├── docs/
│   ├── adr/                      # Architecture Decision Records
│   ├── learnings.md              # Erkenntnisse & Stolpersteine aus dem Aufbau
│   ├── technical_specification.md
│   └── demo-script.md
│
├── tests/
│   ├── conftest.py
│   ├── unit/                     # ein test_*.py pro Modul
│   ├── integration/              # benötigen laufendes Qdrant
│   └── fixtures/
│
└── docker-compose.yml            # nur Qdrant für lokale Entwicklung
```

## 2 · Datenmodell (Domain-Klassen)

```python
# domain/source.py
class SourceDocument(BaseModel):
    doc_id: str                  # UUID
    title: str
    publisher: str               # "Bosch"
    document_number: str         # "6721108192"
    edition: str                 # "2026/02"
    software_version: str | None # "NF87.02"
    country_codes: list[str]     # ["DE", "AT", "CH", "LU", "BE"]
    pdf_path: Path
    config_namespace: str        # zugewiesener Namespace

class SourceRef(BaseModel):
    doc_id: str
    page: int
    section_path: list[str]      # ["5", "5.1", "5.1.2 Menü: Wärmepumpe"]
```

```python
# domain/chunk.py
class TextChunk(BaseModel):
    chunk_id: str
    text: str
    source_ref: SourceRef
    chunk_type: Literal["prose", "table", "list", "safety_notice"]
    safety_level: SafetyLevel | None
    country_restriction: list[str] | None  # z.B. ["DE"] für EVU-Dimmen
    related_image_ids: list[str]           # Bilder im selben Kontext

class ImageChunk(BaseModel):
    chunk_id: str
    image_id: str                # Schlüssel im BlobStore
    description: str             # Vision-LLM erzeugt
    caption: str | None          # "Bild 10  Übersicht Kältekreis"
    source_ref: SourceRef
    related_text_chunk_ids: list[str]
```

```python
# domain/machine.py
class Configuration(BaseModel):
    namespace: str               # cfg__bosch__ui800-9kw-r290__nf87-02__de
    manufacturer: str
    model_family: str            # "UI 800"
    indoor_unit: str | None
    outdoor_unit: str | None
    software_version: str | None
    country: str                 # ISO-2

class Machine(BaseModel):
    machine_id: str              # UUID
    name: str                    # "Wärmepumpe Halle 2"
    aliases: list[str]           # ["WP Halle 2", "die hintere Pumpe"]
    location: str | None
    responsible: str | None
    configuration_namespace: str # FK zu Configuration
```

```python
# domain/menu_path.py
class MenuPath(BaseModel):
    path_id: str
    nodes: list[str]             # ["Service", "Anlageneinstellungen",
                                 #  "Wärmepumpe", "Geräuscharmer Betrieb"]
    leaf_description: str        # was diese Einstellung tut
    source_ref: SourceRef
    namespace: str
```

```python
# domain/safety.py
class SafetyLevel(str, Enum):
    GEFAHR = "GEFAHR"
    WARNUNG = "WARNUNG"
    VORSICHT = "VORSICHT"
    ACHTUNG = "ACHTUNG"
    HINWEIS = "HINWEIS"
```

## 3 · Interfaces (Protocols)

Alle Provider sind über `typing.Protocol` definiert. Adapter müssen diese
Protocols **exakt** erfüllen. Beispiel:

```python
# interfaces/llm_provider.py
class LLMProvider(Protocol):
    def complete(
        self,
        system: str,
        messages: list[Message],
        *,
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ) -> LLMResponse: ...

    def complete_structured(
        self,
        system: str,
        messages: list[Message],
        schema: type[BaseModel],
    ) -> BaseModel: ...
```

```python
# interfaces/vision_provider.py
class VisionProvider(Protocol):
    def describe_image(
        self,
        image: bytes,
        media_type: str,
        context: str,        # umgebender Anleitungstext
        prompt: str,         # aus prompts/image_description.md
    ) -> str: ...
```

```python
# interfaces/vector_store.py
class VectorStore(Protocol):
    def create_namespace(self, namespace: str) -> None: ...
    def upsert(self, namespace: str, items: list[VectorItem]) -> None: ...
    def search(
        self,
        namespace: str,
        query_vector: list[float],
        top_k: int = 10,
        filter: dict | None = None,
    ) -> list[VectorHit]: ...
    def delete_namespace(self, namespace: str) -> None: ...
```

Vollständige Protocols werden in Phase 2 von Claude Code geschrieben — die
hier gezeigten Signaturen sind verbindliche Vorgaben, nicht Vorschläge.

## 4 · Ingestion-Pipeline (Reihenfolge)

```
PDF
 │
 ▼
Docling-Parser ──► strukturiertes Markdown + Bild-Extraktion + Tabellen-JSON
 │
 ▼
SafetyDetector ──► Markiert GEFAHR/WARNUNG/VORSICHT-Blöcke (Regex + LLM-Check)
 │
 ▼
Chunker ──► semantische Chunks (Abschnittsgrenzen!), Tabellen bleiben EINE Einheit
 │
 ▼
MenuPathExtractor ──► strukturierter Index aus Abschnitt "Übersicht Service"
 │
 ▼
ImageDescriber ──► Vision-LLM-Beschreibung pro Bild, mit umgebendem Kontext
 │
 ▼
MetadataAttacher ──► country_restriction, software_version, source_ref, ...
 │
 ▼
EmbeddingProvider ──► Vektoren für Text-Chunks UND Bildbeschreibungen
 │
 ▼
VectorStore.upsert(namespace=cfg__...) + BlobStore.put(bilder)
```

**Wichtig:** Der Schritt **MenuPathExtractor** läuft *zusätzlich* zum normalen
Chunking. Menüpfade werden als eigene Sammlung in Qdrant geführt (Suffix
`__menupaths`). Das ist die im Konzept-Gespräch festgehaltene Erkenntnis.

## 5 · Menüpfad-Index (eigener Subsystem)

Die UI-800-Anleitung enthält in Kapitel 8 einen mehrseitigen, hierarchischen
Servicebaum. Diese Struktur ist für Bediener oft *die* nützliche Antwort
(„wo stelle ich X ein"). Sie wird separat extrahiert und indiziert.

- **Quelle:** Übersicht-Service-Kapitel (Heuristik: hierarchische Listen
  mit `–`-Einrückung über mehrere Seiten). Im Zweifel LLM-gestützte Extraktion.
- **Speicherung:** zwei parallele Strukturen
  1. **Strukturiert** in der Maschinen-Registry-DB als materialisierter Baum
     (Tabelle `menu_paths(namespace, path, leaf_description)`)
  2. **Embedded** in Qdrant-Collection `<namespace>__menupaths` für
     Ähnlichkeitssuche bei vagen Anfragen
- **Abfrage:** Bei Frageintent „wo stelle ich X ein" oder „wie komme ich zu Y"
  wird der Menüpfad-Index **vorrangig** durchsucht; Ergebnis hat eigenes
  Antwortformat (Pfad in Breadcrumb-Darstellung).

## 6 · Agent-Ablauf (zweistufig)

```
User-Frage
 │
 ▼
[Stufe 1: Resolver]
 ├─► IntentClassifier  ──► {troubleshoot, howto, lookup, menu_navigation, safety}
 ├─► MachineResolver   ──► passt zu welcher Konfiguration?
 │      ├─ via Registry-Lookup (explizite Erwähnung)
 │      ├─ via Alias-Match
 │      └─ via LLM-Inferenz aus Kontext
 │
 ├─► Confidence-Check
 │      ├─ confidence < threshold:  Rückfrage stellen, STOP
 │      └─ confidence ≥ threshold:  weiter
 ▼
[Stufe 2: Retrieve + Generate]
 ├─► HybridSearch im richtigen Namespace
 │      ├─ Text-Embedding-Suche
 │      ├─ Bildbeschreibungs-Suche
 │      └─ wenn intent=menu_navigation: MenuPathSearch zusätzlich
 │
 ├─► Reranker (Cross-Encoder oder LLM-basiert)
 │
 ├─► SafetyCheck: ist ein safety_relevant-Chunk im Top-k?
 │
 ├─► AnswerGenerator
 │      ├─ strikter System-Prompt: nur aus Quellen, sonst "unbekannt"
 │      ├─ Sicherheitshinweise wörtlich zitieren (siehe PROJECT §6)
 │      └─ Bild-IDs in der Antwort referenzieren
 ▼
Antwort + Quellen + Bilder (Streamlit zeigt alles)
```

## 7 · Konfigurationsverwaltung

`config.py` lädt aus `.env`:

```python
class Settings(BaseSettings):
    ollama_url: str = "http://localhost:11434"
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: SecretStr | None = None

    data_dir: Path = Path("data")
    sources_dir: Path = Path("data/sources")
    blobs_dir: Path = Path("data/blobs")
    registry_db_path: Path = Path("data/registry.db")

    llm_model: str = "qwen2.5:3b"
    vision_model: str = "moondream2"
    embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2"

    intent_confidence_threshold: float = 0.7
    machine_resolution_threshold: float = 0.75
    retrieval_top_k: int = 10

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
```

## 8 · Logging

`structlog` mit JSON-Output. Pflichtfelder pro Log-Eintrag:
`timestamp, level, event, request_id, namespace?, machine_id?, latency_ms?`.
Anonymisiert: keine User-Identitäten, keine vollständigen Fragen ins Log,
sondern nur Hash + Längen + Intent-Label (für PoC-Eval ausreichend).

## 9 · Testing-Strategie

- **Unit-Tests** für `chunker`, `menu_path_extractor`, `safety_detector`,
  `machine_resolver`. Schnell, ohne API-Calls.
- **Integration-Tests** für `ingestion.pipeline` und `retrieval.hybrid_search`
  gegen ein lokal laufendes Qdrant + Fixture-PDF (3 Seiten aus UI 800).
- **Eval-Tests** über `eval/run_eval.py` mit echtem API-Zugriff — nicht in CI,
  manuell.
- Provider-Adapter werden mit Mock-Responses getestet, nicht gegen echte APIs.
