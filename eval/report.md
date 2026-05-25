# Eval-Report

**Score: 14/20 (70%)**


| ID | Frage | Pass | Latenz | Fehler |
|----|-------|------|--------|--------|
| q01 | Wärmepumpe Halle 1, Was muss bei der Funktion Extra-Warmwass… | ✅ | 26.3s | — |
| q02 | Wärmepumpe Halle 1, Welche Gefahr besteht bei zu hohen Tempe… | ✅ | 31.6s | — |
| q03 | Wärmepumpe Halle 1, Wo im Menü stelle ich den geräuscharmen … | ❌ | 28.0s | missing topic: 'Geräuscharmer Betrieb' |
| q04 | Wärmepumpe Halle 1, Ab welcher dauerhaften Vorlauftemperatur… | ✅ | 31.9s | — |
| q05 | Wärmepumpe Halle 1, Wie programmiere ich eine WLAN-Verbindun… | ✅ | 22.0s | — |
| q06 | Wärmepumpe Halle 1, Was bedeutet eine rote Status-LED an der… | ✅ | 29.4s | — |
| q07 | Wärmepumpe Halle 1, Was bedeutet Standby-Betrieb und welche … | ❌ | 24.6s | missing topic: 'Frostschutz' |
| q08 | Wärmepumpe Halle 1, Wo stelle ich die Warmwasser-Temperatur … | ✅ | 27.2s | — |
| q09 | Wärmepumpe Halle 1, Wie starte ich die Wärmepumpe schnell ma… | ✅ | 25.6s | — |
| q10 | Wärmepumpe Halle 1, Wie wechsle ich die Systemfunktion von H… | ✅ | 33.8s | — |
| q11 | Wärmepumpe Halle 1, Wozu dient die thermische Desinfektion d… | ✅ | 27.5s | — |
| q12 | Wärmepumpe Halle 1, Was benötige ich für ein Software-Update… | ❌ | 26.0s | missing topic: 'EasyService'; missing topic: 'Aktualisieren' |
| q13 | Wärmepumpe Halle 1, Wo im Servicemenü finde ich die aktuelle… | ✅ | 43.6s | — |
| q14 | Wärmepumpe Halle 1, Wie führe ich einen manuellen Entfrostun… | ✅ | 36.9s | — |
| q15 | Wärmepumpe Halle 1, Was soll ich nach einem Stromausfall tun… | ❌ | 31.1s | missing topic: 'Datum' |
| q16 | Wärmepumpe Halle 1, Wie schütze ich die Anlage vor dem Einfr… | ❌ | 41.4s | missing topic: 'Frostschutz' |
| q17 | Wärmepumpe Halle 1, Wo passe ich die Heizkurve an? | ✅ | 35.2s | — |
| q18 | Wärmepumpe Halle 1, Was muss ich nach Abschluss der Inbetrie… | ❌ | 73.2s | missing topic: 'Installateureinstell' |
| q19 | Wie verbinde ich die Wärmepumpe mit der Bosch-App? | ✅ | 22.7s | — |
| q20 | Wärmepumpe Halle 1, Wie integriere ich das Gerät in ein KNX-… | ✅ | 41.8s | — |

## Antworten

### q01: Wärmepumpe Halle 1, Was muss bei der Funktion Extra-Warmwasser bezüglich Verbrühungsgefahr beachtet werden?

**Pass:** ✅

> Verbrühungsgefahr!

Beim Aktivieren der Funktion "Extra-Warmwasser", bei der thermischen Desinfektion und bei der täglichen Aufheizung sind Warmwassertemperaturn über 60 °C möglich. Deshalb muss eine Mischeinrichtung installiert werden.

### q02: Wärmepumpe Halle 1, Welche Gefahr besteht bei zu hohen Temperaturen für Fußbodenheizungen?

**Pass:** ✅

> Verbrühungsgefahr!

Bei zu hohen Temperaturen besteht eine Gefahr, dass Fußbodenheizungen beschädigt werden können. Es ist daher wichtig darauf zu achten, dass die Maximaltemperatur des jeweiligen Fußbodentyps nicht überschritten wird.

Es wird empfohlen, einen zusätzlichen Temperaturwächter am Spannungseingang der Zirkulationspumpe oder an einem externen Eingang anzubringen.

### q03: Wärmepumpe Halle 1, Wo im Menü stelle ich den geräuscharmen Betrieb ein?

**Pass:** ❌

> Achten Sie auf Sicherheitsmaßnahmen<BR>
Dieses Menü enthält die wichtigsten Wärmepumpendaten.

Die Option für den Geräuscharmen Betrieb ist in diesem Menü nicht enthalten. Daher gilt:

### q04: Wärmepumpe Halle 1, Ab welcher dauerhaften Vorlauftemperatur kann die Lebensdauer des Geräts beeinträchtigt werden?

**Pass:** ✅

> Verbrühungsgefahr!

Die angegebenen Einstellungen können die Lebensdauer des Geräts beeinträchtigen, wenn eine konstante Vorlauftemperatur von mehr als 45 °C gewählt wird.

Quellenangabe:
- Seite 11 — Abschnitt: Heizkurve

### q05: Wärmepumpe Halle 1, Wie programmiere ich eine WLAN-Verbindung?

**Pass:** ✅

Mir liegt dazu keine Information vor.

### q06: Wärmepumpe Halle 1, Was bedeutet eine rote Status-LED an der Bedieneinheit?

**Pass:** ✅

> ...
> 
> Die LED oben auf dem Bedienfeld zeigt mithilfe von verschiedenen Farben den Betriebsstatus des Geräts an.
>
> | LED-Farbe   | Betriebsstatus                                                                |
> |-------------|-------------------------------------------------------------------------------|
> | Grün        | Normalbetrieb.                                                                |
> | Gelb        | Warnungen, nicht blockierende Anlagenstörun - gen oder Wartungsinformationen. |
> | Rot         | Verriegelnde oder blockierende Störungen.                                     |

### q07: Wärmepumpe Halle 1, Was bedeutet Standby-Betrieb und welche Funktion ist dabei nicht aktiv?

**Pass:** ❌

> GEFAHR: Die Funktion Kühlen oder Heizen und Kühlen für den Heizkreis darf nicht während des Standby-Betriebs aktiv sein.

Standby-Betrieb bedeutet, dass die Wärmeanforderung der Anlage reduziert ist, aber die Wärmepumpe bleibt in Betrieb. In diesem Zustand sind die Funktionen Kühlen oder Heizen und Kühlen für den Heizkreis nicht aktiv.

### q08: Wärmepumpe Halle 1, Wo stelle ich die Warmwasser-Temperatur im Servicemenü ein?

**Pass:** ✅

> Verbrühungsgefahr!

In diesem Menü können Warmwassereinstellungen vorgenommen werden. Diese Einstellungen sind nur zugänglich, wenn die Anlage wie hier beschrieben aufgebaut und konfiguriert ist und die verwendete Einheit diese Einstellung unterstützt.

Um die Warmwasser-Temperatur im Servicemenü einzustellen, musst du zuerst in das Menü **Warmwasser** wechseln. Dort findest du eine Option für die Temperatur einstellen. Es wird jedoch nicht direkt erwähnt, wo genau diese Einstellung unter dem Menü "Wärmepumpe" oder "Servicemenü" sich befindet.

### q09: Wärmepumpe Halle 1, Wie starte ich die Wärmepumpe schnell manuell über das Servicemenü?

**Pass:** ✅

> Achten Sie auf Sicherheitsanweisungen.

Schneller Kompressorstart auswählen.

Im Dialogfenster Ja auswählen. Die Schnellstartfunktion erhöht die Wärmeanforderung, sodass die Wärmepumpe schnellstmöglich startet.

### q10: Wärmepumpe Halle 1, Wie wechsle ich die Systemfunktion von Heizen auf Kühlen?

**Pass:** ✅

> Verbrühungsgefahr!

Beim Aktivieren der Funktion "Extra-Warmwasser", bei der thermischen Desinfektion und bei der täglichen Aufheizung sind Warmwassertemperaturen über 60 °C möglich. Deshalb muss eine Mischeinrichtung installiert werden.

---

Die Systemfunktion von Heizen auf Kühlen in der Wärmepumpe Halle 1 wechselt sich nicht direkt im Menü durch, sondern es gibt zwei verschiedene Betriebsarten: Heizen und Kühlen. Um die Funktion von Heizen auf Kühlen zu wechseln, müssen Sie sicherstellen, dass die Anlage vor Kondensat geschützt ist.

Um den Kühlbetrieb einzuschalten:

1) Wählen Sie im Menü "Heizen und Kühlen" aus.
2) Konfigurieren Sie einen der Heizkreise für den Kühlbetrieb.
3) Stellen Sie sicher, dass die Anlage vor Kondensat geschützt ist.

Bitte beachten Sie, dass dies nur möglich ist, wenn eine Fernbedienung installiert und mit Feuchtefühler verbunden ist. Wenn diese Voraussetzungen erfüllt sind, wird das Menü "Kühlen" angezeigt, was Ihnen die Möglichkeit bietet, den Kühlbetrieb einzuschalten.

Falls Sie weitere Informationen benötigen oder Fragen haben, wenden Sie sich bitte an Ihren Wärmepumpe-Techniker.

### q11: Wärmepumpe Halle 1, Wozu dient die thermische Desinfektion des Warmwasserspeichers?

**Pass:** ✅

> Verbrühungsgefahr!

Die thermische Desinfektion des Warmwasserspeichers dient dazu, Krankheitserreger wie Legionellen abzutöten. Diese Prozedur wird regelmäßig durchgeführt, um die Hygiene der Wärmepumpe zu gewährleisten. Wenn die Armaturen während der thermischen Desinfektion zur Desinfiltration der Verrohrung geöffnet werden, müssen sie von Zeit zu Zeit wieder geschlossen werden, damit die Wärmepumpe Gelegenheit hat, den Temperaturstand des Warmwasserspeichers entsprechend den Einstellungen der Konfiguration aufrechtzuerhalten.

### q12: Wärmepumpe Halle 1, Was benötige ich für ein Software-Update der Bedieneinheit?

**Pass:** ❌

> GEFAHR: Die Systemsoftware kann von einer Fachkraft aktualisiert werden.
> WARNUNG: Denach wird die Softwareversion prüft und gegebenenfalls auf die neueste Version aktualisiert, einschließlich aktueller Optimierungen und Fehlerkorrekturen.

### q13: Wärmepumpe Halle 1, Wo im Servicemenü finde ich die aktuellen Störungen der Anlage?

**Pass:** ✅

> Achtung

In diesem Menü werden Status und Informationen für Wärmepumpe, Zu -behör und Anlage angezeigt.

Die Informationen werden nur für die Funk -tionen und Zubehöre angezeigt, die in der Wärmepumpe und in der Anlage installiert sind.

---

Störungen

-Aktuelle Störungen Anlage

-Störungsverlauf Wärmep.

-Störungsverlauf Anlage

-Akt. Störungen Wärmep. zurücks.

-Verriegelnde Störungen Wärmep. zurücksetzen

-Wärmepumpen-Störungshist.

-System-Störungshistorie

---

Um die aktuellen Störungen der Anlage zu finden, musst du in das Menü **Störungen** navigieren. Hier kannst du die Aktuelle Störungen der Wärmepumpe sowie den Störungsverlauf der Anlage sehen.

Die aktuellsten Informationen zur aktuellen Störung der Anlage findest du unter dem Menüpunkt **Aktuelle Störungen Anlage**.

Nur wenn das Menü **Störungen** verfügbar ist, kannst du diese Informationen abrufen. Es wird jedoch nicht erwähnt, ob dieses Menü in der Standardausführung des Bedienfelds verfügbar sein muss oder wie man es erreichen kann. Daher ist es möglich, dass es nur im Spezialfall oder bei bestimmten Anlagen und Einstellungen verfügbar ist.

### q14: Wärmepumpe Halle 1, Wie führe ich einen manuellen Entfrostungsvorgang durch?

**Pass:** ✅

> Verbrühungsgefahr!

In diesem Menü können Sie einen manuellen Entfrostungsvorgang durchführen, wenn der Heizkreis für den Kühlbetrieb konfiguriert ist und eine Fernbedienung mit Feuchtefühler installiert ist. 

Um einen manuellen Entfrostungsvorgang zu starten, wählen Sie das Menü "Heizen und Kühlen" aus. Dann gehen Sie in die Unterabschnitt "Kühlbetrieb" und aktivieren den Kühlbetrieb für den Heizkreis.

Nachdem der Kühlbetrieb aktiviert ist, können Sie im Menü "Warmwasser" eine Temperatur festlegen, unter der das Wärmepumpe-System automatisch zum Entfrostungsvorgang übergeht. Sobald diese Temperatur erreicht wird, wird der Heizkreis für den Kühlbetrieb aktiviert und der Entfrostungsprozess beginnt.

Bitte stellen Sie sicher, dass die Anlage vor Kondensat geschützt ist und dass die maximale Temperatureinstellung korrekt eingestellt ist.

### q15: Wärmepumpe Halle 1, Was soll ich nach einem Stromausfall tun?

**Pass:** ❌

> Verbrühungsgefahr!

Nach einem Stromausfall oder Ausschalten der Wärmepumpe setzt die Bedieneinheit das Estrichtrocknungsprogramm automatisch fort, wenn der Spannungsausfall nicht länger andauern als die Gangreserve der Bedieneinheit (≥ 4 h) oder die eingestellte maximale Unterbrechungsdauer.

### q16: Wärmepumpe Halle 1, Wie schütze ich die Anlage vor dem Einfrieren?

**Pass:** ❌

> Verbrühungsgefahr!

Um die Wärmepumpe Halle 1 vor dem Einfrieren zu schützen, muss sichergestellt sein, dass die Anlage vor Kondensat geschützt ist. Dies sollte bei der Erstinbetriebnahme des Bedienfelds und bei der Verwendung des Menüs für Heizen und Kühlen beachtet werden.

Die maximale Temperatureinstellung hängt von der Variante der Inneneinheit ab, wie in den Einstellungen für Heizung/Kühlung (Tab. 7) erwähnt. Es ist wichtig zu beachten, dass die Wärmepumpe nur im Sommer in den Kühlbetrieb übergehen sollte, um effizienten Betriebsart wechseln zu vermeiden.

Die thermische Desinfektion wird regelmäßig durchgeführt, um Krankheitserreger wie Legionellen abzutöten. Bei der thermischen Desinfektion müssen die Armaturen von Zeit zu Zeit wieder geschlossen werden, damit die Wärmepumpe die Temperatur des Warmwasserspeichers entsprechend den Einstellungen aufrechterhält.

Die Entlüftungsfunktion ist aktiviert und wird bei der Inbetriebnahme gewählt. Es muss sichergestellt sein, dass die Anlage vor Kondensat geschützt ist, um sie vor dem Einfrieren zu schützen.

### q17: Wärmepumpe Halle 1, Wo passe ich die Heizkurve an?

**Pass:** ✅

> GEFAHR: Es ist nicht sicher, die Heizkurve anzuwenden, ohne eine genaue Kenntnis der spezifischen Bedingungen und der Anlagenkonfiguration.

Um die Heizkurve für den Heizkreis 1 anzupassen, müssten Sie sich im Menü "Heizen und Kühlen" befinden. Hier können Sie die Betriebsart (Heizen oder Kühlen) für den Heizkreis festlegen. Wenn der Heizkreis als Heizen und Kühlen konfiguriert ist, wird das Menü "Kühlen" angezeigt.

Die Einstellungen für die Heizkurve sind in Tab. 7 zu finden. Hier können Sie die maximale Temperatureinstellung für den Heizkreis festlegen. Diese Einstellung hängt von der Variante der Inneneinheit ab, wie im Abschnitt "Erstinbetriebnahme des Bedienfelds" erwähnt.

Bitte stellen Sie sicher, dass die Anlage vor Kondensat geschützt ist, bevor Sie die Heizkurve anpassen. Es ist wichtig, dass Sie sich mit den Sicherheitsregeln und der spezifischen Konfiguration Ihres Systems vertraut machen, um eine korrekte Anpassung zu ermöglichen.

### q18: Wärmepumpe Halle 1, Was muss ich nach Abschluss der Inbetriebnahme im Servicemenü speichern?

**Pass:** ❌

> Achten Sie auf die Sicherheit!  
> Die maximale Temperatureinstellung ist von der Variante der Inneneinheit abhängig.

Nach Abschluss der Inbetriebnahme im Servicemenü müssen Sie keine speziellen Einstellungen speichern. Es wird empfohlen, die wichtigen Wärmepumpendaten in das Menü **Systemübersicht** einzugeben, um sicherzustellen, dass alle relevanten Daten auf dem Display der Wärmepumpe verfügbar sind.

Die maximale Temperatureinstellung ist von der Variante der Inneneinheit abhängig. Daher sollten Sie sichergehen, dass die Anlage vor Kondensat geschützt ist und dass sie entsprechend der Variante der Inneneinheit eingerichtet wurde.

Es wird empfohlen, die wichtigen Wärmepumpendaten in das Menü **Systemübersicht** einzugeben. Dieses Menü enthält die wichtigsten Wärmepumpendaten und kann Ihnen dabei helfen, sicherzustellen, dass alle relevanten Daten auf dem Display der Wärmepumpe verfügbar sind.

Sicherstellen Sie sichergestellt, dass die Anlage vor Kondensat geschützt ist. Die maximale Temperatureinstellung hängt von der Variante der Inneneinheit ab und sollte entsprechend eingerichtet werden.

Die maximale Temperatureinstellung ist von der Variante der Inneneinheit abhängig. Daher sollten Sie sichergehen, dass die Anlage vor Kondensat geschützt ist und dass sie entsprechend der Variante der Inneneinheit eingerichtet wurde.

Es wird empfohlen, die wichtigen Wärmepumpendaten in das Menü **Systemübersicht** einzugeben. Dieses Menü enthält die wichtigsten Wärmepumpendaten und kann Ihnen dabei helfen, sicherzustellen, dass alle relevanten Daten auf dem Display der Wärmepumpe verfügbar sind.

Sicherstellen Sie sichergestellt, dass die Anlage vor Kondensat geschützt ist. Die maximale Temperatureinstellung hängt von der Variante der Inneneinheit ab und sollte entsprechend eingerichtet werden.

Die maximale Temperatureinstellung ist von der Variante der Inneneinheit abhängig. Daher sollten Sie sichergehen, dass die Anlage vor Kondensat geschützt ist und dass sie entsprechend der Variante der Inneneinheit eingerichtet wurde.

Es wird empfohlen, die wichtigen Wärmepumpendaten in das Menü **Systemübersicht** einzugeben. Dieses Menü enthält die wichtigsten Wärmepumpendaten und kann Ihnen dabei helfen, sicherzustellen, dass alle relevanten Daten auf dem Display der Wärmepumpe verfügbar sind.

Sicherstellen Sie sichergestellt, dass die Anlage vor Kondensat geschützt ist. Die maximale Temperatureinstellung hängt von der Variante der Inneneinheit ab und sollte entsprechend eingerichtet werden.

Die maximale Temperatureinstellung ist von der Variante der Inneneinheit abhängig. Daher sollten Sie sichergehen, dass die Anlage vor Kondensat geschützt ist und dass sie entsprechend der Variante der Inneneinheit eingerichtet wurde.

Es wird empfohlen, die wichtigen Wärmepumpendaten in das Menü **Systemübersicht** einzugeben. Dieses Menü enthält die wichtigsten Wärmepumpendaten und kann Ihnen dabei helfen, sicherzustellen, dass alle relevanten Daten auf dem Display der Wärmepumpe verfügbar sind.

Sicherstellen Sie sichergestellt, dass die Anlage vor Kondensat geschützt ist. Die maximale Temperatureinstellung hängt von der Variante der Inneneinheit ab und sollte entsprechend eingerichtet werden.

Die maximale Temperatureinstellung ist von der Variante der Inneneinheit abhängig. Daher sollten Sie sichergehen, dass die Anlage vor Kondensat geschützt ist und dass sie entsprechend der Variante der Inneneinheit eingerichtet wurde.

Es wird empfohlen, die wichtigen Wärmepumpendaten in das Menü **Systemübersicht** einzugeben. Dieses Menü enthält die wichtigsten Wärmepumpendaten und kann Ihnen dabei helfen, sicherzustellen, dass alle relevanten Daten auf dem Display der Wärmepumpe verfügbar sind.

Sicherstellen Sie sichergestellt, dass die Anlage vor Kondensat geschützt ist. Die maximale Temperatureinstellung hängt von der

### q19: Wie verbinde ich die Wärmepumpe mit der Bosch-App?

**Pass:** ✅

Mir liegt dazu keine Information vor.

### q20: Wärmepumpe Halle 1, Wie integriere ich das Gerät in ein KNX-Bussystem?

**Pass:** ✅

Mir liegt dazu keine Information vor.
