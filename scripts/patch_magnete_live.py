"""QR-Code-Werkzeug: Magnettaschen statt Befestigungslöcher (Einbau von der Rückseite, mit Aufmaß).

Die bisherigen „Befestigungslöcher“ werden zu Magnettaschen an denselben Stellen
(2 Mitte links/rechts, 2 oben oder 4 Ecken); Durchgangslöcher gibt es nicht mehr.
Fehler, wenn eine Tasche in den Code ragt; Warnung bei Ruhezone und Text.

Aufruf: python patch_magnete.py <unverschluesselte index.html>
Die Werte stammen aus dem Handbuch: Kapitel 7.11 (Spiel 0,2 mm je Seite für
Einlegeteile, Pause zum Einschließen), 8.3 (Boden/Deckel mind. 0,6 mm, Wand
mind. 0,8 mm, empfohlen 1,2–1,6 mm) und 8.4 (Presspassung 0,00–0,05 mm je Seite).
"""
import sys

path = sys.argv[1]
s = open(path, encoding="utf-8").read()


def rep(a, b):
    global s
    if a not in s:
        raise SystemExit("Stelle nicht gefunden: " + a[:90])
    s = s.replace(a, b, 1)


# ---------- Formular: Befestigungslöcher entfallen, an ihre Stelle kommen die Magnete
rep('''            <label>Befestigungslöcher<select name="hole"><option value="0">keine</option><option value="2">2 (Mitte links/rechts)</option><option value="3">2 (oben)</option></select></label>
            <label>Loch-Ø (mm)<input name="hd" type="number" step="0.1" min="2"></label>
''', "")
rep('''            <label class="wfull">Text unter dem Code (optional)''',
    '''            <label>Magnete (Rückseite)<select name="mag"><option value="0">keine</option><option value="2">2 (Mitte links/rechts)</option><option value="3">2 (oben)</option><option value="4">4 (Ecken)</option></select></label>
            <label>Einbau<select name="mmode"><option value="press">von hinten einpressen</option><option value="glue">von hinten einkleben</option><option value="pause">eingeschlossen (Pause, Kapitel 7.11)</option></select></label>
            <label>Magnet-Ø (mm)<input name="md" type="number" step="0.5" min="2"></label>
            <label>Magnet-Höhe (mm)<input name="mh" type="number" step="0.5" min="0.5"></label>
            <label>Randabstand Magnetmitte (mm)<input name="me" type="number" step="0.5" min="0" placeholder="automatisch"></label>
            <label>Schichthöhe (mm)<input name="mlh" type="number" step="0.04" min="0.08"></label>
            <label class="wfull">Text unter dem Code (optional)''')

# ---------- Standardwerte
rep('''hd: 4.2, label: "", lh: 4, inv: false, style: "sq" }, sch: {} };''',
    '''hd: 4.2, label: "", lh: 4, inv: false, style: "sq", mag: 0, mmode: "press", md: 6, mh: 2, me: 0, mlh: 0.2 }, sch: {} };''')

# ---------- alte Einstellung „Befestigungslöcher“ wird zu Magneten an derselben Stelle
rep('''    const saveTS = () =>''', '''    if (+TS.qr.hole && !+TS.qr.mag) TS.qr.mag = +TS.qr.hole; TS.qr.hole = 0;
    const saveTS = () =>''')

# ---------- Rechnung der Taschen
rep('''    const qrHoles = () =>''', r'''    // ---------- Magnettaschen: Aufmaß und Lage nach Handbuch 7.11, 8.3 und 8.4
    const MAGFIT = { pause: { side: 0.2, deep: 0.2, t: "Spiel 0,2 mm je Seite (Kapitel 7.11)" }, press: { side: 0.05, deep: 0, t: "Presspassung 0,05 mm je Seite (Kapitel 8.4)" }, glue: { side: 0.15, deep: 0.1, t: "Spielpassung 0,15 mm je Seite für den Kleber (Kapitel 8.4)" } };
    function qrMagnets() {
      const q = TS.qr; if (![2, 3, 4].includes(+q.mag) || !(q.md > 0) || !(q.mh > 0)) return null;
      const f = MAGFIT[q.mmode] || MAGFIT.pause, lay = q.mlh > 0 ? q.mlh : 0.2, up = (v) => Math.ceil(v / lay - 1e-6) * lay;
      const d = q.md + 2 * f.side, r = d / 2;
      // z: Boden unter der Tasche (nur eingeschlossen), Tasche, Deckel bis Plattenoberseite. Alles auf ganze Schichten gerundet
      const floor = q.mmode === "pause" ? up(0.6) : 0, z0 = floor, z1 = up(floor + q.mh + f.deep), cover = q.pt - z1;
      const minCover = up(0.6), recCover = up(1.0), needPt = z1 + minCover;
      const e = q.me > 0 ? q.me : Math.max(r + 2, q.rad > 0 ? q.rad : 0), pos = +q.mag === 2 ? [[e, q.ph / 2], [q.pw - e, q.ph / 2]] : +q.mag === 3 ? [[e, q.ph - e], [q.pw - e, q.ph - e]] : [[e, e], [q.pw - e, e], [e, q.ph - e], [q.pw - e, q.ph - e]];
      // Wand zum Rand, bei runden Ecken zum Bogen gemessen
      const R = Math.min(q.rad, q.pw / 2, q.ph / 2), wallAt = (x, y) => { const dx = Math.min(x, q.pw - x), dy = Math.min(y, q.ph - y); let w = Math.min(dx, dy) - r;
        if (R > 0 && dx < R && dy < R) w = Math.min(w, R - Math.hypot(R - dx, R - dy) - r); return w; };
      const wall = Math.min(...pos.map(([x, y]) => wallAt(x, y))), gapX = q.pw - 2 * e - d, gapY = +q.mag === 4 ? q.ph - 2 * e - d : 99;
      return { d, r, f, lay, floor, z0, z1, cover, minCover, recCover, needPt, e, pos, wall, gapX, gapY, pauseZ: q.mmode === "pause" ? z1 : null };
    }
    // kürzester Abstand Kreis–Rechteck (negativ = überlappt)
    const circRect = (x, y, r, x0, y0, x1, y1) => Math.hypot(Math.max(x0 - x, 0, x - x1), Math.max(y0 - y, 0, y - y1)) - r;
    function magMsgs(M, msgs, B) {
      const q = TS.qr;
      msgs.push(["", `Magnete ${n1(q.md, 1)} × ${n1(q.mh, 1)} mm → Tasche <b>Ø ${n1(M.d, 2)} mm</b>, ${n1(M.z1 - M.z0, 2)} mm tief (${M.f.t}${M.f.deep ? `, ${n1(M.f.deep, 1)} mm Luft in der Tiefe` : ""}, auf ${n1(M.lay, 2)}-mm-Schichten gerundet). Mittenabstand ${+q.mag === 4 ? n1(q.pw - 2 * M.e, 1) + " × " + n1(q.ph - 2 * M.e, 1) : n1(q.pw - 2 * M.e, 1)} mm, Randabstand ${n1(M.e, 1)} mm.`]);
      if (M.cover < M.minCover - 1e-6) msgs.push(["err", `Platte zu dünn für die Magnete: über der Tasche bleiben ${n1(Math.max(0, M.cover), 2)} mm, nötig sind mind. ${n1(M.minCover, 1)} mm (3 Schichten, Kapitel 8.3). Plattendicke mindestens <b>${n1(M.needPt, 2)} mm</b>, besser ${n1(M.z1 + M.recCover, 2)} mm.`]);
      else if (M.cover < M.recCover - 1e-6) msgs.push(["warn", `Deckel über den Magneten nur ${n1(M.cover, 2)} mm – hält, empfohlen sind 1,0–1,2 mm (Kapitel 8.3). Plattendicke ${n1(M.z1 + M.recCover, 2)} mm wäre sicherer.`]);
      if (M.wall < 0.8) msgs.push(["err", `Wand zwischen Magnettasche und Plattenrand nur ${n1(Math.max(0, M.wall), 2)} mm (mind. 0,8 mm, Kapitel 8.3) – Randabstand vergrößern oder kleinere Magnete.`]);
      else if (M.wall < 1.2) msgs.push(["warn", `Wand zum Rand ${n1(M.wall, 2)} mm – druckbar, empfohlen 1,2–1,6 mm (Kapitel 8.3).`]);
      if (M.gapX < 0.8 || M.gapY < 0.8) msgs.push(["err", "Die Magnettaschen berühren sich – Platte größer oder Randabstand kleiner."]);
      // Lage zum Code: Fehler, wenn eine Tasche in den Code ragt; Warnung bei Ruhezone und Text
      const code = [B.cx0, B.cy0, B.cx0 + q.size, B.cy0 + q.size], qz = [code[0] - B.quietMM, code[1] - B.quietMM, code[2] + B.quietMM, code[3] + B.quietMM];
      const dCode = Math.min(...M.pos.map(([x, y]) => circRect(x, y, M.r, ...code))), dQz = Math.min(...M.pos.map(([x, y]) => circRect(x, y, M.r, ...qz)));
      if (dCode < 0) msgs.push(["err", `<b>Magnettasche ragt in den QR-Code</b> (${n1(-dCode, 2)} mm Überdeckung). Platte größer, Code kleiner, Magnete kleiner oder andere Anordnung wählen.`]);
      else if (dQz < 0) msgs.push(["warn", `Magnettasche ragt in die Ruhezone des Codes (${n1(-dQz, 2)} mm). Von vorn unsichtbar, solange der Deckel reicht – besser Abstand halten.`]);
      if (q.label) { const tw = textWidth(q.label, q.lh, true), ty = B.cy0 - B.gap - q.lh, tr = [q.pw / 2 - tw / 2, ty, q.pw / 2 + tw / 2, ty + q.lh];
        if (M.pos.some(([x, y]) => circRect(x, y, M.r, ...tr) < 0)) msgs.push(["warn", "Magnettasche liegt unter dem Text – bei dünnem Deckel zeichnet sich die Tasche ab. Text kürzer oder Magnete versetzen."]); }
      if (q.mmode === "pause") msgs.push(["", `Drucken: <b>Pause bei Z = ${n1(M.pauseZ, 2)} mm</b> einfügen (erste Schicht über der Tasche, Kapitel 7.11). Magnete mit gleicher Polung einlegen (vorher markieren), bündig, nicht überstehend – dann fortsetzen. Bodenschicht unter den Magneten ${n1(M.floor, 2)} mm schwächt die Haltekraft etwas.`]);
      else msgs.push(["", `Taschen sind unten offen: Platte mit der Rückseite auf die Druckplatte, Magnete nach dem Druck ${q.mmode === "press" ? "mit einem Schraubstock gerade einpressen (gedruckte Bohrungen fallen eher klein aus – bei zu strammem Sitz Probekörper drucken, Kapitel 8.4)" : "mit 2K-Epoxid einkleben (Sekundenkleber hält auf Neodym schlecht)"}. Magnetfläche liegt bündig – volle Haltekraft. Polung vorher markieren.`]);
    }
    const qrHoles = () => []; // keine Durchgangslöcher mehr – an ihrer Stelle sitzen Magnettaschen
    const qrHolesAlt = () =>''')

# alte Lochprüfung in qrBuild entfällt
rep('''      { const cq = [cx0 - quietMM, cy0 - quietMM, cx0 + q.size + quietMM, cy0 + q.size + quietMM], e = Math.max(q.hd / 2 + 2.5, q.rad), r = q.hd / 2 + 0.8;
        const H = q.hole == 2 ? [[e, q.ph / 2], [q.pw - e, q.ph / 2]] : q.hole == 3 ? [[e, q.ph - e], [q.pw - e, q.ph - e]] : [];
        if (H.some(([x, y]) => x + r > cq[0] && x - r < cq[2] && y + r > cq[1] && y - r < cq[3])) msgs.push(["warn", "Löcher ragen in den Code oder seine Ruhezone – Platte vergrößern, Löcher „oben“ wählen oder Code kleiner."]); }
''', "")

# Meldungen in qrBuild ergänzen
rep('''      if (!/^https?:\\/\\/\\S+\\.\\S+/.test(q.url)) msgs.push(''',
    '''      { const M = qrMagnets(); if (M) magMsgs(M, msgs, { cx0, cy0, quietMM }); }
      if (!/^https?:\\/\\/\\S+\\.\\S+/.test(q.url)) msgs.push(''')

# ---------- STEP: Platte in Lagen zerlegen, damit die Taschen die richtige Tiefe haben
rep('''      const plate = { name: "Platte", color: [0.95, 0.95, 0.95], z0: 0, z1: q.pt, outer: roundRect(0, 0, q.pw, q.ph, q.rad), holes: [] };
      plate.holesC = []; qrHoles().forEach(([x, y]) => { plate.holes.push(circle(x, y, q.hd / 2)); plate.holesC.push({ cx: x, cy: y, r: q.hd / 2 }); });
      solids.push(plate);''',
    '''      const M = qrMagnets(), outer = roundRect(0, 0, q.pw, q.ph, q.rad);
      // Taschen: in der STEP exakte Zylinder (holesC), für die 3D-Vorschau als Vieleck
      const W = (z0, z1, name, pk) => ({ name, color: [0.95, 0.95, 0.95], z0, z1, outer, holes: pk ? M.pos.map(([x, y]) => circle(x, y, M.r / Math.cos(Math.PI / 48), 48)) : [], holesC: pk ? M.pos.map(([x, y]) => ({ cx: x, cy: y, r: M.r })) : [] });
      if (!M || M.cover <= 0) solids.push(W(0, q.pt, "Platte", false));
      else { if (M.z0 > 0) solids.push(W(0, M.z0, "Platte_Boden", false)); solids.push(W(M.z0, M.z1, "Platte_Magnetlage", true)); solids.push(W(M.z1, q.pt, "Platte_Deckel", false)); }''')

# ---------- Vorschau: Taschen gestrichelt einzeichnen (nicht in der Laser-SVG)
rep('''        (forLaser ? "" : `<rect x="0" y="0" width="${f3(q.pw)}" height="${f3(q.ph)}" rx="${f3(q.rad)}" fill="#fff"/>`) +''',
    '''        (forLaser ? "" : `<rect x="0" y="0" width="${f3(q.pw)}" height="${f3(q.ph)}" rx="${f3(q.rad)}" fill="#fff"/>`) +
        (forLaser ? "" : (() => { const M = qrMagnets(); return M ? `<g fill="none" stroke="#9a5a0b" stroke-width="0.35" stroke-dasharray="1 0.8">${M.pos.map(([x, y]) => `<circle cx="${f3(x)}" cy="${f3(Y(y))}" r="${f3(M.r)}"/>`).join("")}</g>` : ""; })()) +''')

# Beschriftung in 3D/Zeichnung: Magnettasche statt Befestigungsloch
rep('''      const H = qrHoles(); if (H.length) A.push({ p: [H[0][0] - q.hd / 2 * 0.7, H[0][1], q.pt], t: `<b>Befestigungsloch</b> Ø ${n1(q.hd, 1)} mm${H.length > 1 ? ` (${H.length}×)` : ""}`, c: "plate" });''',
    '''      { const M = qrMagnets(); if (M) A.push({ p: [M.pos[0][0], M.pos[0][1], M.z0], t: `<b>Magnettasche</b> Rückseite Ø ${n1(M.d, 2)} × ${n1(M.z1 - M.z0, 2)} mm (${M.pos.length}×) für Magnet ${n1(q.md, 1)} × ${n1(q.mh, 1)} mm`, c: "plate" }); }''')
rep('''      qrHoles().forEach(([x, y], i) => { if (i) return; g += `<g class="dim"><path d="M${f3(x + q.hd / 2 * 0.7)} ${f3(Y(y) + q.hd / 2 * 0.7)}l${f3(4 * s)} ${f3(4 * s)}h${f3(3 * s)}"/><text x="${f3(x + q.hd / 2 * 0.7 + 7.5 * s)}" y="${f3(Y(y) + q.hd / 2 * 0.7 + 4 * s + fs * 0.35)}" font-size="${f3(fs)}">Ø ${n1(q.hd, 1)}</text></g>`; });''',
    '''      { const M = qrMagnets(); if (M) { const [x, y] = M.pos[0], o = M.r * 0.7; g += `<g class="dim"><path d="M${f3(x + o)} ${f3(Y(y) + o)}l${f3(4 * s)} ${f3(4 * s)}h${f3(3 * s)}"/><text x="${f3(x + o + 7.5 * s)}" y="${f3(Y(y) + o + 4 * s + fs * 0.35)}" font-size="${f3(fs)}">Ø ${n1(M.d, 2)} × ${n1(M.z1 - M.z0, 1)} hinten</text></g>`; } }''')

# Infozeile
rep('''<span class="kchip">Modul <b>${n1(B.mod, 2)} mm</b></span></div>` +''',
    '''<span class="kchip">Modul <b>${n1(B.mod, 2)} mm</b></span>${(() => { const M = qrMagnets(); return M ? `<span class="kchip">Magnettasche <b>Ø ${n1(M.d, 2)} × ${n1(M.z1 - M.z0, 2)} mm</b></span>` : ""; })()}</div>` +''')

# Felder je nach Auswahl zeigen
rep('''    function qrForm() {''', '''    function magVis() { const f = $("#q_form"), on = +f.elements.mag.value > 0; ["mmode", "md", "mh", "me", "mlh"].forEach((k) => { f.elements[k].closest("label").hidden = !on; }); if (!(TS.qr.me > 0)) f.elements.me.value = ""; }
    function qrForm() {''')
rep('''TS.qr[el.name] = el.type === "checkbox" ? el.checked : el.type === "number" ? num(el.value) : el.value; saveTS(); qrRender(); });''',
    '''TS.qr[el.name] = el.type === "checkbox" ? el.checked : el.type === "number" ? num(el.value) : el.value; if (el.name === "mag") magVis(); saveTS(); qrRender(); });''')

rep("qrForm(); qrRender(); schForm(); schRender();", "qrForm(); magVis(); qrRender(); schForm(); schRender();")

open(path, "w", encoding="utf-8").write(s)
print("Magnet-Option eingefügt:", path)
