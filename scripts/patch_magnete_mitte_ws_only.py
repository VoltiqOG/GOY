"""1) QR-Werkzeug: Magnettaschen symmetrisch zu den Mittelebenen der Platte (Abstand Mitte ↔ Magnet waagerecht und senkrecht).
2) Typenschild: nur noch die Vorlage „Werksschild“ (Firmenschild 148 × 105); die anderen Vorlagen sind entfernt.
Aufruf: python scripts/aktualisieren.py index.html scripts/patch_magnete_mitte_ws_only.py"""
import sys
p = sys.argv[1]; s = open(p, encoding="utf-8").read()
if "mpx:" in s: sys.exit("schon eingespielt")
def R(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:90], s.count(a)); s = s.replace(a, b)
# ---- Magnete: Abstände von der Mitte
R('mon: false, mps: 8.2, mpd: 2.2, mpo: 10 }, sch: {} };', 'mon: false, mps: 8.2, mpd: 2.2, mpo: 10, mpx: 16, mpy: 21 }, sch: {} };')
R('    function qrMagnets() {', '''    // alte Einstellung „Abstand zur Außenkante“ einmalig in Abstände von der Mitte umrechnen
    { const q = TS.qr; if (q.mpx == null || q.mpy == null || q._mpm !== 1) { const r0 = (q.mps || 0) / 2; if (q._mpm !== 1 && q.mpo != null) { q.mpx = +(q.pw / 2 - q.mpo - r0).toFixed(1); q.mpy = +(q.ph / 2 - q.mpo - r0).toFixed(1); } q._mpm = 1; } }
    function qrMagnets() {''')
R('''      // Abstand zur Außenkante bis zum Taschenrand; Mitte auf die Platte begrenzt (wie qrcode2stl)
      const cl = (v, a, b) => Math.min(b, Math.max(a, v)), xL = cl(q.mpo + r, r, q.pw - r), xR = cl(q.pw - q.mpo - r, r, q.pw - r), yU = cl(q.mpo + r, r, q.ph - r), yO = cl(q.ph - q.mpo - r, r, q.ph - r);''',
  '''      // symmetrisch zu den Mittelebenen der Platte: Mitte ± Abstand (waagerecht/senkrecht), Taschen auf der Platte begrenzt
      const cl = (v, a, b) => Math.min(b, Math.max(a, v)), ax = Math.abs(q.mpx || 0), ay = Math.abs(q.mpy || 0), xL = cl(q.pw / 2 - ax, r, q.pw - r), xR = cl(q.pw / 2 + ax, r, q.pw - r), yU = cl(q.ph / 2 - ay, r, q.ph - r), yO = cl(q.ph / 2 + ay, r, q.ph - r);''')
R('''return { d, r, z0: 0, z1: depth, cover: q.pt - depth, limited, e: q.mpo + r, pos,''', '''return { d, r, z0: 0, z1: depth, cover: q.pt - depth, limited, e: Math.min(xL, yU), pos,''')
R('''auf der Unterseite, ${n1(q.mpo, 1)} mm von der Außenkante (Mittenabstand ${n1(M.pos[1][0] - M.pos[0][0], 1)} × ${n1(M.pos[2][1] - M.pos[0][1], 1)} mm).''',
  '''auf der Unterseite, symmetrisch zur Plattenmitte: ±${n1((M.pos[1][0] - M.pos[0][0]) / 2, 1)} mm waagerecht, ±${n1((M.pos[2][1] - M.pos[0][1]) / 2, 1)} mm senkrecht (Mittenabstand ${n1(M.pos[1][0] - M.pos[0][0], 1)} × ${n1(M.pos[2][1] - M.pos[0][1], 1)} mm, Taschenrand ${n1(Math.min(M.pos[0][0], M.pos[0][1]) - M.r, 1)} mm vom Plattenrand).''')
R('''(${M.pos.length}×) ${n1(q.mpo, 1)} mm vom Rand`''', '''(${M.pos.length}×), Mitte ±${n1((M.pos[1][0] - M.pos[0][0]) / 2, 1)} / ±${n1((M.pos[2][1] - M.pos[0][1]) / 2, 1)} mm`''')
R('''            <label>Abstand zur Außenkante (mm)<input name="mpo" type="number" step="0.1" min="0"></label>''',
  '''            <label>Abstand Mitte ↔ Magnet waagerecht (mm)<input name="mpx" type="number" step="0.1" min="0"></label>
            <label>Abstand Mitte ↔ Magnet senkrecht (mm)<input name="mpy" type="number" step="0.1" min="0"></label>''')
R('''["mps", "mpd", "mpo"].forEach((k) => { f.elements[k].closest("label").hidden = !on; });''', '''["mps", "mpd", "mpx", "mpy"].forEach((k) => { f.elements[k].closest("label").hidden = !on; });''')
R('4 runde Klebetaschen auf der Unterseite, eine nahe jeder Ecke.', '4 runde Klebetaschen auf der Unterseite, symmetrisch zur Plattenmitte: Abstand von der senkrechten Mittelebene nach links/rechts und von der waagerechten nach oben/unten (Mittelpunkt der Tasche).')
# ---- Typenschild: nur Werksschild
import re
m = re.search(r'\n\s*<label class="wfull">Vorlage<select name="preset">.*?</select></label>', s)
assert m, "Vorlage-Auswahl nicht gefunden"; s = s[:m.start()] + s[m.end():]
R('''    if (TS.sch.wsL0 === "Bezeichnung" && TS.sch.wsL2 === "Masch.-Nr.")''', '''    if (TS.sch.preset !== "ws") Object.assign(TS.sch, { preset: "ws", w: 148, h: 105, rad: 3, holes: 4, hd: 3, he: 5, m: 3 }); // einzige Vorlage: Firmenschild
    if (TS.sch.wsL0 === "Bezeichnung" && TS.sch.wsL2 === "Masch.-Nr.")''')
R('''<p>Vorlage wählen (<strong>Maschine allgemein</strong>, <strong>Ballenpresse</strong> nach EN 16252 oder <strong>Gurtförderer</strong> nach EN 620), nur die Eckdaten eintragen – Größe, Schriftgrößen, Löcher und QR-Code ordnet die Seite selbst an. Pflichtfelder sind mit * markiert; fehlt etwas, erscheint ein roter Hinweis. Ergebnis ist eine <strong>SVG mit zwei Ebenen</strong>: „gravieren“ (schwarz) und „schneiden“ (rot, Außenkontur und Löcher)''',
  '''<p>Der Generator baut unser <strong>Firmenschild</strong> nach (148 × 105 mm, 4 Löcher Ø 3 mm im Abstand 138 × 95 mm): Logo oben, Anschrift und Service, CE-Zeichen, Typ über die volle Breite, darunter die Felder links und rechts, unten die Website. Nur die Eckdaten eintragen; das Logo lässt sich als SVG, PNG oder JPG austauschen (Bilder werden nachgezeichnet, Schwelle einstellbar). Fehlt eine Pflichtangabe, erscheint ein roter Hinweis. Ergebnis ist eine <strong>SVG mit Ebenen</strong> zum Gravieren und „schneiden“ (rot, Außenkontur und Löcher)''')
R('''<p class="knote">Pflichtangaben (*) nach Maschinenverordnung (EU) 2023/1230 Art. 10 Abs. 5–7 bzw. EN 16252 7.3.1 / EN 620 7.2.''', '''<p class="knote">Angaben nach Maschinenverordnung (EU) 2023/1230 Art. 10 Abs. 5–7 und Anhang III 1.7.3; bei Ballenpressen zusätzlich EN 16252 7.3.1 (elektrische Anschlusswerte).''')
open(p, "w", encoding="utf-8").write(s); print("Magnete Mitte + nur Werksschild:", p)
