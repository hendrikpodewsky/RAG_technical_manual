# ADR-005: Lokales LLM via Ollama (On-Prem-first)

**Status:** Superseded durch [ADR-006](ADR-006-anthropic-als-default-llm.md)  
**Datum:** 2026-05

## Kontext

Bedienungsanleitungen können vertrauliche Produktionsdaten enthalten.
Gleichzeitig soll das System im PoC schnell aufbaubar sein ohne
Netzwerk-Abhängigkeiten oder API-Keys.

## Entscheidung

**Ollama** mit lokal laufenden Modellen wird als primärer LLM-Backend
eingesetzt (`qwen2.5:3b` für Text, `moondream2` für Vision).

## Begründung

- Vollständig offline — keine Daten verlassen die Infrastruktur.
- Kein API-Key-Management im PoC.
- `qwen2.5:3b` ist auf einem MacBook ohne GPU in akzeptabler Zeit nutzbar.
- Strukturierter Output (JSON) wird über Ollama's `format`-Parameter erzwungen.

## Migrations-/Skalierungspfad

Das `LLMProvider`-Protocol abstrahiert den Adapter vollständig:

```
OllamaLLMProvider  →  AnthropicLLMProvider (claude-sonnet-4-x)
                   →  OpenAILLMProvider
                   →  VLLMProvider (Self-hosted GPU-Cluster)
```

Wechsel erfordert:
1. Neuen Provider unter `providers/` implementieren.
2. `config.py` `llm_model` und `ollama_url` durch modellspezifische Einstellungen ersetzen.
3. Keine Änderungen an Agent, Retrieval oder Ingestion-Schicht.

## Konsequenzen

- Latenz: `qwen2.5:3b` benötigt auf CPU ~3–15 s pro Anfrage.
  Bei Produktivbetrieb sollte auf einen GPU-Server oder Cloud-LLM gewechselt werden.
- Modell-Qualität: Kleinere Modelle paraphrasieren gelegentlich Sicherheitshinweise.
  Der Eval-Check auf `expected_safety_quote` fängt diese Fälle auf.
- Ollama muss vor dem Start laufen; fehlt er, schlagen Provider-Konstruktoren beim
  ersten Call fehl (kein Lazy-Connect im PoC).
