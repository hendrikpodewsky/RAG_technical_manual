# Wissenssystem — Bedienungsanleitung RAG

Agentisches RAG-System für Maschinen-Bedienungsanleitungen. Fragen in natürlicher Sprache,
Antworten mit Text und Originalbildern aus dem maschinenspezifischen Wissensspeicher.

## Quickstart

```bash
# 1. Dependencies installieren
uv sync

# 2. Qdrant starten
docker compose up -d qdrant

# 3. Umgebungsvariablen konfigurieren
cp .env.example .env
# .env öffnen und API-Keys eintragen

# 4. Dokument ingestieren
uv run python -m wissenssystem.cli.ingest data/sources/ui800.pdf \
    --namespace cfg__bosch__ui800-9kw-r290__nf87-02__de

# 5. Streamlit-UI starten
uv run streamlit run src/wissenssystem/ui/streamlit_app.py

# 6. Oder direkt per CLI fragen
uv run python -m wissenssystem.cli.ask "Wie stelle ich den geräuscharmen Betrieb ein?"
```

## Eval ausführen

```bash
uv run python eval/run_eval.py
```

## Tests

```bash
# Unit-Tests
uv run pytest tests/unit -x

# Integration-Tests (benötigt laufendes Qdrant)
uv run pytest tests/integration -m integration
```

## Projektstruktur

Siehe `ARCHITECTURE.md` für die vollständige Verzeichnisstruktur und das Datenmodell.
Fachliche Setzungen und Nicht-Ziele: `PROJECT.md`.
Aufgaben und Abnahmekriterien: `TASKS.md`.
