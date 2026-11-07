"""Materialien: neue Filamente, Hexagon-Grafik der Eigenschaften, Abschnitt 6.8 Glasfaser vs. Kohlefaser.

Aufruf: python patch_materialien.py <unverschluesselte index.html>
Neue Materialien (Daten nach Bambu-Lab-Angaben, Händlerseiten): PLA Tough+ (Datenblatt PLA Tough: 190–230 °C,
Bett 35–45 °C, HDT 55 °C, +20 % Zähigkeit), PA6-GF (260–290 °C, Bett 80–100 °C, Trocknen 80 °C 8–12 h, HDT 182 °C,
AMS ja / AMS lite nein, gehärtete Düse), PC FR (260–280 °C, Bett 90–110 °C, HDT 113 °C, UL 94 V-0, AMS ja / lite nein),
TPU for AMS (68D, 220–240 °C, Bett 30–35 °C mit Kleber, 70 °C 8 h, AMS und AMS lite), Support for ABS.
Hexagon: 6 Achsen wie die Vergleichstabelle in 6.1 (Druckbarkeit, Festigkeit, Zähigkeit, Wärme, UV/außen, Preis);
Preis-Achse aus der eigenen Preisliste (€/kg), die übrigen als Einschätzung 1–5.
GF/CF: 3DXTech „Glass Fiber vs. Carbon Fiber Filled Filaments“ (GF 30–50 % günstiger, CF steifer, GF zäher,
ABS-CF ca. 0,1 % Schwund gegenüber ca. 0,5 % ABS, CF nur schwarz).
"""
import sys

path = sys.argv[1]
s = open(path, encoding="utf-8").read()


def rep(a, b, n=1):
    global s
    if s.count(a) != n:
        raise SystemExit(f"Stelle {s.count(a)}× statt {n}× gefunden: " + a[:90])
    s = s.replace(a, b)


# ---------- Stammdaten
rep('''      "PLA Metall": ["Standard",''', '''      "PLA Tough+": ["Standard", "190–230", "35–45", "kalt, Tür offen", "55 °C, 8 h", "★★ (HDT ca. 55 °C)", "ja", "zähere PLA-Teile: Clips, Halter, Lehren bei Raumtemperatur – bricht weniger schnell als PLA Basic", ALLY],
      "PLA Metall": ["Standard",''')
rep('''      "PLA-CF": ["Faserverstärkt",''', '''      "PC FR": ["Technisch", "260–280", "90–110", "heiß, Tür zu", "80 °C, 8 h (Pflicht)", "113 °C (HDT) · UL 94 V-0", "ja (nicht AMS lite)", "flammhemmende Gehäuse, Abdeckungen und Halter nahe Elektrik und Kabeln", "y y c3 n7 n7"],
      "PLA-CF": ["Faserverstärkt",''')
rep('''      "PET-CF": ["Faserverstärkt",''', '''      "PA6-GF": ["Faserverstärkt", "260–290", "80–100", "warm, Tür zu", "80 °C, 8–12 h (Pflicht)", "182 °C (HDT)", "ja (nicht AMS lite)", "zähe, steife Teile mit Stößen: Halter, Abdeckungen, Greifer – zäher und günstiger als PA6-CF, farbig, isoliert elektrisch", "y y1 c23 n7 n7"],
      "PET-CF": ["Faserverstärkt",''')
rep('''      "Support for PLA": ["Stützmaterial",''', '''      "TPU for AMS": ["Flexibel", "220–240", "30–35 (mit Kleber)", "kalt", "70 °C, 8 h", "★", "ja (auch AMS lite)", "festeres TPU (68D), läuft durchs AMS: Rollen, Puffer, Gelenke, Schutzkappen – auch als weiche Komponente im Mehrfarbdruck", ALLY],
      "Support for PLA": ["Stützmaterial",''')
rep('''      "PVA": ["Stützmaterial",''', '''      "Support for ABS": ["Stützmaterial", "nach Etikett", "wie Hauptmaterial", "warm, Tür zu", "trocken lagern", "–", "ja", "leicht lösbare Kontaktschicht zwischen Stütze und ABS/ASA-Teil", "y y y n5 n5"],
      "PVA": ["Stützmaterial",''')
rep('''["PPS-CF", 133.90, 0.75, 0.08, "Händler"]]''',
    '''["PPS-CF", 133.90, 0.75, 0.08, "Händler"],
        ["PLA Tough+", 25.99, 1, 0, "Richtwert"], ["PC FR", 34.99, 1, 0, "Richtwert"], ["PA6-GF", 54.99, 1, 0.08, "Richtwert"], ["TPU for AMS", 37.99, 1, 0, "Richtwert"], ["Support for ABS", 25.99, 0.5, 0, "Richtwert"]]''')

# ---------- Hexagon-Grafik
rep('''    const MGRP = ["Standard", "Technisch", "Faserverstärkt", "Flexibel", "Stützmaterial"];''',
    '''    const MGRP = ["Standard", "Technisch", "Faserverstärkt", "Flexibel", "Stützmaterial"];
    // Eigenschaften 1–5 (Einschätzung im Vergleich untereinander): Druckbarkeit, Festigkeit, Zähigkeit, Wärme, UV/außen – Preis kommt aus der Preisliste
    const MRAD_AX = ["Druckbarkeit", "Festigkeit", "Zähigkeit", "Wärme", "UV / außen", "Preis"];
    const MRAD = { "PLA Basic": [5, 3, 2, 1, 1], "PLA Matt": [5, 3, 2, 1, 1], "PLA Silk+": [5, 2, 2, 1, 1], "PLA Metall": [4, 2, 2, 1, 1], "PLA Tough+": [5, 3, 3, 1, 1], "PLA-CF": [4, 3, 2, 1, 1],
      "PETG HF": [4, 3, 4, 2, 3], "PETG Translucent": [4, 3, 4, 2, 3], "PETG-CF": [4, 4, 3, 2, 3], "ABS": [3, 3, 4, 4, 2], "ASA": [3, 3, 4, 4, 5], "ABS-GF": [3, 4, 3, 4, 2],
      "PC": [1, 4, 5, 5, 3], "PC FR": [1, 4, 4, 5, 3], "PAHT-CF": [2, 5, 4, 5, 3], "PA6-CF": [2, 5, 4, 5, 3], "PA6-GF": [2, 4, 5, 5, 3], "PET-CF": [2, 5, 3, 5, 4], "PPA-CF": [1, 5, 3, 5, 4], "PPS-CF": [1, 5, 2, 5, 5],
      "TPU 95A HF": [2, 2, 5, 2, 3], "TPU 85A/90A": [1, 1, 5, 2, 3], "TPU for AMS": [3, 2, 5, 2, 3] };
    const priceScore = (kg) => (kg <= 0 ? 3 : kg <= 28 ? 5 : kg <= 40 ? 4 : kg <= 60 ? 3 : kg <= 100 ? 2 : 1);
    function radarSvg(name, kg, refName, refKg) {
      const v = MRAD[name]; if (!v) return "";
      const vals = [...v, priceScore(kg)], ref = refName && MRAD[refName] && refName !== name ? [...MRAD[refName], priceScore(refKg)] : null;
      const R = 86, cx = 150, cy = 118, pt = (i, r) => { const a = (-90 + i * 60) * Math.PI / 180; return [cx + r * Math.cos(a), cy + r * Math.sin(a)]; }, f = (x) => x.toFixed(1);
      const poly = (arr) => arr.map((x, i) => pt(i, R * x / 5).map(f).join(",")).join(" ");
      let g = ""; for (let k = 1; k <= 5; k++) g += `<polygon points="${[0, 1, 2, 3, 4, 5].map((i) => pt(i, R * k / 5).map(f).join(",")).join(" ")}" class="rg${k === 5 ? " o" : ""}"/>`;
      g += [0, 1, 2, 3, 4, 5].map((i) => { const [x, y] = pt(i, R); return `<line x1="${cx}" y1="${cy}" x2="${f(x)}" y2="${f(y)}" class="ra"/>`; }).join("");
      const lab = MRAD_AX.map((t, i) => { const [x, y] = pt(i, R + 16), an = Math.abs(x - cx) < 4 ? "middle" : x > cx ? "start" : "end"; return `<text x="${f(x)}" y="${f(y + (y < cy - 10 ? -2 : y > cy + 10 ? 10 : 4))}" text-anchor="${an}" class="rl">${t} <tspan class="rv">${vals[i]}</tspan></text>`; }).join("");
      return `<svg class="mradar" viewBox="-38 0 376 240" role="img" aria-label="Eigenschaften ${esc(name)}: ${MRAD_AX.map((t, i) => t + " " + vals[i]).join(", ")} von 5">${g}${ref ? `<polygon points="${poly(ref)}" class="rref"/>` : ""}<polygon points="${poly(vals)}" class="rp"/>${vals.map((x, i) => { const [px, py] = pt(i, R * x / 5); return `<circle cx="${f(px)}" cy="${f(py)}" r="3" class="rd"/>`; }).join("")}${lab}</svg>`;
    }
    let mOpen = new Set();''')

rep('''        return `<article class="mcard g-${MGRP.indexOf(m[0])}"><header><h4>${esc(r[0])}</h4><span class="mgrp">${m[0]}</span></header>''',
    '''        const open = mOpen.has(r[0]), hasR = !!MRAD[r[0]], refRow = st.fil.find((x) => x[0] === "PLA Basic"), refKg = refRow && num(refRow[2]) > 0 ? num(refRow[1]) / num(refRow[2]) : 0;
        return `<article class="mcard g-${MGRP.indexOf(m[0])}${open ? " open" : ""}" data-m="${esc(r[0])}"><header><h4>${esc(r[0])}</h4><span class="mgrp">${m[0]}</span></header>
          ${hasR ? `<button type="button" class="mhex" data-hex="${esc(r[0])}" aria-expanded="${open}">${open ? "Eigenschaften ausblenden" : "⬡ Eigenschaften"}</button>` : ""}
          ${open && hasR ? `<div class="mradw">${radarSvg(r[0], kg, "PLA Basic", refKg)}<p class="mradn">${r[0] === "PLA Basic" ? "" : '<span class="rkey ref"></span> PLA Basic zum Vergleich · '}1 = schwach, 5 = sehr gut · Preis aus deiner Preisliste (5 = günstig) · Einschätzung im Vergleich der Materialien untereinander, Werte im Datenblatt haben Vorrang</p></div>` : ""}''')
rep('''        const n = e.target.closest("[data-note]"); if (n) { toast(n.dataset.note); return; }
        const u = e.target.closest("[data-use]"); if (!u) return;''',
    '''        const n = e.target.closest("[data-note]"); if (n) { toast(n.dataset.note); return; }
        const u = e.target.closest("[data-use]");
        if (!u) { const c = e.target.closest(".mcard[data-m]"); if (c && !e.target.closest("a, input, select")) { const k = c.dataset.m; if (MRAD[k]) { mOpen.has(k) ? mOpen.delete(k) : mOpen.add(k); renderMaterials(); } } return; }''')
rep('''.mcard header{display:flex;justify-content:space-between;align-items:center;gap:var(--space-xs)}''',
    '''.mcard header{display:flex;justify-content:space-between;align-items:center;gap:var(--space-xs)}
.mcard[data-m]{cursor:pointer}.mcard[data-m]:hover{box-shadow:inset 0 0 0 1px var(--fg3)}
.mhex{align-self:flex-start;border:0;background:none;padding:2px 0;font:600 13px/1.3 var(--font-body);color:var(--color-accent,var(--fg));cursor:pointer;text-decoration:underline;text-underline-offset:3px}
.mradw{margin:2px 0 4px}.mradar{display:block;width:100%;max-width:400px;height:auto;margin:0 auto}
.mradar .rg{fill:none;stroke:var(--line)}.mradar .rg.o{stroke:var(--fg3)}.mradar .ra{stroke:var(--line)}
.mradar .rp{fill:color-mix(in srgb,var(--druck) 28%,transparent);stroke:var(--druck);stroke-width:2;stroke-linejoin:round}
.mcard.g-1 .mradar .rp{fill:color-mix(in srgb,var(--laser) 28%,transparent);stroke:var(--laser)}.mcard.g-2 .mradar .rp{fill:color-mix(in srgb,var(--fg) 18%,transparent);stroke:var(--fg)}.mcard.g-3 .mradar .rp{fill:color-mix(in srgb,var(--konstr) 28%,transparent);stroke:var(--konstr)}
.mradar .rd{fill:var(--card);stroke:var(--fg);stroke-width:1.5}.mradar .rref{fill:none;stroke:var(--fg3);stroke-width:1.5;stroke-dasharray:4 3}
.mradar .rl{font:12px var(--font-body);fill:var(--fg2)}.mradar .rv{font-weight:700;fill:var(--fg)}
.mradn{font-size:12.5px;color:var(--fg3);margin:4px 0 0;text-align:center}.rkey.ref{display:inline-block;width:18px;border-top:2px dashed var(--fg3);vertical-align:middle}''')

# ---------- Handbuch: Vergleichstabelle 6.1 und neuer Abschnitt 6.8
def dots(v):
    c = "r" if v <= 2 else "y" if v == 3 else "g"
    return f'<span class="dots {c}" role="img" aria-label="{v} von 5"><b>{v}</b>' + "".join("<i class=on></i>" if k < v else "<i></i>" for k in range(5)) + "</span>"


def row(name, vals):
    labs = ["Druckbarkeit", "Festigkeit", "Zähigkeit", "Wärme", "UV / außen", "Preis"]
    return f'<tr><td data-label="Material"><strong>{name}</strong></td>' + "".join(f'<td data-label="{l}">{dots(v)}</td>' for l, v in zip(labs, vals)) + "</tr>"


rep('<tr><td data-label="Material"><strong>PETG</strong></td>', row("PLA Tough+", [5, 3, 3, 1, 1, 5]) + '<tr><td data-label="Material"><strong>PETG</strong></td>')
rep('<tr><td data-label="Material"><strong>PC</strong></td>', row("PA-GF", [2, 4, 5, 5, 3, 3]) + '<tr><td data-label="Material"><strong>PC</strong></td>')

ID = "6-8-glasfaser-gf-oder-kohlefaser-cf"
th = lambda h: "".join(f"<th>{x}</th>" for x in h)


def tab(head, rows):
    return f'<div class="tw"><table class=""><thead><tr>{th(head)}</tr></thead><tbody>' + "".join("<tr>" + "".join(f'<td data-label="{head[i]}"><span class="tc">{c}</span></td>' for i, c in enumerate(r)) + "</tr>" for r in rows) + "</tbody></table></div>"


gfcf = tab(["Eigenschaft", "CF – Kohlefaser", "GF – Glasfaser"], [
    ["<strong>Steifigkeit</strong>", "am höchsten – biegt sich am wenigsten", "hoch, aber deutlich weicher als CF (etwa 40–60 % der CF-Steifigkeit bei gleichem Grundmaterial)"],
    ["<strong>Zähigkeit / Schlag</strong>", "spröder – bricht eher schlagartig", "<strong>zäher</strong> – verträgt Stöße und Schläge besser"],
    ["<strong>Maßhaltigkeit / Verzug</strong>", "sehr gut (z. B. ABS-CF ca. 0,1 % Schwund statt ca. 0,5 % bei ABS)", "sehr gut, knapp hinter CF"],
    ["<strong>Gewicht</strong>", "leichter", "etwas schwerer"],
    ["<strong>Farbe / Oberfläche</strong>", "nur schwarz/dunkelgrau, edel matt", "viele Farben möglich, matt, teils leicht glitzernd"],
    ["<strong>Elektrisch</strong>", "Kohlefaser leitet – je nach Anteil leicht leitfähig: nicht als Isolator einplanen, nicht an Antennen/Funk", "Glas isoliert – geeignet für Gehäuse und Halter an Elektrik"],
    ["<strong>Düse</strong>", "abrasiv – gehärtete Düse Pflicht", "ebenfalls abrasiv – gehärtete Düse Pflicht"],
    ["<strong>Preis</strong>", "teurer", "meist 30–50 % günstiger bei gleichem Grundmaterial"],
    ["<strong>Wann?</strong>", "steife, leichte, maßhaltige Teile: Vorrichtungen, Lehren, Rahmen, Halter ohne Schläge", "Teile mit Stößen, Gehäuse, farbige Teile, Teile an Elektrik"],
])
sec = f'''<h2 id="{ID}"><span class="hn">6.8</span> Glasfaser (GF) oder Kohlefaser (CF) – der Unterschied</h2>
<p>Bei <strong>faserverstärkten Filamenten</strong> sind kurze, gehackte Fasern (meist 10–30 %) in einen normalen Kunststoff gemischt – PLA, PETG, ABS, PA oder PET. Das Kürzel sagt, welche Faser drin ist: <strong>CF</strong> = Kohlefaser (carbon fiber), <strong>GF</strong> = Glasfaser (glass fiber). Das Grundmaterial bestimmt Temperatur, Chemie- und UV-Beständigkeit, die Faser vor allem <strong>Steifigkeit, Zähigkeit, Verzug und Preis</strong>.</p>
{gfcf}
<ul class="bul"><li><strong>Gemeinsam:</strong> beide schrumpfen weniger als das reine Material, drucken meist 10–20 °C heißer, müssen trocken sein und brauchen eine <strong>gehärtete Düse</strong> (<a class="xr" href="#6-7-welches-material-auf-welchem-drucker">Kapitel 6.7</a>).</li><li><strong>Kurze Fasern sind kein Laminat:</strong> Sie machen das Teil vor allem steifer – die Zugfestigkeit steigt viel weniger, als „Carbon“ vermuten lässt. Die Schichtgrenze (Z-Richtung) bleibt die Schwachstelle (<a class="xr" href="#8-6-festigkeit-und-druckrichtung">Kapitel 8.6</a>).</li><li><strong>Faserstaub</strong> beim Schleifen und Bohren: Maske tragen, absaugen – bei Glasfaser juckt der Staub zusätzlich auf der Haut.</li><li><strong>Faustregel:</strong> Muss das Teil <strong>steif und maßhaltig</strong> sein → CF. Bekommt es <strong>Stöße</strong>, muss es <strong>farbig</strong> sein oder sitzt es an <strong>Elektrik</strong> → GF.</li></ul>
<aside class="call tipp"><div class="sym" aria-hidden="true">✓</div><div class="cb"><div class="lab">Tipp</div><h4>Eigenschaften als Grafik</h4><p>Im Kostenrechner unter <strong>Materialien</strong> ein Material anklicken: Ein Sechseck zeigt Druckbarkeit, Festigkeit, Zähigkeit, Wärme, UV/außen und Preis – zum Vergleich gestrichelt PLA Basic.</p></div></aside>
'''
anchor = '<nav class="pnav" aria-label="Kapitel blättern"><a class="pn prev a-druck" href="#kapitel-5">'
rep(anchor, sec + anchor)
rep('<li><a href="#6-7-welches-material-auf-welchem-drucker">6.7 Welches Material auf welchem Drucker?</a></li>',
    f'<li><a href="#6-7-welches-material-auf-welchem-drucker">6.7 Welches Material auf welchem Drucker?</a></li><li><a href="#{ID}">6.8 Glasfaser (GF) oder Kohlefaser (CF) – der Unterschied</a></li>')
rep('<h1 id="kapitel-6-t">Filamente – welches Material wofür?</h1><div class="chs">7 Abschnitte', '<h1 id="kapitel-6-t">Filamente – welches Material wofür?</h1><div class="chs">8 Abschnitte')
rep('<span class="cct">Filamente – welches Material wofür?</span><span class="cca"><span class="ccb">3D-Drucker</span><span class="ccs">7 Abschnitte', '<span class="cct">Filamente – welches Material wofür?</span><span class="cca"><span class="ccb">3D-Drucker</span><span class="ccs">8 Abschnitte')
rep('<li>Hochleistungs-Filamente (PPS-CF, PPA-CF …) und welcher Drucker welches Material kann (6.6, 6.7)</li></ul></div>',
    f'<li>Hochleistungs-Filamente (PPS-CF, PPA-CF …) und welcher Drucker welches Material kann (6.6, 6.7)</li><li>Glasfaser oder Kohlefaser – was der Unterschied bringt (<a class="xr" href="#{ID}">6.8</a>)</li></ul></div>')

open(path, "w", encoding="utf-8").write(s)
print("Materialien + Hexagon + 6.8:", path)
