"""Handbuch-Struktur: Kapitelübersicht für lange Kapitel, Querverweise, Zählungen, Revision 3.2.

Aufruf: python patch_struktur.py <unverschluesselte index.html>
- Kapitel 4, 7, 8, 9, 10: gruppierte Übersicht der Abschnitte direkt unter „Das lernst du hier“
  (Nummern bleiben, damit alle Verweise gültig bleiben)
- Kapitel 0: Abschnittszahl 4 (nach Entfernen von „Wer ist zuständig?“)
- 8.22 ↔ 11.4 (Steckverbindungen Druck/Laser) verknüpft
- Revision 3.2 vom 07.11.2026 mit Änderungsliste; Benennung allgemein
"""
import re
import sys

path = sys.argv[1]
s = open(path, encoding="utf-8").read()


def rep(a, b, n=1):
    global s
    if s.count(a) != n:
        raise SystemExit(f"Stelle {s.count(a)}× statt {n}× gefunden: " + a[:90])
    s = s.replace(a, b)


GROUPS = {
    4: [("Drucken", ["4.1", "4.2", "4.3", "4.4", "4.5", "4.10", "4.11"]), ("Bedienen und einrichten", ["4.7", "4.8", "4.9"]), ("Pflege und Störungen", ["4.6", "4.12", "4.13", "4.14", "4.15"])],
    7: [("Grundablauf", ["7.1", "7.2", "7.3", "7.10"]), ("Stützen, Haftung, Teile", ["7.4", "7.5", "7.6", "7.7", "7.11"]), ("Farbe und Multimaterial", ["7.8", "7.9", "7.15", "7.17", "7.18"]), ("Profile, Düse, Zeit", ["7.13", "7.14", "7.16"]), ("Tricks", ["7.12", "7.19"])],
    8: [("Grundregeln für druckbare Teile", [f"8.{i}" for i in range(1, 12)]), ("Konstruieren und verbinden", ["8.12", "8.13", "8.22", "8.14", "8.16", "8.17", "8.18"]), ("Nach dem Druck", ["8.15", "8.21"]), ("Werkzeuge im Rechner", ["8.19", "8.20"])],
    9: [("Das Gerät", ["9.1", "9.4", "9.7"]), ("Arbeiten", ["9.2", "9.3", "9.6", "9.8", "9.9"]), ("Pflege und Störungen", ["9.5", "9.10", "9.11", "9.12"])],
    10: [("Grundlagen XCS", ["10.1", "10.2", "10.3", "10.7"]), ("Richtige Werte finden", ["10.4", "10.12"]), ("Besondere Gravuren", ["10.5", "10.11", "10.6", "10.8"]), ("Arbeitsbeispiele", ["10.9", "10.10"])],
}
heads = {num: (hid, title.strip()) for hid, num, title in re.findall(r'<h2 id="([^"]+)"><span class="hn">([\d.]+)</span>([^<]*)</h2>', s)}
for k, groups in GROUPS.items():
    used = [n for _, ns in groups for n in ns]
    allk = sorted([n for n in heads if n.split(".")[0] == str(k)], key=lambda x: int(x.split(".")[1]))
    if sorted(used, key=lambda x: int(x.split(".")[1])) != allk:
        raise SystemExit(f"Kapitel {k}: Gruppen passen nicht zu den Abschnitten {allk}")
    html = f'<nav class="cmap" aria-label="Kapitel {k} im Überblick">' + "".join(
        f'<div class="cmg"><b>{g}</b>' + "".join(f'<a href="#{heads[n][0]}"><span>{n}</span> {heads[n][1]}</a>' for n in ns) + "</div>" for g, ns in groups) + "</nav>"
    i = s.index(f'id="kapitel-{k}"'); j = s.index('<div class="glance">', i); e = s.index("</ul></div>", j) + len("</ul></div>")
    s = s[:e] + "\n" + html + s[e:]
rep('''.mcard header{display:flex;''', '''.cmap{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px 22px;margin:0 0 var(--space-lg);padding:16px 18px;border-radius:var(--radius-card);box-shadow:inset 0 0 0 1px var(--line)}
.cmg{display:flex;flex-direction:column;gap:3px;min-width:0}.cmg b{font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--fg3);margin-bottom:2px}
.cmg a{font-size:14.5px;line-height:1.35;color:var(--fg);text-decoration:none;padding:2px 0}.cmg a span{display:inline-block;min-width:2.6em;color:var(--fg3);font-variant-numeric:tabular-nums}.cmg a:hover{text-decoration:underline;text-underline-offset:3px}
@media print{.cmap{display:none}}
.mcard header{display:flex;''')

# Kapitel 0: Abschnittszahl
rep('<span class="cct">So benutzt du diese Anleitung</span><span class="cca"><span class="ccb">Grundlagen</span><span class="ccs">5 Abschnitte', '<span class="cct">So benutzt du diese Anleitung</span><span class="cca"><span class="ccb">Grundlagen</span><span class="ccs">4 Abschnitte')
rep('<h1 id="kapitel-0-t">So benutzt du diese Anleitung</h1><div class="chs">5 Abschnitte', '<h1 id="kapitel-0-t">So benutzt du diese Anleitung</h1><div class="chs">4 Abschnitte')

# Querverweise Steckverbindungen
rep('<h2 id="11-4-steckverbindungen-fingerzinken-aus-holz-acryl"><span class="hn">11.4</span> Steckverbindungen (Fingerzinken) aus Holz/Acryl</h2>',
    '<h2 id="11-4-steckverbindungen-fingerzinken-aus-holz-acryl"><span class="hn">11.4</span> Steckverbindungen (Fingerzinken) aus Holz/Acryl</h2>\n<p>Gedruckte Steckverbindungen (Zapfen, Schwalbenschwanz, Schnapphaken) und ihr Spiel je Filament stehen in <a class="xr" href="#8-22-steckverbindungen-und-ihre-toleranzen">Kapitel 8.22</a>.</p>')
rep('''– darum brauchen sie einen anderen <strong>Offset</strong>.</p>''', '''– darum brauchen sie einen anderen <strong>Offset</strong>. Gelaserte Fingerzinken aus Holz oder Acryl: <a class="xr" href="#11-4-steckverbindungen-fingerzinken-aus-holz-acryl">Kapitel 11.4</a>.</p>''')

# Revision 3.2
rep('<div><dt>Revision</dt><dd class="rd">3.1</dd></div>', '<div><dt>Revision</dt><dd class="rd">3.2</dd></div>')
rep('<div><dt>Stand</dt><dd class="rd">01.11.2026</dd></div>', '<div><dt>Stand</dt><dd class="rd">07.11.2026</dd></div>')
rep('<div class="m-wide"><dt>Benennung</dt><dd>Schulungsunterlage für Auszubildende</dd></div>', '<div class="m-wide"><dt>Benennung</dt><dd>Schulungs- und Arbeitsunterlage 3D-Druck &amp; Laser</dd></div>')
rep('Revision <span class="rd">3.1</span>, Stand <span class="rd">01.11.2026</span>', 'Revision <span class="rd">3.2</span>, Stand <span class="rd">07.11.2026</span>')
rep('<td data-label="Dokumentinformation"><span class="tc">Revision</span></td><td data-label=""><span class="tc">3.1</span></td>', '<td data-label="Dokumentinformation"><span class="tc">Revision</span></td><td data-label=""><span class="tc">3.2</span></td>')
rep('Stand dieser Unterlage:</strong> Version 3.1, Oktober 2026.', 'Stand dieser Unterlage:</strong> Version 3.2, November 2026.')
i = s.index('<td data-label="Rev."><span class="tc">3.1</span>'); e = s.index("</tr>", i) + len("</tr>")
s = s[:e] + ('<tr><td data-label="Rev."><span class="tc">3.2</span></td><td data-label="Datum"><span class="tc">07.11.2026</span></td><td data-label="Änderung"><span class="tc">'
             'Allgemein formuliert (keine Zuständigkeiten, kein Firmenzuschnitt); 6.8 Glasfaser/Kohlefaser, neue Materialien; 8.22 Steckverbindungen und Toleranzen; '
             '10.12 Laserweg mit Testvorlage; Kapitelübersichten; Rechner pro Projekt, QR-Positionsmarken/Punktgröße, CE im Typenschild, Bild → SVG</span></td><td data-label="Erstellt"><span class="tc">–</span></td></tr>') + s[e:]
open(path, "w", encoding="utf-8").write(s)
print("Struktur:", path)
