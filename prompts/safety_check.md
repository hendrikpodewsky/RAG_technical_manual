Du analysierst einen Textblock aus einer Maschinen-Bedienungsanleitung.

Entscheide: Enthält dieser Block einen Sicherheitshinweis, der Personenschäden
(Verbrühung, Stromschlag, Frost, Überdruck, Brand, Vergiftung, Verletzung, Tod)
beschreibt oder davor warnt — auch wenn kein explizites Schlüsselwort
(GEFAHR/WARNUNG/VORSICHT/ACHTUNG/HINWEIS) vorkommt?

Antworte ausschließlich mit JSON:
{"is_safety": true/false, "level": "GEFAHR"|"WARNUNG"|"VORSICHT"|"ACHTUNG"|"HINWEIS"|null}

- "is_safety": true nur bei konkretem Personenschadens-Potenzial
- "level": dein bestes Urteil über die Schwere, oder null wenn is_safety=false
- Keine Erklärung, nur JSON.

Text:
