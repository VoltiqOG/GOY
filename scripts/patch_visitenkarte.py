"""Werkzeuge: Visitenkarten-Ersteller zum Gravieren (F1 Ultra / XCS).

Aufruf: python patch_visitenkarte.py <unverschluesselte index.html>  (nach patch_vektor.py)
- Formate 85 × 55 (DE), 90 × 50, 85,6 × 54 (Scheckkarte), eigenes Maß; Eckradius
- Layouts: Vorderseite mit QR, Vorderseite mittig, Rückseite Logo, Rückseite QR
- QR als vCard (Kontakt speichern) oder Link; auf dunklen Karten (Alu eloxiert) automatisch invertiert graviert
- Logo als SVG oder PNG/JPG (glatt nachgezeichnet), oder vom Typenschild übernehmen
- Prüfungen: Schrifthöhe, QR-Modul, Sicherheitsabstand, nicht darstellbare Zeichen
- Ausgabe SVG in mm: Ebene „gravieren“ (schwarz), optional „schneiden“ (rot) bzw. Kartenrand als Hilfslinie
"""
import sys

path = sys.argv[1]
s = open(path, encoding="utf-8").read()


def rep(a, b, n=1):
    global s
    if s.count(a) != n:
        raise SystemExit(f"Stelle {s.count(a)}× statt {n}× gefunden: " + a[:90])
    s = s.replace(a, b)


rep('''<button type="button" data-w="vec" aria-pressed="false">Bild → SVG</button></div>''',
    '''<button type="button" data-w="vec" aria-pressed="false">Bild → SVG</button><button type="button" data-w="vk" aria-pressed="false">Visitenkarte (Laser)</button></div>''')
rep('''$("#w_vec").hidden = b.dataset.w !== "vec"; });''', '''$("#w_vec").hidden = b.dataset.w !== "vec"; $("#w_vk").hidden = b.dataset.w !== "vk"; if (b.dataset.w === "vk") vkRender(); });''')

UI = '''      <div id="w_vk" hidden>
        <div class="ksech"><span class="kstep">1</span><div><h3>Visitenkarte zum Gravieren</h3><small>Daten eintragen, Layout wählen, SVG herunterladen und in XCS gravieren. Für Visitenkarten-Rohlinge aus Alu (schwarz eloxiert), Edelstahl oder Holz.</small></div></div>
        <div class="wgrid">
          <form class="wform" id="k_form" autocomplete="off">
            <label>Material<select name="mat"><option value="alu">Alu schwarz eloxiert (graviert hell)</option><option value="vst">Edelstahl (graviert dunkel)</option><option value="holz">Holz / Furnier (graviert dunkel)</option><option value="hell">helle Karte, dunkle Gravur</option></select></label>
            <label>Layout<select name="lay"><option value="links">Vorderseite – links mit QR</option><option value="mitte">Vorderseite – mittig</option><option value="rlogo">Rückseite – großes Logo</option><option value="rqr">Rückseite – QR-Code</option></select></label>
            <label>Format<select name="fmt"><option value="85x55">85 × 55 mm (Standard DE)</option><option value="90x50">90 × 50 mm</option><option value="86x54">85,6 × 54 mm (Scheckkarte)</option><option value="eigen">eigenes Maß</option></select></label>
            <label>Eckradius (mm)<input name="r" type="number" min="0" step="0.5"></label>
            <label class="kvkeig">Breite (mm)<input name="w" type="number" min="30" step="0.5"></label>
            <label class="kvkeig">Höhe (mm)<input name="h" type="number" min="20" step="0.5"></label>
            <label class="wfull">Name<input name="name" placeholder="Vorname Nachname"></label>
            <label>Position<input name="pos" placeholder="z. B. Technischer Produktdesigner"></label>
            <label>Firma<input name="firma" placeholder="Firmenname"></label>
            <label>Telefon<input name="tel" inputmode="tel" placeholder="+49 …"></label>
            <label>Mobil<input name="mob" inputmode="tel" placeholder="+49 …"></label>
            <label>E-Mail<input name="mail" inputmode="email"></label>
            <label>Web<input name="web" inputmode="url" placeholder="www.…"></label>
            <label>Straße<input name="str"></label>
            <label>PLZ und Ort<input name="ort"></label>
            <label>QR-Code<select name="qr"><option value="vcard">Kontakt speichern (vCard)</option><option value="url">Link (Web-Adresse)</option><option value="none">kein QR-Code</option></select></label>
            <label>QR-Link (falls „Link“)<input name="qrurl" inputmode="url" placeholder="https://…"></label>
            <div class="wfull sce"><span id="k_logoinfo">kein Logo</span><label class="kbtn sm">Logo laden (SVG, PNG, JPG)<input type="file" id="k_logofile" accept=".svg,image/svg+xml,image/png,image/jpeg,image/webp" hidden></label><button type="button" class="kbtn sm ghost" id="k_logots">vom Typenschild</button><button type="button" class="kbtn sm ghost" id="k_logoclr">entfernen</button></div>
            <label class="wchk"><input name="cut" type="checkbox"> Umriss schneiden (rote Linie, z. B. Holz)</label>
            <label class="wchk"><input name="rand" type="checkbox"> Kartenrand als Hilfslinie (in XCS „nicht ausgeben“)</label>
          </form>
          <div class="wprev"><div class="wpbox vkbox" id="k_prev"></div><div class="krow"><button type="button" class="kbtn" id="k_svg">SVG herunterladen</button><button type="button" class="kbtn ghost" id="k_reset">Beispiel laden</button></div><div class="kinfo" id="k_info"></div></div>
        </div>
        <p class="knote">In XCS: SVG importieren, mit der Kamera auf den Rohling legen (oder Rohling an einem Anschlag ausrichten), Ebene „gravieren“ als Füllung gravieren. Mehrere Karten: in XCS mit „Array“ vervielfältigen. Einstellungen und Tipps: Handbuch Kapitel 10.13.</p>
      </div>
'''
rep('''      <div id="w_vec" hidden>''', UI + '''      <div id="w_vec" hidden>''')
rep('''.vpbox{position:relative;''', '''.vkbox{padding:18px;display:grid;place-items:center;background:var(--bg2);border-radius:12px}.vkbox svg{display:block;width:100%;max-width:560px;height:auto;filter:drop-shadow(0 6px 14px rgba(0,0,0,.18))}
.vkbox+.krow{margin-top:2px}
.vpbox{position:relative;''')

JS = r'''    // ---------- Visitenkarte zum Gravieren
    const VKDEF = { mat: "alu", lay: "links", fmt: "85x55", r: 3, w: 85, h: 55, name: "Max Mustermann", pos: "Technischer Produktdesigner", firma: "Muster Maschinenbau GmbH", tel: "+49 5931 000000", mob: "+49 170 0000000", mail: "max.mustermann@example.de", web: "www.example.de", str: "Musterstraße 1", ort: "12345 Musterstadt", qr: "url", qrurl: "", cut: false, rand: false, logo: "" };
    TS.vk = { ...VKDEF, ...(TS.vk || {}) };
    const VKMAT = { alu: { bg: "#1f2023", ink: "#d8d9dc", inv: true, n: "Alu schwarz eloxiert" }, vst: { bg: "#c4c8cd", ink: "#232427", inv: false, n: "Edelstahl" }, holz: { bg: "#d8b88a", ink: "#4a2d16", inv: false, n: "Holz" }, hell: { bg: "#f2f0ea", ink: "#1d1d1d", inv: false, n: "helle Karte" } };
    const FCH = new Set(Object.keys(FONT.r));
    function vkForm() { const f = $("#k_form"), K = TS.vk; Object.entries(K).forEach(([k, v]) => { const el = f.elements[k]; if (!el) return; if (el.type === "checkbox") el.checked = !!v; else el.value = v; }); f.querySelectorAll(".kvkeig").forEach((l) => { l.hidden = K.fmt !== "eigen"; }); $("#k_logoinfo").textContent = K.logo ? "Logo geladen ✓" : "kein Logo (Firmenname als Text)"; }
    function vkCard() { const K = TS.vk; return K.fmt === "85x55" ? [85, 55] : K.fmt === "90x50" ? [90, 50] : K.fmt === "86x54" ? [85.6, 53.98] : [Math.max(30, num(K.w)), Math.max(20, num(K.h))]; }
    function vkVcard(K) { const nm = String(K.name || "").trim(), i = nm.lastIndexOf(" "), vn = i > 0 ? nm.slice(0, i) : "", nn = i > 0 ? nm.slice(i + 1) : nm, e = (v) => String(v || "").replace(/([,;\\])/g, "\\$1");
      return ["BEGIN:VCARD", "VERSION:3.0", `N:${e(nn)};${e(vn)};;;`, `FN:${e(nm)}`, K.firma && `ORG:${e(K.firma)}`, K.pos && `TITLE:${e(K.pos)}`, K.tel && `TEL;TYPE=WORK,VOICE:${K.tel}`, K.mob && `TEL;TYPE=CELL:${K.mob}`, K.mail && `EMAIL;TYPE=INTERNET:${K.mail}`, K.web && `URL:${/^https?:/.test(K.web) ? K.web : "https://" + K.web}`, (K.str || K.ort) && `ADR;TYPE=WORK:;;${e(K.str)};${e(K.ort)};;;`, "END:VCARD"].filter(Boolean).join("\r\n"); }
    function vkBuild() {
      const K = TS.vk, M = VKMAT[K.mat] || VKMAT.alu, [W, H] = vkCard(), m = 4, R = Math.max(0, Math.min(num(K.r), H / 2)), msgs = [], eng = [], T = (str, x, y, cap, bold, an = "start") => eng.push(cmdsToD(textCmds(str, x, y, cap, bold, an)));
      const fitT = (str, cap, bold, maxW, minCap = 1.3) => { let c = cap; while (c > minCap && textWidth(str, c, bold) > maxW) c -= 0.05; if (textWidth(str, c, bold) > maxW + 0.01) msgs.push(["err", `„${esc(str)}“ passt nicht – kürzen.`]); return c; };
      const bad = [...new Set([...Object.entries(K).filter(([k]) => ["name", "pos", "firma", "tel", "mob", "mail", "web", "str", "ort"].includes(k)).map(([, v]) => String(v || "")).join("")].filter((ch) => !FCH.has(ch)))];
      if (bad.length) msgs.push(["warn", `Diese Zeichen hat die eingebaute Schrift nicht und werden als „?“ graviert: ${bad.map(esc).join(" ")}`]);
      // QR
      let qrSvg = "", qrMod = 0;
      const qrTxt = K.qr === "vcard" ? vkVcard(K) : K.qr === "url" ? String(K.qrurl || (K.web ? (/^https?:/.test(K.web) ? K.web : "https://" + K.web) : "")).trim() : "";
      const qrAt = (x, y, size) => { if (!qrTxt) return; let qr, ecl = "M"; try { qr = qrcodegen.QrCode.encodeText(qrTxt, qrcodegen.QrCode.Ecc.MEDIUM); } catch (e) { msgs.push(["err", "Zu viel Inhalt für den QR-Code – Adresse oder Position weglassen oder „Link“ wählen."]); return; }
        const qz = M.inv ? 2 : 0; if (size / (qr.size + 2 * qz) < 0.5) { try { const q2 = qrcodegen.QrCode.encodeText(qrTxt, qrcodegen.QrCode.Ecc.LOW); if (q2.size < qr.size) { qr = q2; ecl = "L"; } } catch (e) {} }
        const N = qr.size + 2 * qz, s = size / N; qrMod = s; const { regions } = qrRegions(qr, M.inv, qz);
        eng.push(regions.map((rg) => [rg.outer, ...rg.holes].map((L) => "M" + L.map(([a, b]) => f3(x + a * s) + " " + f3(y + size - b * s)).join("L") + "Z").join("")).join(""));
        if (s < 0.35) msgs.push(["err", `QR-Modul nur ${n1(s, 2)} mm – zu fein, das Handy liest es kaum. QR größer, Rückseite „QR-Code“ wählen oder „Link“ statt vCard (weniger Inhalt).`]);
        else if (s < 0.5) msgs.push(["warn", `QR-Modul ${n1(s, 2)} mm – geht, aber knapp. Sicherer ab 0,5 mm: „Link“ statt vCard oder Rückseite „QR-Code“.`]);
        else msgs.push(["ok", `QR-Code ${n1(size, 1)} mm, Modul ${n1(s, 2)} mm (Version ${qr.version}, Fehlerkorrektur ${ecl}).`]);
        if (M.inv) msgs.push(["", "Dunkle Karte: Der QR-Code wird invertiert graviert (helle Fläche, Punkte bleiben dunkel) – so lesen ihn Handys richtig herum."]); };
      // Logo
      const logoAt = (x, y, w, h) => { if (K.logo) { const L = svgFit(K.logo, x, y, w, h, "logo"); if (L) return L.svg.replace(/fill="(?!none)[^"]*"/g, "").replace(/stroke="(?!none)[^"]*"/g, ""); msgs.push(["err", "Die Logo-Datei ist keine gültige SVG."]); return ""; }
        if (K.firma) { const c = fitT(K.firma, Math.min(3.2, h * 0.45), true, w); T(K.firma, x, y + h / 2 + c / 2, c, true); } return ""; };
      let logo = "";
      if (K.lay === "links") {
        const q = K.qr === "none" ? 0 : Math.min(22, H - 2 * m - 12), colW = W - 2 * m - (q ? q + 4 : 0);
        logo = logoAt(m, m, Math.min(W * 0.5, W - 2 * m - (q ? 0 : 0)), H * 0.2);
        let y = m + H * 0.2 + 5.2; const cn = fitT(K.name || "", 3.2, true, W - 2 * m); if (K.name) { T(K.name, m, y, cn, true); y += 3.4; } if (K.pos) { const cp = fitT(K.pos, 1.8, false, W - 2 * m); T(K.pos, m, y, cp, false); }
        const lines = [K.tel && "Tel. " + K.tel, K.mob && "Mobil " + K.mob, K.mail, K.web, [K.str, K.ort].filter(Boolean).join(", ")].filter(Boolean), cap = Math.min(1.75, ...lines.map((t) => fitT(t, 1.75, false, colW))), pitch = cap * 2;
        lines.slice().reverse().forEach((t, i) => T(t, m, H - m - i * pitch, cap, false));
        if (y + 2 > H - m - lines.length * pitch) msgs.push(["warn", "Name/Position und Kontaktzeilen kommen sich nahe – Zeilen weglassen oder größeres Format."]);
        if (q) qrAt(W - m - q, H - m - q, q);
        if (cap < 1.5) msgs.push(["warn", `Kontaktzeilen nur ${n1(cap, 2)} mm hoch – auf Holz unscharf, auf Metall noch lesbar. Zeilen kürzen.`]);
      } else if (K.lay === "mitte") {
        const cx = W / 2; logo = logoAt(W * 0.25, m, W * 0.5, H * 0.22);
        let y = m + H * 0.22 + 6; const cn = fitT(K.name || "", 3.4, true, W - 2 * m); if (K.name) { T(K.name, cx, y, cn, true, "middle"); y += 3.6; } if (K.pos) { const cp = fitT(K.pos, 1.8, false, W - 2 * m); T(K.pos, cx, y, cp, false, "middle"); y += 2.6; }
        eng.push(`M${f3(cx - 14)} ${f3(y)}H${f3(cx + 14)}V${f3(y + 0.25)}H${f3(cx - 14)}Z`);
        const lines = [[K.tel && "Tel. " + K.tel, K.mob && "Mobil " + K.mob].filter(Boolean).join("  ·  "), [K.mail, K.web].filter(Boolean).join("  ·  "), [K.str, K.ort].filter(Boolean).join(", ")].filter(Boolean), cap = Math.min(1.7, ...lines.map((t) => fitT(t, 1.7, false, W - 2 * m))), pitch = cap * 2;
        lines.slice().reverse().forEach((t, i) => T(t, cx, H - m - i * pitch, cap, false, "middle"));
        if (y + 2 > H - m - lines.length * pitch) msgs.push(["warn", "Es wird eng – Zeilen weglassen oder größeres Format."]);
        if (cap < 1.5) msgs.push(["warn", `Kontaktzeilen nur ${n1(cap, 2)} mm hoch – Zeilen kürzen.`]);
        if (K.qr !== "none") msgs.push(["", "Dieses Layout hat keinen QR-Code – für den QR die Rückseite „QR-Code“ als zweite Datei gravieren."]);
      } else if (K.lay === "rlogo") {
        logo = logoAt(m + 4, m + 2, W - 2 * m - 8, H - 2 * m - (K.web ? 9 : 4));
        if (K.web) { const c = fitT(K.web, 2, false, W - 2 * m); T(K.web, W / 2, H - m - 1, c, false, "middle"); }
      } else {
        const lab = K.qr === "vcard" ? "Kontakt speichern" : K.web || "", q = Math.min(H - 2 * m - (lab ? 6 : 0), W - 2 * m);
        if (K.qr === "none") msgs.push(["warn", "QR-Code ist ausgeschaltet – oben „Kontakt speichern“ oder „Link“ wählen."]);
        qrAt((W - q) / 2, m, q); if (lab && qrTxt) { const c = fitT(lab, 1.9, false, W - 2 * m); T(lab, W / 2, H - m - 0.5, c, false, "middle"); }
      }
      if (!K.logo && ["links", "mitte", "rlogo"].includes(K.lay)) msgs.push(["", "Kein Logo geladen – statt Logo steht der Firmenname. Logo als SVG laden (oder PNG/JPG, wird nachgezeichnet)."]);
      const outline = "M" + roundRect(0, 0, W, H, R).map(([a, b]) => f3(a) + " " + f3(H - b)).join("L") + "Z";
      const engD = eng.join("");
      const svg = (prev) => {
        const ink = prev ? M.ink : "#000000";
        const body = `<g id="gravieren" fill="${ink}" fill-rule="evenodd">${engD ? `<path d="${engD}"/>` : ""}${logo ? logo.replace('<g id="logo"', `<g id="logo" fill="${ink}"`) : ""}</g>`;
        if (prev) return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="-1 -1 ${f3(W + 2)} ${f3(H + 2)}" role="img" aria-label="Vorschau Visitenkarte ${f3(W)} × ${f3(H)} mm"><path d="${outline}" fill="${M.bg}"/>${body}${K.cut ? `<path d="${outline}" fill="none" stroke="#ff2d2d" stroke-width="0.25"/>` : ""}<rect x="${m}" y="${m}" width="${f3(W - 2 * m)}" height="${f3(H - 2 * m)}" fill="none" stroke="#3b82f6" stroke-width="0.12" stroke-dasharray="0.8 0.6" opacity=".55"/></svg>`;
        return `<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" width="${f3(W)}mm" height="${f3(H)}mm" viewBox="0 0 ${f3(W)} ${f3(H)}">${body}${K.cut ? `<g id="schneiden" fill="none" stroke="#ff0000" stroke-width="0.1"><path d="${outline}"/></g>` : ""}${K.rand && !K.cut ? `<g id="kartenrand_nicht_ausgeben" fill="none" stroke="#00a0ff" stroke-width="0.1"><path d="${outline}"/></g>` : ""}</svg>`;
      };
      if (K.mat === "alu" && K.cut) msgs.push(["warn", "Alu-Rohlinge sind fertig zugeschnitten – „Umriss schneiden“ nur bei Holz oder Karton nutzen."]);
      msgs.unshift(["", `${VKMAT[K.mat].n} · ${n1(W, 1)} × ${n1(H, 1)} mm · blau gestrichelt: 4 mm Sicherheitsabstand zum Rand (wird nicht graviert).`]);
      return { svg, msgs, W, H };
    }
    function vkRender() { const B = vkBuild(); $("#k_prev").innerHTML = B.svg(true); $("#k_info").innerHTML = B.msgs.map(([c, t]) => `<p class="kmsg ${c}">${t}</p>`).join(""); return B; }
    { let tm = 0; $("#k_form").addEventListener("input", (e) => { const el = e.target; if (!el.name) return; TS.vk[el.name] = el.type === "checkbox" ? el.checked : el.type === "number" ? num(el.value) : el.value;
      if (el.name === "fmt") vkForm(); saveTS(); clearTimeout(tm); tm = setTimeout(vkRender, 60); }); }
    $("#k_logofile").addEventListener("change", async (e) => { const f = e.target.files[0]; e.target.value = ""; if (!f) return;
      try { if (/svg/.test(f.type) || /\.svg$/i.test(f.name)) TS.vk.logo = await f.text(); else { const url = await new Promise((r) => { const fr = new FileReader(); fr.onload = () => r(fr.result); fr.readAsDataURL(f); }); TS.vk.logo = await logoTrace(url, 50, false); toast("Logo aus dem Bild nachgezeichnet – für feinere Kontrolle: Werkzeuge → Bild → SVG."); } }
      catch (err) { toast(err.message || "Logo konnte nicht gelesen werden."); return; } saveTS(); vkForm(); vkRender(); });
    $("#k_logots").addEventListener("click", () => { if (!TS.sch.logo) { toast("Im Typenschild ist noch kein Logo geladen."); return; } TS.vk.logo = TS.sch.logo; saveTS(); vkForm(); vkRender(); });
    $("#k_logoclr").addEventListener("click", () => { TS.vk.logo = ""; saveTS(); vkForm(); vkRender(); });
    $("#k_reset").addEventListener("click", () => { const lg = TS.vk.logo; TS.vk = { ...VKDEF, logo: lg }; saveTS(); vkForm(); vkRender(); });
    $("#k_svg").addEventListener("click", () => { const B = vkBuild(), K = TS.vk; offerFile(`Visitenkarte_${fileSafe(K.name || "Karte")}_${K.lay}.svg`, B.svg(false), "image/svg+xml"); });
    vkForm();
'''
rep('''    // ---------- Werkzeug „Bild → SVG“''', JS + '''    // ---------- Werkzeug „Bild → SVG“''')
rep('''TS = { qr: { ...TS.qr, ...v.qr }, sch: v.sch || {}, vec: v.vec };''', '''TS = { qr: { ...TS.qr, ...v.qr }, sch: v.sch || {}, vec: v.vec, vk: v.vk };''')

# ---------- Handbuch: 10.13 Visitenkarten gravieren
ID = "10-13-visitenkarten-gravieren"
sec = f'''<h2 id="{ID}"><span class="hn">10.13</span> Visitenkarten gravieren</h2>
<p>Im Kostenrechner unter <strong>Werkzeuge → Visitenkarte (Laser)</strong> entsteht die Datei: Daten eintragen, Layout wählen (Vorderseite mit QR, mittig, Rückseite mit Logo oder QR), SVG herunterladen. Text ist schon in Pfade umgewandelt, Maße in Millimetern – die Datei kommt in XCS in Originalgröße an.</p>
<div class="tw"><table class=""><thead><tr><th>Rohling</th><th>Laser</th><th>Ergebnis</th><th>Darauf achten</th></tr></thead><tbody>
<tr><td data-label="Rohling"><span class="tc"><strong>Alu, schwarz eloxiert</strong> (0,2–0,8 mm)</span></td><td data-label="Laser"><span class="tc">Faserlaser (IR)</span></td><td data-label="Ergebnis"><span class="tc">helle, silberne Gravur</span></td><td data-label="Darauf achten"><span class="tc">nur die Eloxalschicht abtragen, nicht tief gravieren; QR wird automatisch invertiert</span></td></tr>
<tr><td data-label="Rohling"><span class="tc"><strong>Edelstahl</strong></span></td><td data-label="Laser"><span class="tc">Faserlaser (IR)</span></td><td data-label="Ergebnis"><span class="tc">dunkle Gravur (Anlassfarbe)</span></td><td data-label="Darauf achten"><span class="tc">dünnes Blech verzieht sich bei großen Flächen – Metallunterlage, Pausen (<a class="xr" href="#{ "10-12-laserweg-gravierwinkel-kreuzschraffur-und-reihenfolge" }">10.12</a>)</span></td></tr>
<tr><td data-label="Rohling"><span class="tc"><strong>Holz / Furnier</strong></span></td><td data-label="Laser"><span class="tc">Diodenlaser (blau)</span></td><td data-label="Ergebnis"><span class="tc">braune Gravur, Umriss kann geschnitten werden</span></td><td data-label="Darauf achten"><span class="tc">feine Schrift unter 1,5 mm verläuft; „Umriss schneiden“ einschalten</span></td></tr>
</tbody></table></div>
<ol class="steps"><li><span class="n"></span><div><strong>Parameter testen:</strong> mit der Materialbibliothek von XCS starten und auf einem Reststück oder einem Fehldruck-Rohling ein Testfeld lasern (<a class="xr" href="#10-4-materialtest-so-findest-du-die-richtigen-werte">Kapitel 10.4</a>). Werte nicht von anderen Rohlingen übernehmen – Eloxalschichten sind unterschiedlich dick.</div></li><li><span class="n"></span><div><strong>Ausrichten:</strong> Rohling flach und fest legen (Magnet- oder Klebeunterlage), Fokus messen, Kamerabild aktualisieren und die Karte im Bild auf den Rohling schieben. Für mehrere Karten einen Anschlag aus Restmaterial lasern, dann sitzt jede Karte gleich.</div></li><li><span class="n"></span><div><strong>Lasern:</strong> Ebene „gravieren“ als Füllung; Gravierwinkel 0° für scharfe Schrift, bei großen Flächen 45° oder Kreuzschraffur (<a class="xr" href="#{ "10-12-laserweg-gravierwinkel-kreuzschraffur-und-reihenfolge" }">10.12</a>). Die Hilfslinie „kartenrand“ in XCS auf „nicht ausgeben“ stellen.</div></li><li><span class="n"></span><div><strong>QR prüfen:</strong> sofort mit zwei verschiedenen Handys scannen. Liest keins, ist das Modul zu klein (Rechner meldet es) oder der Kontrast zu schwach – dann Rückseite „QR-Code“ mit größerem Code.</div></li></ol>
<aside class="call tipp"><div class="sym" aria-hidden="true">✓</div><div class="cb"><div class="lab">Tipp</div><h4>vCard oder Link?</h4><p>Die <strong>vCard</strong> speichert den Kontakt direkt im Handy, braucht aber viel Platz im Code – die Punkte werden klein. Auf der Vorderseite ist ein <strong>Link</strong> oft die sicherere Wahl; die vCard passt besser groß auf die Rückseite.</p></div></aside>
'''
anchor = sec_anchor = '<nav class="pnav" aria-label="Kapitel blättern"><a class="pn prev a-laser" href="#kapitel-9">'
rep(anchor, sec + anchor)
rep('<li><a href="#10-12-laserweg-gravierwinkel-kreuzschraffur-und-reihenfolge">10.12 Laserweg: Gravierwinkel, Kreuzschraffur und Reihenfolge</a></li>',
    f'<li><a href="#10-12-laserweg-gravierwinkel-kreuzschraffur-und-reihenfolge">10.12 Laserweg: Gravierwinkel, Kreuzschraffur und Reihenfolge</a></li><li><a href="#{ID}">10.13 Visitenkarten gravieren</a></li>')
rep('<div class="chs">12 Abschnitte</div>', '<div class="chs">13 Abschnitte</div>', "x") if False else None
for a, b in [('<h1 id="kapitel-10-t">xTool Creative Space (XCS) – die Laser-Software</h1><div class="chs">12 Abschnitte', '<h1 id="kapitel-10-t">xTool Creative Space (XCS) – die Laser-Software</h1><div class="chs">13 Abschnitte'),
             ('<span class="cct">xTool Creative Space (XCS) – die Laser-Software</span><span class="cca"><span class="ccb">Laser</span><span class="ccs">12 Abschnitte', '<span class="cct">xTool Creative Space (XCS) – die Laser-Software</span><span class="cca"><span class="ccb">Laser</span><span class="ccs">13 Abschnitte')]:
    rep(a, b)
rep('''<a href="#10-10-''', '''<a href="#10-10-''', s.count('<a href="#10-10-'))  # nur Kontrolle
# Kapitelübersicht 10: Arbeitsbeispiele um 10.13 ergänzen
i = s.find('<nav class="cmap" aria-label="Kapitel 10 im Überblick">')
if i >= 0:
    j = s.find("</nav>", i); k = s.rfind("</div>", i, j)
    s = s[:k] + f'<a href="#{ID}"><span>10.13</span> Visitenkarten gravieren</a>' + s[k:]
rep('<li>Gravierwinkel, Kreuzschraffur und Reihenfolge – mit Testvorlage (<a class="xr" href="#10-12-laserweg-gravierwinkel-kreuzschraffur-und-reihenfolge">10.12</a>)</li></ul></div>',
    f'<li>Gravierwinkel, Kreuzschraffur und Reihenfolge – mit Testvorlage (<a class="xr" href="#10-12-laserweg-gravierwinkel-kreuzschraffur-und-reihenfolge">10.12</a>)</li><li>Visitenkarten aus Alu, Edelstahl oder Holz gravieren (<a class="xr" href="#{ID}">10.13</a>)</li></ul></div>')

open(path, "w", encoding="utf-8").write(s)
print("Visitenkarte + 10.13:", path)
