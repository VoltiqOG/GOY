# 3D-Druck & Laser – Azubi-Handbuch

Interaktive Schulungsunterlage (Rev. 3.1) für Bambu Lab X1E, Bambu Lab H2C und xTool F1 Ultra: Bedienung, Slicer (Bambu Studio, xTool Creative Space) und Konstruktion für den 3D-Druck.

Statische Seite ohne Build-Schritt, veröffentlicht über GitHub Pages:

- `index.html` – Handbuch mit Kostenrechner (Button „Rechner“, Taste R) für 3D-Druck (3MF, G-Code, STEP) und Laser (SVG, DXF)
- `img/` – Bilder
- `occt/` – STEP-Import ([occt-import-js](https://github.com/kovacsv/occt-import-js), LGPL-2.1, Lizenz im Ordner); wird erst beim Laden einer STEP-Datei nachgeladen
- `prices.json` – Filamentpreise; `scripts/fetch_prices.py` aktualisiert sie täglich über `.github/workflows/preise.yml` aus dem Bambu Lab EU Store (bei Fehlern bleibt die Datei unverändert)
- `Kalkulation_3D-Druck_Laser.xlsx` – dieselbe Kalkulation als Excel-Tabelle

Technische Daten nach Herstellerangaben. Es gilt immer die Betriebsanleitung des Herstellers. Kalkulationswerte sind Beispiele und müssen mit dem Controlling abgestimmt werden.

## Zugang einrichten (Google-Anmeldung und Zugangsanfragen)

Die Anmeldeseite kann zusätzlich zum Passwort **„Mit Google anmelden“** anbieten. Beim ersten Anmelden geht automatisch eine Anfrage per E-Mail an den Verantwortlichen; nach „Freigeben“ öffnet sich die Seite für dieses Google-Konto bei jeder Anmeldung. Das Formular „Zugang anfragen“ (Passwort per E-Mail) läuft über dasselbe Skript. Beides steckt in `scripts/zugang-anfrage.gs` und läuft als Google Apps Script im eigenen Google-Konto (kostenlos, bis 100 Mails pro Tag).

**1. OAuth-Client-ID anlegen** (nur für die Google-Anmeldung, ca. 5 Minuten)

1. [console.cloud.google.com](https://console.cloud.google.com) → neues Projekt (z. B. „Handbuch-Anmeldung“).
2. **APIs & Dienste → OAuth-Zustimmungsbildschirm**: Typ *Extern*, App-Name „Handbuch 3D-Druck & Laser“, eigene E-Mail eintragen, Bereiche nichts hinzufügen, speichern. Veröffentlichungsstatus auf **„In Produktion“** setzen (sonst können sich nur eingetragene Testnutzer anmelden; für die Anmeldung mit Name und E-Mail ist keine Überprüfung durch Google nötig).
3. **APIs & Dienste → Anmeldedaten → Anmeldedaten erstellen → OAuth-Client-ID**, Typ **Webanwendung**, unter *Autorisierte JavaScript-Quellen* `https://voltiqog.github.io` eintragen. Die Client-ID (endet auf `.apps.googleusercontent.com`) kopieren.

**2. Apps Script einrichten**

1. [script.google.com](https://script.google.com) → **Neues Projekt**, Inhalt von `scripts/zugang-anfrage.gs` einfügen, speichern.
2. **Projekteinstellungen → Skripteigenschaften**: `PASSWORT` (Passwort der Seite), `SEITE` (`https://voltiqog.github.io/goy/`), `GOOGLE_CLIENT_ID` (aus Schritt 1). Optional `ADMIN` (andere E-Mail für Anfragen) und `DOMAIN` (nur Konten einer Domain zulassen, z. B. `firma.de`).
3. Funktion `testEinrichtung` ausführen → Berechtigungen erlauben → es kommt eine Test-Mail.
4. **Bereitstellen → Neue Bereitstellung → Web-App**: *Ausführen als* **Ich**, *Zugriff* **Jeder**. Die Web-App-URL (endet auf `/exec`) kopieren.

**3. In der Anmeldeseite eintragen** (`index.html`, oben im Skript; das Handbuch selbst muss dafür nicht neu verschlüsselt werden)

- `const REQ = "…/exec";` – schaltet das Formular „Zugang anfragen“ ein.
- `const GCID = "….apps.googleusercontent.com", AUTH = "…/exec";` – schaltet „Mit Google anmelden“ ein.

**Verwalten:** Jede Anfrage-Mail enthält den Link „Zugänge verwalten“ (nicht weitergeben): Liste der freigegebenen Konten mit „Entziehen“, abgelehnte Konten mit „Doch freigeben“. Ein entzogenes Konto kommt nicht mehr hinein; Geräte, auf denen es mit „angemeldet bleiben“ schon offen ist, sperrt erst ein neues Passwort der Seite. Wird das Passwort geändert, auch `PASSWORT` in den Skripteigenschaften ändern.
