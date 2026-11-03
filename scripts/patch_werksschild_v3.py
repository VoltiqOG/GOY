"""Werksschild wie das Firmenschild 148 × 105 × 1,5 mm (Löcher Ø 3, Lochabstand 138 × 95), Rahmen, Typ-Zeile über die volle Breite,
CE neben dem Service-Block, Website mittig. Logo zusätzlich als JPG/PNG: wird im Browser in Vektorflächen umgewandelt (Schwelle einstellbar).
Aufruf: python scripts/aktualisieren.py index.html scripts/patch_werksschild_v3.py"""
import sys
p = sys.argv[1]; s = open(p, encoding="utf-8").read()
if "logoTrace" in s: sys.exit("schon eingespielt")
def R(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:90], s.count(a)); s = s.replace(a, b)

# --- Felder wie auf dem Firmenschild
R('const WSL = ["Bezeichnung", "Typ", "Masch.-Nr.", "Baujahr", "Gewicht"], WSR = ["Nennspannung", "Antriebsleistung", "Nennstrom", ""]',
  'const WSL = ["Typ", "Fabrik-Nr.", "Zeichnung Nr.", "Baujahr", "Gewicht"], WSR = ["Nennspannung", "Antriebsleistung", "Nennstrom", ""]')
R('    TS.sch = { ...SDEF, ...TS.sch, vals: { ...SDEF.vals, ...(TS.sch.vals || {}) } };',
  '''    TS.sch = { ...SDEF, ...TS.sch, vals: { ...SDEF.vals, ...(TS.sch.vals || {}) } };
    if (TS.sch.wsL0 === "Bezeichnung" && TS.sch.wsL2 === "Masch.-Nr.") WSL.forEach((l, i) => { TS.sch["wsL" + i] = l; }); // alte Standard-Beschriftungen auf das Firmenschild umstellen
    if (TS.sch.logoThr == null) TS.sch.logoThr = 50;''')
R('<option value="ws">Werksschild mit Logo (Rahmen-Layout)</option>', '<option value="ws">Werksschild mit Logo (148 × 105, wie Firmenschild)</option>')
R('if (el.name === "preset" && el.value === "ws" && S.w <= 100) { S.w = 150; S.h = 110; S.holes = 0; }',
  'if (el.name === "preset" && el.value === "ws") Object.assign(S, { w: 148, h: 105, rad: 3, holes: 4, hd: 3, he: 5, m: 3 }); // Maße wie Firmenschild')

# --- Layout: Rahmen, Typ volle Breite, rechte Spalte ab Zeile 2, CE neben Service, Website mittig
R('''      const mx = hp.length ? Math.max(m, S.he + S.hd / 2 + 1.2) : m, t = Math.max(0.5, Math.min(1, H * 0.009));
      // oben und unten ein kräftiger Strich über die volle Breite (bei Löchern davor endend)
      head.push(`M${f3(mx)} ${f3(m)}H${f3(W - mx)}V${f3(m + t)}H${f3(mx)}Z`, `M${f3(mx)} ${f3(H - m - t)}H${f3(W - mx)}V${f3(H - m)}H${f3(mx)}Z`);
      const top = m + t, bot = H - m - t, U = bot - top, Y = (f) => top + U * f;   // Lage als Anteil der Höhe zwischen den Strichen''',
  '''      const t = Math.max(0.5, Math.min(1, H * 0.008)), fr = hp.length ? Math.max(m, S.he + S.hd / 2 + 0.6) : m; // Rahmen knapp innerhalb der Löcher
      head.push(ringRect(fr, fr, W - 2 * fr, H - 2 * fr, t));
      const mx = fr + t + 1.6, top = fr + t, bot = H - fr - t, U = bot - top, Y = (f) => top + U * f;   // Lage als Anteil der Höhe im Rahmen''')
R('''      const ca = Math.max(1.4, Math.min(3, U * 0.032)), lh = 1.55, aY = Y(0.36), rx = W * 0.47;''',
  '''      const ca = Math.max(1.4, Math.min(3, U * 0.032)), lh = 1.55, aY = Y(0.34), rx = W * 0.47, ceH = Math.max(5, Math.min(8, U * 0.085)), ceW = ceH * 1.4;''')
R('''cR = Math.min(ca, ...R.map((x) => fit(x, ca, false, W - mx - rx)));''', '''cR = Math.min(ca, ...R.map((x) => fit(x, ca, false, W - mx - rx - ceW - 3)));''')
R('''      R.forEach((x, i) => head.push(cmdsToD(textCmds(x, rx, aY + cR + (i + 2) * cR * lh, cR, false))));''',
  '''      R.forEach((x, i) => head.push(cmdsToD(textCmds(x, rx, aY + cR + (i + 1) * cR * lh, cR, false))));''')
R('''      const y0 = Math.max(aY + (L.length) * cL * lh + 1.5, aY + (R.length + 2) * cR * lh + 1.2), rows = 6,''',
  '''      const y0 = Math.max(aY + (L.length) * cL * lh + 1.5, aY + (R.length + 1) * cR * lh + 1.2, aY + ceH + 1), rows = 6,''')
R('''      for (let i = 0; i < 5; i++) box(bx, bx2, rowY(i), labL[i], mx, S["wsV" + i], labL[i] || "Feld " + (i + 1), i === 0);
      for (let i = 0; i < 4; i++) box(rbx, rbx2, rowY(i + 2), labR[i], rlx, S["wsRV" + i], labR[i] || "Feld " + (i + 6), false);''',
  '''      for (let i = 0; i < 5; i++) box(bx, i === 0 ? rbx2 : bx2, rowY(i), labL[i], mx, S["wsV" + i], labL[i] || "Feld " + (i + 1), false); // Zeile 1 (Typ) über die volle Breite
      for (let i = 0; i < 4; i++) box(rbx, rbx2, rowY(i + 1), labR[i], rlx, S["wsRV" + i], labR[i] || "Feld " + (i + 6), false);''')
R('''      const web = String(V.web || "").trim().toUpperCase(), sq = 0.78, wcx = (mx + bx2) / 2;''', '''      const web = String(V.web || "").trim().toUpperCase(), sq = 0.78, wcx = W / 2;''')
R('''fit(web, Math.min(3.4, pitch * 0.5), true, (bx2 - mx) / sq)''', '''fit(web, Math.min(3.4, pitch * 0.5), true, (W - 2 * mx) / sq)''')
R('''      const ceH = Math.max(5, Math.min(10, pitch * 1.3)), ceW = ceH * 1.4, ce = ceGroup(W - mx - ceW - 1, rowY(0) + (pitch * 2 - ceH) / 2 + 0.6, ceH);''',
  '''      const ce = ceGroup(W - mx - ceW, aY + 0.3, ceH);''')

# --- Logo auch als JPG/PNG: im Browser nachzeichnen (Vektorflächen für den Laser)
R('''<label class="kbtn sm">Logo (SVG) laden<input type="file" id="s_logofile" accept=".svg,image/svg+xml" hidden></label><button type="button" class="kbtn sm" id="s_logoclear">entfernen</button></div>''',
  '''<label class="kbtn sm">Logo laden (SVG, PNG, JPG)<input type="file" id="s_logofile" accept=".svg,.png,.jpg,.jpeg,.webp,image/svg+xml,image/png,image/jpeg,image/webp" hidden></label><button type="button" class="kbtn sm" id="s_logoclear">entfernen</button></div>
            <label class="wfull wsonly" id="s_logothrl" hidden>Logo aus Bild: Schwelle hell/dunkel <b id="s_logothrv"></b><input type="range" id="s_logothr" min="10" max="90" step="1"></label>
            <label class="wchk wfull wsonly" id="s_logoinvl" hidden><input type="checkbox" id="s_logoinv"> Logo umkehren (helles Logo auf dunklem Grund)</label>''')
R('''$("#s_logoinfo").textContent = S.logo ? "Logo geladen ✓" : "kein Logo geladen";''',
  '''$("#s_logoinfo").textContent = S.logo ? (S.logoRaw ? "Logo aus Bild nachgezeichnet ✓" : "Logo geladen ✓") : "kein Logo geladen";
      $("#s_logothrl").hidden = $("#s_logoinvl").hidden = !(ws && S.logoRaw); $("#s_logothr").value = S.logoThr; $("#s_logothrv").textContent = S.logoThr + " %"; $("#s_logoinv").checked = !!S.logoInv;''')
R('''    $("#s_logofile").addEventListener("change", async (e) => { const f = e.target.files[0]; if (!f) return; const t = await f.text(); if (!/<svg[\\s>]/i.test(t)) { toast("Bitte das Logo als SVG laden."); return; } TS.sch.logo = t; saveTS(); schForm(); schRender(); toast("Logo gespeichert – wird ab jetzt verwendet."); e.target.value = ""; });
    $("#s_logoclear").addEventListener("click", () => { TS.sch.logo = ""; saveTS(); schForm(); schRender(); });''',
  '''    // Pixelbild → Vektorflächen: Graustufen, Schwelle, Umrisse wie beim QR-Code nachfahren (eine Fläche pro zusammenhängendem Bereich)
    const logoTrace = (url, thr, inv) => new Promise((res, rej) => { const im = new Image();
      im.onload = () => { const k = Math.min(1, 900 / Math.max(im.naturalWidth, im.naturalHeight)), w = Math.max(1, Math.round(im.naturalWidth * k)), h = Math.max(1, Math.round(im.naturalHeight * k));
        const cv = document.createElement("canvas"); cv.width = w; cv.height = h; const g = cv.getContext("2d"); g.fillStyle = "#fff"; g.fillRect(0, 0, w, h); g.drawImage(im, 0, 0, w, h);
        const px = g.getImageData(0, 0, w, h).data, T = thr / 100 * 255, dark = new Uint8Array(w * h);
        let n = 0; for (let i = 0; i < w * h; i++) { const l = 0.299 * px[i * 4] + 0.587 * px[i * 4 + 1] + 0.114 * px[i * 4 + 2]; dark[i] = (l < T) !== !!inv ? 1 : 0; n += dark[i]; }
        if (!n || n === w * h) { rej(new Error(n ? "Das ganze Bild ist dunkel – Schwelle senken." : "Im Bild ist nichts Dunkles – Schwelle erhöhen.")); return; }
        const N = Math.max(w, h), grid = { size: N, getModule: (c, r) => c < w && r < h && dark[r * w + c] === 1 }, { regions } = qrRegions(grid, false, 0);
        const d = regions.map((rg) => [rg.outer, ...rg.holes].map((L) => "M" + L.map(([x, y]) => x + " " + (N - y)).join("L") + "Z").join("")).join("");
        res(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${w} ${h}"><path fill-rule="evenodd" d="${d}"/></svg>`); };
      im.onerror = () => rej(new Error("Bild konnte nicht gelesen werden.")); im.src = url; });
    async function logoFromRaw() { const S = TS.sch; try { S.logo = await logoTrace(S.logoRaw, S.logoThr, S.logoInv); } catch (err) { toast(err.message); } saveTS(); schForm(); schRender(); }
    $("#s_logofile").addEventListener("change", async (e) => { const f = e.target.files[0]; if (!f) return; e.target.value = "";
      if (/svg/i.test(f.type) || /\\.svg$/i.test(f.name)) { const t = await f.text(); if (!/<svg[\\s>]/i.test(t)) { toast("Die SVG-Datei ist ungültig."); return; } TS.sch.logo = t; TS.sch.logoRaw = ""; saveTS(); schForm(); schRender(); toast("Logo gespeichert – wird ab jetzt verwendet."); return; }
      if (!/^image\\//.test(f.type)) { toast("Bitte SVG, PNG oder JPG laden."); return; }
      const url = await new Promise((r) => { const fr = new FileReader(); fr.onload = () => r(fr.result); fr.readAsDataURL(f); });
      const sm = await new Promise((r) => { const im = new Image(); im.onload = () => { const k = Math.min(1, 900 / Math.max(im.naturalWidth, im.naturalHeight)), c = document.createElement("canvas"); c.width = Math.round(im.naturalWidth * k); c.height = Math.round(im.naturalHeight * k);
        const g = c.getContext("2d"); g.fillStyle = "#fff"; g.fillRect(0, 0, c.width, c.height); g.drawImage(im, 0, 0, c.width, c.height); r(c.toDataURL("image/png")); }; im.onerror = () => r(""); im.src = url; });
      if (!sm) { toast("Bild konnte nicht gelesen werden."); return; }
      TS.sch.logoRaw = sm; await logoFromRaw(); toast("Logo aus dem Bild nachgezeichnet – mit der Schwelle feinstellen."); });
    { let tm = 0; $("#s_logothr").addEventListener("input", (e) => { TS.sch.logoThr = +e.target.value; $("#s_logothrv").textContent = TS.sch.logoThr + " %"; clearTimeout(tm); tm = setTimeout(logoFromRaw, 250); }); }
    $("#s_logoinv").addEventListener("change", (e) => { TS.sch.logoInv = e.target.checked; logoFromRaw(); });
    $("#s_logoclear").addEventListener("click", () => { TS.sch.logo = ""; TS.sch.logoRaw = ""; saveTS(); schForm(); schRender(); });''')
open(p, "w", encoding="utf-8").write(s); print("Werksschild v3:", p)
