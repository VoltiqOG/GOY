"""Typenschild-Generator: Vorlage „Werksschild mit Logo“ (Rahmen-Layout wie das Firmenschild).

Aufruf (nach patch_farben.py): python patch_werksschild.py <unverschluesselte index.html>
Aufbau: Logo oben (austauschbar, SVG), Anschrift links, Service rechts, Haarlinie,
links 5 und rechts 4 Felder mit Kästen (Beschriftung änderbar), CE, Website unten,
oben und unten ein kräftiger Strich. Werte können eingraviert oder für die spätere
Nachgravur leer gelassen werden.
"""
import sys

path = sys.argv[1]
s = open(path, encoding="utf-8").read()


def rep(a, b):
    global s
    if a not in s:
        raise SystemExit("Stelle nicht gefunden: " + a[:90])
    s = s.replace(a, b, 1)


# ---------- Vorlage und Logo-Knöpfe
rep('''<option value="gf">Gurtförderer (EN 620, 7.2)</option></select></label>''',
    '''<option value="gf">Gurtförderer (EN 620, 7.2)</option><option value="ws">Werksschild mit Logo (Rahmen-Layout)</option></select></label>''')
rep('''            <div class="wfull sce"><span id="s_ceinfo">''',
    '''            <label class="wchk wfull wsonly"><input name="wsfill" type="checkbox"> Werte eingravieren (aus: Kästen leer lassen für die spätere Nachgravur)</label>
            <div class="wfull sce wsonly"><span id="s_logoinfo"></span><label class="kbtn sm">Logo (SVG) laden<input type="file" id="s_logofile" accept=".svg,image/svg+xml" hidden></label><button type="button" class="kbtn sm" id="s_logoclear">entfernen</button></div>
            <div class="wfull sce"><span id="s_ceinfo">''')

# ---------- Felder: zusätzliche Kopfangaben
rep('''["link", "Link zur Betriebsanleitung (QR)", "https://", 0],''',
    '''["link", "Link zur Betriebsanleitung (QR)", "https://", 0],
      ["telfax", "Telefon / Telefax", "", 0], ["hotline", "Service-Hotline", "", 0], ["mail", "Service-E-Mail", "", 0], ["web", "Website (Fußzeile)", "", 0],''')
rep('''    const SLAB = Object.fromEntries(''',
    '''    SPRESET.ws = { name: "Werksschild mit Logo", rows: [], req: ["hersteller", "adresse"], show: ["hersteller", "adresse", "telfax", "hotline", "mail", "web"] };
    const WSL = ["Bezeichnung", "Typ", "Masch.-Nr.", "Baujahr", "Gewicht"], WSR = ["Nennspannung", "Antriebsleistung", "Nennstrom", ""], WSRV = ["3 x 400 V / 50 Hz", "", "", "Kom.: "];
    const SLAB = Object.fromEntries(''')
rep('''color: false, c_kopf: "blau",''',
    '''logo: "", wsfill: true, ...Object.fromEntries(WSL.flatMap((l, i) => [["wsL" + i, l], ["wsV" + i, ""]])), ...Object.fromEntries(WSR.flatMap((l, i) => [["wsRL" + i, l], ["wsRV" + i, WSRV[i]]])), color: false, c_kopf: "blau",''')

# schForm: eigene Feldliste für die Werksschild-Vorlage
rep('''      const S = TS.sch, P = SPRESET[S.preset] || SPRESET.mvo, show = new Set(["hersteller", "adresse", "kontakt", ...P.rows, "link"]);''',
    '''      const S = TS.sch, P = SPRESET[S.preset] || SPRESET.mvo, show = new Set(P.show || ["hersteller", "adresse", "kontakt", ...P.rows, "link"]);''')
rep('''      $("#s_ceinfo").textContent = S.ce ? "CE-Vorlage geladen ✓" : "keine CE-Vorlage geladen";''',
    '''      $("#s_ceinfo").textContent = S.ce ? "CE-Vorlage geladen ✓" : "keine CE-Vorlage geladen";
      const ws = S.preset === "ws"; $$("#s_form .wsonly").forEach((n) => { n.hidden = !ws; }); f.elements.wsfill.checked = !!S.wsfill; $("#s_logoinfo").textContent = S.logo ? "Logo geladen ✓" : "kein Logo geladen";
      ["qr", "qrs", "note"].forEach((k) => { const l = f.elements[k] && f.elements[k].closest("label"); if (l) l.hidden = ws; });
      if (ws) $("#s_fields").insertAdjacentHTML("beforeend", `<p class="wfull kmsg" style="margin:8px 0 0">Felder links (Beschriftung · Wert)</p>` + WSL.map((_, i) => `<label class="sfl"><span>Beschriftung ${i + 1}</span><input name="wsL${i}" value="${esc(S["wsL" + i] ?? "")}" autocomplete="off"></label><label class="sfl"><span>Wert ${i + 1}</span><input name="wsV${i}" value="${esc(S["wsV" + i] ?? "")}" autocomplete="off"></label>`).join("") +
        `<p class="wfull kmsg" style="margin:8px 0 0">Felder rechts (Beschriftung · Wert)</p>` + WSR.map((_, i) => `<label class="sfl"><span>Beschriftung ${i + 6}</span><input name="wsRL${i}" value="${esc(S["wsRL" + i] ?? "")}" autocomplete="off"></label><label class="sfl"><span>Wert ${i + 6}</span><input name="wsRV${i}" value="${esc(S["wsRV" + i] ?? "")}" autocomplete="off"></label>`).join(""));''')

# ---------- SVG einer Datei in einen Kasten einpassen (Logo, CE)
rep('''    function ceGroup(x, y, h) {''',
    '''    function svgFit(text, x, y, maxW, maxH, id) {
      try { const doc = new DOMParser().parseFromString(text, "image/svg+xml"), r = doc.documentElement; if (r.nodeName.toLowerCase() !== "svg") return null;
        let vb = (r.getAttribute("viewBox") || "").split(/[\\s,]+/).map(Number);
        if (vb.length !== 4 || !vb.every(isFinite) || !(vb[2] > 0) || !(vb[3] > 0)) vb = [0, 0, parseFloat(r.getAttribute("width")) || 100, parseFloat(r.getAttribute("height")) || 50];
        const k = Math.min(maxW / vb[2], maxH / vb[3]), w = vb[2] * k, h = vb[3] * k, ox = x + (maxW - w) / 2, oy = y + (maxH - h) / 2;
        r.querySelectorAll("script,foreignObject,image").forEach((n) => n.remove()); [...r.querySelectorAll("*")].forEach((n) => [...n.attributes].forEach((a) => { if (/^on/i.test(a.name)) n.removeAttribute(a.name); }));
        return { svg: `<g id="${id}" transform="translate(${f3(ox - vb[0] * k)} ${f3(oy - vb[1] * k)}) scale(${f3(k)})">${[...r.childNodes].map((n) => n.outerHTML || "").join("")}</g>`, w, h, hasImg: /<image[\\s>]/i.test(text) };
      } catch (e) { return null; }
    }
    function ceGroup(x, y, h) {''')

# ---------- Aufbau des Werksschilds
rep('''    function schBuild() {''',
    r'''    const ringRect = (x, y, w, h, t) => `M${f3(x)} ${f3(y)}H${f3(x + w)}V${f3(y + h)}H${f3(x)}Z` + `M${f3(x + t)} ${f3(y + t)}V${f3(y + h - t)}H${f3(x + w - t)}V${f3(y + t)}Z`;
    function wsBuild() {
      const S = TS.sch, V = S.vals, W = S.w, H = S.h, m = S.m, msgs = [], cut = [], head = [], fld = [], vals = [];
      const colOf = (k) => (S.color ? S[k] : "schwarz") || "schwarz";
      const fit = (str, cap, bold, maxW, minCap = 1.4) => { let c = cap; while (c > minCap && textWidth(str, c, bold) > maxW) c -= 0.05; return c; };
      ["hersteller", "adresse"].forEach((k) => { if (!String(V[k] || "").trim()) msgs.push(["err", `Pflichtangabe fehlt: ${SLAB[k]}`]); });
      const hp = S.holes == 4 ? [[S.he, S.he], [W - S.he, S.he], [S.he, H - S.he], [W - S.he, H - S.he]] : S.holes == 2 ? [[S.he, H / 2], [W - S.he, H / 2]] : [];
      const mx = hp.length ? Math.max(m, S.he + S.hd / 2 + 1.2) : m, t = Math.max(0.5, Math.min(1, H * 0.009));
      // oben und unten ein kräftiger Strich über die volle Breite innerhalb des Rands
      head.push(`M${f3(mx)} ${f3(m)}H${f3(W - mx)}V${f3(m + t)}H${f3(mx)}Z`, `M${f3(mx)} ${f3(H - m - t)}H${f3(W - mx)}V${f3(H - m)}H${f3(mx)}Z`); // Striche enden vor den Löchern
      // Logo
      const lgY = m + t + 2, lgH = H * 0.24, lgW = W * 0.66, lgX = (W - lgW) / 2; let logo = null, logoSvg = "";
      if (S.logo) { logo = svgFit(S.logo, lgX, lgY, lgW, lgH, "logo"); if (!logo) msgs.push(["err", "Die Logo-Datei ist keine gültige SVG."]); else if (logo.hasImg) msgs.push(["warn", "Das Logo enthält ein eingebettetes Pixelbild – das wurde entfernt. Bitte ein Vektor-Logo nehmen (Pixelbild in Inkscape oder XCS vektorisieren)."]); }
      else msgs.push(["warn", "Kein Logo geladen – gestrichelter Platzhalter (wird nicht gelasert). Logo als SVG laden; am besten einfarbig, Schrift in Pfade umgewandelt."]);
      const lgBottom = logo ? lgY + (lgH + logo.h) / 2 : lgY + lgH;
      // Anschrift links, Service rechts
      let y = lgBottom + 3; const ca = Math.max(1.6, Math.min(2.6, H * 0.03)), colW = W * 0.46 - mx, rx = W * 0.5;
      const L = [V.hersteller, V.adresse, V.telfax].filter((x) => String(x || "").trim()), R = [V.hotline ? "Service-Hotline  " + V.hotline : "", V.mail].filter((x) => String(x || "").trim());
      const cL = Math.min(...L.map((x) => fit(x, ca, false, colW)), ca), cR = Math.min(...R.map((x) => fit(x, ca, false, W - mx - rx)), ca);
      L.forEach((x, i) => head.push(cmdsToD(textCmds(x, mx, y + cL + i * cL * 1.6, cL, false))));
      R.forEach((x, i) => head.push(cmdsToD(textCmds(x, rx, y + cR + (i + 1) * cR * 1.6, cR, false))));
      y += Math.max(L.length * cL * 1.6, (R.length + 1) * cR * 1.6) + 1.2;
      head.push(`M${f3(mx)} ${f3(y)}H${f3(W - mx)}V${f3(y + 0.25)}H${f3(mx)}Z`); y += 1.6;
      // Website unten
      const web = String(V.web || "").trim(), cw = web ? fit(web.toUpperCase(), Math.min(3.4, H * 0.04), true, W - 2 * mx) : 0, webBase = H - m - t - 1.6;
      if (web) head.push(cmdsToD(textCmds(web.toUpperCase(), W / 2, webBase, cw, true, "middle")));
      const fBottom = web ? webBase - cw - 2 : H - m - t - 1.5;
      // Felder: links 5 Zeilen, rechts 4 Zeilen ab der zweiten; erste Zeile reicht bis zum CE-Zeichen
      const rows = 5, pitch = (fBottom - y) / rows, bh = pitch * 0.8, lc = Math.max(1.4, Math.min(2.4, pitch * 0.32)), vc0 = Math.max(1.4, Math.min(3.4, bh * 0.55)), rt = 0.3;
      if (pitch < 4) msgs.push(["err", `Zu wenig Höhe für die Felder (Zeile ${n1(pitch, 1)} mm) – Schild höher machen.`]);
      const labL = WSL.map((_, i) => String(S["wsL" + i] || "")), labR = WSR.map((_, i) => String(S["wsRL" + i] || ""));
      const lw = Math.max(0, ...labL.map((x) => textWidth(x, lc, false))), rw = Math.max(0, ...labR.map((x) => textWidth(x, lc, false)));
      const bx = mx + (lw ? lw + 2 : 0), bx2 = W * 0.44, rlx = W * 0.47, rbx = rlx + (rw ? rw + 2 : 0), rbx2 = W - mx;
      const ceH = Math.max(5, Math.min(9, bh * 1.1)), ceW = ceH * 1.4, row1End = W - mx - ceW - 3;
      const box = (x1, x2, yy, label, lx, value, name) => {
        if (label) fld.push(cmdsToD(textCmds(label, lx, yy + (bh + lc) / 2, lc, false)));
        fld.push(ringRect(x1, yy, x2 - x1, bh, rt));
        if (S.wsfill && String(value || "").trim()) { const vw = x2 - x1 - 3, vc = fit(value, vc0, false, vw);
          if (textWidth(value, vc, false) > vw + 0.01) msgs.push(["err", `„${esc(name)}“ passt nicht in den Kasten – kürzen.`]);
          vals.push(cmdsToD(textCmds(value, x1 + 1.5, yy + (bh + vc) / 2, vc, false))); }
        if (x2 - x1 < 12) msgs.push(["warn", `Kasten „${esc(name)}“ ist sehr schmal – Beschriftung kürzen oder Schild breiter.`]); };
      for (let i = 0; i < rows; i++) { const yy = y + pitch * i + (pitch - bh) / 2;
        box(bx, i === 0 ? row1End : bx2, yy, labL[i], mx, S["wsV" + i], labL[i] || "Feld " + (i + 1));
        if (i > 0) box(rbx, rbx2, yy, labR[i - 1], rlx, S["wsRV" + (i - 1)], labR[i - 1] || "Feld " + (i + 5)); }
      // CE rechts in der ersten Zeile
      const ce = ceGroup(W - mx - ceW, y + (pitch - ceH) / 2, ceH);
      if (!S.ce) msgs.push(["warn", "Keine CE-Vorlage geladen – blau gestrichelter Platzhalter. Offizielle CE-Datei der EU laden (Höhe ≥ 5 mm)."]);
      msgs.push(["", "Maschinenverordnung (EU) 2023/1230, Anhang III 1.7.3: Name und Anschrift des Herstellers, Bezeichnung, CE, Baureihe oder Typ, Seriennummer (falls vorhanden) und Baujahr gehören auf das Schild – die Feldbeschriftungen entsprechend wählen."]);
      // Schnitt
      if (S.outline) cut.push("M" + roundRect(0, 0, W, H, S.rad).map(([a, b]) => f3(a) + " " + f3(H - b)).join("L") + "Z");
      hp.forEach(([a, b]) => cut.push(`M${f3(a + S.hd / 2)} ${f3(b)}A${f3(S.hd / 2)} ${f3(S.hd / 2)} 0 1 0 ${f3(a - S.hd / 2)} ${f3(b)}A${f3(S.hd / 2)} ${f3(S.hd / 2)} 0 1 0 ${f3(a + S.hd / 2)} ${f3(b)}Z`));
      if (!msgs.some((x) => x[0] === "err")) msgs.unshift(["ok", "Werksschild passt – Logo, Felder und Text liegen innerhalb des Rands."]);
      if (S.color) msgs.push(["warn", "Farbmarkierung: Kapitel 10.11 – für Schilder an Maschinen in der Recyclinghalle oder außen keine Farben, dort schwarz markieren."]);
      const svg = (prev) => { const C = (k) => (prev ? SCOL[colOf(k)].view : SCOL[colOf(k)].hex);
        const lg = logo ? logo.svg.replace('<g id="logo"', `<g id="logo" fill="${C("c_kopf")}"`) : prev ? `<g id="hinweis_logo" fill="none" stroke="#1e6fd9" stroke-width="0.2" stroke-dasharray="1 0.6"><rect x="${f3(lgX)}" y="${f3(lgY)}" width="${f3(lgW)}" height="${f3(lgH)}"/></g>` : "";
        const grp = (id, k, d) => (d.length ? `<g id="${id}" fill="${C(k)}" fill-rule="nonzero"><path d="${d.join("")}"/></g>` : "");
        const ceS = prev || S.ce ? (S.ce && S.color ? ce.svg.replace('<g id="ce"', `<g id="ce" fill="${C("c_ce")}"`) : ce.svg) : "";
        return `<svg xmlns="http://www.w3.org/2000/svg" width="${f3(W)}mm" height="${f3(H)}mm" viewBox="0 0 ${f3(W)} ${f3(H)}">` + (prev ? `<rect width="${f3(W)}" height="${f3(H)}" rx="${f3(S.rad)}" fill="#e9ecef"/>` : "") +
          grp("kopf", "c_kopf", head) + lg + grp("felder", "c_kopf", fld) + grp("werte", "c_werte", vals) + ceS + `<g id="schneiden" fill="none" stroke="#ff0000" stroke-width="0.1"><path d="${cut.join("")}"/></g></svg>`; };
      return { svg, msgs };
    }
    function schBuild() {
      if (TS.sch.preset === "ws") return wsBuild();''')

# Formular-Ereignisse: Vorlagenwechsel setzt passende Größe, Logo laden/entfernen
rep('''      if (el.name === "preset" || el.name === "color") schForm(); saveTS(); schRender(); });''',
    '''      if (el.name === "preset" && el.value === "ws" && S.w <= 100) { S.w = 150; S.h = 95; S.holes = 4; }
      if (el.name === "preset" || el.name === "color") schForm(); saveTS(); schRender(); });
    $("#s_logofile").addEventListener("change", async (e) => { const f = e.target.files[0]; if (!f) return; const t = await f.text(); if (!/<svg[\\s>]/i.test(t)) { toast("Bitte das Logo als SVG laden."); return; } TS.sch.logo = t; saveTS(); schForm(); schRender(); toast("Logo gespeichert – wird ab jetzt verwendet."); e.target.value = ""; });
    $("#s_logoclear").addEventListener("click", () => { TS.sch.logo = ""; saveTS(); schForm(); schRender(); });''')

open(path, "w", encoding="utf-8").write(s)
print("Werksschild eingefügt:", path)
