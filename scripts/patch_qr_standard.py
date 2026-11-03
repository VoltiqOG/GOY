"""QR-Werkzeug: Standardmaße wie unsere Platte (50 × 50 × 3 mm, Code 42,5 mm, R4, Fehlerkorrektur L, 4 Magnettaschen Ø 4,2 × 2,1 mm, Mittenabstand 37,5 × 37,5 mm)
und Knopf „Standardmaße“ zum Zurücksetzen (Link und Text bleiben). Aufruf über scripts/aktualisieren.py"""
import sys
p = sys.argv[1]; s = open(p, encoding="utf-8").read()
if "QRSTD" in s: sys.exit("schon eingespielt")
def R(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:90], s.count(a)); s = s.replace(a, b)
R('''    let TS = { qr: { url: "https://", ecc: "Q", pw: 60, ph: 70, pt: 2, size: 46, qh: 1, quiet: 2, rad: 3, hole: 0, hd: 4.2, label: "", lh: 4, inv: false, style: "sq", mon: false, mps: 8.2, mpd: 2.2, mpo: 10, mpx: 16, mpy: 21, mdx: 32, mdy: 42 }, sch: {} };''',
  '''    const QRSTD = { ecc: "L", pw: 50, ph: 50, pt: 3, size: 42.5, qh: 1, quiet: 2, rad: 4, hole: 0, hd: 4.2, lh: 4, inv: false, style: "sq", mon: true, mps: 4.2, mpd: 2.1, mpo: 4.15, mpx: 18.75, mpy: 18.75, mdx: 37.5, mdy: 37.5, _mpm: 1, _mpm2: 1 }; // Standard = unsere QR-Platte
    let TS = { qr: { url: "https://", label: "", ...QRSTD }, sch: {} };''')
R('''<p class="wfull kmsg mhint">''', '''<p class="wfull krow" style="margin:0"><button type="button" class="kbtn sm" id="q_std">Standardmaße (50 × 50, Magnete 37,5 × 37,5)</button></p>
            <p class="wfull kmsg mhint">''')
R('''    function qrForm() {''', '''    document.addEventListener("click", (e) => { if (!e.target.closest || !e.target.closest("#q_std")) return; Object.assign(TS.qr, QRSTD); saveTS(); qrForm(); if (typeof magVis === "function") magVis(); qrRender(); toast("Standardmaße eingestellt – Link und Text bleiben."); });
    function qrForm() {''')
R('''      if (dCode < 0) msgs.push(["err", `<b>Magnettasche ragt in den QR-Code</b> (${n1(-dCode, 2)} mm Überdeckung). Platte größer, Code kleiner, Abstand zur Außenkante kleiner oder kleinere Magnete.`]);''',
  '''      if (dCode < 0) msgs.push(["warn", `<b>Magnettaschen liegen unter dem QR-Code</b> (${n1(-dCode, 2)} mm Überdeckung). Bei hellem Filament kann der Magnet durch den Boden scheinen und den Kontrast stören – Scan am ersten Druck testen; sicherer mit dunklem Code auf hellem, blickdichtem Filament, Fehlerkorrektur M/Q oder Mittenabstand größer.`]);''')
open(p, "w", encoding="utf-8").write(s); print("QR-Standard:", p)
