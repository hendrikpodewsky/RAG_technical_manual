# Eval-Report

**Score: 5/5 (100%)**


| ID | Frage | Pass | Bilder | Latenz | Fehler |
|----|-------|------|--------|--------|--------|
| a01 | Wärmepumpe Halle 1, Was bedeuten die verschiedenen LED-Farbe… | ✅ | 0 | 16.5s | — |
| a02 | Wärmepumpe Halle 1, Wie stelle ich die Heizkurve ein und wel… | ✅ | 1 | 31.5s | — |
| a03 | Wärmepumpe Halle 1, Wie läuft das Estrichtrocknungsprogramm … | ✅ | 1 | 31.1s | — |
| a04 | Wärmepumpe Halle 1, Wie ist der Kältekreislauf der Wärmepump… | ✅ | 1 | 23.5s | — |
| a05 | Wärmepumpe Halle 1, Welche Einstellmöglichkeiten gibt es für… | ✅ | 0 | 33.3s | — |

## Antworten

### a01: Wärmepumpe Halle 1, Was bedeuten die verschiedenen LED-Farben und welche Betriebszustände signalisieren sie jeweils?

**Pass:** ✅

Die Status-LED oben auf dem Bedienfeld zeigt mithilfe von verschiedenen Farben den Betriebsstatus des Geräts an. Die Bedeutung der einzelnen LED-Farben ist wie folgt:

| LED-Farbe | Betriebsstatus |
|-------------|-------------------------------------------------------------------------------|
| Grün | Normalbetrieb. |
| Gelb | Warnungen, nicht blockierende Anlagenstörungen oder Wartungsinformationen. |
| Rot | Verriegelnde oder blockierende Störungen. |

- Dokument: Bedienungsanleitung Wärmepumpe
- Seite: 3
- Abschnitt: Status-LED (Abschnitt 3.3)

### a02: Wärmepumpe Halle 1, Wie stelle ich die Heizkurve ein und welche Parameter kann ich dabei anpassen?

**Pass:** ✅

## Einstellung der Heizkurve

### Verfügbare Regelungsarten

Für die Heizkurve stehen zwei Varianten zur Auswahl, die im Menü **Heizen und Kühlen** unter dem Menüpunkt **Heizkurve** eingestellt werden können:

| Menüpunkt | Einstellintervall |
|-------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Heizkurve | Es sind zwei Varianten der Heizkurve für die Regelung entsprechend der Außentemperatur vorhanden: |
| | ▶ Regelungsart >Außentemperatur geführt 1) : ist eine aufwärts gekrümmte Heizkurve, die auf einer optimierten Zuordnung der Vorlauftemperatur entsprechend der Außentemperatur beruht. Es müssen nur die gewünschte Temperatur und die maximale Temperatur eingestellt werden. Diese Variante ist die Grundeinstellung und eignet sich für gängige Anwendungsfälle. |
| | ▶ Regelungsart >Außentemperatur mit Fußpunkt: Die Außentemperatur mit Fußpunkt ist eine klassische Heizkurveneinstellung, die verschiedene Optionen bietet, um den individuellen Anforderungen des Gebäudes gerecht zu werden. Diese Heizkurve hat einen Fuß- und einen Endpunkt. Während der Übergangszeit kann der Installateur einen Komfortpunkt einstellen, um die Heizkurve leicht zu erhöhen. |
| | Der Fußpunkt entspricht der Vorlauftemperatur, die bei einer Außenlufttemperatur von 20 °C erreicht wird. |
| | Der Endpunkt ist die Vorlauftemperatur, die bei der niedrigsten Außenlufttemperatur in der Region erreicht wird, und beeinflusst demzufolge die Steigung der Heizkurve. |
| | Der Komfortpunkt ermöglicht die Erhöhung der Vorlauftemperatur in der Übergangszeit Frühling/Herbst. Optional kann der Benutzer bei beiden außentemperaturgeführten Regelungsarten einen Grenzwert für die minimale Vorlauftemperatur einstellen (Einstellung min. Vorlauftemp.= Ein). |

### Weitere einstellbare Parameter im Menü Heizen

Zusätzlich zur Heizkurve können im Menü **Heizen** folgende Parameter angepasst werden:

| Menüpunkt | Beschreibung |
|-------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| | ▶ Heizen • Heizkurve. Als Auswahl möglich sind: - Außentemperatur geführt -oder- - Außentemperatur mit Fußpunkt -oder- - Einzelraumgeführt • Max. Temperatur. Maximale Vorlauftemperatur für die Anlage einstellen. • Minimale Vorlauftemperatur. Minimale Vorlauftemperatur einstellen, optional. • Heizkurve. Menü zur grafischen Einstellung der Heizkurve. • Raumeinfluss HK. Dieser Faktor legt fest, wie stark die gemessene Raumtemperatur die Vorlauftemperatur durch Parallelverschiebung der Heizkurve beeinflussen darf. Je höher der eingestellte Wert ist, desto stärker wird die Abweichung gewichtet und desto größer ist der Einfluss. • Solareinfluss. Dieser Faktor kann den Einfluss des Sonnenlichts kompensieren. Aus auswählen, um die Kompensation des Einflusses des Sonnenlichts zu deaktiv

### a03: Wärmepumpe Halle 1, Wie läuft das Estrichtrocknungsprogramm ab und welche Temperaturen werden während des Programms erreicht?

**Pass:** ✅

> **Gefahr der Schädigung oder Zerstörung des Estrichs!**
> Bei Mehrkreisanlagen kann diese Funktion nur in Verbindung mit einem gemischten Heizkreis verwendet werden.
> Estrichtrocknung nach den Angaben des Estrichherstellers einstellen.
> Anlagen trotz Estrichtrocknung täglich besuchen und das vorgeschriebene Protokoll führen.

## Ablauf des Estrichtrocknungsprogramms

Das Estrichtrocknungsprogramm durchläuft die Heizung einmal selbsttätig. Es besteht aus mehreren aufeinanderfolgenden Phasen, die im **Menü Estrichtrocknung** eingestellt werden:

### Phasen und Temperaturen

**1. Wartezeit vor Start**
Optional: Das Estrichtrocknungsprogramm startet nach der eingestellten Wartezeit [1 ... 50] Tage. Die gewählten Heizkreise sind während der Wartezeit ausgeschaltet, der Frostschutz ist aktiv. Alternativ kann die Wartezeit übersprungen werden, sodass das Programm sofort startet.

**2. Startphase**
- Dauer: [1 ... 3 ... 30] Tage (oder übersprungen)
- **Startphase Temperatur**: [20 ... 25 ... 55] °C – Vorlauftemperatur während der Startphase
- Laut Kennfeld-Diagramm: ca. 30 °C bei Tag 0–1

**3. Aufheizphase**
- **Aufheizphase Schrittweite**: [1 ... 10] Tage – zeitlicher Abstand zwischen den Stufen
- **Temp.diff. in Aufheizph.**: [1 ... 5 ... 35] K – Temperaturdifferenz zwischen den Stufen
- Laut Kennfeld-Diagramm: Anstieg auf ca. 45 °C (Tag 2–3), dann weiter auf ca. 60 °C (Tag 4–6)
- Die Aufheizphase kann auch übersprungen werden

**4. Haltephase**
- **Haltephase Dauer**: [1 ... 7 ... 99] Tage – Haltedauer der Maximaltemperatur
- **Haltephase Temperatur**: [20 ... 55] °C – Vorlauftemperatur während der Haltephase (Maximaltemperatur)
- Laut Kennfeld-Diagramm: ca. 60 °C als Maximaltemperatur-Plateau (Tag 4–6)

**5. Abkühlphase**
- **Abkühlphase Schrittweite**: [1 ... 10] Tage – zeitlicher Abstand zwischen den Stufen
- **Temp.diff. in Abkühlph.**: [1 ... 5 ... 35] K – Temperaturdifferenz zwischen den Stufen
- Laut Kennfeld-Diagramm: Abkühlung auf ca. 30 °C (Tag 10–14)
- Die Abkühlphase kann auch übersprungen werden

**6. Endphase**
- **Endphase Dauer**: [1 ... 30] Tage oder „Dauerh. an" (kein Endzeitpunkt festgelegt), oder übersprungen
- **Temperatur der Endphase**: [20 ... 25 ... 55] °C – Vorlauftemperatur während der Endphase

### Verhalten bei Unterbrechung

Nach einem Stromausfall oder einem Ausschalten der Wärmepumpe setzt die Bedieneinheit das Estrichtrocknungsprogramm automatisch fort, sofern der Spannungsausfall nicht länger andauert als die Gangreserve der Bedieneinheit (≥ 4 h) oder die eingestellte maximale Unterbrechungsd

### a04: Wärmepumpe Halle 1, Wie ist der Kältekreislauf der Wärmepumpe aufgebaut und welche Hauptkomponenten sind enthalten?

**Pass:** ✅

Der Kältekreislauf der Wärmepumpe ist als geschlossener Kreislauf aufgebaut und umfasst folgende Hauptkomponenten:

1. **Kompressor** — Verdichtungseinheit des Kältemittels (oberer Bereich, zentral)
2. **Kondensator/Verflüssiger** — Wärmeabgabe-Wärmetauscher (rechts oben)
3. **Expansionsventil/Drosselorgan** — Druckregelung (rechts unten)
4. **Verdampfer** — Wärmeeingabe-Wärmetauscher (links unten)
5. **Zirkulations-/Umwälzpumpe** — Fluidtransport (links)

Der Kältemittelkreislauf verläuft im Uhrzeigersinn:
- **Saugseite**: Verdampfer → Kompressor (blaue Linie)
- **Druckseite**: Kompressor → Kondensator (rote Linie)
- **Rücklauf**: durch das Expansionsventil zurück zum Verdampfer

Die typischen Temperaturen im Kreislauf betragen +5 °C, +35 °C, +65 °C und -5 °C an den jeweiligen Messpunkten.

Die Außeneinheit fungiert dabei als Verdampfer, der Wärmeenergie aus der Umgebungsluft aufnimmt und diese an den Kältemittelkreislauf abgibt. Die ovale Frontöffnung der Außeneinheit ermöglicht optimale Luftströmung zur Effizienzmaximierung.

---

- Dokument, Seite 18 — Technische Beschreibung: Wärmepumpen-Kreislaufschema
- Dokument, Seite 4 — Technische Beschreibung: Außeneinheit einer Luft-Wasser-Wärmepumpe

### a05: Wärmepumpe Halle 1, Welche Einstellmöglichkeiten gibt es für eine angeschlossene Solarthermieanlage im Servicemenü?

**Pass:** ✅

Im Servicemenü unter **Service > Solar** stehen folgende Einstellmöglichkeiten für eine angeschlossene Solarthermieanlage zur Verfügung:

**Tab. 12 Übersicht Einstellungen für Solarthermieanlagen**

| Menüpunkt | Beschreibung |
|---|---|
| Solarerweiterungsmodul | Ein auswählen, um das Solarerweiterungsmodul für die Solarthermieanlage zu aktivieren. -oder- Zum Deaktivieren Aus auswählen. |
| Aktuelle Solarkonfiguration | Zeigt die aktuelle Konfiguration der Solarthermieanlage. |
| Solarkonfiguration ändern | Bestätigen auswählen, um die Konfiguration der Solarthermieanlage zu bearbeiten. -oder- Um zurückzukehren, Abbrechen auswählen. Um die gewünschte Anlagenkonfiguration auszuwählen und Komponenten hinzuzufügen, durch die Menüoptionen scrollen. Element hinzufügen auswählen, um die ausgewählten Komponenten hinzuzufügen. -oder- Zum Beenden Hinzufügen beenden auswählen. Konfig. abschließen auswählen, wenn die Konfigura- |
| Einstellungen | ▶ Solarkreis. ▶ Speicher (Wärmesenken). Einstellungen für den im Solarkreis installierten Speicherbehälter, Wärmetauscher oder Pool vornehmen. ▶ Solarertrag. In diesem Menü können Einstellungen für die Energierückgewinnung und den geschätzten Solarenergieertrag konfiguriert werden. Die Werte können zurückgesetzt werden. |

**Tab. 13 Einstellungen für Solarthermieanlagen**

| Menüpunkt | Beschreibung |
|---|---|
| Solarsystem starten | Ein auswählen, um die Solarthermieanlage zu aktivieren, wenn sie befüllt, entlüftet und betriebsbereit ist. |

Unter dem Menüpunkt **Einstellungen > Solarkreis** sind u. a. folgende Parameter verfügbar:
- PS1 Drehzahlreg. Solarp.
- PS1 Min. Drehzahl Solarp.
- PS1 Einschaltdiff. Solarp.
- PS1 Ausschaltdiff. Solarp.
- Solltemp. Vario-Match-Flow
- PS4 Drehzahlreg. Solarp. 2
- PS4 Min. Drehzahl Solarp. 2
- PS4 Einschaltdiff. Solarp. 2
- PS4 Ausschaltdiff. Solarp. 2
- Max. Kollektortemperatur
- Min. Kollektortemperatur
- PS1 Vakuumr.-Pumpenkick
- PS4 Vakuumr.-Pumpenkick
- Südeuropafunktion
- Außentemperatur
- Kollektorkühlfunktion

Unter **Einstellungen > Speicher (Wärmesenken)**:
- Max. Temp. Speicher 1
- Max. Temp. Speicher 2
- Max. Temp. Pool
- Max. Temp. Speicher 3 (mehrfach)
- Vorrangspeicher
- Prüfintervall Vorrangspeicher
- Prüfdauer Vorrangspeicher
- Ventillaufzeit Speicher 2
- PS5 Einschalttemp.-Diff.
- PS5 Ausschalttemp.-Diff.
- Frostschutz

Unter **Einstellungen > Solarertrag**:
- Brutto-Kollektorfläche 1
- Typ Kollektorfeld 1 (Flachkolle
