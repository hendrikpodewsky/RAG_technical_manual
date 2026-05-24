# Demo-Skript — Wissenssystem (15 Minuten)

> Ziel: zeigen, dass das System aus einem PDF eine Wissens­basis baut und
> natürlichsprachliche Fragen mit Quellenangabe beantwortet.

---

## Vorbereitung (vor der Demo, nicht live)

```bash
uv sync
ollama pull qwen2.5:3b
ollama pull moondream2
docker compose up -d qdrant   # optional; ohne Docker: In-Memory-Fallback

cp .env.example .env
```

PDF bereithalten: `data/sources/ui800.pdf` (Bosch UI 800 Bedienungsanleitung).

---

## Block 1 — Ingest live zeigen (~4 min)

**Was zeigen:** Das System verarbeitet ein reales PDF zu einem durchsuchbaren Index.

```bash
# Registry mit Maschinen-Stammdaten befüllen
uv run python -m wissenssystem.cli.seed_registry \
    --db data/registry.db \
    --yaml data/machines.yaml

# PDF ingestieren (zeigt Live-Output mit Chunk-/Bild-/Menüpfad-Counts)
uv run python -m wissenssystem.cli.ingest data/sources/ui800.pdf \
    --namespace cfg__bosch__ui800__nf87-02__de \
    --db data/registry.db
```

**Erklären während Ingest läuft:**
- Docling parst das PDF in strukturierte Blöcke (Text, Tabellen, Bilder, Überschriften).
- Der Chunker teilt Prosa in max. 1.500-Token-Abschnitte — Tabellen werden nie geteilt.
- Der SafetyDetector markiert GEFAHR/WARNUNG/VORSICHT/ACHTUNG-Blöcke.
- Der MenuPathExtractor baut den Menü-Index aus dem Service-Kapitel.
- Alle Embeddings landen in Qdrant; Bilder im lokalen BlobStore.

**Erwartete Ausgabe:**
```
IngestReport: 180 chunks, 23 images, 67 menu paths, 12 safety notices
```

---

## Block 2 — Interaktive Demo in der UI (~7 min)

```bash
uv run streamlit run src/wissenssystem/ui/streamlit_app.py
```

Öffnet `http://localhost:8501`.

### Frage 1 — Sicherheitshinweis (zeigt: Verbatim-Zitat)

> „Welche Gefahren bestehen beim Öffnen des Geräts?"

Erwartetes Verhalten:
- Antwort enthält den originalen GEFAHR-Hinweis wörtlich (nicht paraphrasiert).
- Quellen-Expander zeigt Seite und Abschnitt.

### Frage 2 — Menünavigation (zeigt: Menüpfad-Index)

> „Wo im Menü stelle ich den geräuscharmen Betrieb ein?"

Erwartetes Verhalten:
- Antwort nennt den vollständigen Pfad:
  `Service → Anlageneinstellungen → Wärmepumpe → Geräuscharmer Betrieb`
- Pfad stammt aus dem verifizierten Index, nicht vom LLM erfunden.

### Frage 3 — Nicht beantwortbare Frage (zeigt: ehrliche Grenze)

> „Wie programmiere ich eine WLAN-Verbindung?"

Erwartetes Verhalten:
- Antwort: „Mir liegt dazu keine Information vor."
- Kein Halluzinieren eines Antwortpfades, der im Handbuch nicht existiert.

---

## Block 3 — Eval-Run live (~3 min)

```bash
uv run python eval/run_eval.py --output eval/report.md
```

**Erklären:**
- Das Eval prüft 20 Fragen automatisch gegen Themen-Stichworte, Safety-Keywords
  und Menüpfade.
- Ziel: ≥ 80 % Pass-Rate (PoC-Erfolgskriterium).
- `eval/report.md` öffnen und kurz zeigen.

---

## Block 4 — Code-Tour (~2 min)

Vier Schichten, je eine Datei exemplarisch öffnen:

| Schicht | Datei | Was zeigen |
|---------|-------|------------|
| Domain | `src/wissenssystem/domain/machine.py` | Immutable Pydantic-Modell, Namespace-Schema |
| Provider | `src/wissenssystem/providers/qdrant_store.py` | Adapter hinter Protocol, kein Leak nach oben |
| Agent | `src/wissenssystem/agent/orchestrator.py` | Zweistufiger Ablauf: Resolver → Retrieve+Generate |
| UI | `src/wissenssystem/ui/streamlit_app.py` | `@st.cache_resource`, Bild-Rendering, Quellen-Expander |

Prompts zeigen: `prompts/answer_generation.md` — alle Regeln (Verbatim-Zitat,
kein Erfinden, Bild-Referenz-Format) stehen hier, nicht im Code.

---

## Häufige Fragen

**„Kann man eine zweite Maschine hinzufügen?"**
→ Eintrag in `data/machines.yaml`, `seed_registry` erneut, PDF ingestieren.
   MachineResolver erkennt sie automatisch.

**„Was passiert wenn Ollama nicht läuft?"**
→ Provider wirft `ProviderError` beim ersten LLM-Call; UI zeigt Fehlermeldung.

**„Wie skaliert das auf 50 Maschinen?"**
→ Qdrant-Collections pro Namespace skalieren linear.
   LLM-Bottleneck: Ollama durch Cloud-LLM ersetzen — `LLMProvider`-Protocol
   macht das zum Einzeiler (ADR-005).
