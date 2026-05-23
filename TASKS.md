# TASKS.md — Aufgaben für Claude Code

> **So arbeitest du diese Datei ab:**
> - Phasen werden **strikt in Reihenfolge** abgearbeitet.
> - Jede Aufgabe hat: *Eingabe · Ausgabe · Abnahmekriterien · Tests*.
> - Wenn ein Abnahmekriterium nicht erfüllt werden kann, **stoppen und fragen**.
> - Vor jeder Phase einmal `PROJECT.md` und `ARCHITECTURE.md` quer lesen.
> - Jede Aufgabe = mindestens ein Git-Commit mit aussagekräftiger Message.

---

## Phase 0 · Setup (Tag 1)

### Task 0.1 — Projekt-Skelett anlegen
- **Eingabe:** Verzeichnisstruktur aus `ARCHITECTURE.md` §1.
- **Ausgabe:** Leeres aber komplettes Verzeichnis, `pyproject.toml` mit
  Dependencies (anthropic, voyageai, qdrant-client, docling, streamlit,
  pydantic-settings, structlog, pytest, ruff), `.env.example`, `.gitignore`,
  `README.md` mit Quickstart.
- **Abnahme:** `uv sync` läuft fehlerfrei durch; `ruff check .` ist clean.
- **Tests:** keine.

### Task 0.2 — Docker-Compose für Qdrant
- **Eingabe:** —
- **Ausgabe:** `docker-compose.yml` mit Qdrant-Service (Port 6333), Volume
  für Persistenz unter `./data/qdrant_storage`.
- **Abnahme:** `docker compose up -d qdrant` startet; `curl http://localhost:6333`
  antwortet mit Qdrant-Info.

### Task 0.3 — Settings & Logging
- **Eingabe:** `ARCHITECTURE.md` §7, §8.
- **Ausgabe:** `src/wissenssystem/config.py` mit `Settings`-Klasse;
  `src/wissenssystem/logging_setup.py` mit `structlog`-Konfiguration.
- **Abnahme:** Settings laden aus `.env`; Log-Aufruf produziert JSON.
- **Tests:** `tests/unit/test_config.py` — Default-Werte, Override via env.

---

## Phase 1 · Domain & Interfaces (Tag 1–2)

### Task 1.1 — Domain-Klassen
- **Eingabe:** `ARCHITECTURE.md` §2.
- **Ausgabe:** Alle Pydantic-Modelle in `src/wissenssystem/domain/`.
- **Abnahme:** Modelle sind immutable (`model_config = ConfigDict(frozen=True)`),
  haben Docstrings, sind aus `domain/__init__.py` exportiert.
- **Tests:** `tests/unit/test_domain.py` — Konstruktion, Validation,
  Serialisierung.

### Task 1.2 — Interface-Protocols
- **Eingabe:** `ARCHITECTURE.md` §3.
- **Ausgabe:** Alle Protocols in `src/wissenssystem/interfaces/`.
  `runtime_checkable` wo sinnvoll. Vollständige Type-Hints.
- **Abnahme:** `mypy src/wissenssystem/interfaces/` ist clean.
- **Tests:** keine (reine Typdefinitionen).

### Task 1.3 — Namespace-Naming-Utility
- **Eingabe:** `PROJECT.md` §4 (Namespace-Schreibweise).
- **Ausgabe:** `src/wissenssystem/domain/namespace.py` mit Funktion
  `build_namespace(manufacturer, model_family, sw_version, country) -> str`
  und `parse_namespace(ns: str) -> Configuration`.
- **Abnahme:** Round-Trip `parse(build(...))` ist verlustfrei.
- **Tests:** Property-basierte Tests mit `hypothesis` (mindestens
  20 Generierungs-Roundtrips).

---

## Phase 2 · Provider-Adapter (Tag 2–4)

### Task 2.1 — Anthropic-Provider (LLM + Vision)
- **Eingabe:** Interfaces, `ARCHITECTURE.md` §7.
- **Ausgabe:** `providers/anthropic_provider.py` mit Klassen
  `AnthropicLLMProvider` und `AnthropicVisionProvider`. Retry mit
  Exponential Backoff bei `RateLimitError` (max 3 Versuche).
- **Abnahme:** Beide Klassen erfüllen jeweiliges Protocol; Fehlerpfade
  werfen domänenspezifische Exceptions (`ProviderError`, `RateLimitError`).
- **Tests:** Unit-Test mit `respx` o.ä. — mock HTTP, prüfe Request-Format
  und Response-Parsing.
- **STOPP-und-frage:** Wenn `claude-sonnet-4-6` als Model-String nicht
  funktioniert: Nutzer fragen, welches Modell stattdessen.

### Task 2.2 — Voyage-Embeddings
- **Eingabe:** Interface, Voyage SDK.
- **Ausgabe:** `providers/voyage_embeddings.py`. Batch-Embedding bis
  128 Texte/Call.
- **Abnahme:** Erfüllt `EmbeddingProvider`-Protocol. Embedding-Dimension
  wird gegen Settings geprüft.
- **Tests:** Unit-Test mit gemockter HTTP-Antwort.

### Task 2.3 — Qdrant-VectorStore
- **Eingabe:** Interface, Qdrant-SDK.
- **Ausgabe:** `providers/qdrant_store.py`. Methoden:
  `create_namespace`, `upsert`, `search`, `delete_namespace`,
  `list_namespaces`. Bei `create_namespace` wird die korrekte Dimension
  und Distance (Cosine) gesetzt.
- **Abnahme:** Integration-Test gegen lokal laufendes Qdrant durchläuft
  Create→Upsert→Search→Delete.
- **Tests:** `tests/integration/test_qdrant_store.py`. Markiert als
  `@pytest.mark.integration`, in CI skippen.

### Task 2.4 — LocalBlobStore
- **Eingabe:** Interface.
- **Ausgabe:** `providers/local_blob_store.py`. Speichert unter
  `data/blobs/<sha256>.<ext>`, gibt `image_id` = sha256 zurück.
  Implementiert `BlobStore`-Protocol.
- **Abnahme:** put/get/delete Roundtrip, Idempotenz (gleicher Inhalt =
  gleiche ID).
- **Tests:** Unit-Test mit `tmp_path`.

### Task 2.5 — Docling-Parser-Adapter
- **Eingabe:** Interface, Docling-SDK.
- **Ausgabe:** `providers/docling_parser.py`. Gibt strukturiertes Ergebnis
  zurück: Liste von `ParsedBlock` (Text/Tabelle/Bild/Überschrift) mit
  Seite, Position, Hierarchie. Bilder werden extrahiert und im BlobStore
  abgelegt.
- **Abnahme:** Parsing der 3-Seiten-Fixture aus UI 800 liefert die
  erwarteten Block-Typen in der erwarteten Reihenfolge.
- **Tests:** `tests/integration/test_docling_parser.py` gegen Fixture-PDF.
- **STOPP-und-frage:** Wenn Docling Tabellen aus UI 800 (Tab. 5 ist
  besonders kritisch — mehrseitig) **zerreißt**: Nutzer fragen, ob wir
  manuelle Tabellen-Stitching-Logik bauen oder Parser-Wechsel erwägen.

---

## Phase 3 · Ingestion-Pipeline (Tag 4–6)

### Task 3.1 — SafetyDetector
- **Eingabe:** `PROJECT.md` §6.
- **Ausgabe:** `ingestion/safety_detector.py`. Erkennt Blöcke, die mit
  GEFAHR/WARNUNG/VORSICHT/ACHTUNG/HINWEIS markiert sind. Regex-basiert
  als erste Stufe, LLM-basierter Zweit-Check für unklare Fälle.
- **Abnahme:** Bei den 4 Warnhinweis-Blöcken in UI 800 Kapitel 4
  (Verbrühungsgefahr, Fußbodenschäden) werden alle 4 erkannt mit
  korrektem `SafetyLevel`.
- **Tests:** Unit-Test mit synthetischen Beispielen + UI-800-Fixture.

### Task 3.2 — Chunker
- **Eingabe:** `ARCHITECTURE.md` §4.
- **Ausgabe:** `ingestion/chunker.py`. Regeln:
  - Tabellen sind **immer** ein einziger Chunk (auch mehrseitige).
  - Listen werden zusammengehalten, wenn < 1000 Tokens.
  - Prosa wird an Abschnittsgrenzen geteilt (Heading-basiert).
  - Maximale Chunk-Größe: 1500 Tokens.
  - Mindest-Chunk-Größe: 100 Tokens (kürzere mit Nachbarn mergen).
  - Jeder Chunk trägt seinen `section_path` als Metadatum.
- **Abnahme:** UI-800-Fixture produziert keine zerschnittene Tabelle;
  Snapshot-Test gegen `expected_chunks.json`.
- **Tests:** Unit-Test mit synthetischen Strukturen + Snapshot-Test.

### Task 3.3 — MenuPathExtractor
- **Eingabe:** `ARCHITECTURE.md` §5.
- **Ausgabe:** `ingestion/menu_path_extractor.py`. Erkennt den
  Service-Übersichts-Block (Kapitel 8 in UI 800), extrahiert die
  hierarchische Liste. Bei mehrdeutiger Struktur LLM-gestützter
  Hilfsschritt mit Prompt aus `prompts/menu_path_extraction.md`.
- **Abnahme:** Aus UI 800 werden ≥ 50 Menüpfade extrahiert. Stichprobe:
  Pfad zu „Geräuscharmer Betrieb" wird als
  `["Service", "Anlageneinstellungen", "Wärmepumpe", "Geräuscharmer Betrieb"]`
  erkannt.
- **Tests:** Snapshot-Test gegen `expected_menu_paths.json`.

### Task 3.4 — ImageDescriber
- **Eingabe:** Interfaces, `prompts/image_description.md`.
- **Ausgabe:** `ingestion/image_describer.py`. Erzeugt für jedes Bild
  eine Beschreibung mit Vision-Provider. Eingaben in Prompt:
  - das Bild selbst,
  - umgebender Text (vorheriger + nachfolgender Absatz),
  - Bildunterschrift (falls vorhanden),
  - Dokumenttitel.
- **Abnahme:** Für Bild 10 (Kältekreis-Schema) enthält die Beschreibung
  mindestens die Begriffe „Kompressor", „Verflüssiger", „Verdampfer",
  „Expansionsventil" und nennt mindestens 4 der Temperaturwerte.
- **Tests:** Integration-Test mit echtem API-Call (nicht in CI).
- **STOPP-und-frage:** Wenn Beschreibungen wiederholt zu generisch sind:
  Prompt-Iteration mit Nutzer.

### Task 3.5 — Pipeline-Orchestrierung
- **Eingabe:** alle vorherigen Komponenten.
- **Ausgabe:** `ingestion/pipeline.py` mit Klasse `IngestionPipeline`,
  Methode `ingest(pdf_path: Path, namespace: str) -> IngestReport`.
  Schritte gemäß `ARCHITECTURE.md` §4. Idempotent (re-ingest desselben
  Dokuments überschreibt sauber, keine Dubletten).
- **Abnahme:** `python -m wissenssystem.cli.ingest data/sources/ui800.pdf
  --namespace cfg__bosch__ui800__nf87-02__de` läuft end-to-end durch und
  produziert IngestReport mit Counts (Chunks, Bilder, Menüpfade,
  Safety-Notices).
- **Tests:** Integration-Test gegen UI-800-Fixture.

---

## Phase 4 · Maschinen-Registry (Tag 6–7)

### Task 4.1 — Registry-Schema
- **Eingabe:** `ARCHITECTURE.md` §1 (Registry-Modul).
- **Ausgabe:** `registry/schema.sql` mit Tabellen `machines`,
  `configurations`, `menu_paths`. `registry/machine_registry.py` mit
  CRUD-Operationen über `sqlite3` (kein ORM für PoC).
- **Abnahme:** Schema-Migration läuft idempotent (CREATE IF NOT EXISTS).
- **Tests:** Unit-Test mit `:memory:`-SQLite — Insert, Query, Alias-Suche.

### Task 4.2 — Registry-Seed
- **Eingabe:** —
- **Ausgabe:** `cli/seed_registry.py`, das die PoC-Maschinen aus einer
  YAML-Datei (`data/machines.yaml`) lädt. Format pro Maschine: name,
  aliases, location, responsible, configuration_namespace.
- **Abnahme:** Nach Seed sind die 2–3 PoC-Maschinen in der Registry, mit
  Aliassen suchbar.
- **STOPP-und-frage:** Welche 2 weiteren Maschinen außer UI 800?

---

## Phase 5 · Retrieval (Tag 7–9)

### Task 5.1 — HybridSearch
- **Eingabe:** `ARCHITECTURE.md` §6.
- **Ausgabe:** `retrieval/hybrid_search.py`. Führt zwei parallele Suchen
  im Namespace (Text-Chunks, Bildbeschreibungen). Vereinigt Ergebnisse,
  dedupliziert (Bild + zugehöriger Text = ein Treffer-Cluster).
- **Abnahme:** Anfrage „Schaltbild Kältekreis" findet sowohl Bild 10 als
  auch den umgebenden Text.
- **Tests:** Integration-Test mit ingestiertem UI 800.

### Task 5.2 — MenuPathSearch
- **Eingabe:** Menüpfad-Index aus Phase 3.
- **Ausgabe:** `retrieval/menu_path_search.py`. Bei Frage „wo stelle ich
  X ein" gibt Top-3 Pfade zurück, jeweils mit Breadcrumb-String und
  Quellangabe.
- **Abnahme:** Frage „wo stelle ich den geräuscharmen Betrieb ein" liefert
  den korrekten Pfad als Top-1.

### Task 5.3 — Reranker
- **Eingabe:** Hybrid-Search-Ergebnisse.
- **Ausgabe:** `retrieval/reranker.py`. LLM-basiert (Sonnet 4.5 mit
  strukturiertem JSON-Output: Liste der Top-K-Chunks neu sortiert).
- **Abnahme:** Bei Frage „Verbrühung bei Warmwasser" ist Top-1 der
  Warnhinweis-Chunk, nicht ein zufälliger Temperatur-Chunk.

---

## Phase 6 · Agent (Tag 9–11)

### Task 6.1 — IntentClassifier
- **Eingabe:** `prompts/intent_classification.md` (zu erstellen).
- **Ausgabe:** `agent/intent_classifier.py`. Strukturierter Output:
  `{intent: Enum, confidence: float, reasoning: str}`. Intents:
  `troubleshoot`, `howto`, `lookup`, `menu_navigation`, `safety`,
  `unclear`.
- **Abnahme:** 10 Beispielfragen werden korrekt klassifiziert.
- **Tests:** Eval-Style-Test mit Fixture-Fragen.

### Task 6.2 — MachineResolver
- **Eingabe:** Registry, optionaler User-Kontext.
- **Ausgabe:** `agent/machine_resolver.py`. Drei Stufen:
  1. Exakter Match auf Name/Alias in der Frage.
  2. Fuzzy-Match auf Aliasse.
  3. LLM-gestützte Inferenz wenn nur 2 Maschinen in Registry.
  Gibt `(machine, confidence)` zurück oder `Ambiguous(candidates)`.
- **Abnahme:** „WP Halle 2" matcht Maschine via Alias. „Die Pumpe" mit
  mehreren Kandidaten ergibt `Ambiguous`.

### Task 6.3 — AnswerGenerator
- **Eingabe:** `prompts/answer_generation.md`. Strikte Anweisungen:
  - Antworte ausschließlich aus den Quellen.
  - Sicherheitshinweise wörtlich, nicht paraphrasiert.
  - Wenn keine Information: „Mir liegt dazu keine Information vor."
  - Menüpfade nur aus Menüpfad-Index, nicht erfinden.
  - Bild-IDs referenzieren als `[BILD:image_id]` (UI ersetzt durch
    eingebettetes Bild).
- **Ausgabe:** `agent/answer_generator.py`.
- **Abnahme:** Bei Frage zur Verbrühungsgefahr wird der originale
  Warnhinweis wörtlich enthalten.

### Task 6.4 — Orchestrator
- **Eingabe:** alle Agent-Komponenten.
- **Ausgabe:** `agent/orchestrator.py` mit `answer(question: str,
  context: dict) -> AnswerResult`. Implementiert zweistufigen Ablauf
  aus `ARCHITECTURE.md` §6 inkl. Confidence-Checks und Rückfragen.
- **Abnahme:** End-to-End-Test mit 5 Beispielfragen.

---

## Phase 7 · UI (Tag 11–12)

### Task 7.1 — Streamlit-App
- **Eingabe:** Orchestrator.
- **Ausgabe:** `ui/streamlit_app.py`. Features:
  - Eingabefeld für Fragen.
  - Maschinen-Selector (oder „automatisch erkennen").
  - Antwortbereich mit Markdown-Rendering.
  - Bilder werden inline angezeigt (geladen aus BlobStore).
  - Quellen-Block unter jeder Antwort: Dokument, Seite, Abschnitt.
  - Bei Rückfrage des Agents: UI fragt nach.
- **Abnahme:** Manuelle Bedienbarkeit: 3 Beispielfragen durchspielen,
  inkl. einer mit Bild-Antwort und einer mit Rückfrage.

---

## Phase 8 · Eval (Tag 12–13)

### Task 8.1 — Eval-Set erstellen
- **Eingabe:** —
- **Ausgabe:** `eval/questions.yaml` mit ≥ 20 Fragen, je mit:
  - `question`
  - `expected_machine` (Namespace)
  - `expected_topics` (Liste von Stichworten, die in der Antwort vorkommen sollen)
  - `expected_images` (Liste von erwarteten Bild-Captions, falls relevant)
  - `expected_menu_path` (falls Frage menu_navigation)
  - `expected_safety_quote` (falls Sicherheits-Frage)
  - `should_be_answerable` (bool — auch „unbeantwortbar" wird getestet)
- **STOPP-und-frage:** Erste 5 Fragen mit Nutzer durchgehen, bevor weitere
  geschrieben werden.

### Task 8.2 — Eval-Runner
- **Eingabe:** Eval-Set.
- **Ausgabe:** `eval/run_eval.py`. Iteriert über Fragen, ruft
  Orchestrator, prüft erwartete Stichworte/Bilder/Pfade. Output:
  Markdown-Report mit Pass/Fail pro Frage und Aggregat-Score.
- **Abnahme:** Run produziert Bericht; Erfolgsquote ≥ 80 % gemäß
  PoC-Erfolgskriterium.

---

## Phase 9 · Dokumentation & Übergabe (Tag 13–14)

### Task 9.1 — README & Setup-Doku
- **Ausgabe:** `README.md` mit:
  - Quickstart (`uv sync`, `docker compose up`, `cp .env.example .env`).
  - Wie ingest ich ein Dokument.
  - Wie starte ich die UI.
  - Wie laufe ich das Eval.

### Task 9.2 — Architecture-Decision-Records
- **Ausgabe:** `docs/adr/` mit kurzen ADRs für:
  - ADR-001: Qdrant statt pgvector
  - ADR-002: Docling statt Unstructured.io
  - ADR-003: Konfigurations-Granularität für Namespaces
  - ADR-004: Menüpfade als eigener Index
  - ADR-005: API-basiert statt lokales LLM (mit On-Prem-Migrationspfad)

### Task 9.3 — Übergabe-Demo
- **Ausgabe:** Skript für eine 15-Minuten-Demo:
  - Ingest live zeigen
  - 3 Eval-Fragen interaktiv beantworten lassen
  - Eval-Run live
  - Wo finde ich was im Code? (Tour durch die vier Schichten)

---

## Globale Regeln

1. **Vor jedem `git commit`:** `ruff format`, `ruff check --fix`,
   `pytest tests/unit -x`. Erst dann committen.
2. **Commit-Messages:** `<phase>.<task>: <kurze Beschreibung>`,
   z. B. `3.2: chunker keeps multi-page tables together`.
3. **Wenn du unsicher bist, ob etwas in den Scope gehört:** lies
   `PROJECT.md` §5 (Nicht-Ziele). Wenn unklar bleibt, frage.
4. **Wenn du ein Prompt brauchst:** schreibe es nach `prompts/` und
   lade es. Nie im Code als String einbetten.
5. **Wenn ein Test rot wird, der vorher grün war:** repariere ihn,
   *bevor* du die nächste Task anfängst.
6. **Du darfst Tasks aufteilen**, wenn sie zu groß werden.
   Aber: nie *Phasen* überspringen.
