"""QR-Werkzeug: Magnettaschen wie bei qrcode2stl (printer.tools) – nach patch_magnete_live.py.

Aufruf: python patch_magnete_v2.py <unverschluesselte index.html>
Bedienung wie qrcode2stl: Schalter „Magnettaschen“, Taschen-Ø, Taschentiefe, Abstand zur
Außenkante; runde Klebetaschen auf der Unterseite, eine nahe jeder Ecke. Ist die Platte
zu dünn, wird die Tiefe so begrenzt, dass mindestens 0,6 mm Material über dem Magneten
bleibt (wie dort, und Kapitel 8.3: Deckel mind. 3 Schichten). Zusätzlich bleiben unsere
Prüfungen: Fehler, wenn eine Tasche in den Code ragt; Wand zum Rand; Taschen berühren sich.
"""
import sys

path = sys.argv[1]
s = open(path, encoding="utf-8").read()


def rep(a, b):
    global s
    if a not in s:
        raise SystemExit("Stelle nicht gefunden: " + a[:90])
    s = s.replace(a, b, 1)


def cut(start, end, new):
    """Ersetzt den Abschnitt von start (inklusive) bis end (exklusive)."""
    global s
    i = s.find(start)
    j = s.find(end, i)
    if i < 0 or j < 0:
        raise SystemExit("Abschnitt nicht gefunden: " + start[:60])
    s = s[:i] + new + s[j:]


# ---------- Formular wie qrcode2stl
cut('''            <label>Magnete (Rückseite)<select name="mag">''', '''            <label class="wfull">Text unter dem Code (optional)''',
    '''            <label class="wchk wfull"><input name="mon" type="checkbox"> Magnettaschen</label>
            <label>Taschen-Ø (mm)<input name="mps" type="number" step="0.1" min="0"></label>
            <label>Taschentiefe (mm)<input name="mpd" type="number" step="0.1" min="0"></label>
            <label>Abstand zur Außenkante (mm)<input name="mpo" type="number" step="0.1" min="0"></label>
            <p class="wfull kmsg mhint">4 runde Klebetaschen auf der Unterseite, eine nahe jeder Ecke. Richtwert: Taschen-Ø = Magnet-Ø + 0,2 mm, Tiefe = Magnethöhe + 0,2 mm – z. B. Magnet 8 × 2 mm → 8,2 / 2,2 mm (Spiel 0,1 mm je Seite für den Kleber; Kapitel 7.11 und 8.4).</p>
''')

# ---------- Standardwerte wie qrcode2stl (8,2 / 2,2 / 10 mm); alte Einstellungen übernehmen
rep('''mag: 0, mmode: "press", md: 6, mh: 2, me: 0, mlh: 0.2 }, sch: {} };''',
    '''mon: false, mps: 8.2, mpd: 2.2, mpo: 10 }, sch: {} };''')
rep('''    if (+TS.qr.hole && !+TS.qr.mag) TS.qr.mag = +TS.qr.hole; TS.qr.hole = 0;''',
    '''    if (+TS.qr.hole || +TS.qr.mag) { TS.qr.mon = true; if (TS.qr.md > 0) { TS.qr.mps = +(TS.qr.md + 0.2).toFixed(2); TS.qr.mpd = +((TS.qr.mh || 2) + 0.2).toFixed(2); } }
    ["hole", "mag", "mmode", "md", "mh", "me", "mlh"].forEach((k) => delete TS.qr[k]);''')

# ---------- Lage und Tiefe der Taschen
cut('''    const MAGFIT = {''', '''    // kürzester Abstand Kreis–Rechteck''',
    '''    const MIN_FLOOR = 0.6; // mindestens so viel Material bleibt über dem Magneten (qrcode2stl, Kapitel 8.3)
    function qrMagnets() {
      const q = TS.qr; if (!q.mon || !(q.mps > 0) || !(q.mpd > 0)) return null;
      const d = q.mps, r = d / 2, maxDepth = Math.max(0, q.pt - MIN_FLOOR), depth = Math.min(maxDepth, q.mpd), limited = q.mpd > maxDepth + 1e-6;
      if (!(depth > 0)) return { d, r, z0: 0, z1: 0, cover: q.pt, limited, e: 0, pos: [], wall: 99, gapX: 99, gapY: 99, none: true };
      // Abstand zur Außenkante bis zum Taschenrand; Mitte auf die Platte begrenzt (wie qrcode2stl)
      const cl = (v, a, b) => Math.min(b, Math.max(a, v)), xL = cl(q.mpo + r, r, q.pw - r), xR = cl(q.pw - q.mpo - r, r, q.pw - r), yU = cl(q.mpo + r, r, q.ph - r), yO = cl(q.ph - q.mpo - r, r, q.ph - r);
      const pos = [[xL, yU], [xR, yU], [xL, yO], [xR, yO]];
      const R = Math.min(q.rad, q.pw / 2, q.ph / 2), wallAt = (x, y) => { const dx = Math.min(x, q.pw - x), dy = Math.min(y, q.ph - y); let w = Math.min(dx, dy) - r;
        if (R > 0 && dx < R && dy < R) w = Math.min(w, R - Math.hypot(R - dx, R - dy) - r); return w; };
      return { d, r, z0: 0, z1: depth, cover: q.pt - depth, limited, e: q.mpo + r, pos, wall: Math.min(...pos.map(([x, y]) => wallAt(x, y))), gapX: xR - xL - d, gapY: yO - yU - d };
    }
''')

# ---------- Meldungen
rep('''      msgs.push(["", `Magnete ${n1(q.md, 1)} × ${n1(q.mh, 1)} mm → Tasche <b>Ø ${n1(M.d, 2)} mm</b>, ${n1(M.z1 - M.z0, 2)} mm tief (${M.f.t}${M.f.deep ? `, ${n1(M.f.deep, 1)} mm Luft in der Tiefe` : ""}, auf ${n1(M.lay, 2)}-mm-Schichten gerundet). Mittenabstand ${+q.mag === 4 ? n1(q.pw - 2 * M.e, 1) + " × " + n1(q.ph - 2 * M.e, 1) : n1(q.pw - 2 * M.e, 1)} mm, Randabstand ${n1(M.e, 1)} mm.`]);''',
    '''      if (M.none) { msgs.push(["err", `Keine Magnettaschen möglich: Die Platte ist ${n1(q.pt, 1)} mm dick, über dem Magneten müssen mindestens ${n1(MIN_FLOOR, 1)} mm bleiben. Platte dicker machen.`]); return; }
      msgs.push(["", `4 Magnettaschen <b>Ø ${n1(M.d, 2)} × ${n1(M.z1, 2)} mm</b> auf der Unterseite, ${n1(q.mpo, 1)} mm von der Außenkante (Mittenabstand ${n1(M.pos[1][0] - M.pos[0][0], 1)} × ${n1(M.pos[2][1] - M.pos[0][1], 1)} mm). Über den Magneten bleiben ${n1(M.cover, 2)} mm.`]);
      if (M.limited) msgs.push(["warn", `<b>Magnettaschen auf ${n1(M.z1, 1)} mm Tiefe reduziert.</b> Über den Magneten müssen mindestens ${n1(MIN_FLOOR, 1)} mm Material bleiben, sonst brechen die Taschen durch die Platte. Für ${n1(q.mpd, 1)} mm tiefe Taschen die Plattendicke auf ${n1(q.mpd + MIN_FLOOR, 1)} mm erhöhen.`]);
      else if (M.cover < 1 - 1e-6) msgs.push(["warn", `Über den Magneten nur ${n1(M.cover, 2)} mm – hält, empfohlen sind 1,0–1,2 mm (Kapitel 8.3).`]);''')
cut('''      if (M.cover < M.minCover - 1e-6)''', '''      if (M.wall < 0.8)''', "")
rep('''Randabstand vergrößern oder kleinere Magnete.`]);''', '''Abstand zur Außenkante vergrößern oder kleinere Taschen.`]);''')
rep('''"Die Magnettaschen berühren sich – Platte größer oder Randabstand kleiner."''', '''"Die Magnettaschen berühren sich – Platte größer oder Abstand zur Außenkante kleiner."''')
rep('''Platte größer, Code kleiner, Magnete kleiner oder andere Anordnung wählen.''', '''Platte größer, Code kleiner, Abstand zur Außenkante kleiner oder kleinere Magnete.''')
cut('''      if (q.mmode === "pause") msgs.push(''', '''    }
    const qrHoles''',
    '''      msgs.push(["", "Drucken: Platte mit der Unterseite auf die Druckplatte (Taschen unten offen, keine Stützen nötig). Magnete nach dem Druck mit 2K-Epoxid einkleben, Polung vorher markieren – alle gleich herum, sonst stoßen sie sich an der Wand ab."]);
''')

# Beschriftung in 3D/Zeichnung
rep('''für Magnet ${n1(q.md, 1)} × ${n1(q.mh, 1)} mm`, c: "plate" }); }''', '''${n1(q.mpo, 1)} mm vom Rand`, c: "plate" }); }''')
rep('''{ const M = qrMagnets(); if (M) A.push(''', '''{ const M = qrMagnets(); if (M && !M.none) A.push(''')
rep('''{ const M = qrMagnets(); if (M) { const [x, y] = M.pos[0]''', '''{ const M = qrMagnets(); if (M && !M.none) { const [x, y] = M.pos[0]''')

# ohne mögliche Tiefe: keine Taschen in Modell und Vorschau
rep('''if (!M || M.cover <= 0)''', '''if (!M || M.none || M.cover <= 0)''')
rep('''const M = qrMagnets(); return M ? `<span class="kchip">''', '''const M = qrMagnets(); return M && !M.none ? `<span class="kchip">''')

# Felder nur bei eingeschaltetem Schalter zeigen
cut('''    function magVis() {''', '''    function qrForm() {''',
    '''    function magVis() { const f = $("#q_form"), on = !!f.elements.mon.checked; ["mps", "mpd", "mpo"].forEach((k) => { f.elements[k].closest("label").hidden = !on; }); f.querySelector(".mhint").hidden = !on; }
''')
rep('''if (el.name === "mag") magVis();''', '''if (el.name === "mon") magVis();''')

open(path, "w", encoding="utf-8").write(s)
print("Magnettaschen wie qrcode2stl:", path)
