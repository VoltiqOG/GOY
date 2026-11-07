"""Typenschild: CE-Zeichen fest eingebaut (nachkonstruiert nach dem Raster aus VO (EG) 765/2008, Anhang II).

Aufruf: python patch_ce_fest.py <unverschluesselte index.html>
Konstruktion (Rastereinheit u, Höhe 10 u): C und E sind Halbkreis-Ringe (außen r = 5 u, Strich 1,5 u),
deren Enden 1 u über den Halbkreis hinaus waagerecht verlängert sind; die Kreise berühren sich, überlappen
nicht; der Mittelstrich des E endet 1 u vor dem Kreismittelpunkt. Breite 16 u → Seitenverhältnis 1,6 : 1.
Eine eigene (offizielle) CE-Datei kann weiterhin geladen werden und hat dann Vorrang.
"""
import sys

path = sys.argv[1]
s = open(path, encoding="utf-8").read()


def rep(a, b, n=1):
    global s
    if s.count(a) != n:
        raise SystemExit(f"Stelle {s.count(a)}× statt {n}× gefunden: " + a[:90])
    s = s.replace(a, b)


CE_D = "M6 0H5A5 5 0 0 0 5 10H6V8.5H5A3.5 3.5 0 0 1 5 1.5H6ZM16 0H15A5 5 0 0 0 15 10H16V8.5H15A3.5 3.5 0 0 1 15 1.5H16ZM10.75 4.25V5.75H14V4.25Z"

rep('''    function ceGroup(x, y, h) { // hochgeladene offizielle CE-Vorlage einpassen (Höhe h mm)
      const S = TS.sch; if (!S.ce) return { svg: `<g id="hinweis" fill="none" stroke="#1e6fd9" stroke-width="0.2" stroke-dasharray="1 0.6"><rect x="${f3(x)}" y="${f3(y)}" width="${f3(h * 1.4)}" height="${f3(h)}"/></g>`, w: h * 1.4 };
      try { const doc = new DOMParser().parseFromString(S.ce, "image/svg+xml"),''',
    f'''    // CE-Zeichen fest eingebaut – nach dem Raster aus VO (EG) 765/2008 Anhang II (Halbkreis-Ringe, Enden 1 Raster verlängert, Mittelstrich 1 Raster kürzer)
    const CE_STD = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 10"><path d="{CE_D}"/></svg>';
    const ceSrc = () => TS.sch.ce || CE_STD;
    function ceRatio() {{ try {{ const r = new DOMParser().parseFromString(ceSrc(), "image/svg+xml").documentElement, vb = (r.getAttribute("viewBox") || "").split(/[\\s,]+/).map(Number); if (vb.length === 4 && vb.every(isFinite) && vb[3] > 0) return vb[2] / vb[3]; }} catch (e) {{}} return 1.6; }}
    function ceGroup(x, y, h) {{ // CE-Zeichen einpassen (Höhe h mm): eigene Datei, sonst das eingebaute
      const S = TS.sch;
      try {{ const doc = new DOMParser().parseFromString(ceSrc(), "image/svg+xml"),''')
# Breite aus dem echten Seitenverhältnis
rep('''ceH = Math.max(5, Math.min(8, U * 0.085)), ceW = ceH * 1.4;''', '''ceH = Math.max(5, Math.min(8, U * 0.085)), ceW = ceH * ceRatio();''')
rep('''ce = ceGroup(W - mx - ceH * 1.4, m, ceH);''', '''ce = ceGroup(W - mx - ceH * ceRatio(), m, ceH);''')
# keine Platzhalter-Warnungen mehr
rep('''      if (!S.ce) msgs.push(["warn", "Keine CE-Vorlage geladen – blau gestrichelter Platzhalter. Offizielle CE-Datei der EU laden (Höhe ≥ 5 mm)."]);''',
    '''      if (ceH < 5) msgs.push(["err", "CE-Zeichen kleiner als 5 mm – Schild höher machen (VO (EG) 765/2008: mindestens 5 mm)."]);''')
rep('''      if (!S.ce) msgs.push(["warn", "Keine CE-Vorlage geladen – blau gestrichelter Platzhalter (wird nicht gelasert). Offizielle CE-Datei der EU laden (Proportionen nach VO (EG) 765/2008, Höhe ≥ 5 mm)."]);\n''', "")
# immer ausgeben, Farbe wie bisher
rep('''const ceS = prev || S.ce ? (S.ce && S.color ? ce.svg.replace('<g id="ce"', `<g id="ce" fill="${C("c_ce")}"`) : ce.svg) : "";''',
    '''const ceS = S.color ? ce.svg.replace('<g id="ce"', `<g id="ce" fill="${C("c_ce")}"`) : ce.svg;''')
rep('''...(S.ce ? ["c_ce"] : [])''', '''"c_ce"''')
rep('''ceSvg = prev || S.ce ? (S.ce && S.color ? ce.svg.replace(''', '''ceSvg = (S.color ? ce.svg.replace(''')
rep('''`<g id="ce" fill="${prev ? ceCol.view : ceCol.hex}" style="fill:${prev ? ceCol.view : ceCol.hex}"`) : ce.svg) : "";''',
    '''`<g id="ce" fill="${prev ? ceCol.view : ceCol.hex}" style="fill:${prev ? ceCol.view : ceCol.hex}"`) : ce.svg);''')
# Bedienung
rep('''<span id="s_ceinfo"></span><label class="kbtn sm">CE-Vorlage (SVG) laden<input type="file" id="s_cefile" accept=".svg,image/svg+xml" hidden></label><button type="button" class="kbtn sm" id="s_ceclear">entfernen</button><a href="https://single-market-economy.ec.europa.eu/single-market/ce-marking_en" target="_blank" rel="noopener">offizielle CE-Vorlage der EU ↗</a>''',
    '''<span id="s_ceinfo"></span><label class="kbtn sm ghost">Eigene CE-Datei laden (optional)<input type="file" id="s_cefile" accept=".svg,image/svg+xml" hidden></label><button type="button" class="kbtn sm ghost" id="s_ceclear">eingebautes CE nehmen</button><a href="https://single-market-economy.ec.europa.eu/single-market/ce-marking_en" target="_blank" rel="noopener">CE-Kennzeichnung bei der EU ↗</a>''')
rep('''$("#s_ceinfo").textContent = S.ce ? "CE-Vorlage geladen ✓" : "keine CE-Vorlage geladen";''',
    '''$("#s_ceinfo").textContent = S.ce ? "CE: eigene Datei ✓" : "CE-Zeichen ist eingebaut ✓"; $("#s_ceclear").hidden = !S.ce;''')
rep('''toast("CE-Vorlage gespeichert – wird ab jetzt immer verwendet.");''', '''toast("Eigene CE-Datei gespeichert – wird statt des eingebauten CE verwendet.");''')

open(path, "w", encoding="utf-8").write(s)
print("CE fest eingebaut:", path)
