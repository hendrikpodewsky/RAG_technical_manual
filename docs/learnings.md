# RAG-System Learnings

Erkenntnisse aus dem Aufbau des agentischen RAG-Systems für Maschinenbedienungsanleitungen.

---

## 1. Retrieval

### BM25 braucht Stemming für Deutsch

Deutsch ist eine stark flektierende Sprache. Ein reines `text.lower()` reicht nicht.

- `"rote"` ≠ `"rot"`, `"Störungen"` ≠ `"Störung"`, `"heizen"` ≠ `"Heizung"`
- **Fix:** Light-Stemmer mit Suffix-Stripping (`-e`, `-en`, `-er`, `-em`, `-es`) als Vorverarbeitungsschritt in `_tokenize()`
- Für Produktion: Snowball-Stemmer für Deutsch (z.B. `nltk`, `PyStemmer`) statt handgeschriebenem Suffix-Stripping

### Tabellen-Chunks brauchen Kontext beim Embedding

Eine Tabelle `| LED-Farbe | Betriebsstatus | ... | Rot | Störung |` ist semantisch arm ohne Kontext — das Embedding findet keine Ähnlichkeit zur Frage "Was bedeutet eine rote Status-LED?".

- **Fix:** Section-Titel als Präfix beim Vector-Embedding: `f"{section_title}: {table_text}"`
- **Achtung:** Diesen Prefix NICHT für BM25 verwenden — er verändert IDF-Gewichte und lässt irrelevante Tabellen aus anderen Sections für denselben Section-Titel hoher ranken

### BM25-Only-Hits brauchen Payload-Fetch

BM25 gibt nur Chunk-IDs zurück, keine Payloads. Chunks die BM25 findet, aber Vector-Search nicht, haben keinen Payload im Ergebnis — sie fallen beim Zusammenbauen des Results stillschweigend raus.

- **Fix:** BM25-only IDs nachträglich via `fetch_by_ids()` aus Qdrant holen

### Hybrid Search (Dense + BM25 + RRF) ist klar besser als nur Dense

- Dense allein: findet semantisch ähnliche Chunks, verpasst exakte Terme (Fehlercodes, Modellnummern, kurze Tabellen)
- BM25 allein: verpasst Synonyme und Paraphrasen, keine Robustheit bei Wortformvarianz
- **RRF-Fusion** (Reciprocal Rank Fusion) kombiniert beide Listen ohne Skalierungsprobleme

### HyDE verbessert das Query-Embedding spürbar

Direkte Fragen ("Wo stelle ich X ein?") embedden anders als Antwort-Passagen ("X stellt man unter Menü > Y ein").

- **HyDE** (Hypothetical Document Embeddings): LLM generiert eine hypothetische Antwort → diese wird als Suchvektor verwendet
- Überbrückt die semantische Lücke zwischen Frage-Form und Antwort-Form

### Reranker-Kontextfenster nicht zu klein wählen

Bei `max_chars_per_chunk = 400` werden lange Chunks abgeschnitten → der relevante Teil ist möglicherweise im zweiten Drittel des Texts.

- **Fix:** Auf `800` Zeichen erhöhen — deutlich bessere Reranking-Qualität ohne nennenswerten Latenzanstieg

---

## 2. Ingestion / Chunking

### Parent-Child-Chunking: Sibling-Tabellen aktiv nachladen

Section-Heading-Parents sind oft nicht als eigene Chunks indexiert. Der naive Ansatz "ersetze Kind durch Parent" hat zwei Fallen:

1. **Silent Drop**: Wenn mehrere Siblings denselben Parent haben, wird nur das erste Kind behalten — alle anderen werden verworfen. Tabellarische Siblings (z.B. die LED-Farbtabelle) landen nie im Kontext des Answer-Generators.
2. **Falsche Ersetzung**: Der Parent-Chunk ist oft nur eine Section-Überschrift ohne Inhalt.

- **Fix:** Wenn Parent nicht in Qdrant gefunden: alle Kinder einzeln behalten (kein Dedup). Zusätzlich: für jeden retrievten Prose-Chunk aktiv alle Table-Siblings desselben Parents via `fetch_by_parent_id()` nachladen, unabhängig vom Ranking.

### Vision-basierte Menüpfad-Extraktion ist weit überlegen

Heuristische Pfad-Extraktion aus dem geparsten Text fand ~9 Menüpfade. Claude-Vision-Extraktion aus PDF-Seiten-Screenshots fand **149–158 Pfade** für dasselbe Dokument.

- Menüpfade tauchen oft in Tabellen oder als Schritt-für-Schritt-Abfolgen auf — strukturell schwer heuristisch zu erfassen
- **Konsequenz:** Menünavigations-Fragen ("Wo im Menü stelle ich X ein?") funktionieren nur mit Vision-Extraktion zuverlässig

### Tabellen nicht zerschneiden

Wenn der Parser (Docling) eine Tabelle auf mehrere Chunks aufteilt, gehen Zeilen-Zusammenhänge verloren.

- Auf kompakte Tabellen-Chunks achten, die die komplette Tabelle enthalten
- Sehr große Tabellen: besser zeilenweise mit Section-Kontext als Prefix indexieren

---

## 3. Embedding-Modell

### E5-Modelle brauchen explizite Query/Passage-Präfixe

`intfloat/multilingual-e5-large` — und alle E5-Varianten — erwarten:

- `"query: <text>"` für Suchanfragen
- `"passage: <text>"` für indexierte Dokumente

Ohne diese Präfixe ist das Embedding semantisch schlechter. Die Präfixe müssen automatisch anhand des Modellnamens erkannt werden.

### Modellwechsel erfordert vollständigen Re-Ingest

Vektordimensionen ändern sich (MiniLM: 384, E5-large: 1024). Alte Collections in Qdrant sind **inkompatibel** — führen zu `shape mismatch`-Fehlern.

- **Konsequenz:** Bei Modellwechsel alle Qdrant-Collections löschen und komplett neu einlesen
- `.env`-Datei und `config.py` müssen konsistent sein — `.env` überschreibt `config.py`

### `intfloat/multilingual-e5-large` > `paraphrase-multilingual-MiniLM-L12-v2` für technisches Deutsch

In unserem Eval: MiniLM erreichte ~75%, E5-large ~80–90% bei identischer Pipeline.

---

## 4. Maschinen-Registry

### Alias-Liste muss den vollständigen Maschinennamen enthalten

Der Maschinen-Resolver macht Alias-Prefix-Matching. Wenn der vollständige Name (`"Wärmepumpe Halle 1"`) nicht explizit in der Alias-Liste steht, schlägt Stage 1 fehl — auch wenn er als `name`-Feld gesetzt ist.

- **Fix:** Immer den vollständigen Namen zusätzlich als Alias eintragen

### Doppelte Registry-Einträge führen zu ambiguous-Ergebnissen

Zwei identische Maschinen in der Registry → LLM kann nicht disambiguieren → `machine_id = None` → keine Antwort.

- Registry immer auf Duplikate prüfen, besonders nach Seed-Skript-Wiederholungen

---

## 5. Eval-Design

### Expected Topics sollten zuverlässige Oberflächenformen sein

Eval prüft Substring-Match (`topic.lower() in answer.lower()`). Verbformen wie `"Aktualisieren"` tauchen in Antworten seltener auf als Nominalformen wie `"Aktualisierung"`.

- **Regel:** Expected Topics wählen die in jeder korrekten Antwort auftauchen — keine Infinitive, keine seltenen Formen

### Unanswerable-Fragen sind genauso wichtig wie Answerable

Halluzination (System antwortet, obwohl kein Dokument das abdeckt) ist ein ernstes Problem.

- Fragen zu nicht-dokumentierten Features (WLAN, Bosch-App, KNX) explizit als `should_be_answerable: false` testen
- Retrieval-Kontext der Antwort immer prüfen: stammt er wirklich aus dem richtigen Dokument?

---

## 6. Bild-Chunks

### Dekorative Bild-Chunks müssen nach dem Ingest bereinigt werden

Docling extrahiert alle Bilder aus dem PDF — auch rein dekorative Elemente: Hersteller-Logos, Info-Icons (`ℹ`), Warnschilder-Symbole, QR-Codes. Diese Chunks landen im Vektorindex und werden bei Retrieval-Anfragen mitgeliefert.

- **Problem:** Dekorative Bild-Chunks erhöhen den Rausch-Anteil im Retrieval, werden als Bild-Anhang in der UI angezeigt, und verwirren den Nutzer (z.B. ein „i"-Icon als Antwort auf eine technische Frage)
- **Fix (kurzfristig):** Nach dem Ingest alle Bild-Chunks prüfen und Chunks mit dekorativen `description`-Schlagwörtern aus Qdrant + BlobStore löschen. Keyword-Liste: `"Herstellerlogo"`, `"Markenzeichen"`, `"Ikonografisches Symbol"`, `"Informationssymbol"`, `"Warnsymbol"`, `"Stift-/Marker-Symbol"` u.ä.
- **Fix (langfristig):** Die Ingestion-Pipeline sollte dekorative Bilder beim Beschreiben per Vision-LLM bereits erkennen und nicht indexieren. Kriterium: Bilder kleiner als ~50×50 px oder mit Beschreibung, die nur aus Symbolen/Logos besteht, überspringen.
- **Bosch UI 800:** 40 von 69 Bild-Chunks waren dekorativ (58 %) — nur 29 technische Diagramme/Schemata blieben übrig

### Ein visueller Audit aller Bild-Chunks ist nach jedem Ingest zwingend

Keyword-Filter auf der `description` sind **nicht ausreichend**. Das Vision-LLM benennt kleine Info-Icons (`ℹ`) systematisch als „Menüschnittstelle", „Konfigurationsanleitung" oder „Interface-Screenshot" — Beschreibungen, die keinem Dekorativ-Keyword entsprechen, aber ebenfalls wertlos sind.

- **Befund (Bosch UI 800, zweiter Audit):** 16 von 28 verbleibenden Bild-Chunks (57 %) waren entweder Info-Icons mit falscher Beschreibung, QR-Codes, CE-Symbole oder Warnzeichen. Übrig blieben 12 echte technische Diagramme.
- **Fehlertypen der Vision-LLM-Fehlbeschreibungen:**
  - Info-Icon (`ℹ`) → beschrieben als „Menüschnittstelle Solarthermieanlage", „Warmwasserbetrieb-Konfigurationsanleitung", „PV-System Einstellungsmenü" usw.
  - QR-Code → beschrieben als „Luft-Wasser-Wärmepumpen-Schema"
  - Warndreieck → beschrieben als „MU100-Modul (Schematische Darstellung)"
- **Pflicht-Schritt:** Nach jedem Ingest alle Bild-Chunks mit Vision durchsehen und nicht-technische Chunks vor dem Go-Live aus Qdrant + BlobStore löschen. Skript: Chunk-IDs per `client.scroll()` holen, Blob laden, visuell oder per LLM prüfen, `client.delete()` + `blob_path.unlink()`.
- **Keyword-Filter im Orchestrator** (`_DECORATIVE_KEYWORDS`) bleibt als Sicherheitsnetz, ersetzt aber den Audit nicht.

---

## 7. Architektur / Betrieb

### Qdrant Local File Lock verhindert parallele Zugriffe

`QdrantClient(path=...)` setzt einen exklusiven File-Lock. Zwei Prozesse (z.B. Eval + interaktive Shell) können nicht gleichzeitig zugreifen.

- Für Produktion: Qdrant als Server betreiben (`QdrantClient(url=...)`)

### Sicherheitshinweise wörtlich zitieren, nicht paraphrasieren

Das LLM neigt dazu, Sicherheitshinweise (`GEFAHR`, `WARNUNG`, `ACHTUNG`) umzuformulieren. Das ist bei technischen Handbüchern inakzeptabel.

- **Fix:** Explizite Regel im Answer-Generation-Prompt: Sicherheitshinweise als Blockzitat, wörtlich übernommen

### Prompt-Regeln müssen alle Datenquellen explizit benennen

Das LLM folgt Prompt-Regeln wörtlich. Wenn der Prompt sagt "Antworte NUR aus den Quellpassagen" und Menüpfade als separater Abschnitt `"Gefundene Menüpfade:"` übergeben werden, ignoriert das LLM diesen Abschnitt — er ist keine "Quellpassage".

- **Symptom:** Menünavigations-Fragen werden mit "Mir liegt dazu keine Information vor." beantwortet, obwohl die richtigen Menüpfade retrievt wurden
- **Fix:** Im Prompt explizit festlegen: `"Gefundene Menüpfade"` sind eine vollwertige Quelle und dürfen direkt für Navigations-Fragen verwendet werden
- **Regel:** Jede Datenquelle die dem LLM übergeben wird muss im System-Prompt als gültige Quelle deklariert sein
