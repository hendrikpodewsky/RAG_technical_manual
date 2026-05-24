# ADR-003: Konfigurations-Granularität für Namespaces

**Status:** Akzeptiert  
**Datum:** 2026-05

## Kontext

Mehrere physische Maschinen können die gleiche Konfiguration (Hersteller,
Modell, Softwareversion) teilen und damit dieselbe Bedienungsanleitung nutzen.
Gleichzeitig muss das System wissen, zu welcher Konfiguration ein Nutzer fragt.

## Entscheidung

Zwei-Ebenen-Modell:

1. **Configuration** (Namespace): repräsentiert eine Anleitung, z. B.
   `cfg__bosch__ui800__nf87-02__de`. Vektoren werden pro Namespace indiziert.
2. **Machine**: eine physische Anlage mit Standort, Alias-Liste und Verweis
   auf einen Namespace. Mehrere Maschinen können denselben Namespace teilen.

Namespace-Schema: `cfg__<hersteller>__<modell>__<sw-version>__<land>`

## Begründung

- Verschiedene physische Maschinen eines Typs teilen einen Index — kein
  doppelter Speicher, kein redundanter Ingest.
- Der `MachineResolver` arbeitet auf Maschinen-Ebene (Alias-Match); die
  Retrieval-Schicht arbeitet auf Namespace-Ebene.
- Erweiterbar: neue Softwareversion → neuer Namespace, alter bleibt erhalten.

## Konsequenzen

- `MachineRegistry` führt beide Tabellen (`configurations`, `machines`).
- Bei Abfragen: Resolver gibt Namespace zurück; HybridSearch sucht darin.
- Änderung des Namespace-Schemas erfordert Re-Ingest aller Dokumente.
