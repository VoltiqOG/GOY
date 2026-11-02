# 3D-Druck & Laser – Azubi-Handbuch

Interaktive Schulungsunterlage (Rev. 3.1) für Bambu Lab X1E, Bambu Lab H2C und xTool F1 Ultra: Bedienung, Slicer (Bambu Studio, xTool Creative Space) und Konstruktion für den 3D-Druck.

Statische Seite ohne Build-Schritt, veröffentlicht über GitHub Pages:

- `index.html` – Handbuch mit Kostenrechner (Button „Rechner“, Taste R) für 3D-Druck (3MF, G-Code, STEP) und Laser (SVG, DXF)
- `img/` – Bilder
- `occt/` – STEP-Import ([occt-import-js](https://github.com/kovacsv/occt-import-js), LGPL-2.1, Lizenz im Ordner); wird erst beim Laden einer STEP-Datei nachgeladen
- `prices.json` – Filamentpreise; `scripts/fetch_prices.py` aktualisiert sie täglich über `.github/workflows/preise.yml` aus dem Bambu Lab EU Store (bei Fehlern bleibt die Datei unverändert)
- `Kalkulation_3D-Druck_Laser.xlsx` – dieselbe Kalkulation als Excel-Tabelle

Technische Daten nach Herstellerangaben. Es gilt immer die Betriebsanleitung des Herstellers. Kalkulationswerte sind Beispiele und müssen mit dem Controlling abgestimmt werden.
