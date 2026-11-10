# 3D-Druck & Laser – Handbuch mit Rechner und Werkzeugen

Schulungsunterlage für Bambu Lab X1E, Bambu Lab H2C und xTool F1 Ultra: Bedienung, Slicer, Konstruktion, dazu Kostenrechner und Werkzeuge (QR-Platte, Typenschild, Bild → SVG, Visitenkarte, Präger).

Statische Seite auf GitHub Pages, ohne Server. Der Inhalt liegt verschlüsselt in der `index.html`; geöffnet wird er mit einem Benutzerkonto.

## Aufbau

| Pfad | Inhalt |
|---|---|
| `index.html` | Anmeldeseite, Kontenliste und der verschlüsselte Inhalt |
| `scripts/anmeldeseite.html` | Vorlage der Anmeldeseite (HTML, CSS, JavaScript) |
| `scripts/seite.py` | Inhalt auspacken, bearbeiten, wieder einpacken |
| `scripts/konten.py` | Konten verwalten |
| `scripts/google-anmeldung.gs` | Apps Script für „Mit Google anmelden“ (optional) |
| `scripts/fetch_prices.py`, `prices.json` | Filamentpreise, täglich über `.github/workflows/preise.yml` |
| `img/`, `dateien/`, `occt/` | Bilder, Vorlagen, STEP-Import ([occt-import-js](https://github.com/kovacsv/occt-import-js), LGPL-2.1) |

Einmalig: `pip install cryptography`. Die Skripte fragen nach dem eigenen Benutzernamen und Passwort (oder lesen `SEITEN_BENUTZER` / `SEITEN_PASSWORT`).

## Inhalt ändern

```
python scripts/seite.py auspacken quelle.html
# quelle.html bearbeiten
python scripts/seite.py einpacken quelle.html
git commit -am "…" && git push
```

`quelle.html` ist der unverschlüsselte Inhalt und steht in `.gitignore` – nicht committen.
Die Anmeldeseite selbst ändert man in `scripts/anmeldeseite.html`, danach `python scripts/seite.py anmeldeseite`.

## Konten

Jede Person hat ein eigenes Konto. Passwörter stehen nirgends, auch nicht als Hash.

**Neues Konto:** Auf der Anmeldeseite „Konto anlegen“. Die Anfrage erscheint beim Verwalter in der Seite; zusätzlich zeigt die Anmeldeseite einen Konto-Code (`SU3DL1.…`), den man ihm schicken kann. Der Code enthält das Passwort nicht.

**Verwalten in der Seite** (Konto-Menü → „Konten verwalten“, nur Verwalter): Anfragen freigeben, Rechte per Haken, Konten entfernen. Gespeichert wird als Commit; dafür braucht der Browser des Verwalters einmalig ein *Fine-grained Token* für dieses Repository mit „Contents: Read and write“.

**Verwalten per Skript:**

| Befehl | Wirkung |
|---|---|
| `python scripts/konten.py liste` | alle Konten mit Rechten |
| `… freigeben CODE` | Konto-Code freischalten (`--ersetzen`: neues Passwort für ein vorhandenes Konto) |
| `… anlegen m.mustermann "Max Mustermann"` | Konto mit Startpasswort |
| `… rechte m.mustermann doku,qr` | Rechte setzen: `*` oder `doku rechner material pruefen qr sch vec vk pr`, dazu `admin` |
| `… entfernen m.mustermann` | Konto löschen und Seitenschlüssel wechseln |

**Passwort ändern oder vergessen:** neuen Konto-Code für denselben Benutzernamen erzeugen („Passwort vergessen?“ bzw. Konto-Menü → „Passwort ändern“) und freigeben lassen.

### So ist es geschützt

- Der Inhalt ist mit einem zufälligen Seitenschlüssel verschlüsselt (AES-256-GCM).
- Jedes Konto hat ein Schlüsselpaar (ECDH P-256). Der private Schlüssel ist mit dem Passwort verschlüsselt (PBKDF2-SHA256, 600 000 Runden); der Seitenschlüssel ist für jeden öffentlichen Schlüssel einzeln eingepackt.
- „Entfernen“ wechselt den Seitenschlüssel: Das entfernte Konto kommt an keine neuen Stände mehr, alle anderen melden sich einmal neu an.

Grenzen: Die Datei ist öffentlich abrufbar, der Schutz hängt an der Passwortlänge. Rechte blenden Bereiche aus, sind aber kein Kopierschutz – nach der Anmeldung liegt die ganze Seite im Browser. Eine Kopie, die jemand vor dem Entfernen gespeichert hat, bleibt lesbar.

### Benachrichtigung über Anfragen

Anfragen gehen verschlüsselt über einen öffentlichen Kanal (ntfy.sh) und erscheinen als roter Punkt am Konto-Symbol. Der Kanal behält Nachrichten 12 Stunden; die Anmeldeseite sendet offene Anfragen beim nächsten Besuch erneut. Der Konto-Code von Hand funktioniert immer.

## Mit Google anmelden (optional)

Eingebaut, aber aus, bis zwei Werte eingetragen sind. Google-Konten sind normale Konten (`g-…`) und werden genauso freigegeben und entfernt.

1. **OAuth-Client-ID** ([console.cloud.google.com](https://console.cloud.google.com)): Projekt anlegen → OAuth-Zustimmungsbildschirm (Extern, „In Produktion“) → Anmeldedaten → OAuth-Client-ID, Typ *Webanwendung*, JavaScript-Quelle `https://voltiqog.github.io`.
2. **Apps Script** ([script.google.com](https://script.google.com)): `scripts/google-anmeldung.gs` einfügen, Skripteigenschaft `GOOGLE_CLIENT_ID` setzen, `testEinrichtung` einmal ausführen, als Web-App bereitstellen (Ausführen als *Ich*, Zugriff *Jeder*).
3. `python scripts/seite.py google CLIENT_ID WEB-APP-URL` – ausschalten mit `… google aus`.

Die Skripteigenschaft `MASTER` entsteht automatisch und darf nicht geändert werden. Das Apps Script gehört in das Google-Konto des Verwalters.

---

Technische Daten nach Herstellerangaben; es gilt die Betriebsanleitung des Herstellers. Kalkulationswerte sind Beispiele.
