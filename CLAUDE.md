# CLAUDE.md — Einstieg für Claude Code

> Dies ist die erste Datei, die du in jeder Session liest.

## Was ist dieses Projekt?

Wir bauen ein **agentisches RAG-System** für Bedienungsanleitungen von
Maschinen. Nutzer fragen in natürlicher Sprache, das System liefert
Antworten mit Text **und** Originalbildern aus dem maschinenspezifischen
Wissensspeicher.

Stand: **PoC** mit 2–3 Maschinen, ~1–2 Wochen Aufwand.

## Die drei wichtigen Dateien (immer in dieser Reihenfolge lesen)

1. **`PROJECT.md`** — Ziel, Setzungen, Glossar, Nicht-Ziele, Anti-Patterns,
   Stopp-und-frage-Punkte.
2. **`ARCHITECTURE.md`** — Verzeichnisstruktur, Datenmodell, Interfaces,
   Pipeline, Agent-Ablauf.
3. **`TASKS.md`** — Konkrete Aufgaben in Reihenfolge, mit Abnahmekriterien.

**Beginne jede Session mit:** „Ich lese kurz `PROJECT.md`,
`ARCHITECTURE.md` und den Status in `TASKS.md`, dann setze ich an Phase X
Task Y fort."

## Goldene Regeln (Kurzform)

1. **Setzungen sind Setzungen.** Tech-Stack-Entscheidungen, Namespace-Schema,
   Sicherheits-Regeln — nicht neu diskutieren. Bei echtem Konflikt: fragen.
2. **Prompts in `prompts/`** — niemals als Strings im Code.
3. **Adapter-Pattern strikt.** Niemand außer einem Provider-Modul redet
   mit einer externen API.
4. **Tabellen werden nicht zerschnitten.** Wenn der Parser das tut, stoppen
   und fragen.
5. **Antworten ohne Quellenangabe sind ein Bug.**
6. **Sicherheitshinweise werden wörtlich zitiert, nicht paraphrasiert.**
7. **Menüpfade sind ein eigener Index** — nicht aus dem LLM erfinden.
8. **Bei Unsicherheit ob etwas Scope ist:** `PROJECT.md` §5 lesen, dann fragen.

## Workflow pro Task

```
1. TASKS.md öffnen, nächste offene Task wählen
2. Eingabe + Abnahmekriterien lesen
3. Falls etwas unklar: STOPPEN, fragen
4. Implementieren
5. Tests schreiben (gemäß "Tests"-Feld der Task)
6. ruff format && ruff check --fix && pytest tests/unit -x
7. git commit mit Format "<phase>.<task>: <beschreibung>"
8. Task in TASKS.md als ✅ markieren
9. Nächste Task
```

## Wenn du nicht weiterkommst

Mache **explizit**:

- Was du erreichen wolltest.
- Was du versucht hast.
- Was schiefging (Fehlermeldung, unerwartetes Verhalten).
- Welche zwei oder drei Lösungswege du siehst.
- Welchen du empfiehlst und warum.

Dann **frage**. Nicht raten.

## Aktueller Stand

- [x] Phase 0 — Setup
- [x] Phase 1 — Domain & Interfaces
- [x] Phase 2 — Provider-Adapter
- [x] Phase 3 — Ingestion-Pipeline
- [x] Phase 4 — Maschinen-Registry
- [x] Phase 5 — Retrieval
- [x] Phase 6 — Agent
- [x] Phase 7 — UI
- [x] Phase 8 — Eval
- [x] Phase 9 — Dokumentation & Übergabe

(Bei Fortschritt diese Liste aktualisieren.)
