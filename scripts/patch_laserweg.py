"""Handbuch: 10.12 „Laserweg“ (Gravierwinkel, Kreuzschraffur, Pfadplanung, Reihenfolge) + Testvorlage,
CE-Texte an das eingebaute CE-Zeichen angepasst, Hinweis auf „Bild → SVG“.

Aufruf: python patch_laserweg.py <unverschluesselte index.html>
Quellen: xTool-Support „How to Set Engraving Angle and Cross Hatch“ (F1 Ultra, XCS ≥ 2.3, Vektorgravur,
„Process on flat surface“ → „Advanced settings“), „Processing Path with Auto Planning & User Define Mode“
(Auto-Plan, One-by-One, All Together, Smart Engraving; Reihenfolge Gravieren → Ritzen → Schneiden),
„Import XCS Parameter Settings“ (Parameter Settings Manager: Export/Import, Cloud-Sync ab XCS 2.3).
"""
import sys

path = sys.argv[1]
s = open(path, encoding="utf-8").read()


def rep(a, b, n=1):
    global s
    if s.count(a) != n:
        raise SystemExit(f"Stelle {s.count(a)}× statt {n}× gefunden: " + a[:90])
    s = s.replace(a, b)


ID = "10-12-laserweg-gravierwinkel-kreuzschraffur-und-reihenfolge"


def tab(head, rows):
    th = "".join(f"<th>{h}</th>" for h in head)
    tr = "".join("<tr>" + "".join(f'<td data-label="{head[i]}"><span class="tc">{c}</span></td>' for i, c in enumerate(r)) + "</tr>" for r in rows)
    return f'<div class="tw"><table class=""><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'


def call(kind, sym, lab, h, body):
    return f'<aside class="call {kind}"><div class="sym" aria-hidden="true">{sym}</div><div class="cb"><div class="lab">{lab}</div><h4>{h}</h4>{body}</div></aside>'


winkel = tab(["Einstellung", "Was passiert", "Gut für", "Nachteil"], [
    ["<strong>0°</strong> (Standard)", "waagerechte Gravurlinien", "Text, einfache Flächen, schnelle Jobs", "schräge und runde Kanten zeigen feine Treppen, waagerechte Streifen in großen Flächen"],
    ["<strong>45°</strong>", "Linien schräg – waagerechte und senkrechte Kanten werden gleich behandelt", "Logos, Schilder mit vielen geraden Kanten in beide Richtungen", "Kanten unter 45° selbst werden etwas unruhiger"],
    ["<strong>90°</strong>", "senkrechte Linien", "Motive, deren wichtige Kanten senkrecht laufen", "wie 0°, nur gedreht"],
    ["<strong>Kreuzschraffur</strong>", "zweiter Durchgang um 90° gedreht", "gleichmäßig dunkle oder tiefe Flächen (Metall schwarz, Holz)", "doppelte Zeit und Wärme – nicht für Farbgravur (Kapitel 10.11)"],
    ["<strong>Winkel inkrementell</strong>, z. B. 4 Durchgänge, +45°", "jeder Durchgang in einer anderen Richtung", "Tiefengravur in Metall, Stempel, sehr gleichmäßige Flächen ohne Streifen", "Zeit × Durchgänge; dünnes Blech wird heiß"],
])
pfad = tab(["Pfadplanung (XCS)", "Was XCS macht", "Wann"], [
    ["<strong>Automatisch</strong> (Auto-Plan, Standard)", "mischt „einzeln“ und „alles zusammen“, möglichst kurze Zeit", "fast immer – erst ändern, wenn das Ergebnis nicht passt"],
    ["<strong>Einzeln nacheinander</strong> (One-by-One)", "jedes Objekt für sich fertig, leere Bereiche dazwischen werden übersprungen", "mehrere getrennte Teile auf der Fläche, z. B. Serie von Schildern"],
    ["<strong>Alles zusammen</strong> (All Together)", "Zeile für Zeile von oben nach unten über alle Objekte", "ein großes zusammenhängendes Motiv, gleichmäßige Fläche"],
    ["<strong>Smart Engraving</strong>", "überspringt große leere Bereiche", "große Flächen mit viel Leerraum – xTool nennt es für den F1; ob es beim F1 Ultra angeboten wird, zeigt das Menü deiner XCS-Version"],
])

sec = f'''<h2 id="{ID}"><span class="hn">10.12</span> Laserweg: Gravierwinkel, Kreuzschraffur und Reihenfolge</h2>
<p>Der F1 Ultra ist ein <strong>Galvo-Laser</strong>: Zwei kleine Spiegel lenken den Strahl, der Laserkopf fährt nicht über das Werkstück. Leerwege kosten deshalb kaum Zeit. Wichtig für das Ergebnis ist, <strong>in welcher Richtung</strong> die Gravurlinien liegen, <strong>wie oft und in welchem Winkel</strong> eine Fläche überfahren wird und <strong>in welcher Reihenfolge</strong> XCS die Objekte bearbeitet.</p>
<h3>Gravierwinkel und Kreuzschraffur</h3>
<p>So stellst du es ein: oben in XCS <strong>„Auf ebener Fläche bearbeiten“</strong> wählen (engl. Process on flat surface) → Objekt anklicken → rechts <strong>„Erweiterte Einstellungen“</strong> (Advanced settings) → Gravierwinkel (fest oder inkrementell), Durchgänge, Kreuzschraffur. Das gibt es ab XCS 2.3 für die <strong>Vektorgravur</strong>.</p>
{winkel}
<h3>Reihenfolge: Pfadplanung</h3>
<p>Bei gemischten Jobs arbeitet XCS immer in der Reihenfolge <strong>Gravieren → Ritzen → Schneiden</strong>. So fällt kein Teil heraus, bevor es graviert ist. Innerhalb der Vektorgravur legt die Pfadplanung die Reihenfolge fest:</p>
{pfad}
<ul class="bul"><li><strong>Innenkonturen vor Außenkonturen schneiden:</strong> Wird zuerst außen geschnitten, kann das Teil verrutschen und das Loch landet daneben. In der <strong>Vorschau</strong> prüfen; wenn die Reihenfolge nicht stimmt, Innenkonturen als eigenen Job zuerst laufen lassen.</li><li><strong>Vorschau immer ansehen:</strong> Sie zeigt den Weg und die Zeit – ein Job, der viel länger dauert als erwartet, hat meist zu viele Durchgänge oder einen zu feinen Linienabstand.</li></ul>
<h3>Einstell-Tipps aus der Praxis</h3>
<ul class="bul"><li><strong>Erst Fokus, dann Position:</strong> Fokus messen (<a class="xr" href="#9-3-fokus-der-haeufigste-fehler">Kapitel 9.3</a>), danach das Kamerabild aktualisieren – sonst sitzt die Gravur daneben.</li><li><strong>Linienabstand zum Material:</strong> zu grob gibt Streifen, zu fein überhitzt das Material (<a class="xr" href="#10-3-die-parameter-verstehen">Kapitel 10.3</a>). Streifen trotz passendem Abstand → 45° oder Kreuzschraffur probieren.</li><li><strong>Eine Sache auf einmal ändern:</strong> Leistung und Geschwindigkeit festhalten und nur den Winkel testen – sonst weißt du nicht, was gewirkt hat.</li><li><strong>Dünnes Blech:</strong> große Flächen in Abschnitte teilen, als einzelne Jobs mit Pausen laufen lassen, Blech auf eine Metallplatte legen.</li><li><strong>Gute Werte sofort speichern:</strong> im Parameterfeld auf das Speichern-Symbol, Name nach dem Muster <code>Material_Dicke_Zweck</code>, z. B. <code>Edelstahl_0,8_schwarz_45grad</code>, und in die Parametertabelle eintragen.</li></ul>
<h3>Testvorlage zum Herunterladen</h3>
<p><a class="kbtn sm" href="dateien/laser-testvorlage-gravierwinkel.svg" download>Testvorlage Gravierwinkel (SVG, 120 × 74 mm)</a></p>
<ol class="steps"><li><span class="n"></span><div><strong>In XCS importieren</strong> und die Gruppierung aufheben – jedes Feld A–F ist ein eigenes Objekt (Quadrat mit Loch Ø 6, Linien 0,1 / 0,2 / 0,3 mm, eine Schräge).</div></li><li><span class="n"></span><div><strong>Allen Feldern dieselbe Leistung, Geschwindigkeit und denselben Linienabstand</strong> geben, dann nur den Winkel ändern: A 0°, B 45°, C 90°, D Kreuzschraffur, E 4 Durchgänge inkrementell +45°, F frei.</div></li><li><span class="n"></span><div><strong>Lasern und vergleichen:</strong> Kante am Loch (rund?), dünnste noch sichtbare Linie, Streifen in der Fläche, Farbe/Tiefe. Die rote Außenkontur nur mitlasern, wenn die Probe ausgeschnitten werden soll.</div></li><li><span class="n"></span><div><strong>Bestes Feld übernehmen:</strong> als Parameter speichern und in die Parametertabelle eintragen.</div></li></ol>
{call("info", "i", "Info", "Geht das als fertige Einstellungsdatei für XCS?", "<p>Nur zum Teil. XCS liest aus einer SVG <strong>keine Lasereinstellungen</strong> – die Ebenen dienen nur zum Trennen. Die Einstellungen hängen am <strong>XCS-Projekt (.xcs)</strong> oder an gespeicherten <strong>Parameter-Voreinstellungen</strong>. Diese lassen sich in XCS im Parameter-Einstellungsmanager (engl. Parameter Settings Manager) <strong>exportieren und importieren</strong> bzw. ab XCS 2.3 über das xTool-Konto synchronisieren. Eine fertige .xcs-Datei kann diese Seite nicht erzeugen, weil xTool das Dateiformat nicht offenlegt.</p><p><strong>So geht es trotzdem einmalig:</strong> Testvorlage in XCS einrichten, als <code>.xcs</code>-Projekt im Projektordner speichern und die bewährten Parameter exportieren. Auf einem anderen Rechner Projekt öffnen bzw. Parameter importieren – dann hat jeder dieselben Werte.</p>")}
{call("tipp", "✓", "Tipp", "Logo oder Zeichnung nur als PNG/JPG?", "<p>Im Kostenrechner unter <strong>Werkzeuge → Bild → SVG</strong> wird daraus eine saubere Vektordatei: Schwelle automatisch, Flecken entfernen, Kanten glätten, Breite in mm – als Fläche zum Gravieren, als Kontur zum Schneiden oder direkt als Logo für das Typenschild. Fotos dagegen als Bitmap direkt in XCS gravieren (<a class=\"xr\" href=\"#10-5-bilder-und-fotos-gravieren-bitmap-modus\">Kapitel 10.5</a>).</p>")}
'''

# vor der Blätter-Navigation am Ende von Kapitel 10
anchor = '<nav class="pnav" aria-label="Kapitel blättern"><a class="pn prev a-laser" href="#kapitel-9">'
rep(anchor, sec + anchor)
rep('<li><a href="#10-11-farbgravur-auf-edelstahl">10.11 Farbgravur auf Edelstahl</a></li>',
    f'<li><a href="#10-11-farbgravur-auf-edelstahl">10.11 Farbgravur auf Edelstahl</a></li><li><a href="#{ID}">10.12 Laserweg: Gravierwinkel, Kreuzschraffur und Reihenfolge</a></li>')
rep('<h1 id="kapitel-10-t">xTool Creative Space (XCS) – die Laser-Software</h1><div class="chs">11 Abschnitte', '<h1 id="kapitel-10-t">xTool Creative Space (XCS) – die Laser-Software</h1><div class="chs">12 Abschnitte')
rep('<span class="cct">xTool Creative Space (XCS) – die Laser-Software</span><span class="cca"><span class="ccb">Laser</span><span class="ccs">11 Abschnitte', '<span class="cct">xTool Creative Space (XCS) – die Laser-Software</span><span class="cca"><span class="ccb">Laser</span><span class="ccs">12 Abschnitte')
rep('<li>Farbgravur auf Edelstahl (<a class="xr" href="#10-11-farbgravur-auf-edelstahl">10.11</a>)</li></ul></div>',
    f'<li>Farbgravur auf Edelstahl (<a class="xr" href="#10-11-farbgravur-auf-edelstahl">10.11</a>)</li><li>Gravierwinkel, Kreuzschraffur und Reihenfolge – mit Testvorlage (<a class="xr" href="#{ID}">10.12</a>)</li></ul></div>')

# ---------- CE-Texte: CE ist jetzt eingebaut
rep('''<aside class="call verboten"><div class="sym" aria-hidden="true">✕</div><div class="cb"><div class="lab">Verboten</div><h4>CE-Zeichen nicht selbst zeichnen</h4><p>Das CE-Zeichen hat feste Proportionen (VO (EG) 765/2008) und darf nur angebracht werden, wenn die Konformitätsbewertung abgeschlossen ist. Der Generator zeichnet es deshalb <strong>nicht</strong> – lade die <strong>offizielle Vorlage der EU-Kommission</strong> als SVG hoch. Ohne Vorlage zeigt die Vorschau nur einen blau gestrichelten Platzhalter, der nicht gelasert wird. Welche Angaben eure Maschinen genau brauchen, legt die Konstruktion fest – das Schild vor der Serie freigeben lassen.</p></div></aside>''',
    '''<aside class="call achtung"><div class="sym" aria-hidden="true">!</div><div class="cb"><div class="lab">Achtung</div><h4>CE-Zeichen nur nach der Konformitätsbewertung</h4><p>Das CE-Zeichen ist im Generator <strong>fest eingebaut</strong> – nachkonstruiert nach dem Raster aus VO (EG) 765/2008 Anhang II: C und E sind Halbkreis-Ringe, deren Enden um ein Rasterfeld verlängert sind, die Kreise berühren sich nicht, der Mittelstrich des E ist ein Rasterfeld kürzer. Mindesthöhe 5 mm, die Proportionen bleiben beim Vergrößern gleich. Wer die offizielle Grafik als SVG hat, kann sie optional laden – sie ersetzt dann das eingebaute Zeichen.</p><p>Das Zeichen darf aber nur auf das Schild, wenn die <strong>Konformitätsbewertung der Maschine abgeschlossen</strong> ist. Welche Angaben die Maschine genau braucht, legt die Konstruktion fest – das Schild vor der Serie freigeben lassen.</p></div></aside>''')
rep('''und das CE-Zeichen <strong>nie selbst nachzeichnen</strong>, sondern die offizielle Grafik nutzen.''',
    '''und das CE-Zeichen nicht frei Hand zeichnen, sondern das maßhaltige Zeichen aus dem Typenschild-Generator oder die offizielle Grafik nutzen – angebracht wird es erst nach abgeschlossener Konformitätsbewertung.''')
rep('<span class="tc">Ballenpresse zusätzlich: elektrische Anschlusswerte</span>', '<span class="tc">je nach Maschinenart zusätzlich, z. B. Ballenpressen: elektrische Anschlusswerte</span>')

open(path, "w", encoding="utf-8").write(s)
print("10.12 Laserweg + CE-Texte:", path)
