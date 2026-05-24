# ADR-004: Menüpfade als eigener Index

**Status:** Akzeptiert  
**Datum:** 2026-05

## Kontext

Bedienungsanleitungen enthalten strukturierte Menünavigations-Kapitel mit
verschachtelten Pfaden (z. B. `Service → Anlageneinstellungen → Wärmepumpe →
Geräuscharmer Betrieb`). Nutzer fragen häufig: „Wo stelle ich X ein?"

## Entscheidung

Menüpfade werden während des Ingests als eigener Vektorindex gespeichert
(Namespace `<namespace>__menupaths`) und über `MenuPathSearch` separat abgefragt.

## Begründung

- Das LLM soll Menüpfade **nie erfinden** — sie müssen aus einem verifizierten
  Index stammen (Goldene Regel Nr. 7 in CLAUDE.md).
- Semantic Embedding des Leaf-Node-Textes ermöglicht unscharfe Suche
  (`"Geräusch einstellen"` → `"Geräuscharmer Betrieb"`).
- Getrennt vom Text-Index: Menüpfad-Treffer werden im `AnswerResult` als
  eigenes Feld `menu_hits` ausgeliefert, damit UI und Eval sie separat prüfen können.

## Konsequenzen

- `MenuPathExtractor` muss beim Ingest zuverlässig laufen; Fehler hier führen
  zu fehlenden Navigationshilfen, nicht zu falschen Antworten.
- Zwei Qdrant-Collections pro Namespace; `delete_namespace` löscht beide.
- `MenuPathSearch` wird vom Orchestrator nur bei `Intent.MENU_NAVIGATION`
  aufgerufen — kein Overhead bei anderen Intents.
