"""QR-Werkzeug: Modulform und Positionsmarken getrennt wählbar, Punktgröße einstellbar.

Aufruf: python patch_qr_formen.py <unverschluesselte index.html>
- Module: Quadrate oder Punkte; Punktgröße 60–95 % des Moduls (Standard 90 %, vorher fest 80 %)
- Positionsmarken (die drei großen Ecken): Quadrat oder Kreis – unabhängig von den Modulen
- Warnung/Fehler nach Punkt-Ø gegenüber der Düse (0,4 mm): < 1,0 mm Fehler, < 1,2 mm Warnung
"""
import sys

path = sys.argv[1]
s = open(path, encoding="utf-8").read()


def rep(a, b, n=1):
    global s
    if s.count(a) != n:
        raise SystemExit(f"Stelle {s.count(a)}× statt {n}× gefunden: " + a[:90])
    s = s.replace(a, b)


rep('''            <label>Aussehen<select name="style"><option value="sq">Quadrate (klassisch)</option><option value="dot">Punkte, runde Ecken</option></select></label>''',
    '''            <label>Module<select name="style"><option value="sq">Quadrate (klassisch)</option><option value="dot">Punkte</option></select></label>
            <label>Positionsmarken (Ecken)<select name="fst"><option value="sq">Quadrat</option><option value="round">Kreis</option></select></label>
            <label class="qdotl">Punktgröße <output id="q_dszv"></output><input name="dsz" type="range" min="60" max="95" step="5"></label>''')

rep('''    const QDOT = 0.40; // Punktradius in Modulen (Ø 0,8 Modul, Spalt 0,2 Modul)
    function qrDotRegions(qr, invert = false, quiet = 0) {''',
    '''    const qDotR = () => Math.max(0.3, Math.min(0.475, (+TS.qr.dsz || 90) / 200)); // Punktradius in Modulen (90 % → Ø 0,9 Modul)
    const sqL = (cx, cy, h) => [[cx - h, cy - h], [cx + h, cy - h], [cx + h, cy + h], [cx - h, cy + h]]; // Quadrat gegen den Uhrzeigersinn (y nach oben)
    // Module und Positionsmarken frei kombinierbar: Quadrat/Punkt × Quadrat/Kreis
    function qrStyledRegions(qr, invert = false, quiet = 0) {
      const q = TS.qr, dot = q.style === "dot", rnd = (q.fst || (dot ? "round" : "sq")) === "round";
      if (!dot && !rnd) return qrRegions(qr, invert, quiet);
      const n = qr.size, Nq = n + 2 * quiet, R = qDotR(), isF = (c, r) => (c < 7 && r < 7) || (c >= n - 7 && r < 7) || (c < 7 && r >= n - 7);
      const finders = [[0, 0], [n - 7, 0], [0, n - 7]].map(([c, r]) => [quiet + c + 3.5, Nq - quiet - r - 3.5]), C = (cx, cy, r) => ({ cx, cy, r });
      const noF = { size: n, getModule: (c, r) => !isF(c, r) && qr.getModule(c, r) }, out = [];
      if (!invert) {
        if (dot) { for (let r = 0; r < n; r++) for (let c = 0; c < n; c++) if (noF.getModule(c, r)) { const x = quiet + c + 0.5, y = Nq - quiet - r - 0.5; out.push({ outer: ccw(x, y, R, 16), holes: [], oc: C(x, y, R), hc: [] }); } }
        else qrRegions(noF, false, quiet).regions.forEach((rg) => out.push(rg));
        for (const [x, y] of finders) {
          if (rnd) { out.push({ outer: ccw(x, y, 3.5, 64), holes: [ccw(x, y, 2.5, 56).reverse()], oc: C(x, y, 3.5), hc: [C(x, y, 2.5)] }); out.push({ outer: ccw(x, y, 1.5, 40), holes: [], oc: C(x, y, 1.5), hc: [] }); }
          else { out.push({ outer: sqL(x, y, 3.5), holes: [sqL(x, y, 2.5).reverse()] }); out.push({ outer: sqL(x, y, 1.5), holes: [] }); }
        }
        return { regions: out, N: Nq };
      }
      // invertiert (nur SVG, gerade/ungerade-Füllung): Fläche minus Module und Marken
      out.push({ outer: [[0, 0], [Nq, 0], [Nq, Nq], [0, Nq]], holes: [] });
      if (dot) { for (let r = 0; r < n; r++) for (let c = 0; c < n; c++) if (noF.getModule(c, r)) out.push({ outer: ccw(quiet + c + 0.5, Nq - quiet - r - 0.5, R, 16), holes: [] }); }
      else qrRegions(noF, false, quiet).regions.forEach((rg) => out.push(rg));
      for (const [x, y] of finders) for (const rr of [3.5, 2.5, 1.5]) out.push({ outer: rnd ? ccw(x, y, rr, 56) : sqL(x, y, rr), holes: [] });
      return { regions: out, N: Nq };
    }
    function qrDotRegions(qr, invert = false, quiet = 0) {''')
rep('''    const qrRegs = (qr, invert, quiet) => (TS.qr.style === "dot" ? qrDotRegions : qrRegions)(qr, invert, quiet);''',
    '''    const qrRegs = (qr, invert, quiet) => qrStyledRegions(qr, invert, quiet);''')
# alte Konstante noch im alten Punkt-Code
rep('''out.push({ outer: ccw(x, y, QDOT, 14), holes: [], oc: C(x, y, QDOT), hc: [] }); }''', '''out.push({ outer: ccw(x, y, qDotR(), 14), holes: [], oc: C(x, y, qDotR()), hc: [] }); }''')
rep('''out.push({ outer: ccw(quiet + c + 0.5, Nq - quiet - r - 0.5, QDOT, 14), holes: [] });''', '''out.push({ outer: ccw(quiet + c + 0.5, Nq - quiet - r - 0.5, qDotR(), 14), holes: [] });''')
# Standardwerte: bestehende Nutzer mit Punkten behalten runde Marken
rep('''inv: false, style: "sq", mon: true,''', '''inv: false, style: "sq", fst: "sq", dsz: 90, mon: true,''')
rep('''    ["hole", "mag", "mmode", "md", "mh", "me", "mlh"].forEach((k) => delete TS.qr[k]);''',
    '''    ["hole", "mag", "mmode", "md", "mh", "me", "mlh"].forEach((k) => delete TS.qr[k]);
    if (!TS.qr._fst) { TS.qr._fst = 1; TS.qr.fst = TS.qr.style === "dot" ? "round" : "sq"; if (!(+TS.qr.dsz)) TS.qr.dsz = 90; }''')
# Meldungen zum Punkt-Ø
rep('''      if (q.style === "dot") { const dd = 2 * QDOT * mod, gap = (1 - 2 * QDOT) * mod;
        if (dd < 1.2) msgs.push(["warn", `Punkt-Stil: Punkte nur Ø ${n1(dd, 2)} mm – wird beim Druck eckig oder fließt zusammen. Für Punkte Modul ≥ 1,5 mm (Code größer, kürzerer Link) oder Stil „Quadrate“.`]);
        else msgs.push(["ok", `Punkt-Stil: Punkte Ø ${n1(dd, 2)} mm, Spalt ${n1(gap, 2)} mm${gap < 0.4 ? " – schmaler als eine Linie, Punkte können sich berühren (scannt trotzdem)" : ""}.`]); }''',
    '''      if (q.style === "dot") { const dd = 2 * qDotR() * mod, gap = (1 - 2 * qDotR()) * mod, need = Math.min(95, Math.ceil(120 / mod / 5) * 5);
        if (dd < 1.0) msgs.push(["err", `Punkte nur Ø ${n1(dd, 2)} mm – das sind keine 3 Linien der 0,4-mm-Düse, die Punkte werden klumpig oder fehlen. ${need <= 95 && need > (+q.dsz || 90) ? `Punktgröße auf ${need} % stellen, ` : ""}Code größer, kürzerer Link (Fehlerkorrektur L) oder Module „Quadrate“.`]);
        else if (dd < 1.2) msgs.push(["warn", `Punkte Ø ${n1(dd, 2)} mm – an der Grenze für die 0,4-mm-Düse. Sicherer ab 1,2 mm: ${need <= 95 && need > (+q.dsz || 90) ? `Punktgröße ${need} %, ` : ""}Code größer oder Module „Quadrate“.`]);
        else msgs.push(["ok", `Punkte Ø ${n1(dd, 2)} mm, Spalt ${n1(gap, 2)} mm${gap < 0.4 ? " – schmaler als eine Linie, Punkte können zusammenlaufen (scannt meist trotzdem)" : ""}.`]); }''')
rep('''      if (q.qh < 0.4) msgs.push(["warn", "Code-Höhe unter 0,4 mm''', '''      if ((q.fst || "sq") === "round") msgs.push(["warn", "Runde Positionsmarken: Die meisten Handy-Kameras lesen sie, einfache Scanner-Apps und Industrie-Scanner oft nicht (im Test hat die OpenCV-Erkennung runde Marken nicht gefunden). Probedruck mit euren Geräten scannen – für sicheres Lesen „Quadrat“."]);
      if (q.qh < 0.4) msgs.push(["warn", "Code-Höhe unter 0,4 mm''')
rep('''Punkt Ø ${n1(2 * QDOT * B.mod, 2)} mm''', '''Punkt Ø ${n1(2 * qDotR() * B.mod, 2)} mm''')
# Punktgröße nur bei Punkten zeigen, Wert anzeigen
rep('''    function qrForm() { const f = $("#q_form"); Object.entries(TS.qr).forEach(([k, v]) => { const el = f.elements[k]; if (!el) return; if (el.type === "checkbox") el.checked = !!v; else el.value = v; }); }''',
    '''    function qrForm() { const f = $("#q_form"); Object.entries(TS.qr).forEach(([k, v]) => { const el = f.elements[k]; if (!el) return; if (el.type === "checkbox") el.checked = !!v; else el.value = v; }); qrDotVis(); }
    function qrDotVis() { const f = $("#q_form"); f.querySelector(".qdotl").hidden = TS.qr.style !== "dot"; $("#q_dszv").textContent = (+TS.qr.dsz || 90) + " %"; }''')
rep('''if (el.name === "mon") magVis(); saveTS(); qrRender(); });''', '''if (el.name === "mon") magVis(); if (el.name === "style" || el.name === "dsz") qrDotVis(); saveTS(); qrRender(); });''')

open(path, "w", encoding="utf-8").write(s)
print("QR: Module/Positionsmarken/Punktgröße:", path)
