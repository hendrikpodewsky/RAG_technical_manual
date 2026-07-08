# PROJECT.md — Wissenssystem für Maschinen-Bedienungsanleitungen

> **Wichtig für Claude Code:** Diese Datei ist der Einstiegspunkt. Lies sie am
> Anfang jeder Session. Sie definiert Ziel, Architektur und harte Setzungen.
> Treffe **keine** Entscheidungen, die hier oder in `ARCHITECTURE.md` bereits
> festgelegt sind, neu — frage stattdessen den Nutzer.

## 1 · Ziel

Ein agentisches RAG-System, das Bedienungsanleitungen für Maschinen (zunächst
2–3) als Wissensquelle nutzbar macht. Nutzer schildern in natürlicher Sprache
ein Problem; das System identifiziert Intent + Maschine, sucht im
**maschinenspezifischen, isolierten Wissensspeicher** und antwortet mit Text
**und** referenzierten Originalbildern (insbesondere Schaltplänen).

Der Prototyp ist ein **PoC nach Abschnitt 7 des Konzepts**: 2–3 Maschinen,
einfaches Web-UI, ~1–2 Wochen Arbeit.

## 2 · Architektur in vier Schichten

Genaues Datenmodell und Interfaces siehe `ARCHITECTURE.md`. Kurz:

1. **Quellen** — PDFs mit Adapter-Pattern; weitere Datentypen später.
2. **Ingestion-Pipeline** — Docling-Parsing, semantisches Chunking,
   Vision-LLM-Bildbeschreibungen, Metadaten.
3. **Storage pro Maschine** — Qdrant-Collection je Konfiguration (siehe §4),
   Bilder im BlobStore (lokal im PoC, S3-Interface).
4. **Agent & Antwort** — zentraler Agent mit Tool-Zugriff pro Namespace;
   zweistufig (Intent/Maschine erkennen → Retrieval + Generation).

## 3 · Tech-Stack (Setzung — nicht neu verhandeln)

| Komponente       | Wahl                          | Hinter Interface?              |
|------------------|-------------------------------|--------------------------------|
| Vektor-DB        | Qdrant (Docker)               | `VectorStore`                  |
| Parser           | Docling                       | `DocumentParser`               |
| LLM              | Anthropic (`claude-sonnet-4-6`); Fallback: Ollama (`qwen2.5:3b`) — s. ADR-006 | `LLMProvider` |
| Vision-LLM       | Anthropic (Claude Haiku: Bildbeschreibung, Menüpfade); Fallback: Ollama (`moondream2`) | `VisionProvider` |
| Embeddings       | sentence-transformers (`intfloat/multilingual-e5-large`) | `EmbeddingProvider` |
| Bild-Storage     | Lokales Dateisystem           | `BlobStore`                    |
| Web-UI           | Streamlit                     | —                              |
| Sprache          | Python ≥ 3.11                 | —                              |
| Dep-Management   | `uv`                          | —                              |
| Tests            | `pytest`                      | —                              |
| Konfiguration    | `pydantic-settings` + `.env`  | —                              |

**Begründungen sind in dieser Datei dokumentiert; nicht erneut diskutieren.**
On-Prem-Migration ist später ein Adapter-Wechsel, kein Rewrite — genau dafür
gibt es die Interfaces.

**Migrations-Pfad (LLM bereits gegangen, s. ADR-006):** Der Wechsel
Ollama → Anthropic erfolgte per `llm_factory` über `LLM_PROVIDER` in `.env` —
ohne Änderung am restlichen Code. Für Embeddings bleibt
`VoyageEmbeddingProvider` als Option hinter `EmbeddingProvider`.

## 4 · Zentrale Begriffe (Glossar)

- **Maschine** — physisches Gerät (z. B. „Wärmepumpe in Halle 2"). Hat eine
  Identität, einen Standort, einen Verantwortlichen.
- **Konfiguration** — Tupel aus *(Modell-Familie, Inneneinheit, Außeneinheit,
  Softwareversion, Land)*. **Ein Namespace pro Konfiguration**, nicht pro
  physischer Maschine. Begründung: Die UI-800-Anleitung enthält massiv
  länder- und varianten-abhängige Optionen (z. B. „nur in DE", „nur in AT für
  R290 >7 kW") — diese müssen sauber getrennt sein.
- **Namespace** — eine Qdrant-Collection. Repräsentiert genau eine
  Konfiguration. Schreibweise: `cfg__<hersteller>__<modell>__<sw-version>__<land>`,
  z. B. `cfg__bosch__ui800-9kw-r290__nf87-02__de`.
- **Chunk** — semantisch geschnittenes Stück Anleitung mit Metadaten. Enthält
  Text *oder* Bild-Referenz, immer mit Quellenangabe (Dokument, Seite, Abschnitt).
- **Menüpfad** — strukturierter Pfad durch die Geräte-Menühierarchie (z. B.
  *Service → Anlageneinstellungen → Wärmepumpe → Geräuscharmer Betrieb*).
  **Eigener Index neben den Vektor-Chunks** (siehe `ARCHITECTURE.md` §5).
- **Maschinen-Registry** — separate Datenbank, kennt physische Maschinen,
  ihre Aliasse, Standorte, **welcher Konfiguration sie zugeordnet sind**.
  Routing-Rückgrat.

## 5 · Nicht-Ziele für den PoC (explizit ausgeschlossen)

Diese Punkte sind **nicht** Teil des PoC. Wenn etwas davon nötig erscheint:
stoppen und nachfragen, nicht implementieren.

- ❌ Authentifizierung, Rollen, Rechte (LDAP/AD)
- ❌ Mehrsprachigkeit (UI und Korpus erstmal Deutsch)
- ❌ Audit-Logging im regulatorischen Sinn (einfaches Logging ja, Audit nein)
- ❌ Lokales LLM-Hosting (Ollama/vLLM) — Interfaces ja, Implementierung nein
- ❌ Automatische Re-Ingest-Pipelines / Versions-Diff
- ❌ Direkte CLIP-Bildsuche — nur Text-über-Bildbeschreibung
- ❌ Fine-Tuning irgendeines Modells
- ❌ CAD-Daten, Video-Tutorials, Service-Tickets als Quellen
- ❌ Mobile App
- ❌ Production-grade Deployment (Kubernetes, etc.)

## 6 · Sicherheitsrelevante Inhalte (harte Regel)

Bedienungsanleitungen enthalten Hinweise mit Personenschadens-Potenzial
(GEFAHR / WARNUNG / VORSICHT). Für solche Inhalte gilt:

- Beim Ingest werden Warnhinweis-Blöcke als `safety_relevant: true` markiert.
- Der Agent **paraphrasiert** sicherheitsrelevante Inhalte **nicht**, sondern
  zitiert sie wörtlich und zeigt — falls vorhanden — das zugehörige Originalbild.
- Wenn das Retrieval keinen sicherheitsrelevanten Treffer hat, aber die Frage
  sicherheitskritisch wirkt (Verbrühung, Stromschlag, Frost, Druck), wird das
  in der Antwort offen gesagt: „Mir liegt keine sicherheitsgeprüfte Information
  hierzu vor, bitte Originaldokumentation konsultieren."

## 7 · Stopp-und-frage-Punkte für Claude Code

An diesen Stellen **nicht selbst entscheiden**, sondern den Nutzer fragen:

1. **Wahl der konkreten Maschinen für den PoC** (Welche 2–3 Anleitungen?).
   Default: UI 800 ist gesetzt, zwei weitere sind offen.
2. **Definition einer neuen Konfiguration / eines neuen Namespaces** —
   Konfigurations-Tupel ist menschliche Entscheidung, nicht Heuristik.
3. **Schwellenwerte für Confidence** (Intent-Klassifikation, Retrieval-Score)
   — Default vorschlagen, vom Nutzer bestätigen lassen.
4. **Wenn eine Frage des Eval-Sets nicht beantwortbar ist** — entscheiden, ob
   Daten fehlen oder System fehlerhaft ist, ist Nutzer-Aufgabe.
5. **Erweiterung der Nicht-Ziele-Liste** — wenn Scope wächst, vorher fragen.

## 8 · Anti-Patterns (was nicht passieren darf)

- 🚫 **Prompts als hardcodierte Strings im Code.** Prompts liegen in
  `prompts/`, sind versioniert, werden geladen.
- 🚫 **Tabellenzerschneidung beim Chunking.** Mehrseitige Tabellen bleiben
  zusammen. Docling-Tabellenstruktur-Erkennung **muss** aktiv sein.
- 🚫 **Antworten ohne Quellenangabe.** Jede Aussage hat einen Verweis auf
  Chunk-ID(s) und ggf. Bild-ID(s). Streamlit-UI zeigt Quellen sichtbar an.
- 🚫 **Paraphrasierte Sicherheitshinweise.** Siehe §6.
- 🚫 **Direkte Provider-API-Aufrufe außerhalb der Adapter.** Niemand außer
  `providers/anthropic_provider.py` darf `anthropic.Anthropic` instanziieren.
- 🚫 **Halluzinieren von Menüpfaden.** Menüpfade kommen ausschließlich aus
  dem strukturierten Menüpfad-Index, nicht aus freier LLM-Generierung.
- 🚫 **Hardcodierte Pfade.** Konfiguration via `.env` und `pydantic-settings`.
- 🚫 **Tests im selben Lauf wie Ingest.** Tests verwenden Fixtures, nicht
  echte API-Aufrufe (Ausnahme: explizit markierte Integration-Tests).

## 9 · Erfolgskriterien für den PoC

Der PoC gilt als erfolgreich, wenn:

1. UI 800 + 2 weitere Anleitungen vollständig ingested sind.
2. Das Eval-Set (siehe `TASKS.md` Phase 4) mit ≥ 80 % korrekt beantwortet wird.
3. Bei mindestens 5 Eval-Fragen werden **Bilder** korrekt mit ausgegeben.
4. Das System erkennt mindestens einen Fall, in dem die Information **nicht**
   im Korpus ist, und antwortet ehrlich „unbekannt".
5. Das System unterscheidet die 2–3 Maschinen korrekt — bei mehrdeutigen
   Anfragen erfolgt eine Rückfrage statt einer falschen Zuordnung.
6. Sicherheitsrelevante Hinweise werden wörtlich zitiert.
7. Menüpfade werden korrekt zurückgegeben, wo gefragt.

## 10 · Lebenszyklus dieses Dokuments

`PROJECT.md` ist die Wahrheit. Bei Konflikt zwischen Code und dieser Datei
gewinnt die Datei. Änderungen an Setzungen erfordern explizite Nutzerbestätigung
und werden im Git-Commit dokumentiert.
