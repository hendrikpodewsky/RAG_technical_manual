Du analysierst eine Seite aus einer Maschinen-Bedienungsanleitung als Bild.

Deine Aufgabe: Extrahiere alle Menünavigationspfade, die auf dieser Seite sichtbar sind.

Ein Menüpfad ist eine hierarchische Navigationskette wie:
→ "Hauptmenü > Einstellungen > Warmwasser > Solltemperatur"
→ "Service > Anlageneinstellungen > Wärmepumpe > Geräuscharmer Betrieb"

Erkennungsmerkmale für Menüpfade auf der Seite:
- Pfeilsymbole (>, →, ▶) zwischen Menübezeichnungen
- Navigationspfade in Schritt-für-Schritt-Anleitungen ("Tippen Sie auf ... > ... > ...")
- Menüstruktur-Diagramme oder Baumdarstellungen
- Schrittweise beschriebene Menünavigation im Fließtext

Antworte ausschließlich mit JSON:
{"paths": [{"nodes": ["Ebene1", "Ebene2", "Ebene3", ...]}, ...]}

Regeln:
- Nur tatsächlich auf der Seite sichtbare Pfade — keine Erfindungen.
- Jeder Pfad als geordnete Liste der Menüebenen von oben nach unten.
- Wenn keine Menüpfade erkennbar sind: {"paths": []}
- Keine Erklärung, nur JSON.
