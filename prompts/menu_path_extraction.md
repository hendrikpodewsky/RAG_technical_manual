Du analysierst einen Textabschnitt aus einer Maschinen-Bedienungsanleitung.

Extrahiere alle Menüpfade aus dem Servicemenü. Ein Menüpfad ist eine geordnete
Liste von Ebenen-Bezeichnungen vom Hauptmenü bis zum Endpunkt (Blatt), z. B.:
["Service", "Anlageneinstellungen", "Wärmepumpe", "Geräuscharmer Betrieb"]

Regeln:
- Nur tatsächlich im Text enthaltene Pfade extrahieren, keine erfundenen.
- Die erste Ebene ist immer der Name des Hauptmenüs (z. B. "Service").
- Jeder Pfad führt bis zu einem Endpunkt (Einstellung, Parameter, Aktion).
- Zwischenebenen (Untermenüs) als eigene Pfade aufnehmen, wenn sie navigierbar sind.

Antworte ausschließlich mit JSON:
{"paths": [{"nodes": ["Ebene1", "Ebene2", ...]}, ...]}

- Keine Erklärung, nur JSON.

Text:
