# ADR-001: Qdrant statt pgvector

**Status:** Akzeptiert  
**Datum:** 2026-05

## Kontext

Für den Vektor-Index werden Embeddings von Text-Chunks, Bildbeschreibungen und
Menüpfaden gespeichert und nach Cosine-Ähnlichkeit abgefragt. Die Auswahl fiel
auf eine dedizierte Vektordatenbank vs. eine Erweiterung einer relationalen DB.

## Entscheidung

**Qdrant** wird als Vektorspeicher eingesetzt.

## Begründung

| Kriterium | Qdrant | pgvector |
|-----------|--------|----------|
| Lokales Deployment | Docker-Image, kein Postgres nötig | Postgres-Instanz erforderlich |
| Namespace-Isolation | native Collections | separate Tabellen oder Partitionen |
| In-Memory-Fallback | `QdrantClient(":memory:")` ohne Docker | nein |
| Payload-Filter | ja, nativ | über SQL WHERE |
| PoC-Komplexität | gering | höher (Postgres + pgvector Extension) |

Der In-Memory-Fallback ist für Entwicklung und CI entscheidend, da kein
Docker-Daemon vorauszusetzen ist.

## Konsequenzen

- Kein SQL-JOIN zwischen Registry (SQLite) und Vektorindex; Orchestrator führt
  beide Quellen manuell zusammen.
- Bei Produktivbetrieb: Qdrant-Volume sichern (`./data/qdrant_storage`).
- Migrationspfad zu pgvector: `QdrantVectorStore` hinter `VectorStore`-Protocol —
  Austausch ohne Änderungen an Retrieval-Schicht möglich.
