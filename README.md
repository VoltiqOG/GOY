# 3D-Druck & Laser – Azubi-Handbuch

Interaktive Schulungsunterlage (Rev. 3.1) für Bambu Lab X1E, Bambu Lab H2C und xTool F1 Ultra: Bedienung, Slicer (Bambu Studio, xTool Creative Space) und Konstruktion für den 3D-Druck.

Statische Seite ohne Build-Schritt, veröffentlicht über GitHub Pages:

- `index.html` – Handbuch mit Kostenrechner (Button „Rechner“, Taste R) für 3D-Druck (3MF, G-Code, STEP) und Laser (SVG, DXF)
- `img/` – Bilder
- `occt/` – STEP-Import ([occt-import-js](https://github.com/kovacsv/occt-import-js), LGPL-2.1, Lizenz im Ordner); wird erst beim Laden einer STEP-Datei nachgeladen
- `prices.json` – Filamentpreise; `scripts/fetch_prices.py` aktualisiert sie täglich über `.github/workflows/preise.yml` aus dem Bambu Lab EU Store (bei Fehlern bleibt die Datei unverändert)
- `Kalkulation_3D-Druck_Laser.xlsx` – dieselbe Kalkulation als Excel-Tabelle

Technische Daten nach Herstellerangaben. Es gilt immer die Betriebsanleitung des Herstellers. Kalkulationswerte sind Beispiele und müssen mit dem Controlling abgestimmt werden.

## Zugangsanfragen einrichten

Die Anmeldeseite hat ein Formular „Kein Passwort? Zugang anfragen“. Die Anfrage geht per E-Mail an den Verantwortlichen; erst nach seiner Freigabe bekommt die Person das Passwort per E-Mail. Dafür läuft `scripts/zugang-anfrage.gs` als Google Apps Script im eigenen Google-Konto (kostenlos, bis 100 Mails pro Tag).

1. [script.google.com](https://script.google.com) → **Neues Projekt**, Namen vergeben, den Inhalt von `scripts/zugang-anfrage.gs` einfügen, speichern.
2. **Projekteinstellungen** (Zahnrad) → **Skripteigenschaften** hinzufügen: `PASSWORT` (das Passwort der Seite), `SEITE` (`https://voltiqog.github.io/goy/`), optional `ADMIN` (andere E-Mail für Anfragen).
3. Im Editor die Funktion `testEinrichtung` auswählen → **Ausführen** → Berechtigungen erlauben. Es kommt eine Test-Mail.
4. **Bereitstellen → Neue Bereitstellung** → Typ **Web-App**: *Ausführen als* **Ich**, *Zugriff* **Jeder**. Die Web-App-URL (endet auf `/exec`) kopieren.
5. In `index.html` die URL eintragen: `const REQ = "https://script.google.com/macros/s/…/exec";`

Das Passwort steht nur in den Skripteigenschaften, nicht im Repo. Wird das Passwort der Seite geändert, auch `PASSWORT` dort ändern.
