"""Handbuch: neuer Abschnitt 8.22 „Steckverbindungen und ihre Toleranzen“ mit Offset je Filament.

Aufruf: python patch_steckverbindungen.py <unverschluesselte index.html>
Quellen: Bambu-Wiki „3D prints shrinkage“ (Startwerte X-Y-Lochkompensation), Bambu-Wiki
„XY hole/contour compensation“ (Vorzeichen, Wirkung), Hubs „Snap-fit joints“ (Fußradius, Breite),
Biegebalken-Formel für Schnapphaken (Kragbalken mit Rechteckquerschnitt).
"""
import sys

path = sys.argv[1]
s = open(path, encoding="utf-8").read()
if 'id="8-22-steckverbindungen' in s:
    sys.exit("Abschnitt 8.22 ist schon drin.")


def rep(a, b, n=1):
    global s
    if s.count(a) != n:
        raise SystemExit(f"Stelle {s.count(a)}× statt {n}× gefunden: " + a[:90])
    s = s.replace(a, b)


ID = "8-22-steckverbindungen-und-ihre-toleranzen"


def tab(head, rows, cls=""):
    th = "".join(f"<th>{h}</th>" for h in head)
    tr = "".join("<tr>" + "".join(f'<td data-label="{head[i]}"><span class="tc">{c}</span></td>' for i, c in enumerate(r)) + "</tr>" for r in rows)
    return f'<div class="tw"><table class="{cls}"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'


def call(kind, sym, lab, h, body):
    return f'<aside class="call {kind}"><div class="sym" aria-hidden="true">{sym}</div><div class="cb"><div class="lab">{lab}</div><h4>{h}</h4>{body}</div></aside>'


arten = tab(["Steckverbindung", "Spalt je Seite (PLA)", "Wofür", "Darauf achten"], [
    ["<strong>Presssitz</strong> (Stift, Zapfen fest)", "0,00–0,05 mm", "Passstift, Lager, Achse einpressen", "einmal fügen; kurze Fase zum Einführen, Wand um die Bohrung ≥ 2 mm, sonst reißt sie"],
    ["<strong>Zapfen + Kleber</strong>", "0,10–0,15 mm", "geteilte Modelle (Kapitel 8.13)", "Spalt ist der Klebespalt – zu eng drückt den Kleber heraus"],
    ["<strong>Steckpassung lösbar</strong> (Zapfen/Loch, Stecker)", "0,15–0,20 mm", "Deckel, Einsätze, Steckteile, die wieder raus sollen", "hält nur durch Reibung – für festen Halt eine Rastnase dazu"],
    ["<strong>Schiebend</strong> (Schwalbenschwanz, Nut/Feder, Schublade)", "0,20–0,25 mm", "Abdeckungen, Schieber, Führungen", "je Flanke rechnen; ab ca. 50 mm Länge +0,05 mm, weil sich Maßfehler aufaddieren"],
    ["<strong>Schnapphaken / Rastnase</strong>", "0,20–0,30 mm seitlich", "Gehäuse, Clips, Deckel ohne Schrauben", "Hinterschnitt nach Formel unten auslegen, nicht schätzen"],
    ["<strong>Bajonett / Drehverschluss</strong>", "0,25–0,35 mm", "Verschlüsse, Halter mit Vierteldrehung", "Rastbuckel am Ende, sonst dreht er sich los"],
    ["<strong>Lose / drehbar</strong> (Gelenk, „print-in-place“)", "0,30–0,40 mm", "Scharnier, Achse, Gelenk", "bei print-in-place nie unter 0,3 mm – sonst verschweißen die Teile"],
])

FIL = [
    ("PLA", "0,00–0,05", "0,15", "0,20", "0,30", "+0,05", "maßhaltig, schrumpft wenig – aber spröde: Presssitz knapp halten, sonst platzt die Bohrung."),
    ("PETG", "0,05", "0,20", "0,25", "0,35–0,40", "+0,10", "fließt nach, Kanten werden etwas dicker und Bohrungen kleiner; zäh, verzeiht einen Presssitz."),
    ("PETG-CF / PET-CF", "0,05", "0,15–0,20", "0,20–0,25", "0,30", "+0,10*", "die Fasern bremsen den Schwund – maßhaltiger als PETG, aber rau und spröder."),
    ("ABS / ASA", "0,05", "0,20", "0,25", "0,35", "+0,10", "schrumpft beim Abkühlen stärker – bei Teilen über ca. 50 mm zusätzlich den Schwund im Filamentprofil einstellen (20-mm-Würfel messen)."),
    ("PA6-CF / PAHT-CF", "0,05", "0,20", "0,25", "0,35", "+0,15", "nimmt Feuchte auf und quillt – vorher trocknen (Kapitel 6.4), die Passung erst nach ein paar Tagen Lagerung endgültig prüfen."),
    ("TPU (in hartes Teil)", "−0,10 bis 0,00", "0,00–0,10", "–", "–", "–", "weich: hält über Übermaß und klemmt elastisch – Spiel macht es lose."),
]
filament = tab(["Material", "Presssitz", "Steckpassung lösbar", "Schiebend", "Lose / drehbar", "oder Slicer: Loch­kompensation"],
               [[f"<strong>{r[0]}</strong>", *r[1:6]] for r in FIL]) + '<ul class="bul">' + "".join(f"<li><strong>{r[0]}:</strong> {r[6]}</li>" for r in FIL) + "</ul>"

svg = '''<figure class="fig narrow"><svg viewBox="0 0 640 250" role="img" aria-label="Schnapphaken im Schnitt: Länge L, Dicke t, Hinterschnitt y, Fügewinkel, Haltewinkel und Radius am Fuß" style="display:block;width:100%;height:auto;color:var(--fg);font:13px var(--f-text, sans-serif)">
<rect x="20" y="30" width="60" height="190" fill="var(--bg2)" stroke="currentColor" stroke-width="1.5"/>
<text x="50" y="240" text-anchor="middle" fill="var(--fg2)">Wand</text>
<path d="M80 84 H440 L440 84 L470 134 H440 V114 H92 Q80 114 80 126" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
<path d="M440 114 V134" stroke="currentColor" stroke-width="2"/>
<g stroke="var(--konstr, #2563eb)" fill="var(--konstr, #2563eb)" stroke-width="1.2">
<path d="M80 50 H440" /><path d="M80 45 V55 M440 45 V55"/><text x="260" y="44" text-anchor="middle" stroke="none">L = Länge des Hakens</text>
<path d="M150 86 V112" /><path d="M145 86 H155 M145 112 H155"/><text x="162" y="104" stroke="none">t = Dicke am Fuß</text>
<path d="M480 114 H500 M480 134 H500" stroke-dasharray="3 3"/><path d="M496 114 V134"/><path d="M491 114 H501 M491 134 H501"/><text x="508" y="128" stroke="none">y = Hinterschnitt</text>
<path d="M462 112 L520 70" stroke-width="1"/><text x="524" y="70" stroke="none">Fügeschräge ≈ 30°</text>
<path d="M436 124 L400 196" stroke-width="1"/><text x="400" y="212" text-anchor="middle" stroke="none">Haltewinkel: 45° lösbar · 90° fest</text>
<path d="M84 140 L90 124" stroke-width="1"/><text x="88" y="156" stroke="none">R ≥ 0,5 · t (Ausrundung am Fuß)</text>
</g>
</svg><figcaption>Schnapphaken im Schnitt – die Maße für die Formel. Biegung immer in der Druckebene (X/Y), nie quer zu den Schichten.</figcaption></figure>'''

dehn = tab(["Material", "zulässige Dehnung ε, einmal fügen", "oft öffnen (× 0,6)", "Beispiel L = 15 mm, t = 1,6 mm → max. Weg y"], [
    ["PLA", "1,5–2 %", "≈ 1 %", "1,4–1,9 mm"],
    ["PETG", "3 %", "≈ 2 %", "2,8 mm"],
    ["ABS / ASA", "2,5 %", "≈ 1,5 %", "2,4 mm"],
    ["PETG-CF, PET-CF, PA6-CF", "1–1,5 %", "≈ 0,8 %", "0,9–1,4 mm"],
    ["TPU", "kein Schnapphaken nötig", "–", "TPU-Teil klemmt über Übermaß"],
])

sec = f'''<h2 id="{ID}"><span class="hn">8.22</span> Steckverbindungen und ihre Toleranzen</h2>
<p>Bei einer <strong>Steckverbindung</strong> werden Teile ohne Schraube zusammengesteckt, geschoben oder eingerastet. Ob sie klemmt, sauber hält oder wackelt, entscheidet allein der <strong>Spalt</strong> zwischen den Teilen. Die Grundwerte aus <a class="xr" href="#8-4-passungen-und-spiel">Kapitel 8.4</a> gelten für <strong>PLA</strong>. Andere Filamente schrumpfen, fließen und federn anders – darum brauchen sie einen anderen <strong>Offset</strong>.</p>
<h3>Was „Offset“ hier heißt</h3>
<ul class="bul"><li><strong>Offset = Spalt je Seite.</strong> Bei einer Bohrung wirkt er zweimal: Zapfen Ø 8 mm, Offset 0,2 mm → Bohrung <strong>Ø 8,4 mm</strong>.</li><li><strong>Nur ein Teil bekommt den Offset</strong> – meist die Aufnahme (Bohrung, Nut). Der Zapfen bleibt auf Nennmaß. So passt er auch noch, wenn du ihn später aus einem anderen Material druckst.</li><li>Im CAD am besten als <strong>Parameter</strong> anlegen (z. B. <code>spalt = 0,2</code>), dann änderst du für ein anderes Filament nur einen Wert.</li></ul>
<h3>Spalt je Art der Steckverbindung</h3>
{arten}
<h3>Offset je Filament</h3>
<p>Spalt je Seite in mm, gedruckt auf X1E oder H2C mit 0,4-mm-Düse und den Standardprofilen. Die letzte Spalte ist der Startwert, wenn du den Spalt stattdessen im Slicer einstellst (siehe Kasten darunter) – nicht beides.</p>
{filament}
<p class="knote">Richtwerte zum Starten, keine Normwerte. Die Startwerte für die Lochkompensation stammen aus dem Bambu-Wiki (PLA 0,05, PETG 0,10, ABS 0,10, Nylon 0,15 mm); *für die CF-Varianten gibt Bambu keinen Wert an, dort wie PETG anfangen. Die Spalte „Lose“ und die CF-Werte sind Erfahrungswerte – <strong>immer mit dem Probekörper unten bestätigen</strong>.</p>
{call("achtung", "!", "Achtung", "Offset nur einmal – entweder CAD oder Slicer", "<p>Bambu Studio kann Bohrungen selbst aufweiten: <strong>Prozess → Qualität → X-Y-Lochkompensation</strong> (positiv = Loch größer) und <strong>X-Y-Konturkompensation</strong> (positiv = Außenkontur größer, negativ = kleiner). Wenn du den Spalt schon im CAD eingerechnet hast, müssen beide auf <strong>0</strong> stehen – sonst ist das Spiel doppelt so groß.</p><p>Die Lochkompensation wirkt nur auf <strong>geschlossene runde Löcher</strong>. Nuten, Schlitze und Schwalbenschwänze bekommen den Spalt deshalb <strong>immer im CAD</strong>. Welche Kompensation in den Firmenprofilen steht, legt der Verantwortliche fest (<a class=\"xr\" href=\"#7-13-firmen-profile-bitte-mit-dem-verantwortlichen-festlegen\">Kapitel 7.13</a>).</p>")}
<h3>Was die Passung zusätzlich verändert</h3>
<ul class="bul"><li><strong>Druckrichtung der Bohrung:</strong> Senkrechte Bohrungen (Achse in Z) werden rund. Waagerechte Bohrungen hängen oben etwas durch – dort <strong>+0,05 mm</strong> oder gleich die Tropfenform aus <a class="xr" href="#8-2-bruecken-und-waagerechte-bohrungen">Kapitel 8.2</a>.</li><li><strong>Elefantenfuß:</strong> Die ersten Schichten werden breiter. Steckteile, die mit der Steckfläche auf der Platte stehen, unten mit einer <strong>Fase 0,4–0,5 mm</strong> versehen (<a class="xr" href="#8-5-kanten-unten-fase-statt-radius">Kapitel 8.5</a>).</li><li><strong>Schichthöhe:</strong> Bei 0,28 mm statt 0,20 mm wird die Wand rauer – Steckpassungen dann eher +0,05 mm.</li><li><strong>Tempern</strong> ändert die Maße um Prozente – Passungen erst danach prüfen (<a class="xr" href="#8-21-tempern-bauteile-nachtraeglich-waermebehandeln">Kapitel 8.21</a>).</li></ul>
<h3>Schnapphaken richtig auslegen</h3>
<p>Ein Schnapphaken ist ein kleiner Biegebalken: Beim Stecken biegt er sich um den Hinterschnitt <strong>y</strong> weg und springt dann zurück. Biegt er sich weiter, als das Material verträgt, bricht er am Fuß. Wie weit er sich biegen darf, sagt die Formel für einen Haken mit gleichbleibender Dicke:</p>
{svg}
<p style="text-align:center;font-size:1.1em"><strong>y = 0,67 · ε · L² / t</strong></p>
<p><strong>ε</strong> = zulässige Dehnung (als Dezimalzahl, 2 % = 0,02), <strong>L</strong> = Länge, <strong>t</strong> = Dicke am Fuß. Der Hinterschnitt muss <strong>kleiner</strong> als das errechnete y sein. Beispiel PLA: 0,67 · 0,02 · 15² / 1,6 = <strong>1,9 mm</strong> → ein Hinterschnitt von 1,0–1,2 mm ist sicher.</p>
{dehn}
<p class="knote">Die Dehnungswerte sind vorsichtige Auslegungswerte für gedruckte Haken, die in der Druckebene liegen – deutlich unter den Werten aus Datenblättern für Spritzguss. Ist der Haken zu steif: <strong>länger</strong> machen hilft am meisten (L geht im Quadrat ein), dünner geht nur bis ca. 1,2 mm (3 Wandlinien).</p>
<ul class="bul"><li><strong>Fuß ausrunden:</strong> Radius mindestens <strong>0,5 · t</strong> – an der scharfen Ecke bricht der Haken zuerst.</li><li><strong>Breite</strong> mindestens <strong>5 mm</strong>, sonst wird er wackelig und bricht seitlich.</li><li><strong>Druckrichtung:</strong> Haken flach in X/Y legen. Steht er senkrecht (Biegung quer zu den Schichten), bricht er schon bei der Hälfte – dann lieber anders konstruieren (<a class="xr" href="#8-6-festigkeit-und-druckrichtung">Kapitel 8.6</a>).</li><li><strong>Wände 100 %:</strong> Haken immer massiv drucken (Wandlinien statt Füllung), z. B. mit einem Modifizierer (<a class="xr" href="#7-6-modifizierer-verschiedene-einstellungen-in-einem-teil">Kapitel 7.6</a>).</li></ul>
<h3>Probekörper: einmal je Material drucken</h3>
<ol class="steps"><li><span class="n"></span><div><strong>Lochleiste konstruieren:</strong> ein Zapfen Ø 10 mm, 10 mm hoch, und eine Leiste mit 8 Bohrungen von Ø 10,10 bis Ø 10,80 mm (Spalt je Seite 0,05 bis 0,40 mm in 0,05er-Schritten). Spalt neben jede Bohrung gravieren.</div></li><li><span class="n"></span><div><strong>Mit dem Firmenprofil drucken</strong>, X-Y-Lochkompensation auf 0. Bohrungen senkrecht (Achse in Z).</div></li><li><span class="n"></span><div><strong>Abkühlen lassen</strong> (mindestens 30 Minuten, PA-CF einen Tag), dann den Zapfen in jede Bohrung stecken: Wo geht er stramm rein = Presssitz, wo lässt er sich von Hand stecken und ziehen = Steckpassung, wo dreht er frei = lose.</div></li><li><span class="n"></span><div><strong>Werte eintragen</strong> – hier und in den Kasten in <a class="xr" href="#8-4-passungen-und-spiel">Kapitel 8.4</a>:</div></li></ol>
<div class="tw"><table class=""><thead><tr><th>Drucker / Material</th><th>Presssitz</th><th>Steckpassung</th><th>Lose</th><th>geprüft am / von</th></tr></thead><tbody><tr><td data-label="Drucker / Material"><span class="tc">X1E / PLA</span></td><td data-label="Presssitz"><span class="tc"></span></td><td data-label="Steckpassung"><span class="tc"></span></td><td data-label="Lose"><span class="tc"></span></td><td data-label="geprüft am / von"><span class="tc"></span></td></tr><tr><td data-label="Drucker / Material"><span class="tc">X1E / PETG</span></td><td data-label="Presssitz"><span class="tc"></span></td><td data-label="Steckpassung"><span class="tc"></span></td><td data-label="Lose"><span class="tc"></span></td><td data-label="geprüft am / von"><span class="tc"></span></td></tr><tr><td data-label="Drucker / Material"><span class="tc">X1E / PETG-CF</span></td><td data-label="Presssitz"><span class="tc"></span></td><td data-label="Steckpassung"><span class="tc"></span></td><td data-label="Lose"><span class="tc"></span></td><td data-label="geprüft am / von"><span class="tc"></span></td></tr><tr><td data-label="Drucker / Material"><span class="tc">H2C / PLA</span></td><td data-label="Presssitz"><span class="tc"></span></td><td data-label="Steckpassung"><span class="tc"></span></td><td data-label="Lose"><span class="tc"></span></td><td data-label="geprüft am / von"><span class="tc"></span></td></tr><tr><td data-label="Drucker / Material"><span class="tc">H2C / PETG</span></td><td data-label="Presssitz"><span class="tc"></span></td><td data-label="Steckpassung"><span class="tc"></span></td><td data-label="Lose"><span class="tc"></span></td><td data-label="geprüft am / von"><span class="tc"></span></td></tr></tbody></table></div>
{call("merke", "★", "Merke", "In einem Satz", "<p>Spalt je Seite aus der Tabelle für dein Filament nehmen, <strong>nur an einem Teil</strong> und <strong>nur einmal</strong> (CAD oder Slicer) einrechnen, Schnapphaken mit der Formel auslegen – und vor dem großen Teil den 10-Minuten-Probekörper drucken.</p>")}
'''

# hinter 8.21 (vor dem Blätter-Menü des Kapitels 8) einfügen
rep('''<nav class="pnav" aria-label="Kapitel blättern"><a class="pn prev a-slicer" href="#kapitel-7">''',
    sec + '''<nav class="pnav" aria-label="Kapitel blättern"><a class="pn prev a-slicer" href="#kapitel-7">''')
# Inhaltsverzeichnis, Abschnittszahl, „Das lernst du hier“
rep('''8.21 Tempern – Bauteile nachträglich wärmebehandeln</a></li></ol>''',
    f'''8.21 Tempern – Bauteile nachträglich wärmebehandeln</a></li><li><a href="#{ID}">8.22 Steckverbindungen und ihre Toleranzen</a></li></ol>''')
rep('''<span class="cct">Konstruieren für den 3D-Druck</span><span class="cca"><span class="ccb">Konstruktion</span><span class="ccs">21 Abschnitte</span>''',
    '''<span class="cct">Konstruieren für den 3D-Druck</span><span class="cca"><span class="ccb">Konstruktion</span><span class="ccs">22 Abschnitte</span>''')
rep('''<h1 id="kapitel-8-t">Konstruieren für den 3D-Druck</h1><div class="chs">21 Abschnitte</div>''',
    '''<h1 id="kapitel-8-t">Konstruieren für den 3D-Druck</h1><div class="chs">22 Abschnitte</div>''')
rep('''welche Temperaturen (<a class="xr" href="#8-21-tempern-bauteile-nachtraeglich-waermebehandeln">8.21</a>)</li></ul></div>''',
    f'''welche Temperaturen (<a class="xr" href="#8-21-tempern-bauteile-nachtraeglich-waermebehandeln">8.21</a>)</li><li>Steckverbindungen: Spalt je Verbindungsart, Offset je Filament und Schnapphaken nachrechnen (<a class="xr" href="#{ID}">8.22</a>)</li></ul></div>''')
# Querverweise aus 8.4 und 8.13
rep('''Die Werte gelten je Material und Drucker unterschiedlich – <strong>ermittelte Werte hier eintragen:</strong></p>''',
    f'''Die Werte gelten je Material und Drucker unterschiedlich – Offset je Filament und ein fertiger Probekörper stehen in <a class="xr" href="#{ID}">Kapitel 8.22</a>. <strong>Ermittelte Werte hier eintragen:</strong></p>''')
rep('''<h2 id="8-13-teile-verbinden"><span class="hn">8.13</span> Teile verbinden</h2>''',
    f'''<h2 id="8-13-teile-verbinden"><span class="hn">8.13</span> Teile verbinden</h2>
<p>Welcher Spalt für Zapfen, Schwalbenschwanz und Schnapphaken je Filament passt, steht in <a class="xr" href="#{ID}">Kapitel 8.22</a>.</p>''')

open(path, "w", encoding="utf-8").write(s)
print("Abschnitt 8.22 Steckverbindungen:", path)
