# ADR-002: Docling statt Unstructured.io

**Status:** Akzeptiert  
**Datum:** 2026-05

## Kontext

PDFs von Bedienungsanleitungen enthalten Fließtext, Tabellen, Bilder,
Überschriften und verschachtelte Listen. Ein robuster Parser muss Tabellen
erhalten und Blocktypen korrekt klassifizieren.

## Entscheidung

**Docling** wird als PDF-Parser eingesetzt.

## Begründung

- Docling liefert strukturierten Output mit expliziten Block-Typen
  (`text`, `table`, `picture`, `section_header`) — keine Heuristik nötig.
- Vollständig lokal und offline, keine externen API-Calls.
- Tabellen werden als einzelne Blöcke exportiert; der Chunker muss sie nicht
  erkennen/zusammensetzen.
- Unstructured.io ist leistungsfähig, hat aber eine SaaS-Abhängigkeit für
  beste Ergebnisse; die lokale Variante ist schlechter dokumentiert.

## Konsequenzen

- Docling ist ein schweres Paket (PyTorch-Abhängigkeiten). `uv sync` dauert
  beim ersten Mal mehrere Minuten.
- Mehrseitige Tabellen: Docling erkennt Tabellenfortsetzungen; falls nicht,
  muss der Chunker einen Stitching-Schritt nachrüsten (STOPP-und-frage in
  Task 2.5 als Absicherung).
- Migrationspfad: `DocumentParser`-Protocol abstrahiert den Adapter —
  Parserwechsel ohne Änderungen an der Pipeline möglich.
