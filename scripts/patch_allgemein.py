"""Handbuch allgemein machen: keine Zuständigkeiten, keine Firmen-Zuschnitte.

Aufruf: python patch_allgemein.py <unverschluesselte index.html>
- „Wer ist zuständig?“ und 13.5 „Rollen und Verantwortlichkeiten“ entfernt (13.6 → 13.5)
- „der Verantwortliche“ → fachkundige Person / Vorgesetzte bzw. neutral formuliert
- „unsere/bei uns/Firmen-Profile“ → neutral; Branchenbeispiele (Ballenpresse, Recyclinghalle) → allgemein
Die Normhinweise (z. B. EN 16252 als Beispiel) und der Typenschild-Generator bleiben.
"""
import re
import sys

path = sys.argv[1]
s = open(path, encoding="utf-8").read()


def rep(a, b, n=1):
    global s
    c = s.count(a)
    if (n == "all" and c < 1) or (n != "all" and c != n):
        raise SystemExit(f"Stelle {c}× statt {n}× gefunden: " + a[:100])
    s = s.replace(a, b)


def cut(start, end):
    global s
    i = s.find(start); j = s.find(end, i)
    if i < 0 or j < 0:
        raise SystemExit("Abschnitt nicht gefunden: " + start[:60])
    s = s[:i] + s[j:]


# ---------- ganze Abschnitte raus
cut('<h2 id="wer-ist-zustaendig">Wer ist zuständig?</h2>', '<h2 id="die-kaesten-in-dieser-anleitung">')
rep('<li><a href="#wer-ist-zustaendig">Wer ist zuständig?</a></li>', '')
rep('<li>Wer bei Fragen zuständig ist</li>', '')
cut('<h2 id="13-5-rollen-und-verantwortlichkeiten">', '<h2 id="13-6-druck-und-laserauftrag-formular">')
rep('<li><a href="#13-5-rollen-und-verantwortlichkeiten">13.5 Rollen und Verantwortlichkeiten</a></li>', '')
rep('<h2 id="13-6-druck-und-laserauftrag-formular"><span class="hn">13.6</span>', '<h2 id="13-6-druck-und-laserauftrag-formular"><span class="hn">13.5</span>')
rep('<li><a href="#13-6-druck-und-laserauftrag-formular">13.6 Druck- und Laserauftrag (Formular)</a></li>', '<li><a href="#13-6-druck-und-laserauftrag-formular">13.5 Druck- und Laserauftrag (Formular)</a></li>')
rep('<span class="cct">Ablauf eines Auftrags</span><span class="cca"><span class="ccb">Organisation</span><span class="ccs">6 Abschnitte', '<span class="cct">Ablauf eines Auftrags</span><span class="cca"><span class="ccb">Organisation</span><span class="ccs">5 Abschnitte')
rep('<h1 id="kapitel-13-t">Ablauf eines Auftrags</h1><div class="chs">6 Abschnitte', '<h1 id="kapitel-13-t">Ablauf eines Auftrags</h1><div class="chs">5 Abschnitte')
# Querverweise auf das alte 13.6 / 13.5 im Fließtext
s = re.sub(r'(<a class="xr" href="#13-6-druck-und-laserauftrag-formular">)(?:Kapitel )?13\.6(</a>)', lambda m: m.group(1) + ("Kapitel " if "Kapitel" in m.group(0) else "") + "13.5" + m.group(2), s)
s = re.sub(r'<a class="xr" href="#13-5-rollen-und-verantwortlichkeiten">[^<]*</a>', 'Kapitel 13', s)
rep('<tr><td data-label="Dokumentinformation"><span class="tc">Verteiler</span></td><td data-label=""><span class="tc">Ausbildung, Konstruktion, Arbeitssicherheit, Werkstatt 3D-Druck/Laser</span></td></tr>', '')

# ---------- „der Verantwortliche“ neutral
R = [
    ("Hier entscheidest du nicht allein. Erst den Verantwortlichen fragen.", "Hier entscheidest du nicht allein. Erst eine fachkundige Person fragen (Ausbilder/in oder Vorgesetzte)."),
    ("abziehen und an den Verantwortlichen zurückgeben.", "abziehen und sicher verwahren."),
    ("Verantwortlichen bzw. Vorgesetzten informieren – auch bei kleinen Vorfällen.", "Vorgesetzte informieren – auch bei kleinen Vorfällen."),
    ("Störungsmeldung ausfüllen, Verantwortlichen informieren.", "Störungsmeldung ausfüllen, Vorgesetzte informieren."),
    ("Arbeiten am Hotend und Firmware-Updates nur durch den Verantwortlichen.", "Arbeiten am Hotend und Firmware-Updates nur durch fachkundige Personen."),
    ("Unterschrift Verantwortlicher ________________________", "Unterschrift ________________________"),
    ("Bedienung nur durch unterwiesene und vom Verantwortlichen freigegebene Personen.", "Bedienung nur durch unterwiesene und dafür freigegebene Personen."),
    ("Job abbrechen, Ursache prüfen, Verantwortlichen informieren.", "Job abbrechen, Ursache prüfen, Vorgesetzte informieren."),
    ("Kalibrierung und Firmware-Updates nur durch den Verantwortlichen.", "Kalibrierung und Firmware-Updates nur durch fachkundige Personen."),
    ("Vor einer Anschaffung aktuelle Daten prüfen und mit dem Verantwortlichen klären, welche Materialien", "Vor einer Anschaffung aktuelle Daten prüfen und klären, welche Materialien"),
    ("Welche Platten wir haben: ______________________________________ (vom Verantwortlichen eintragen)", "Vorhandene Platten: ______________________________________ (hier eintragen)"),
    ("tauschen – der Drucker meldet das. Firmware-Updates nur durch den Verantwortlichen.", "tauschen – der Drucker meldet das. Firmware-Updates nur durch fachkundige Personen."),
    ("Welcher bei uns gilt, legen der Verantwortliche und die IT fest.", "Welcher Weg passt, hängt vom Netzwerk ab – mit der IT abstimmen."),
    ("Nur für den Verantwortlichen", "Nur für fachkundige Personen"),
    ("Bei Unsicherheit Verantwortlichen holen.", "Bei Unsicherheit eine fachkundige Person holen."),
    ("Tür geschlossen lassen, Verantwortlichen alarmieren.", "Tür geschlossen lassen, Vorgesetzte alarmieren."),
    ("Bei Verstopfung, die so nicht weggeht: Verantwortlichen holen.", "Bei Verstopfung, die so nicht weggeht: fachkundige Person holen."),
    (") und Verantwortlichen informieren.", ") und Vorgesetzte informieren."),
    ("</strong> – Verantwortlichen holen", "</strong> – fachkundige Person holen"),
    ("wiederholt sich der Fehler: Verantwortlichen holen", "wiederholt sich der Fehler: fachkundige Person holen"),
    ("Stecke Hotends nur in die Plätze, die der Verantwortliche vorgibt, und trage Änderungen am Drucker ein.", "Stecke Hotends nur in die festgelegten Plätze und trage Änderungen am Drucker ein."),
    ("Bei Verstopfung: Verantwortlichen holen.", "Bei Verstopfung: fachkundige Person holen."),
    ("sondern an den Verantwortlichen weitergeben und im Wartungsprotokoll eintragen.", "sondern weitergeben und im Wartungsprotokoll eintragen."),
    ("Neue Sorten richtet der Verantwortliche ein – du solltest den Ablauf kennen:", "Neue Sorten richtet am besten eine erfahrene Person ein – du solltest den Ablauf kennen:"),
    ("Firmen-Profile (bitte mit dem Verantwortlichen festlegen)", "Eigene Standard-Profile festlegen"),
    ("Der Verantwortliche legt die verbindlichen Profile fest und speichert sie in Bambu Studio (Benutzerprofile synchronisieren sich über das Firmenkonto).", "Die verbindlichen Profile einmal festlegen und in Bambu Studio als Benutzerprofile speichern (sie synchronisieren sich über das gemeinsame Bambu-Konto)."),
    ("Düsen beim X1E wechselt nur der Verantwortliche.", "Düsen beim X1E nur nach Einweisung wechseln."),
    ("Welche Kompensation in den Firmenprofilen steht, legt der Verantwortliche fest (", "Welche Kompensation in den Standard-Profilen steht, wird einmal festgelegt ("),
    ("in den Geräteeinstellungen ausführen bzw. den Verantwortlichen holen.", "in den Geräteeinstellungen ausführen bzw. eine fachkundige Person holen."),
    ("Firmware/XCS-Updates (nur Verantwortlicher)", "Firmware/XCS-Updates (nur fachkundige Personen)"),
    ("nach Arbeitsende abziehen und beim Verantwortlichen abgeben", "nach Arbeitsende abziehen und sicher verwahren"),
    ("zu langsam), Verantwortlichen informieren", "zu langsam), Vorgesetzte informieren"),
    ("gleiches Netzwerk? Sonst IT/Verantwortlicher", "gleiches Netzwerk? Sonst IT fragen"),
    ("Nach jedem Transport: Kalibrierung durch den Verantwortlichen.", "Nach jedem Transport: Kalibrierung durch eine fachkundige Person."),
    ("Filament trocknen, Verantwortlichen wegen Düse fragen", "Filament trocknen, wegen der Düse eine fachkundige Person fragen"),
    ("Bei PLA Tür/Deckel öffnen; Verantwortlichen holen", "Bei PLA Tür/Deckel öffnen; fachkundige Person holen"),
    ("Laser mit offener Haube: Verantwortlichen draufschauen lassen", "Laser mit offener Haube: eine erfahrene Person draufschauen lassen"),
    ("OK vom Verantwortlichen", "OK einer erfahrenen Person"),
    ("Termin-Konflikte klärt der Verantwortliche.", "Termin-Konflikte früh ansprechen."),
    ("(genauen Pfad vom Verantwortlichen)", "(Pfad einmal festlegen)"),
    ("werden nur mit Freigabe des Verantwortlichen nachgebaut.", "werden nur mit Freigabe durch die Konstruktion nachgebaut."),
    ("Skripte ändert nur der Verantwortliche.", "Skripte nur abgestimmt ändern."),
    ("nur mit Freigabe der IT und des Verantwortlichen.", "nur mit Freigabe der IT."),
    ("Firmenprofile/Vorlagen vom Verantwortlichen freigegeben?", "Standard-Profile/Vorlagen festgelegt und geprüft?"),
    ("(beim Verantwortlichen / der Fachkraft für Arbeitssicherheit)", "(bei der Fachkraft für Arbeitssicherheit)"),
]
miss = []
def soft(a, b):
    global s
    if a in s: s = s.replace(a, b)
    else: miss.append(a)
for a, b in R:
    soft(a, b)
# Tabellenzellen „Wer?“ = Verantwortlicher
s = s.replace('<span class="tc">Verantwortlicher</span>', '<span class="tc">fachkundige Person</span>')

# ---------- Firma / bei uns / unsere
R2 = [
    ("Firmen-Profile anlegen (siehe 7.13)", "Standard-Profile anlegen (siehe 7.13)"),
    ("Firmen-Profil wählen", "Standard-Profil wählen"),
    ("Eigene Teile mit Firmen-Profilen slicen", "Eigene Teile mit den Standard-Profilen slicen"),
    ("Mit dem Firmenprofil drucken", "Mit dem Standard-Profil drucken"),
    ("Vorlagen und Firmenprofile, damit nicht jeder bei null anfängt", "Vorlagen und Standard-Profile, damit nicht jeder bei null anfängt"),
    ("Platte, Firmenprofil und Filamenten", "Platte, Standard-Profil und Filamenten"),
    ("mit dem Firmenprofil slicen lassen", "mit dem Standard-Profil slicen lassen"),
    ("★ EMPFEHLUNG</strong> ist unser Standard", "★ EMPFEHLUNG</strong> ist der empfohlene Standard"),
    ("wie du unsere drei Maschinen bedienst", "wie du die drei Maschinen bedienst"),
    ("vergleiche kurz mit den anderen Wegen, die es in unserer Firma gibt:", "vergleiche kurz mit den anderen Fertigungswegen:"),
    ("Unsere Drucker arbeiten mit dem FDM-Verfahren", "Die Drucker X1E und H2C arbeiten mit dem FDM-Verfahren"),
    ("Unsere Maschinen im Überblick", "Die Maschinen im Überblick"),
    (">Unsere Maschinen<", ">Die Maschinen<"),
    ("Neben unseren beiden Druckern", "Neben X1E und H2C"),
    ("X1E (bei uns)", "X1E"), ("H2C (bei uns)", "H2C"),
    ("Azubi-Übungen", "Übungsteile"),
    ("Ist bei uns eins montiert,", "Ist eins montiert,"),
    ("Trage unseren tatsächlichen Bestand ein", "Trage den tatsächlichen Bestand ein"),
    ("Die Tabelle zeigt die Materialien, die bei uns vorkommen.", "Die Tabelle zeigt die gängigen Materialien."),
    ("Einsatz bei uns", "Typischer Einsatz"),
    ("Die Recycling-Realität mitdenken", "Die Einsatzumgebung mitdenken"),
    ("Teile für unsere Anlagen sehen Staub, Feuchte, Öl, Stöße und Sonne (bei offenen Hallen).", "Teile an Maschinen und Anlagen sehen oft Staub, Feuchte, Öl, Stöße und Sonne (bei offenen Hallen oder im Außenbereich)."),
    ("bei unseren Druckern fast nie nötig", "bei X1E und H2C fast nie nötig"),
    ("Unser Startwert TPU+PETG", "Startwert TPU+PETG"),
    ("unsere Standardkombination für hart/weich", "bewährte Standardkombination für hart/weich"),
    ("Der Generator baut unser Firmenschild nach", "Der Generator baut ein Werksschild im Rahmen-Layout"),
    ("Typisch bei uns", "Typische Anwendungen"),
    ("Unsere getesteten Parameter (bitte ausfüllen)", "Getestete Parameter (bitte ausfüllen)"),
    ("Unsere Farbtabelle (bitte ausfüllen)", "Farbtabelle (bitte ausfüllen)"),
    ("Aufgabe:</strong> Für eine Ballenpresse soll", "Aufgabe:</strong> Für eine Maschine soll"),
    ("Für Typenschilder an Ballenpressen, Förderern usw. in feuchter, staubiger oder aggressiver Umgebung (Recyclinghalle, außen)", "Für Typenschilder an Maschinen in feuchter, staubiger oder aggressiver Umgebung (Produktionshalle, außen)"),
    ("Das legt nicht der Azubi fest:", "Das legst du nicht allein fest:"),
    ("Material aus unserer Liste auswählen", "Material aus der Materialliste auswählen"),
    ("An einer Ballenpresse soll ein Typenschild", "An einer Maschine soll ein Typenschild"),
    ("unsere Wahl", "die Wahl"),
    ("Wofür wir 3D-Scannen einsetzen", "Wofür sich 3D-Scannen eignet"),
    ("Beispiel aus unserem Bereich", "Beispiel aus dem Maschinenbau"),
    ("Welches Werkzeug es in unserem CAD gibt, zeigt dir dein Ausbilder.", "Welches Werkzeug dein CAD-Programm dafür hat, steht in dessen Hilfe."),
    ("Für unsere Zwecke heißt das:", "In der Praxis heißt das:"),
    ("Das Druckprofil vorher auf unseren Drucker und unser Filament prüfen.", "Das Druckprofil vorher auf den eigenen Drucker und das eigene Filament prüfen."),
    ("passen selten genau zu unserem Material", "passen selten genau zum eigenen Material"),
    ("die Zahlen zeigen die Größenordnung, nicht einen garantierten Wert für unser Filament.", "die Zahlen zeigen die Größenordnung, nicht einen garantierten Wert für jedes Filament."),
    ("Daten bleiben in der Firma", "Daten bleiben im eigenen Netz"),
    ("für Schilder an Maschinen in der Recyclinghalle oder außen keine Farben", "für Schilder an Maschinen in rauer Umgebung oder außen keine Farben"),
    ("Für Typenschilder an Ballenpressen, Förderern usw. in feuchter, staubiger oder aggressiver Umgebung (Recyclinghalle, außen) <b>keine Farbmarkierung</b>", "Für Typenschilder an Maschinen in feuchter, staubiger oder aggressiver Umgebung (Produktionshalle, außen) <b>keine Farbmarkierung</b>"),
    ("<strong>Firmenprofile und Skripte</strong> ändert nur der Verantwortliche.", "<strong>Standard-Profile und Skripte</strong> nur abgestimmt ändern."),
    ("<strong>nur mit Freigabe der IT</strong> und des Verantwortlichen.", "<strong>nur mit Freigabe der IT</strong>."),
    ("<p>Unsere Drucker arbeiten mit dem <strong>FDM-Verfahren</strong>", "<p>Die Drucker X1E und H2C arbeiten mit dem <strong>FDM-Verfahren</strong>"),
    ("Teile für unsere Anlagen sehen <strong>Staub, Feuchte, Öl, Stöße und Sonne</strong>", "Teile an Maschinen und Anlagen sehen oft <strong>Staub, Feuchte, Öl, Stöße und Sonne</strong>"),
    ("<strong>unsere Standardkombination</strong>", "<strong>bewährte Standardkombination</strong>"),
    ("Der Generator baut unser <strong>Firmenschild</strong> nach", "Der Generator baut ein <strong>Werksschild im Rahmen-Layout</strong>"),
    ("Das legt <strong>nicht</strong> der Azubi fest:", "Das legst du <strong>nicht</strong> allein fest:"),
    ("Für Typenschilder an Ballenpressen, Förderern usw. in <strong>feuchter", "Für Typenschilder an Maschinen in <strong>feuchter"),
    ("(Recyclinghalle, außen) deshalb", "(Produktionshalle, außen) deshalb"),
    ("Firmenprofile weitergeben", "Standard-Profile weitergeben"),
    ("Inhalt mit der Konstruktion bzw. dem CE-Verantwortlichen abstimmen.", "Inhalt mit der Konstruktion abstimmen."),
]
for a, b in R2:
    soft(a, b)
# Option-Texte im Rechner „X1E (bei uns)“ sind oben schon erfasst; restliche „(bei uns)“
s = s.replace(" (bei uns)", "")
open(path, "w", encoding="utf-8").write(s)
left = [w for w in ["Verantwortliche", "Firmenprofil", "Firmen-Profil", "Recyclinghalle", "bei uns ", "unsere ", "Unsere "] if w in re.sub(r"<script.*?</script>", "", s, flags=re.S)]
print("Allgemein gemacht:", path, "| übrig (Handbuchtext):", left)
for m in miss: print("  nicht gefunden:", m[:80])
