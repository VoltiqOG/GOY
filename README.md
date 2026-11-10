# 3D-Druck & Laser – Azubi-Handbuch

Interaktive Schulungsunterlage (Rev. 3.1) für Bambu Lab X1E, Bambu Lab H2C und xTool F1 Ultra: Bedienung, Slicer (Bambu Studio, xTool Creative Space) und Konstruktion für den 3D-Druck.

Statische Seite ohne Build-Schritt, veröffentlicht über GitHub Pages:

- `index.html` – Handbuch mit Kostenrechner (Button „Rechner“, Taste R) für 3D-Druck (3MF, G-Code, STEP) und Laser (SVG, DXF)
- `img/` – Bilder
- `occt/` – STEP-Import ([occt-import-js](https://github.com/kovacsv/occt-import-js), LGPL-2.1, Lizenz im Ordner); wird erst beim Laden einer STEP-Datei nachgeladen
- `prices.json` – Filamentpreise; `scripts/fetch_prices.py` aktualisiert sie täglich über `.github/workflows/preise.yml` aus dem Bambu Lab EU Store (bei Fehlern bleibt die Datei unverändert)
- `Kalkulation_3D-Druck_Laser.xlsx` – dieselbe Kalkulation als Excel-Tabelle

Technische Daten nach Herstellerangaben. Es gilt immer die Betriebsanleitung des Herstellers. Kalkulationswerte sind Beispiele und müssen mit dem Controlling abgestimmt werden.

## Anmeldung mit Benutzerkonten

Jede Person hat ein eigenes Konto (Benutzername + Passwort). Es gibt keinen Server: Die Seite ist verschlüsselt, und für jedes Konto steckt der Seitenschlüssel einzeln eingepackt in der `index.html`. Passwörter stehen nirgends, auch nicht als Hash.

**Neues Konto (die Person selbst)**

1. Auf der Anmeldeseite **„Konto anlegen“**: Name, Benutzername und Passwort (mindestens 10 Zeichen) eingeben.
2. Den angezeigten **Konto-Code** (beginnt mit `SU3DL1.`) an den Verantwortlichen schicken. Der Code enthält das Passwort nicht.

**Freigeben (Verantwortlicher)**

```
pip install cryptography          # einmalig
python scripts/benutzer.py freigeben SU3DL1.xxxxx
git commit -am "Konto freigegeben" && git push
```

Das Skript fragt nach dem eigenen Benutzernamen und Passwort (oder `SEITEN_BENUTZER` / `SEITEN_PASSWORT`).

| Befehl | Wirkung |
|---|---|
| `python scripts/benutzer.py liste` | alle Konten (Benutzername, Name) |
| `… freigeben CODE` | Konto-Code freischalten |
| `… freigeben CODE --ersetzen` | neues Passwort für ein vorhandenes Konto (vorher bei der Person nachfragen, ob der Code von ihr kommt) |
| `… anlegen m.mustermann "Max Mustermann"` | Konto mit zufälligem Startpasswort anlegen |
| `… entfernen m.mustermann` | Konto löschen **und** Seitenschlüssel wechseln |
| `… schluessel` | nur den Seitenschlüssel wechseln |

**Passwort ändern / vergessen:** „Passwort vergessen?“ auf der Anmeldeseite oder „Passwort ändern“ im Konto-Menü erzeugt einen neuen Konto-Code für denselben Benutzernamen → `freigeben … --ersetzen`.

**Grenzen (ehrlich):** Die Datei ist öffentlich abrufbar; der Schutz hängt an der Passwortlänge (PBKDF2 mit 600 000 Runden bremst das Durchprobieren, verhindert es bei schwachen Passwörtern aber nicht). Nach „entfernen“ kommt das Konto an keine neuen Stände mehr – eine Kopie, die jemand vorher gespeichert hat, bleibt lesbar. Alle anderen melden sich nach einem Schlüsselwechsel einmal neu an. Wer am Repository Schreibrechte hat, verwaltet die Konten.

Inhalt ändern: `python scripts/aktualisieren.py index.html scripts/patch_x.py` (Anmeldung mit dem eigenen Konto).

## Zusätzlich: Mit Google anmelden

Eingebaut, aber aus, bis zwei Werte eingetragen sind. Google-Konten sind ganz normale Konten (`g-…`): beim ersten Anmelden bekommt der Verantwortliche eine E-Mail mit dem fertigen `freigeben`-Befehl; Entfernen wie bei jedem Konto.

1. **OAuth-Client-ID** ([console.cloud.google.com](https://console.cloud.google.com)): neues Projekt → *APIs & Dienste → OAuth-Zustimmungsbildschirm* (Extern, App-Name, eigene E-Mail, Status „In Produktion“) → *Anmeldedaten → OAuth-Client-ID*, Typ **Webanwendung**, autorisierte JavaScript-Quelle `https://voltiqog.github.io`. Client-ID kopieren.
2. **Apps Script** ([script.google.com](https://script.google.com)): neues Projekt, Inhalt von `scripts/google-anmeldung.gs` einfügen. *Projekteinstellungen → Skripteigenschaften*: `GOOGLE_CLIENT_ID` (aus Schritt 1), optional `ADMIN`, `DOMAIN`. Funktion `testEinrichtung` einmal ausführen (Berechtigungen erlauben, Test-Mail kommt). *Bereitstellen → Web-App*: Ausführen als **Ich**, Zugriff **Jeder**. URL (endet auf `/exec`) kopieren.
3. **Einschalten:** `python scripts/gate_google.py index.html CLIENT_ID WEBAPP_URL`, committen, pushen. Ausschalten: `… index.html aus`.

Die Skripteigenschaft `MASTER` entsteht automatisch und darf nicht geändert werden – sonst müssen alle Google-Konten neu freigegeben werden. Wer das Apps Script verwaltet, könnte sich als jedes freigegebene Google-Konto anmelden; es gehört deshalb in das Google-Konto des Verantwortlichen.
