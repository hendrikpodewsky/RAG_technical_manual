# Eval-Report

**Score: 10/20 (50%)**


| ID | Frage | Pass | Latenz | Fehler |
|----|-------|------|--------|--------|
| q01 | Wärmepumpe Halle 1, Was muss bei der Funktion Extra-Warmwass… | ✅ | 29.4s | — |
| q02 | Wärmepumpe Halle 1, Welche Gefahr besteht bei zu hohen Tempe… | ✅ | 41.4s | — |
| q03 | Wärmepumpe Halle 1, Wo im Menü stelle ich den geräuscharmen … | ❌ | 34.8s | missing topic: 'Geräuscharmer Betrieb' |
| q04 | Wärmepumpe Halle 1, Ab welcher dauerhaften Vorlauftemperatur… | ✅ | 36.7s | — |
| q05 | Wärmepumpe Halle 1, Wie programmiere ich eine WLAN-Verbindun… | ❌ | 83.3s | should be unanswerable but got a real answer |
| q06 | Wärmepumpe Halle 1, Was bedeutet eine rote Status-LED an der… | ✅ | 29.2s | — |
| q07 | Wärmepumpe Halle 1, Was bedeutet Standby-Betrieb und welche … | ❌ | 32.5s | missing topic: 'Frostschutz' |
| q08 | Wärmepumpe Halle 1, Wo stelle ich die Warmwasser-Temperatur … | ✅ | 34.2s | — |
| q09 | Wärmepumpe Halle 1, Wie starte ich die Wärmepumpe schnell ma… | ❌ | 32.4s | missing topic: 'Schnellstart'; missing topic: 'Kompressor' |
| q10 | Wärmepumpe Halle 1, Wie wechsle ich die Systemfunktion von H… | ✅ | 36.7s | — |
| q11 | Wärmepumpe Halle 1, Wozu dient die thermische Desinfektion d… | ✅ | 49.4s | — |
| q12 | Wärmepumpe Halle 1, Was benötige ich für ein Software-Update… | ❌ | 34.2s | should be answerable but got no-info response; missing topic: 'EasyService'; missing topic: 'Aktualisieren' |
| q13 | Wärmepumpe Halle 1, Wo im Servicemenü finde ich die aktuelle… | ✅ | 58.2s | — |
| q14 | Wärmepumpe Halle 1, Wie führe ich einen manuellen Entfrostun… | ✅ | 34.0s | — |
| q15 | Wärmepumpe Halle 1, Was soll ich nach einem Stromausfall tun… | ❌ | 39.3s | missing topic: 'Datum' |
| q16 | Wärmepumpe Halle 1, Wie schütze ich die Anlage vor dem Einfr… | ❌ | 38.1s | missing topic: 'Frostschutz' |
| q17 | Wärmepumpe Halle 1, Wo passe ich die Heizkurve an? | ❌ | 72.6s | missing topic: 'Heizkurve' |
| q18 | Wärmepumpe Halle 1, Was muss ich nach Abschluss der Inbetrie… | ❌ | 50.4s | missing topic: 'speichern'; missing topic: 'Installateureinstell' |
| q19 | Wie verbinde ich die Wärmepumpe mit der Bosch-App? | ✅ | 30.5s | — |
| q20 | Wärmepumpe Halle 1, Wie integriere ich das Gerät in ein KNX-… | ❌ | 36.4s | should be unanswerable but got a real answer |

## Antworten

### q01: Wärmepumpe Halle 1, Was muss bei der Funktion Extra-Warmwasser bezüglich Verbrühungsgefahr beachtet werden?

**Pass:** ✅

> Verbrühungsgefahr!

Beim Aktivieren der Funktion "Extra-Warmwasser", bei der thermischen Desinfektion und bei der täglichen Aufheizung sind Warmwassertemperaturn über 60 °C möglich. Deshalb muss eine Mischeinrichtung installiert werden, um Verbrühungsgefahr zu vermeiden.

### q02: Wärmepumpe Halle 1, Welche Gefahr besteht bei zu hohen Temperaturen für Fußbodenheizungen?

**Pass:** ✅

> Verbrühungsgefahr!

Beim Aktivieren der Funktion "Extra-Warmwasser", bei der thermischen Desinfektion und bei der täglichen Aufheizung sind Warmwassertemperaturen über 60 °C möglich. Deshalb muss eine Mischeinrichtung installiert werden.

Bei zu hohen Temperaturen für Fußbodenheizungen besteht Gefahr, dass Schäden am Fußboden auftreten. Hierbei ist es wichtig darauf zu achten, dass die Maximaltemperatur des jeweiligen Fußbodentyps nicht überschritten wird. In solchen Fällen kann es nützlich sein, einen zusätzlichen Temperaturwächter an den Spannungseingang der Zirkulationspumpe oder an einen externen Eingang anzuschließen.

Es besteht also eine Verbrühungsgefahr bei zu hohen Temperaturen für Fußbodenheizungen. Um diese Gefahr zu vermeiden, sollte die Maximaltemperatur nicht überschritten werden und es kann hilfreich sein, einen Temperaturwächter einzubauen.

### q03: Wärmepumpe Halle 1, Wo im Menü stelle ich den geräuscharmen Betrieb ein?

**Pass:** ❌

> Achten Sie auf die Sicherheitshinweise

### q04: Wärmepumpe Halle 1, Ab welcher dauerhaften Vorlauftemperatur kann die Lebensdauer des Geräts beeinträchtigt werden?

**Pass:** ✅

> Verbrühungsgefahr!

Wenn eine konstante Vorlauftemperatur von mehr als 45 °C gewählt wird, kann die Lebensdauer des Geräts beeinträchtigt werden.

### q05: Wärmepumpe Halle 1, Wie programmiere ich eine WLAN-Verbindung?

**Pass:** ❌

Hier ist eine Überarbeitung des Textes mit einer besseren Struktur und Einordnung:

---

### Anlageninfo

#### Heiz- und Kühlstatus
- **Wärmepumpenstatus**
  - Wärmepumpe-Sicht
  - Kompressorstatus
  - Zuheizerstatus
  - Kompressor-Aufheizphase
  - Max. Temperatur erreicht
  - Vorlauftemperatur zu niedrig
  - Max. Zuheizertemperatur überschritten
  - Niedriger Durchfluss in Heizung
- **Heiz-/Kühlbetrieb**
  - Heizbetrieb aus, Außentemperatur zu niedrig
  - Heizbetrieb aus, Außentemperatur zu warm
  - Kühlbetrieb aus, Außentemperatur zu niedrig
  - Kühlbetrieb aus, Außentemperatur zu hoch
- **Sperre Energieversorger aktiv**
- **PV aktivierter Betrieb**
- **Smart Grid aktivierter Betrieb**

#### Eingänge und Ausgänge
- Externer Eingang 1
- Externer Eingang 2
- Externer Eingang 3
- Externer Eingang 4
- Betriebsdruck
- MR0 Niederdruck-Schalter
- MR1 Hochdruck-Schalter
- MB1 Druckschalter Kollektor
- Alarm elektr. Zuheizer
- Temperatur
- TB0 Solekreis Eintritt
- TB1 Solekreis Austritt
- TB2 Grundwasser Temp. Ein
- TB3 Grundwasser Temp. Aus
- TL2 Luftansaugtemperatur
- TB5 Abluftmodul Eintritt
- TB6 Abluftmodul Austritt
- TL2 Abflutmodul Zuluft
- TL1 Abluftmodul Abluft
- JR0 Niederdruckfühler
- TR5 Temperatur Saugleitung
- Kompressor-Aufheizen Ist
- Kompressor-Aufheizen Stopp
- TR6 Heißgastemperatur
- JR1 Hochdruckfühler
- TR3 Verflüssigertemp. Heizung
- TR4 Verdampfertemp.
- TC3 Verflüssigertemp.
- TC1 Vorlauftemp. primär
- TC0 Rücklauftemperatur
- TC1 Ende WW-Anforderung
- TA4 Temp. Kondensatwanne

#### Ausgänge
- Sammelalarm
- Kompressor
  - Kompr. Istdrehzahl
  - Max. Kompressordrehzahl
  - Kompr. Solldrehzahl
  - PC0 prim. Heizungspumpe
  - PC0 Drehzahl
  - Zuheizer Stufe 1
  - Zuheizer Stufe 2
  - Zuheizer Stufe 3
- Leistung Zuheizer
  - Elektrischer Zuheizer WW
- PL3 Gebläse
- VR0 Expansionsventil
- VR1 Expansionsventil
- Pumpenblockierschutz
- Übersicht Timer
  - Kompressorstart
  - Restzeit im Heizbetrieb
  - Restzeit im WW-Betrieb
  - Einschaltverzög. Zuheizer
  - Verzög. So-/Wi-Umschaltung
- Nur Alarme
  - Niederdruck-Störung
  - Verzög. starten nach Abtauung
  - Therm. Desinf. Warmhaltung
  - Entlüftungsfunktion aktiv

#### Heiz- und Kühlstatus (Fortsetzung)
- Umschaltverzögerung Heizen
- Verzögerung Zuheizer
- Power Meter
  - Stromverbrauch
  - 48h Mittelwert Strom
  - 48h Spitzenwert Strom
- Statistik
  - Laufzeit
  - Kompressorstarts
  - Energieverbrauch
  - Abgegebene Energie
- Rücksetzen der Statistiken

#### Anlageninfo
- Außentemperatur
- Dämpfung Gebäudeart
- Vorlaufsollwert
- Rücklauftemperatur
- Heizkreis 1
  - Betriebsart
  - Vorlaufsollwert
  - Vorlauftemperatur
  - Raum-Solltemperatur HK1
  - Akt

### q06: Wärmepumpe Halle 1, Was bedeutet eine rote Status-LED an der Bedieneinheit?

**Pass:** ✅

> ...
> 
> | LED-Farbe   | Betriebsstatus                                                                |
> |-------------|-------------------------------------------------------------------------------|
> | Grün        | Normalbetrieb.                                                                |
> | Gelb        | Warnungen, nicht blockierende Anlagenstörun - gen oder Wartungsinformationen. |
> | Rot         | Verriegelnde oder blockierende Störungen.                                     |

Eine rote Status-LED an der Bedieneinheit bedeutet **Verriegelnde oder blockierende Störungen**.

### q07: Wärmepumpe Halle 1, Was bedeutet Standby-Betrieb und welche Funktion ist dabei nicht aktiv?

**Pass:** ❌

> Sperre Energieversorger aktiv

Standby-Betrieb bedeutet, dass bestimmte Funktionen nicht aktiv sind, während andere inaktiv bleiben. In diesem Fall ist der Heizbetrieb und der Kühlbetrieb nicht aktiv, da die Wärmepumpe im Standby-Betrieb ist.

### q08: Wärmepumpe Halle 1, Wo stelle ich die Warmwasser-Temperatur im Servicemenü ein?

**Pass:** ✅

In diesem Menü können Warmwassereinstellungen vorgenommen werden, die für die Wärmepumpe relevant sind. Um die gewünschte Temperatur für den Warmwasserbetrieb zu setzen, musst du in das entsprechende Menü gehen und dort die Einstellung für die Starttemperatur angeben.

Die beschriebenen Einstellungen sind nur zugänglich, wenn die Anlage wie hier beschrieben aufgebaut und konfiguriert ist. Diese Einstellungen finden sich in der entsprechenden Anleitung der Inneneinheit.

Um die gewünschte Temperatur für den Warmwasserbetrieb zu setzen, musst du im Menü Warmwasser die Option Temperatur wählen und dann den gewünschten Wert eingeben.

### q09: Wärmepumpe Halle 1, Wie starte ich die Wärmepumpe schnell manuell über das Servicemenü?

**Pass:** ❌

> Verbrühungsgefahr!

Strich die Menüauswahl hängt von der installierten Wärmepumpe ab.

Für die Manuelle Inbetriebnahme der Wärmepumpe Halle 1 über das Servicemenü ist keine spezifische Menüauswahl oder Einstellung in den beschriebenen Passagen erwähnt. Daher:

>

### q10: Wärmepumpe Halle 1, Wie wechsle ich die Systemfunktion von Heizen auf Kühlen?

**Pass:** ✅

> Verbrühungsgefahr!

Beim Aktivieren der Funktion "Extra-Warmwasser", bei der thermischen Desinfektion und bei der täglichen Aufheizung sind Warmwassertemperaturen über 60 °C möglich. Deshalb muss eine Mischeinrichtung installiert werden.

Um die Systemfunktion von Heizen auf Kühlen zu wechseln, müssen Sie folgende Schritte ausführen:

1) Wählen Sie das Menü "Heizen und Kühl" aus.
2) Konfigurieren Sie den Heizkreis für den Kühlbetrieb. Dies geschieht nur, wenn eine Fernbedienung mit Feuchtefühler installiert ist.
3) Wenn die Anlage bereits vor Kondensat geschützt ist, können Sie das Menü "Kühl" anzeigen lassen.

Bitte stellen Sie sicher, dass die Anlage vor Kondensat geschützt ist. Die maximale Temperatureinstellung hängt von der Variante der Inneneinheit ab.

Wenn für den Heizkreis nur Kühl oder Heizen und Kühl als Betriebsart festgelegt sind, wird das Menü "Kühl" angezeigt. Wenn Sie die Anlage nicht vor Kondensat geschützt haben, ist es nicht sicher, die Systemfunktion von Heizen auf Kühl zu wechseln.

Bitte beachten Sie, dass diese Schritte nur für bestimmte Länder verfügbar sind und nur bei bestimmten Anlagenkombinationen angewendet werden können.

### q11: Wärmepumpe Halle 1, Wozu dient die thermische Desinfektion des Warmwasserspeichers?

**Pass:** ✅

> Verbrühungsgefahr!

Die thermische Desinfektion des Warmwasserspeichers dient dazu, Krankheitserreger wie Legionellen abzutöten. Diese Funktion wird im Menü Warmwasser aktiviert und ermöglicht es, die Temperatur des Warmwasserspeichers zu erhöhen, wenn der Armaturen zur Desinfektion der Verrohrung geöffnet werden. Es wird empfohlen, diese Einstellung regelmäßig durchzuführen, um sicherzustellen, dass die Wärmepumpe die Temperatur des Warmwasserspeichers entsprechend den Einstellungen der Konfiguration aufrechterhält.

Die thermische Desinfektion erfolgt bei der Aktivierung der Funktion "Extra-Warmwasser", bei der thermischen Desinfektion und bei der täglichen Aufheizung. Diese Maßnahmen sind jedoch nur möglich, wenn eine Mischeinrichtung installiert ist, um Warmwassertemperaturen über 60 °C zu vermeiden.

Die Einstellungen für die thermische Desinfektion finden sich im Menü Warmwasser und hängen von der installierten Kombination von Wärmepumpe und Inneneinheit ab. Es wird empfohlen, diese Einstellungen bei der Inbetriebnahme zu prüfen und ggf. anzupassen, um sicherzustellen, dass der Warmwasserbetrieb einwandfrei funktioniert.

Die maximale Temperatureinstellung ist von der Variante der Inneneinheit abhängig und muss sichergestellt werden, dass die Anlage vor Kondensat geschützt ist. Es wird empfohlen, den Hochdruckschalter-Test in Österreich durchzuführen, wenn das Wärmepumpe-Kältemittel R290 verwendet wird und eine Heizleistung von mehr als 7 kW bereitgestellt wird.

Die thermische Desinfektion des Warmwasserspeichers ist daher ein wichtiger Bestandteil der Wärmepumpen-Systeme, um sicherzustellen, dass die Anlagen hygienisch und effizient funktionieren.

### q12: Wärmepumpe Halle 1, Was benötige ich für ein Software-Update der Bedieneinheit?

**Pass:** ❌

Mir liegt dazu keine Information vor.

### q13: Wärmepumpe Halle 1, Wo im Servicemenü finde ich die aktuellen Störungen der Anlage?

**Pass:** ✅

> **Übersicht der Menüpfade und Informationen zur Störungsbehandlung:**
>
> In der beschriebenen Systemstruktur ist es wichtig zu beachten, dass das Servicemenü für die Überprüfung von Warnungen und Störungen sowie die Rücksetzung des Störungsverlaufs verfügbar ist. Dieses Menü wird in Kapitel 5 auf Seite 6 genauer behandelt.
>
> **Störungsbehandlung:**
>
> Die Störungsbehandlung erfolgt im Servicemenü, das sich in der beschriebenen Systemstruktur befindet. Es bietet eine Überprüfung und Rücksetzung von Warnungen sowie den Störungsverlauf an. Diese Funktion wird in Kapitel 5 auf Seite 6 genauer behandelt.
>
> **Menüpfade zur Lüftung:**
>
> Die Einstellungen für die Lüftung sind im Menü "Lüftung" verfügbar, das sich ebenfalls in der beschriebenen Systemstruktur befindet. Diese Informationen werden in Kapitel 5 auf Seite 14 genauer behandelt.
>
> **Gefundene Menüpfade:**
>
> - Um im Sommer in den Kühlbetrieb zu wechseln, muss einer der Heizkreise für den Kühlbetrieb konfiguriert werden. (Seite 10)
> - Verfügbar wenn ein Energy Manager angeschlossen und konfiguriert ist. (Seite 14)

**Fazit:**
Es wird empfohlen, das Servicemenü im System zu überprüfen, um Warnungen und Störungsverlaufe zu beheben. Die Einstellungen für die Lüftung sind in der Menüebene "Lüftung" verfügbar. Es ist wichtig, dass ein Energy Manager angeschlossen und konfiguriert ist, damit die entsprechenden Einstellungen zur Verfügung stehen.

---

**Anmerkungen:**
- Das Servicemenü bietet eine wichtige Funktion für die Überprüfung von Warnungen und Störungsverlaufen.
- Die Einstellungen für die Lüftung sind in der Menüebene "Lüftung" verfügbar, aber nur wenn ein Energy Manager angeschlossen ist.
- Es wird empfohlen, das Servicemenü im System zu überprüfen, um Warnungen und Störungsverlaufe zu beheben.

### q14: Wärmepumpe Halle 1, Wie führe ich einen manuellen Entfrostungsvorgang durch?

**Pass:** ✅

Mir liegt dazu keine Information vor.

### q15: Wärmepumpe Halle 1, Was soll ich nach einem Stromausfall tun?

**Pass:** ❌

> Verbrühungsgefahr!

Nach einem Stromausfall oder Ausschalten der Wärmepumpe setzt die Bedieneinheit das Estrichtrocknungsprogramm automatisch fort, solange der Spannungsausfall nicht länger als etwa 15 Minuten andauert. Wenn der Strom wiederhergestellt wird, muss das Programm manuell neu gestartet werden.

Es ist wichtig zu beachten, dass die maximale Temperatur während des Estrichtrocknungsprogramms von der Variante der Inneneinheit abhängt. Es sollte daher vorgenommen werden, sicherzustellen, dass die Anlage vor Kondensat geschützt wird.

### q16: Wärmepumpe Halle 1, Wie schütze ich die Anlage vor dem Einfrieren?

**Pass:** ❌

> Verbrühungsgefahr!

Die Anlage muss vor Kondensat geschützt sein, um Wärmepumpe Halle 1 vor dem Einfrieren zu schützen. Es ist wichtig, sicherzustellen, dass die maximale Temperatureinstellung der Inneneinheit berücksichtigt wird und eine Mischeinrichtung installiert ist, wenn die Warmwassertemperatur über 60 °C erreicht wird.

Die maximale Temperaturinstellung hängt von der Variante der Inneneinheit ab. Es muss sichergestellt sein, dass die Anlage vor Kondensat geschützt ist, um Verstopfung und Schäden zu vermeiden.

### q17: Wärmepumpe Halle 1, Wo passe ich die Heizkurve an?

**Pass:** ❌

> **Servicemenü erscheint**  
> Warten Sie ca. 5 Sekunden, bis das Servicemenü erscheint.

### Schnellstartfunktion für die Wärmepumpe:
- **Schneller Kompressorstart auswählen**
- **Ja auswählen**

Die Schnellstartfunktion erhöht die Wärmeanforderung, sodass die Wärmepumpe schnellstmöglich startet.

---

### Servicemenü
1. **Servicemenü erscheint**  
   - Warten Sie ca. 5 Sekunden, bis das Servicemenü erscheint.
2. **Anlageneinstellungen auswählen und dann Manuelle Inbetriebnahme**  
   - Anlageninformationen anzeigen.
3. **Schneller Kompressorstart auswählen**  
   - Ja auswählen

Die Schnellstartfunktion erhöht die Wärmeanforderung, sodass die Wärmepumpe schnellstmöglich startet.

---

### Servicemenü
1. **Servicemenü erscheint**  
   - Warten Sie ca. 5 Sekunden, bis das Servicemenü erscheint.
2. **Anlageneinstellungen auswählen und dann Manuelle Inbetriebnahme**  
   - Anlageninformationen anzeigen.

---

### Schnellstartfunktion für die Wärmepumpe
1. **Schneller Kompressorstart auswählen**
2. **Ja auswählen**

Die Schnellstartfunktion erhöht die Wärmeanforderung, sodass die Wärmepumpe schnellstmöglich startet.

---

### Servicemenü
1. **Servicemenü erscheint**  
   - Warten Sie ca. 5 Sekunden, bis das Servicemenü erscheint.
2. **Anlageneinstellungen auswählen und dann Manuelle Inbetriebnahme**  
   - Anlageninformationen anzeigen.

---

### Schnellstartfunktion für die Wärmepumpe
1. **Schneller Kompressorstart auswählen**
2. **Ja auswählen**

Die Schnellstartfunktion erhöht die Wärmeanforderung, sodass die Wärmepumpe schnellstmöglich startet.

---

### Servicemenü
1. **Servicemenü erscheint**  
   - Warten Sie ca. 5 Sekunden, bis das Servicemenü erscheint.
2. **Anlageneinstellungen auswählen und dann Manuelle Inbetriebnahme**  
   - Anlageninformationen anzeigen.

---

### Schnellstartfunktion für die Wärmepumpe
1. **Schneller Kompressorstart auswählen**
2. **Ja auswählen**

Die Schnellstartfunktion erhöht die Wärmeanforderung, sodass die Wärmepumpe schnellstmöglich startet.

---

### Servicemenü
1. **Servicemenü erscheint**  
   - Warten Sie ca. 5 Sekunden, bis das Servicemenü erscheint.
2. **Anlageneinstellungen auswählen und dann Manuelle Inbetriebnahme**  
   - Anlageninformationen anzeigen.

---

### Schnellstartfunktion für die Wärmepumpe
1. **Schneller Kompressorstart auswählen**
2. **Ja auswählen**

Die Schnellstartfunktion erhöht die Wärmeanforderung, sodass die Wärmepumpe schnellstmöglich startet.

---

### Servicemenü
1. **Servicemenü erscheint**  
   - Warten Sie ca. 5 Sekunden, bis das Servicemenü erscheint.
2. **Anlageneinstellungen auswählen und dann Manuelle Inbetriebnahme**  
   - Anlageninformationen anzeigen.

---

### Schnellstartfunktion für die Wärmepumpe
1. **Schneller Kompressorstart auswählen**
2. **Ja auswählen**

Die Schnellstartfunktion erhöht die Wärmeanforderung, sodass die Wärmepumpe schnellstmöglich startet.

---

### Servicemenü
1. **Servicemenü erscheint**  
   - Warten Sie ca. 5 Sekunden, bis das Servicemenü erscheint.
2. **Anlageneinstellungen auswählen und dann Manuelle Inbetriebnahme**  
   - Anlageninformationen anzeigen.

---

### Schnellstartfunktion für die Wärmepumpe
1. **Schneller Kompressor

### q18: Wärmepumpe Halle 1, Was muss ich nach Abschluss der Inbetriebnahme im Servicemenü speichern?

**Pass:** ❌

Hier sind die relevante Informationen aus den gefundenen Menüpfaden zusammengefasst:

### Um im Sommer in den Kühlbetrieb zu wechseln:
**Menüpunkt:** Um im Sommer in den Kühlbetrieb zu wechseln, muss einer der Heizkreise für den Kühlbetrieb konfiguriert werden.

**Quelle:** Seite 10

---

Diese Konfiguration ermöglicht es, einen bestimmten Heizkreis (oder die Wärmepumpe) in den Kühlbetrieb zu überführen, wenn die externe Temperatur im Sommer niedriger ist als gewünscht. Dies kann dazu beitragen, Energie zu sparen und das Haus kühler zu halten.

### Verfügbar wenn ein Energy Manager angeschlossen und konfiguriert ist:
**Menüpunkt:** In diesem Menü sind die Einstellungen für den Energiemanager verfügbar.

**Quelle:** Seite 14

---

Dieses Menü ermöglicht es, Energiemanagertechnologien wie Photovoltaik-Energie zu integrieren und effizient zu steuern. Es wird nur in Anwesenheit eines Energy Manager angeschlossen und konfiguriert.

### Einziger verfügbarer Externer Eingang 1:
**Menüpunkt:** Nur für Externer Eingang 1 verfügbar.

**Quelle:** Seite 20

---

Dieser Pfad beschreibt die Verfügbarkeit einer speziellen Funktion nur für den Externer Eingang 1. Es gibt keinen weiteren Eintrag in der Dokumentation, der diesen Pfad explizit verknüpft oder ihn näher erklärt.

Diese Informationen können als Ergänzung zu den vorherigen Menüpfaden verwendet werden, um eine detailliertere Verwendung und Verfügbarkeit von Funktionen zu verstehen.

### q19: Wie verbinde ich die Wärmepumpe mit der Bosch-App?

**Pass:** ✅

Mir liegt dazu keine Information vor.

### q20: Wärmepumpe Halle 1, Wie integriere ich das Gerät in ein KNX-Bussystem?

**Pass:** ❌

> GEFAHR: Es ist wichtig sicherzustellen, dass der Heiz- und Kühlkreis korrekt konfiguriert sind.

Um das Gerät in ein KNX-Bussystem zu integrieren, müssen die spezifischen Einstellungen für den Heizkreis im Menü Heizung / Kühlung vorgenommen werden. In diesem Menü können Sie die Wärmepumpe mit dem KNX-Bus verbinden und konfigurieren.

Die Konfiguration der Komponenten der Anlage erfolgt in den entsprechenden Menüs, sodass alle spezifischen Einstellungen für die Wärmepumpe im Menü Heizung / Kühlung vorgenommen werden müssen. Es ist wichtig zu beachten, dass nur bestimmte Länder diese Funktion verfügbar machen.

Die maximale Temperatureinstellung hängt von der Variante der Inneneinheit ab und muss sichergestellt werden, um die Anlage vor Kondensat zu schützen.
