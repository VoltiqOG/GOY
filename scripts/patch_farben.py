"""Typenschild-Generator: Farbmarkierung auf Edelstahl (Faserlaser) als eigene Farbebenen.

Aufruf: python patch_farben.py <unverschluesselte index.html>
Grundlage im Handbuch, Kapitel 10.11 „Farbgravur auf Edelstahl“:
jede Farbe eigene Ebene mit eigenen Parametern, Flächen dürfen sich nicht
überlappen, helle Farben (wenig Energie) zuerst, Werte nur aus dem Testraster,
F1 Ultra ist kein MOPA-Laser, keine Farbmarkierung für Typenschilder in
feuchter/staubiger Umgebung (Recyclinghalle, außen).
"""
import sys

path = sys.argv[1]
s = open(path, encoding="utf-8").read()


def rep(a, b):
    global s
    if a not in s:
        raise SystemExit("Stelle nicht gefunden: " + a[:90])
    s = s.replace(a, b, 1)


# ---------- Formular: Schalter und vier Farbwahlen
OPTS = "".join(f'<option value="{k}">{t}</option>' for k, t in [("schwarz", "Schwarz (Kontrast)"), ("gelb", "Gelb / Gold"), ("orange", "Orange / Bronze"), ("violett", "Violett"), ("blau", "Blau"), ("gruen", "Grün / Cyan")])
rep('''            <div class="wfull sce"><span id="s_ceinfo">''',
    '''            <label class="wchk wfull"><input name="color" type="checkbox"> Farbmarkierung (Edelstahl, Faserlaser, Kapitel 10.11)</label>
            <label class="scol">Kopf (Hersteller)<select name="c_kopf">''' + OPTS + '''</select></label>
            <label class="scol">Angaben<select name="c_werte">''' + OPTS + '''</select></label>
            <label class="scol">QR-Code<select name="c_qr">''' + OPTS + '''</select></label>
            <label class="scol">CE-Zeichen<select name="c_ce">''' + OPTS + '''</select></label>
            <div class="wfull sce"><span id="s_ceinfo">''')

# ---------- Standardwerte
rep('''qr: true, qrs: 16, outline: true, note: false, ce: "",''',
    '''qr: true, qrs: 16, outline: true, note: false, ce: "", color: false, c_kopf: "blau", c_werte: "schwarz", c_qr: "schwarz", c_ce: "schwarz",''')
rep('''["preset", "w", "h", "rad", "m", "holes", "hd", "he", "qrs"].forEach((k) => { if (f.elements[k]) f.elements[k].value = S[k]; }); ["qr", "outline", "note"].forEach''',
    '''["preset", "w", "h", "rad", "m", "holes", "hd", "he", "qrs", "c_kopf", "c_werte", "c_qr", "c_ce"].forEach((k) => { if (f.elements[k]) f.elements[k].value = S[k]; }); f.querySelectorAll(".scol").forEach((l) => { l.hidden = !S.color; }); ["qr", "outline", "note", "color"].forEach''')

# ---------- Farbtabelle: Reihenfolge = steigende Energie (helle Farben zuerst, Kapitel 10.11)
rep('''    function schBuild() {''',
    '''    // Farben der Ebenen: hex = Ebenenfarbe in der SVG (XCS trennt nach Farbe), view = ungefährer Farbeindruck für die Vorschau
    const SCOL = { gelb: { n: "Gelb / Gold", hex: "#ffcc00", view: "#c9a227" }, orange: { n: "Orange / Bronze", hex: "#ff8000", view: "#b8722c" }, violett: { n: "Violett", hex: "#8000ff", view: "#6a4c93" },
      blau: { n: "Blau", hex: "#0040ff", view: "#2f5aa8" }, gruen: { n: "Grün / Cyan", hex: "#00c0a0", view: "#2f8f86" }, schwarz: { n: "Schwarz (Kontrast)", hex: "#000000", view: "#1d1d1d" } };
    const SCOL_ORDER = ["gelb", "orange", "violett", "blau", "gruen", "schwarz"];
    function schBuild() {''')

# ---------- Gravur nach Elementen getrennt sammeln
rep('''      const S = TS.sch, P = SPRESET[S.preset] || SPRESET.mvo, V = S.vals, W = S.w, H = S.h, m = S.m, msgs = [], eng = [], cut = [];''',
    '''      const S = TS.sch, P = SPRESET[S.preset] || SPRESET.mvo, V = S.vals, W = S.w, H = S.h, m = S.m, msgs = [], cut = [];
      const part = { kopf: [], werte: [], qr: [] }; let eng = part.kopf;''')
rep('''y = Math.max(y, m + ceH) + 1.6; eng.push(`M${f3(mx)} ${f3(y)}H${f3(W - mx)}V${f3(y + 0.3)}H${f3(mx)}Z`); y += 1.8;''',
    '''y = Math.max(y, m + ceH) + 1.6; eng.push(`M${f3(mx)} ${f3(y)}H${f3(W - mx)}V${f3(y + 0.3)}H${f3(mx)}Z`); y += 1.8; eng = part.werte;''')
rep('''      if (qrOn) { const q = qrPath(V.link, W - mx - qs, Math.max(y, bottom - qs), qs); eng.push(q.d);''',
    '''      if (qrOn) { const q = qrPath(V.link, W - mx - qs, Math.max(y, bottom - qs), qs); part.qr.push(q.d);''')

# ---------- Hinweise zur Farbmarkierung (alles aus Kapitel 10.11)
rep('''      if (!msgs.some((x) => x[0] === "err")) msgs.unshift(["ok", "Alle Pflichtangaben vorhanden, Text passt."]);''',
    '''      const colOf = (k) => (S.color ? S[k] : "schwarz") || "schwarz";
      if (S.color) {
        msgs.push(["warn", `<b>Farbmarkierung und Typenschild:</b> Laut Kapitel 10.11 leidet beim Farbmarkieren die Passivschicht des Edelstahls. Für Typenschilder an Ballenpressen, Förderern usw. in feuchter, staubiger oder aggressiver Umgebung (Recyclinghalle, außen) <b>keine Farbmarkierung</b> – dort die schwarze Markierung nehmen. Farben nur für Schilder im Innenbereich, Muster oder Schaustücke.`]);
        const used = [...new Set(["c_kopf", "c_werte", ...(qrOn ? ["c_qr"] : []), ...(S.ce ? ["c_ce"] : [])].map(colOf))];
        msgs.push(["", `Die SVG enthält je Farbe eine eigene Ebene (${SCOL_ORDER.filter((c) => used.includes(c)).map((c) => SCOL[c].n).join(", ")}), in der Reihenfolge helle Farbe zuerst. In XCS jeder Ebene die Werte aus <b>eurer Farbtabelle (Kapitel 10.11)</b> zuweisen: Faser, Gravieren (Füllung), Leistung, Geschwindigkeit, Linien/cm, Frequenz. Ohne Testraster auf derselben Blechcharge keine Farben zusagen – der F1 Ultra ist kein MOPA-Laser, die Farben sind matter und weniger zahlreich.`]);
        if (colOf("c_qr") !== "schwarz") msgs.push(["warn", "QR-Code farbig: Farbmarkierungen haben wenig Kontrast, Scanner lesen sie oft schlecht. Für den QR-Code Schwarz empfohlen."]);
        if (W > 60 || H > 60) msgs.push(["", `Schild ${n1(W)} × ${n1(H)} mm: Farbflächen möglichst nah an die Mitte des Arbeitsfelds legen (zum Rand kippt die Farbe). Bei dünnem Blech Farben als einzelne Jobs starten und dazwischen abkühlen lassen, Blech auf eine Metallplatte legen.`]);
      } else msgs.push(["", "Farben: Farbmarkierung einschalten, um Kopf, Angaben, QR-Code und CE-Zeichen in Anlauffarben zu lasern (nur Edelstahl mit dem Faserlaser). Andere Wege zu Farbe: farbig eloxiertes Aluminium (der Laser legt hell frei) oder lackiertes Blech, das der Laser freilegt – beides vorher testen."]);
      if (!msgs.some((x) => x[0] === "err")) msgs.unshift(["ok", "Alle Pflichtangaben vorhanden, Text passt."]);''')

# ---------- SVG: je Farbe eine Ebene, Vorschau im Farbeindruck
rep('''        `<g id="gravieren" fill="#000" fill-rule="nonzero"><path d="${eng.join("")}"/></g>${prev || S.ce ? ce.svg : ""}<g id="schneiden"''',
    '''        (() => { const byCol = {}; [["c_kopf", part.kopf], ["c_werte", part.werte], ["c_qr", part.qr]].forEach(([k, d]) => { if (d.length) (byCol[colOf(k)] = byCol[colOf(k)] || []).push(...d); });
          const ceCol = SCOL[colOf("c_ce")], ceSvg = prev || S.ce ? (S.ce && S.color ? ce.svg.replace(/<g id="ce"/, `<g id="ce" fill="${prev ? ceCol.view : ceCol.hex}" style="fill:${prev ? ceCol.view : ceCol.hex}"`) : ce.svg) : "";
          if (!S.color) return `<g id="gravieren" fill="#000" fill-rule="nonzero"><path d="${Object.values(byCol).flat().join("")}"/></g>${ceSvg}`;
          return SCOL_ORDER.filter((c) => byCol[c]).map((c) => `<g id="farbe_${c}" fill="${prev ? SCOL[c].view : SCOL[c].hex}" fill-rule="nonzero"><path d="${byCol[c].join("")}"/></g>`).join("") + ceSvg; })() + `<g id="schneiden"''')

# Hinweistext unter der Vorschau
rep('''`<p class="kmsg">Ebenen: <b>gravieren</b> (schwarz) · <b>schneiden</b> (rot, 0,1 mm) – in XCS je Farbe die Bearbeitung zuweisen.''',
    '''(TS.sch.color ? `<p class="kmsg">Ebenen: je Farbe eine Ebene (Vorschau zeigt den ungefähren Farbeindruck) · <b>schneiden</b> (rot, 0,1 mm).` : `<p class="kmsg">Ebenen: <b>gravieren</b> (schwarz) · <b>schneiden</b> (rot, 0,1 mm) – in XCS je Farbe die Bearbeitung zuweisen.`) + `''')

# Felder ein-/ausblenden beim Umschalten
rep('''      if (el.name === "preset") schForm(); saveTS(); schRender(); });''',
    '''      if (el.name === "preset" || el.name === "color") schForm(); saveTS(); schRender(); });''')

open(path, "w", encoding="utf-8").write(s)
print("Farbmarkierung eingefügt:", path)
