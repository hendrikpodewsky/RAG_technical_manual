# Eval-Report (Archiv, Stand 2026-05-26)

> ⚠️ **Veralteter Zwischenstand** — abgelöst durch [`eval/report.md`](../report.md) (20/20, bestätigt 2026-05-27). Aufbewahrt zur Dokumentation des Entwicklungsverlaufs.

**Score: 14/20 (70%)**


| ID | Frage | Pass | Latenz | Fehler |
|----|-------|------|--------|--------|
| q01 | Wärmepumpe Halle 1, Was muss bei der Funktion Extra-Warmwass… | ✅ | 20.7s | — |
| q02 | Wärmepumpe Halle 1, Welche Gefahr besteht bei zu hohen Tempe… | ✅ | 18.1s | — |
| q03 | Wärmepumpe Halle 1, Wo im Menü stelle ich den geräuscharmen … | ❌ | 14.6s | should be answerable but got no-info response; missing topic: 'Geräuscharmer Betrieb' |
| q04 | Wärmepumpe Halle 1, Ab welcher dauerhaften Vorlauftemperatur… | ❌ | 10.7s | should be answerable but got no-info response; missing topic: '45'; missing topic: 'Lebensdauer' |
| q05 | Wärmepumpe Halle 1, Wie programmiere ich eine WLAN-Verbindun… | ✅ | 17.7s | — |
| q06 | Wärmepumpe Halle 1, Was bedeutet eine rote Status-LED an der… | ❌ | 18.0s | missing topic: 'Störung' |
| q07 | Wärmepumpe Halle 1, Was bedeutet Standby-Betrieb und welche … | ❌ | 17.9s | should be answerable but got no-info response; missing topic: 'Standby'; missing topic: 'Frostschutz' |
| q08 | Wärmepumpe Halle 1, Wo stelle ich die Warmwasser-Temperatur … | ✅ | 26.7s | — |
| q09 | Wärmepumpe Halle 1, Wie starte ich die Wärmepumpe schnell ma… | ✅ | 20.7s | — |
| q10 | Wärmepumpe Halle 1, Wie wechsle ich die Systemfunktion von H… | ✅ | 23.6s | — |
| q11 | Wärmepumpe Halle 1, Wozu dient die thermische Desinfektion d… | ✅ | 24.2s | — |
| q12 | Wärmepumpe Halle 1, Was benötige ich für ein Software-Update… | ✅ | 27.0s | — |
| q13 | Wärmepumpe Halle 1, Wo im Servicemenü finde ich die aktuelle… | ✅ | 18.3s | — |
| q14 | Wärmepumpe Halle 1, Wie führe ich einen manuellen Entfrostun… | ❌ | 24.7s | should be unanswerable but got a real answer |
| q15 | Wärmepumpe Halle 1, Was soll ich nach einem Stromausfall tun… | ❌ | 16.5s | should be answerable but got no-info response; missing topic: 'Stromausfall'; missing topic: 'Datum' |
| q16 | Wärmepumpe Halle 1, Wie schütze ich die Anlage vor dem Einfr… | ✅ | 19.9s | — |
| q17 | Wärmepumpe Halle 1, Wo passe ich die Heizkurve an? | ✅ | 23.4s | — |
| q18 | Wärmepumpe Halle 1, Was muss ich nach Abschluss der Inbetrie… | ✅ | 17.5s | — |
| q19 | Wie verbinde ich die Wärmepumpe mit der Bosch-App? | ✅ | 14.8s | — |
| q20 | Wärmepumpe Halle 1, Wie integriere ich das Gerät in ein KNX-… | ✅ | 16.0s | — |

## Antworten

### q01: Wärmepumpe Halle 1, Was muss bei der Funktion Extra-Warmwasser bezüglich Verbrühungsgefahr beachtet werden?

**Pass:** ✅

> **Verbrühungsgefahr!**
> Beim Aktivieren der Funktion "Extra-Warmwasser", bei der thermischen Desinfektion und bei der täglichen Aufheizung sind Warmwassertemperaturen über 60 °C möglich. Deshalb muss eine Mischeinrichtung installiert werden.

---

**Quellenangabe:**
- Dokument: Installationsanleitung Wärmepumpe Halle 1, Seite 3, Abschnitt: Verbrühungsgefahr!

### q02: Wärmepumpe Halle 1, Welche Gefahr besteht bei zu hohen Temperaturen für Fußbodenheizungen?

**Pass:** ✅

> **ACHTUNG – Schäden am Fußboden!**
> Bei zu hohen Temperaturen sind Schäden am Fußboden möglich.
> Bei Fußbodenheizung darauf achten, dass die Maximaltemperatur des jeweiligen Fußbodentyps nicht überschritten wird.
> Ggf. einen zusätzlichen Temperaturwächter am Spannungseingang der jeweiligen Zirkulationspumpe oder an einen der externen Eingänge anschließen.

Bei zu hohen Temperaturen besteht die Gefahr von **Schäden am Fußboden**. Es muss sichergestellt werden, dass die Maximaltemperatur des jeweiligen Fußbodentyps nicht überschritten wird. Als Schutzmaßnahme kann ggf. ein zusätzlicher Temperaturwächter am Spannungseingang der jeweiligen Zirkulationspumpe oder an einen der externen Eingänge angeschlossen werden.

---

- Dokument: Bedienungsanleitung Wärmepumpe Halle 1, Seite 3, Abschnitt: „Schäden am Fußboden!"

### q03: Wärmepumpe Halle 1, Wo im Menü stelle ich den geräuscharmen Betrieb ein?

**Pass:** ❌

Mir liegt dazu keine Information vor.

### q04: Wärmepumpe Halle 1, Ab welcher dauerhaften Vorlauftemperatur kann die Lebensdauer des Geräts beeinträchtigt werden?

**Pass:** ❌

Mir liegt dazu keine Information vor.

### q05: Wärmepumpe Halle 1, Wie programmiere ich eine WLAN-Verbindung?

**Pass:** ✅

Mir liegt dazu keine Information vor.

### q06: Wärmepumpe Halle 1, Was bedeutet eine rote Status-LED an der Bedieneinheit?

**Pass:** ❌

Die Quellpassagen enthalten zwar einen Abschnitt zur **Status-LED** (Passage 1, Seite 3, Abschnitt 3.3), der beschreibt, dass die LED oben auf dem Bedienfeld mithilfe von verschiedenen Farben den Betriebsstatus des Geräts anzeigt — jedoch wird die Bedeutung der **roten** Status-LED in den vorliegenden Passagen nicht konkret erläutert.

### q07: Wärmepumpe Halle 1, Was bedeutet Standby-Betrieb und welche Funktion ist dabei nicht aktiv?

**Pass:** ❌

Mir liegt dazu keine Information vor.

### q08: Wärmepumpe Halle 1, Wo stelle ich die Warmwasser-Temperatur im Servicemenü ein?

**Pass:** ✅

Die Quellpassagen beschreiben das Servicemenü und das Menü „Warmwasser", enthalten jedoch keine konkrete Schritt-für-Schritt-Anleitung, an welcher genauen Stelle im Servicemenü die Warmwasser-Temperatur eingestellt wird.

Aus den vorliegenden Passagen lässt sich jedoch Folgendes entnehmen:

**Aufruf des Servicemenüs:**
Laut Abschnitt 5 (Seite 6) gilt: „Um das Servicemenü aufzurufen, Taste Menü gedrückt halten, bis der Countdown abgelaufen ist (ca. 5 Sekunden)."

**Relevanter Menüpunkt im Servicemenü:**
In der Übersicht (Seite 23, Abschnitt „Info") ist unter dem Bereich **Warmwasser** folgender Eintrag aufgeführt:
- **TW1 Starttemperatur WW**
- TW1 Temperatur WW
- TW2 Auslauftemp. WW

Ergänzend beschreibt Passage 1 (Seite 13, Abschnitt 5.1.8 „Menü: Warmwasser"):
„Ist im Warmwasserspeicher ein Temperaturfühler (TW1) installiert, wird die Warmwasserbereitung angefordert, sobald die gewählte **Starttemperatur** an TW1 unterschritten wird."

Sowie aus Abschnitt 4.2.2 (Seite 5): „Die Einstellungen im **Menü Warmwasser** müssen bei der Inbetriebnahme geprüft und ggf. angepasst werden."

> **Verbrühungsgefahr!**
> Beim Aktivieren der Funktion "Extra-Warmwasser", bei der thermischen Desinfektion und bei der täglichen Aufheizung sind Warmwassertemperaturen über 60 °C möglich. Deshalb muss eine Mischeinrichtung installiert werden.

Die Warmwasser-Temperatur (Starttemperatur) wird demnach im Servicemenü unter dem Menü **Warmwasser** → **TW1 Starttemperatur WW** eingestellt.

---

- Dokument: Installationsanleitung Wärmepumpe
- Seite 6, Abschnitt 5 „Servicemenü"
- Seite 13, Abschnitt 5.1.8 „Menü: Warmwasser"
- Seite 5, Abschnitt 4.2.2 „Wichtige Einstellungen für den Warmwasserbetrieb"
- Seite 23, Abschnitt 8 „Übersicht Service"
- Seite 3, Abschnitt „Verbrühungsgefahr!"

### q09: Wärmepumpe Halle 1, Wie starte ich die Wärmepumpe schnell manuell über das Servicemenü?

**Pass:** ✅

Laut den vorliegenden Quellpassagen gehen Sie wie folgt vor, um die Wärmepumpe schnell manuell über das Servicemenü zu starten:

1. **Servicemenü aufrufen:** Die Taste **Menü** gedrückt halten, bis der Countdown abgelaufen ist (ca. 5 Sekunden), bis das Servicemenü erscheint.

2. **Navigation:** **Anlageneinstellungen** auswählen und dann **Manuelle Inbetriebnahme** auswählen.

3. **Schnellstart auswählen:** **Schneller Kompressorstart** auswählen.

4. **Bestätigen:** Im Dialogfenster **Ja** auswählen.

Die Schnellstartfunktion erhöht die Wärmeanforderung, sodass die Wärmepumpe schnellstmöglich startet.

---

**Quellen:**
- Dokument: Bedienfeld UI 800, Luft-Wasser-Wärmepumpe
- Seite 5, Abschnitt: 4.6 Schnellstart der Wärmepumpe
- Seite 6, Abschnitt: 5 Servicemenü

### q10: Wärmepumpe Halle 1, Wie wechsle ich die Systemfunktion von Heizen auf Kühlen?

**Pass:** ✅

Zum Wechsel der Systemfunktion von Heizen auf Kühlen sind folgende Informationen aus der Dokumentation relevant:

> **HINWEIS:** Für einen effizienten Wärmepumpenbetrieb sollte vermieden werden, die Betriebsart (Heizen oder Kühlen) für einen Tag zu wechseln.

> **HINWEIS:** Es muss sichergestellt sein, dass die Anlage vor Kondensat geschützt ist.

Gemäß Abschnitt **5.1.5 Menü: Heizen und Kühlen** gilt folgendes Vorgehen:

Um im Sommer in den **Kühlbetrieb** zu wechseln, muss **einer der Heizkreise für den Kühlbetrieb konfiguriert werden**. Die Konfiguration erfolgt im Menü **Heizen und Kühlen**. Die dort angegebenen Einstellungen gelten für alle Heizkreise.

Wenn für den Heizkreis **Kühlen** oder **Heizen und Kühlen** als Betriebsart festgelegt ist, wird das Menü **Kühlen** angezeigt.

Die Einstellungen für den Heizkreis müssen im Menü **Heizung / Kühlung** vorgenommen werden (vgl. Abschnitt 5.1.1 Manuelle Inbetriebnahme).

---

**Quellenangabe:**
- Dokument: Wärmepumpe Bedienungsanleitung, Seite 10, Abschnitt 5.1.5 „Menü: Heizen und Kühlen"
- Dokument: Wärmepumpe Bedienungsanleitung, Seite 6, Abschnitt 5.1.1 „Manuelle Inbetriebnahme"

### q11: Wärmepumpe Halle 1, Wozu dient die thermische Desinfektion des Warmwasserspeichers?

**Pass:** ✅

Die thermische Desinfektion des Warmwasserspeichers dient dazu, Krankheitserreger (z. B. Legionellen) abzutöten. Für größere Warmwasseranlagen gelten gegebenenfalls spezielle Rechtsbestimmungen für die thermische Desinfektion.

> **Verbrühungsgefahr!**
> Beim Aktivieren der Funktion "Extra-Warmwasser", bei der thermischen Desinfektion und bei der täglichen Aufheizung sind Warmwassertemperaturen über 60 °C möglich. Deshalb muss eine Mischeinrichtung installiert werden.

Zusätzlich wird darauf hingewiesen: Wenn die Armaturen während der thermischen Desinfektion zur Desinfizierung der Verrohrung geöffnet werden, die Armaturen von Zeit zu Zeit wieder schließen, um der Wärmepumpe die Gelegenheit zu geben, die Temperatur des Warmwasserspeichers entsprechend den Einstellungen der Konfiguration aufrechtzuerhalten.

---

- Dokument: Bedienungsanleitung Wärmepumpe Halle 1, Seite 13, Abschnitt: **Menü: Warmwasser** (5.1.8)
- Dokument: Bedienungsanleitung Wärmepumpe Halle 1, Seite 3, Abschnitt: **Verbrühungsgefahr!**

### q12: Wärmepumpe Halle 1, Was benötige ich für ein Software-Update der Bedieneinheit?

**Pass:** ✅

Für ein Software-Update der Bedieneinheit benötigen Sie folgendes:

**Mobilgerät mit Service-App:**

Zum Durchführen eines Software-Updates wird die **Service-App Bosch EasyService** benötigt, die im Apple App Store oder Google Play Store erhältlich ist. Für den Download der Software-Datenbank auf das Mobilgerät ist eine **Internetverbindung** erforderlich. Für die eigentliche Aktualisierung des Geräts vor Ort ist hingegen **keine Internetverbindung** erforderlich, da die Software-Datenbank auf dem Mobilgerät gespeichert wird.

**Vorbereitung der App:**
- Service-App Bosch EasyService herunterladen und installieren
- Nutzungsbedingungen sowie die kontinuierliche Aktualisierung der Datenbank bestätigen
- Manuell den ersten Download der Software-Datenbank starten

**Durchführung des Updates am Gerät:**
- Funktion **Software-Aktualisierung** im Servicemenü des Geräts auswählen
- In der Service-App **Software-Aktualisierung > Software-Aktualisierung starten** auswählen
- Den auf dem Gerät angezeigten **QR-Code** mit der Service-App auf dem Mobilgerät scannen
- Nach Verbindungsaufbau in der Service-App **Systemaktualisierung starten** auswählen

Die Updates werden auf den **K40 RF** übertragen, der die Updates an das Gerät verteilt, neu startet und die Einstellungen wiederherstellt. Nach der Aktualisierung wird ein Bericht (PDF) in der Service-App erstellt.

> Hinweis: Die Systemsoftware kann von einer **Fachkraft** aktualisiert werden. Den Kunden darüber informieren, dass für die Aktualisierung des Geräts beim Kunden bestimmte Daten an Bosch übertragen werden, beispielsweise die Seriennummer. Diese Daten werden anonymisiert.

---

- Dokument: Installationsanleitung, Seite 18–19, Abschnitt 5.5 „Aktualisieren der Systemsoftware", „App herunterladen und installieren", „Auf dem Gerät auf Updates prüfen"

### q13: Wärmepumpe Halle 1, Wo im Servicemenü finde ich die aktuellen Störungen der Anlage?

**Pass:** ✅

Im Servicemenü finden Sie die aktuellen Störungen der Anlage im **Menü: Störungen**.

Laut den Quellpassagen gilt dazu Folgendes:

> In diesem Menü werden die aktuellen Alarme und der Alarmverlauf angezeigt.

Um das Servicemenü aufzurufen, müssen Sie die **Taste Menü gedrückt halten, bis der Countdown abgelaufen ist (ca. 5 Sekunden)**. Anschließend können Sie auf die Überschrift **Störungen** drücken, um das Menü zu öffnen.

---

**Quellen:**
- Dokument: Bedienungsanleitung Wärmepumpe, Seite 17, Abschnitt: Menü: Störungen
- Dokument: Bedienungsanleitung Wärmepumpe, Seite 6, Abschnitt: Servicemenü

### q14: Wärmepumpe Halle 1, Wie führe ich einen manuellen Entfrostungsvorgang durch?

**Pass:** ❌

Zur manuellen Entfrostung findet sich in den vorliegenden Quellpassagen folgender relevanter Hinweis:

In der Menüstruktur unter **Anlageneinstellungen** > **Wärmepumpe** ist der Menüpunkt **Manuelle Abtauung** aufgeführt.

Der genaue Navigationsweg lautet gemäß der Menüübersicht:

**Anlageneinstellungen** → **Wärmepumpe** → **Manuelle Abtauung**

Weitere Details zur Durchführung des manuellen Entfrostungsvorgangs (z. B. konkrete Bedienschritte oder Beschreibung der Funktion) sind in den vorliegenden Quellpassagen nicht enthalten.

---

**Quellenangabe:**
- Dokument: Wärmepumpe Bedienungsanleitung, Seite 19, Abschnitt: Anlageneinstellungen

### q15: Wärmepumpe Halle 1, Was soll ich nach einem Stromausfall tun?

**Pass:** ❌

Mir liegt dazu keine Information vor.

### q16: Wärmepumpe Halle 1, Wie schütze ich die Anlage vor dem Einfrieren?

**Pass:** ✅

Aus den vorliegenden Quellpassagen geht hervor, dass der **Standby-Betrieb** einen relevanten Aspekt beim Thema Frostschutz darstellt. Dazu wird ausdrücklich gewarnt:

> **Standby bedeutet, dass die Anlage komplett ausgeschaltet ist und keine Sicherheitsfunktionen, wie Frostschutz, aktiv sind.**

Das bedeutet: Wenn die Anlage in den Standby-Betrieb versetzt wird, ist der Frostschutz **nicht** aktiv. Um die Anlage vor dem Einfrieren zu schützen, darf sie **nicht** in den Standby-Betrieb geschaltet werden, da in diesem Zustand keinerlei Sicherheitsfunktionen – einschließlich des Frostschutzes – aktiv sind.

Darüber hinaus enthalten die vorliegenden Quellpassagen keine weiteren konkreten Anweisungen oder Einstellungen zum Schutz der Anlage vor dem Einfrieren.

---

**Quellenangabe:**
- Dokument: Bedienungsanleitung Wärmepumpe, Seite 5, Abschnitt: *4.5 Abschaltung*

### q17: Wärmepumpe Halle 1, Wo passe ich die Heizkurve an?

**Pass:** ✅

Die Heizkurve wird im **Menü Heizung / Kühlung** unter dem Menüpunkt **Heizkurve** für den jeweiligen **Heizkreis 1…4** angepasst.

Laut Passage 1 (Seite 5) gilt dazu:

> „Einstellungen im Menü für Heizkreis 1 …4 überprüfen. Heizkurve entsprechend den Anlagenanforderungen einstellen."

Für die Heizkurve stehen zwei Varianten zur Verfügung (Menüpunkt **Regelungsart**):

| Menüpunkt | Einstellintervall |
|---|---|
| Heizkurve | Es sind zwei Varianten der Heizkurve für die Regelung entsprechend der Außentemperatur vorhanden: |
| | ▶ Regelungsart > **Außentemperatur geführt**: ist eine aufwärts gekrümmte Heizkurve, die auf einer optimierten Zuordnung der Vorlauftemperatur entsprechend der Außentemperatur beruht. Es müssen nur die gewünschte Temperatur und die maximale Temperatur eingestellt werden. Diese Variante ist die Grundeinstellung und eignet sich für gängige Anwendungsfälle. |
| | ▶ Regelungsart > **Außentemperatur mit Fußpunkt**: Die Außentemperatur mit Fußpunkt ist eine klassische Heizkurveneinstellung, die verschiedene Optionen bietet, um den individuellen Anforderungen des Gebäudes gerecht zu werden. Diese Heizkurve hat einen Fuß- und einen Endpunkt. Während der Übergangszeit kann der Installateur einen Komfortpunkt einstellen, um die Heizkurve leicht zu erhöhen. |
| | Der Fußpunkt entspricht der Vorlauftemperatur, die bei einer Außenlufttemperatur von 20 °C erreicht wird. |
| | Der Endpunkt ist die Vorlauftemperatur, die bei der niedrigsten Außenlufttemperatur in der Region erreicht wird, und beeinflusst demzufolge die Steigung der Heizkurve. |
| | Der Komfortpunkt ermöglicht die Erhöhung der Vorlauftemperatur in der Übergangszeit Frühling/Herbst. Optional kann der Benutzer bei beiden außentemperaturgeführten Regelungsarten einen Grenzwert für die minimale Vorlauftemperatur einstellen (Einstellung min. Vorlauftemp. = Ein). |

---

- Dokument, Seite 5, Abschnitt: „Wichtige Einstellungen für den Heizbetrieb"
- Dokument, Seite 11, Abschnitt: „Heizkurve"
- Dokument, Seite 21, Abschnitt: „-Heizkurve"

### q18: Wärmepumpe Halle 1, Was muss ich nach Abschluss der Inbetriebnahme im Servicemenü speichern?

**Pass:** ✅

Nach Abschluss der Inbetriebnahme müssen alle Einstellungen im Servicemenü gespeichert werden. Laut der Bedienungsanleitung gilt folgendes:

**Nach dem Abschluss der Inbetriebnahme unbedingt alle Einstellungen speichern. Dafür im Servicemenü auf `Installateureinstell. speichern` tippen.**

---

**Quellen:**
- Dokument: Bedienungsanleitung Wärmepumpe
- Seite 5, Abschnitt: *Weitere Einstellungen für die Inbetriebnahme* (Kapitel 4.2)

### q19: Wie verbinde ich die Wärmepumpe mit der Bosch-App?

**Pass:** ✅

Mir liegt dazu keine Information vor.

### q20: Wärmepumpe Halle 1, Wie integriere ich das Gerät in ein KNX-Bussystem?

**Pass:** ✅

Mir liegt dazu keine Information vor.
