# ADR-006: Anthropic Claude als Default-LLM (Ollama als Fallback)

**Status:** Akzeptiert
**Datum:** 2026-07 (dokumentiert nachträglich die Umstellung von Mai 2026)
**Ersetzt:** [ADR-005](ADR-005-lokales-llm-on-prem.md)

## Kontext

ADR-005 setzte Ollama (`qwen2.5:3b` / `moondream2`) als primären LLM-Backend,
mit dem `LLMProvider`-Protocol als vorbereitetem Migrationspfad. Im Verlauf
der Eval-Iterationen zeigten sich Grenzen der kleinen lokalen Modelle:

- `qwen2.5:3b` paraphrasierte gelegentlich Sicherheitshinweise, statt sie
  wörtlich zu zitieren (Verstoß gegen goldene Regel 6).
- Heuristische Menüpfad-Extraktion fand ~9 Pfade; Claude-Vision-Extraktion
  aus Seiten-Screenshots fand 149–158 Pfade für dasselbe Dokument
  (s. `docs/learnings.md` §2).
- Bildbeschreibungen mit `moondream2` waren für technische Grafiken
  (Schaltpläne, Heizkurven-Diagramme) zu unspezifisch.

## Entscheidung

**Anthropic Claude** wird Default für LLM und Vision:

| Rolle | Modell | Auswahl über |
|---|---|---|
| Text-LLM (Intent, Antwortgenerierung, Reranking) | `claude-sonnet-4-6` | `LLM_PROVIDER=anthropic` |
| Vision (Bildbeschreibung, Menüpfad-Extraktion, optionaler Seiten-Parser) | Claude Haiku | `ANTHROPIC_API_KEY` gesetzt |
| Fallback (vollständig offline) | Ollama `qwen2.5:3b` / `moondream2` | `LLM_PROVIDER=ollama` |

Die Umschaltung erfolgt ausschließlich über `llm_factory` / Konfiguration —
der in ADR-005 vorbereitete Adapter-Wechsel, wie vorgesehen ohne Änderung an
Agent-, Retrieval- oder Ingestion-Schicht.

## Begründung

- Eval-Score stieg im Zusammenspiel mit den Retrieval-Verbesserungen auf
  20/20 (`eval/report.md`); die Vision-Menüpfad-Extraktion war dafür
  notwendige Bedingung (Menünavigations-Fragen).
- Wörtliches Zitieren von Sicherheitshinweisen ist mit Claude zuverlässig.
- Der On-Prem-Pfad bleibt erhalten: `LLM_PROVIDER=ollama` stellt den
  ADR-005-Zustand ohne Codeänderung wieder her.

## Konsequenzen

- API-Key-Management nötig (`ANTHROPIC_API_KEY` in `.env`); Dokumentinhalte
  verlassen bei Ingest (Vision) und Query (Generierung) die lokale
  Infrastruktur. Für vertrauliche Handbücher: Ollama-Fallback nutzen und
  Qualitätseinbußen akzeptieren, oder On-Prem-GPU mit größerem Modell
  (`VLLMProvider`-Pfad aus ADR-005).
- Ingest-Kosten skalieren mit Seitenzahl (eine Vision-Anfrage pro Seite für
  die Menüpfad-Extraktion).
- Ohne gesetzten API-Key degradiert die Pipeline automatisch: Docling-Parser,
  Ollama-Vision, keine Vision-Menüpfade.
