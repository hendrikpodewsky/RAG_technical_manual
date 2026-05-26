# Technische Spezifikation — Wissenssystem für Maschinen-Bedienungsanleitungen

**Version:** PoC 1.0  
**Eval-Score:** 20/20 (100 %)  
**Stand:** Mai 2026

---

## 1. Was das System macht

Ein **agentisches RAG-System** (Retrieval-Augmented Generation), das Bedienungsanleitungen von Industriemaschinen als durchsuchbare Wissensbasis bereitstellt. Nutzer stellen Fragen in natürlicher Sprache — das System identifiziert automatisch die gemeinte Maschine und beantwortet die Frage ausschließlich auf Basis der hinterlegten Dokumentation, inklusive Quellenangabe.

**Typische Fragen:**
- „Wärmepumpe Halle 1, was bedeutet eine rote Status-LED?"
- „Wo im Menü stelle ich den geräuscharmen Betrieb ein?"
- „Ab welcher Vorlauftemperatur kann die Lebensdauer beeinträchtigt werden?"
- „Wie schütze ich die Anlage vor dem Einfrieren?"

Das System antwortet mit Text, Quellenangabe (Dokument, Seite, Abschnitt) und Menüpfaden. Wenn die Information nicht im Korpus vorhanden ist, antwortet es transparent mit „Mir liegt dazu keine Information vor" — keine Halluzination.

---

## 2. Warum dieses Design

### Problem
Industrielle Bedienungsanleitungen sind umfangreich (oft 50–200 Seiten), stark strukturiert (Menühierarchien, Tabellen, Sicherheitshinweise) und maschinenspezifisch (gleiche Geräteserie, unterschiedliche Software-Versionen, Länder-Varianten). Einfache Volltextsuche scheitert an Wortformvarianz und fehlender semantischer Ähnlichkeit.

### Lösungsansatz
Mehrschichtige Retrieval-Pipeline kombiniert semantische Vektorsuche, exaktes Keyword-Matching (BM25) und einen dedizierten Menüpfad-Index. Ein LLM-Agent orchestriert die Suche und generiert eine grounded Antwort — keine freie Erfindung, sondern strikt quellengebunden.

### Namespace-Isolation
Jede Maschinenkonfiguration (Hersteller + Modell + Softwareversion + Land) bekommt einen eigenen Vektorspeicher. Fragen zur Wärmepumpe Halle 1 suchen ausschließlich im Namespace `cfg__bosch__ui800__nf87-02__de` — keine Kreuzkontamination zwischen Maschinen.

---

## 3. Tech-Stack

| Komponente | Implementierung | Interface |
|---|---|---|
| Sprache | Python 3.14 | — |
| Dependency-Management | `uv` | — |
| LLM | Claude Sonnet 4.6 (Anthropic API) | `LLMProvider` |
| Vision-LLM | Claude Haiku 4.5 (Anthropic API) | — |
| Embeddings | `intfloat/multilingual-e5-large` (lokal, CPU) | `EmbeddingProvider` |
| Vektordatenbank | Qdrant (lokal, file-based) | `VectorStore` |
| Dokumenten-Parser | Docling + RapidOCR (Fallback) | `DocumentParser` |
| BM25-Index | `rank_bm25` (in-Memory, persistiert als `.pkl`) | — |
| Maschinen-Registry | SQLite | — |
| Web-UI | Streamlit | — |
| Konfiguration | `pydantic-settings` + `.env` | — |

---

## 4. Systemarchitektur

### 4.1 Übersicht

```
PDF-Dokument
     │
     ▼
┌─────────────────────────────┐
│      Ingestion-Pipeline     │
│  Docling → Chunking →       │
│  Vision-Extraktion →        │
│  Embedding → Qdrant         │
└─────────────────────────────┘
              │
              ▼
┌─────────────────────────────┐
│         Storage             │
│  Qdrant: Text + Bilder      │
│  Qdrant: Menüpfade          │
│  SQLite: Maschinen-Registry │
│  BM25-Index: .pkl           │
└─────────────────────────────┘
              │
              ▼
┌─────────────────────────────┐
│     Agent-Pipeline          │
│  Intent → Maschine →        │
│  Hybrid-Search → Reranker → │
│  Answer-Generator           │
└─────────────────────────────┘
              │
              ▼
         Streamlit-UI
```

### 4.2 Verzeichnisstruktur

```
wissenssystem/
├── src/wissenssystem/
│   ├── config.py                          # Settings via pydantic-settings
│   ├── domain/                            # Datenklassen (keine I/O)
│   │   ├── chunk.py                       # TextChunk, ImageChunk
│   │   ├── machine.py                     # Machine, Configuration
│   │   ├── menu_path.py                   # MenuPath
│   │   └── safety.py                      # SafetyLevel
│   ├── interfaces/                        # Protocols (Adapter-Pattern)
│   │   ├── llm_provider.py
│   │   ├── embedding_provider.py
│   │   └── vector_store.py
│   ├── providers/                         # Konkrete Implementierungen
│   │   ├── anthropic_provider.py
│   │   ├── claude_vision_menu_extractor.py
│   │   ├── sentence_transformer_embeddings.py
│   │   ├── qdrant_store.py
│   │   └── llm_factory.py
│   ├── ingestion/
│   │   ├── pipeline.py                    # Orchestrierung
│   │   └── chunker.py                     # Semantisches Chunking
│   ├── registry/
│   │   └── machine_registry.py            # SQLite-Registry
│   ├── retrieval/
│   │   ├── hybrid_search.py               # Dense + BM25 + RRF
│   │   ├── bm25_index.py                  # BM25 mit German Stemming
│   │   ├── menu_path_search.py
│   │   └── reranker.py
│   ├── agent/
│   │   ├── orchestrator.py
│   │   ├── intent_classifier.py
│   │   ├── machine_resolver.py
│   │   └── answer_generator.py
│   └── ui/
│       └── streamlit_app.py
├── prompts/                               # Versionierte LLM-Prompts
│   ├── answer_generation.md
│   ├── intent_classification.md
│   ├── machine_resolution.md
│   ├── hyde_generation.md
│   ├── reranker.md
│   └── vision_menu_extraction.md
├── data/
│   ├── sources/                           # Original-PDFs
│   ├── qdrant_storage/                    # Vektordatenbank (lokal)
│   ├── bm25/                              # BM25-Indizes (.pkl)
│   └── registry.db                        # SQLite
└── eval/
    ├── questions.yaml                     # 20 Testfragen
    └── run_eval.py
```

---

## 5. Ingestion-Pipeline

Verarbeitet ein PDF-Dokument in fünf Stufen:

```
PDF → Docling-Parser → SafetyDetector → Chunker → Vision-Extraktion → Embedding → Qdrant
```

**Schritt 1 — Docling-Parser**  
Konvertiert PDF zu strukturiertem Markdown. Erkennt Tabellen, Überschriften, Listen und Bilder. RapidOCR als Fallback für Scan-Seiten.

**Schritt 2 — SafetyDetector**  
Markiert Sicherheitshinweise (`GEFAHR`, `WARNUNG`, `VORSICHT`, `ACHTUNG`, `HINWEIS`) mit `safety_level`. Diese werden vom Answer-Generator wörtlich zitiert, nicht paraphrasiert.

**Schritt 3 — Chunker (Parent-Child)**  
Semantisches Chunking entlang von Abschnittsgrenzen. Section-Headings werden als Parent-Chunks angelegt; Prose- und Table-Chunks als Kinder mit `parent_chunk_id`. Tabellen bleiben als Einheit erhalten.

**Schritt 4 — Vision-Menüpfad-Extraktion**  
Claude Haiku analysiert jede PDF-Seite als Screenshot und extrahiert Menünavigationspfade (z.B. `Servicemenü > Geräuscharmer Betrieb > Betriebsart`). Ergebnis: 149–158 Pfade pro Dokument, vs. ~9 mit heuristischer Extraktion. Werden separat in `<namespace>__menupaths` indexiert.

**Schritt 5 — Embedding + Qdrant**  
Text-Chunks werden mit `multilingual-e5-large` embedded (mit `"passage: "` Präfix). Tabellen erhalten den Section-Titel als Präfix für bessere semantische Qualität. Parallel wird ein BM25-Index mit German Light-Stemming gebaut.

**Ausgabe pro Ingest:**
- Qdrant Collection `<namespace>`: Text- + Bild-Chunks (1024-dim Vektoren)
- Qdrant Collection `<namespace>__menupaths`: Menüpfade
- BM25-Index: `data/bm25/<namespace>.pkl`
- Ingest-Report: Chunks, Bilder, Menüpfade, Sicherheitshinweise

---

## 6. Retrieval-Pipeline

### 6.1 Hybrid Search (Dense + BM25 + RRF)

Pro Suchanfrage werden zwei Legs parallel ausgeführt und via Reciprocal Rank Fusion (RRF) kombiniert:

**Dense-Leg:**
1. HyDE (Hypothetical Document Embeddings): LLM generiert eine hypothetische Antwort auf die Frage
2. Hypothetische Antwort wird mit `"query: "` Präfix embedded
3. Cosine-Similarity-Suche in Qdrant (Top-20 Kandidaten)
4. Parallel: Suche im `__images`-Namespace für Bild-Chunks

**BM25-Leg:**
1. Query tokenisiert mit German Light-Stemmer (Suffix-Stripping: `-e`, `-en`, `-er`, `-em`, `-es`)
2. BM25-Okapi Scoring über alle indexierten Chunks (Top-20)
3. Payloads für BM25-Only-Hits via `fetch_by_ids()` aus Qdrant nachgeladen

**RRF-Fusion:**
```
score(chunk) = Σ 1 / (60 + rank + 1)
```
Beide Rankings werden zusammengeführt; kein manuelles Score-Tuning nötig.

### 6.2 Sibling-Table-Injection

Wenn ein retrievter Prose-Chunk Geschwister-Tabellen im selben Parent hat, die nicht eigenständig hoch genug gerankt wurden, werden diese aktiv über `fetch_by_parent_id()` nachgeladen. Sicherstellung dass z.B. eine LED-Farbtabelle immer zusammen mit dem zugehörigen Erklärungstext übergeben wird.

### 6.3 Menüpfad-Suche

Bei Intent `MENU_NAVIGATION` wird zusätzlich der Menüpfad-Index (vector-only, keine BM25) durchsucht. Ergebnisse werden als `"Gefundene Menüpfade:"` separat an den Answer-Generator übergeben.

### 6.4 Reranker

LLM-basierter Cross-Encoder rankt die Top-K Kandidaten nach Relevanz für die konkrete Frage neu. Max. 800 Zeichen pro Chunk im Reranker-Kontext.

---

## 7. Agent-Pipeline

```
Nutzer-Frage
     │
     ▼
IntentClassifier  ─────► {menu_navigation, troubleshoot, howto, lookup, safety}
     │                    Confidence-Score; bei < Threshold: Rückfrage
     ▼
MachineResolver   ─────► Namespace-Lookup in 3 Stufen:
     │                    1. Alias-Prefix-Match (Registry)
     │                    2. Partial-Name-Match (Registry)
     │                    3. LLM-Inferenz aus Kontext
     ▼
HybridSearch      ─────► Top-K Chunks aus dem Namespace
     │                    + MenuPathSearch (wenn menu_navigation)
     ▼
Reranker          ─────► Neu-Ranking nach Relevanz
     ▼
AnswerGenerator   ─────► Strikt quellengebunden
     │                    Sicherheitshinweise wörtlich
     │                    Menüpfade nur aus Index
     │                    Keine Halluzination
     ▼
Antwort + Quellen
```

---

## 8. Maschinen-Registry

SQLite-Datenbank mit:
- **Machines**: Name, Aliases, Standort, Verantwortlicher, Konfigurationsreferenz
- **Configurations**: Namespace, Hersteller, Modell, Softwareversion, Land

Seed-Datei: `data/machines.yaml` → `python -m wissenssystem.cli.seed_registry`

Aktuell indexiert:

| Maschine | Namespace | Aliases |
|---|---|---|
| Wärmepumpe Halle 1 | `cfg__bosch__ui800__nf87-02__de` | UI 800, WP Halle 1, Bosch WP, Wärmepumpe Halle 1 |

---

## 9. Konfiguration

Alle Einstellungen via `.env` (Vorlage in `.env.example`):

```env
ANTHROPIC_API_KEY=sk-ant-...

QDRANT_URL=http://localhost:6333      # optional; falls nicht erreichbar: lokal
EMBEDDING_MODEL=intfloat/multilingual-e5-large
LLM_MODEL=claude-sonnet-4-6
LLM_PROVIDER=anthropic

RETRIEVAL_TOP_K=10
MACHINE_RESOLUTION_THRESHOLD=0.75
INTENT_CONFIDENCE_THRESHOLD=0.7

DATA_DIR=data
```

---

## 10. Eval-Framework

20 Testfragen decken ab:

| Typ | Anzahl | Beispiel |
|---|---|---|
| Answerable — Factual | 12 | „Was bedeutet Standby-Betrieb?" |
| Answerable — Menünavigation | 3 | „Wo stelle ich die Heizkurve ein?" |
| Answerable — Sicherheit | 2 | „Welche Gefahr besteht bei zu hohen Temperaturen?" |
| Unanswerable (Halluzinations-Test) | 4 | „Wie verbinde ich mit der Bosch-App?" |

**Bewertungskriterien:** Substring-Match auf Expected-Topics, Erkennung von No-Info-Antworten, Unanswerable-Erkennung.

**Aktueller Score: 20/20 (100 %)**

---

## 11. Betrieb

### Ingest
```bash
python -m wissenssystem.cli.ingest data/sources/<dokument>.pdf \
  --namespace cfg__bosch__ui800__nf87-02__de
```

### Registry befüllen
```bash
python -m wissenssystem.cli.seed_registry
```

### Web-UI starten
```bash
streamlit run src/wissenssystem/ui/streamlit_app.py
```

### Eval ausführen
```bash
python eval/run_eval.py
```

---

## 12. Sicherheitsregeln (nicht verhandelbar)

1. **Sicherheitshinweise wörtlich zitieren** — keine Paraphrase von GEFAHR/WARNUNG/VORSICHT/ACHTUNG
2. **Keine Halluzination** — Antworten ausschließlich aus retrievten Quellen
3. **Menüpfade nur aus Index** — keine LLM-Erfindung von Navigationspfaden
4. **Namespace-Isolation** — Fragen zu Maschine A greifen nie auf Daten von Maschine B zu
5. **Kein Secret im Code** — API-Keys ausschließlich via `.env`

---

## 13. Bekannte Grenzen (PoC-Scope)

- Keine Authentifizierung / Rechteverwaltung
- Keine Bild-Anzeige im UI (Bild-IDs werden referenziert, nicht gerendert)
- Qdrant lokal (kein paralleler Multi-User-Zugriff)
- Latenz: ~5–30s pro Anfrage (4 serielle LLM-Calls)
- Eine Maschine produktiv indexiert (Bosch UI 800, DE)
- Kein automatischer Re-Ingest bei Dokumenten-Updates
- Kein Feedback-Loop / keine Qualitäts-Metriken über Zeit

---

## 14. Migrationspfade

Das Adapter-Pattern ermöglicht spätere Austausche ohne Rewrite:

| Heute | Produktion |
|---|---|
| Qdrant lokal | Qdrant Server / Cloud |
| `multilingual-e5-large` lokal | Voyage AI Embedding API |
| Claude Sonnet 4.6 | Anderes Anthropic-Modell oder On-Prem-LLM |
| Streamlit | React-Frontend mit FastAPI-Backend |
| SQLite Registry | PostgreSQL |
| Lokaler BlobStore | S3 / Azure Blob Storage |
