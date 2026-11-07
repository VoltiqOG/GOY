"""Werkzeuge: „Bild → SVG“ – Pixelbild (PNG/JPG/WebP) als glatte Vektorflächen für den Laser.

Aufruf: python patch_vektor.py <unverschluesselte index.html>
Verfahren: Graustufen → Schwelle (automatisch nach Otsu oder von Hand) → kleine Flecken entfernen →
Umrisse nachfahren → Treppenstufen über Kantenmitten glätten → Douglas-Peucker → Bézier-Kurven mit
Eckenerkennung (scharfe Ecken bleiben eckig). Das Logo im Typenschild nutzt dasselbe Verfahren.
"""
import sys

path = sys.argv[1]
s = open(path, encoding="utf-8").read()


def rep(a, b, n=1):
    global s
    if s.count(a) != n:
        raise SystemExit(f"Stelle {s.count(a)}× statt {n}× gefunden: " + a[:90])
    s = s.replace(a, b)


# ---------- Schalter und Bereich
rep('''<button type="button" data-w="sch" aria-pressed="false">Typenschild (Laser)</button></div>''',
    '''<button type="button" data-w="sch" aria-pressed="false">Typenschild (Laser)</button><button type="button" data-w="vec" aria-pressed="false">Bild → SVG</button></div>''')
rep('''        <p class="knote">Angaben nach Maschinenverordnung (EU) 2023/1230 Art. 10 Abs. 5–7 und Anhang III 1.7.3;''',
    '''        <p class="knote">Angaben nach Maschinenverordnung (EU) 2023/1230 Art. 10 Abs. 5–7 und Anhang III 1.7.3;''')
i = s.find('''        <p class="knote">Angaben nach Maschinenverordnung (EU) 2023/1230 Art. 10 Abs. 5–7''')
j = s.find("</div>\n    </section>", i)
if i < 0 or j < 0:
    raise SystemExit("Ende des Typenschild-Bereichs nicht gefunden")
j += len("</div>\n")
s = s[:j] + '''      <div id="w_vec" hidden>
        <div class="ksech"><span class="kstep">1</span><div><h3>Bild → SVG</h3><small>PNG oder JPG laden – wird zu glatten Vektorflächen zum Gravieren oder zu einer Kontur zum Schneiden. Am besten mit Logos, Schriftzügen, Symbolen und Strichzeichnungen; Fotos bitte als Bitmap direkt in XCS gravieren (Kapitel 10.5).</small></div></div>
        <div class="wgrid">
          <form class="wform" id="v_form" autocomplete="off">
            <div class="wfull sce"><span id="v_name">kein Bild geladen</span><label class="kbtn sm">Bild laden (PNG, JPG, WebP)<input type="file" id="v_file" accept="image/png,image/jpeg,image/webp,image/bmp,image/gif" hidden></label></div>
            <label class="wchk"><input name="auto" type="checkbox"> Schwelle automatisch</label>
            <label class="wchk"><input name="inv" type="checkbox"> Umkehren (helles Motiv auf dunklem Grund)</label>
            <label class="wfull" id="v_thrl">Schwelle hell/dunkel <b id="v_thrv"></b><input name="thr" type="range" min="5" max="95" step="1"></label>
            <label>Glättung<select name="sm"><option value="0">aus (Pixelkanten)</option><option value="1">fein</option><option value="2">mittel (empfohlen)</option><option value="3">stark</option></select></label>
            <label>Flecken entfernen bis (Pixel)<input name="spk" type="number" min="0" step="1"></label>
            <label>Breite der SVG (mm)<input name="wmm" type="number" min="1" step="0.5"></label>
            <label>Auflösung (lange Seite)<select name="res"><option value="600">600 px – schnell</option><option value="1000">1000 px (empfohlen)</option><option value="1600">1600 px – feine Details</option></select></label>
            <label class="wfull">Ausgabe<select name="out"><option value="fill">Fläche gravieren (schwarz gefüllt)</option><option value="cut">Umriss schneiden (rote Haarlinie)</option><option value="both">beides – Gravur und Umriss</option></select></label>
          </form>
          <div class="wprev"><div class="wpbox vpbox" id="v_prev"><p class="knote">Noch kein Bild geladen.</p></div><div class="krow"><button type="button" class="kbtn" id="v_svg" disabled>SVG herunterladen</button><button type="button" class="kbtn ghost" id="v_logo" disabled>Als Logo ins Typenschild</button><button type="button" class="kbtn ghost" id="v_orig" disabled aria-pressed="false">Original darüberlegen</button></div><div class="kinfo" id="v_info"></div></div>
        </div>
        <p class="knote">Tipps: Bild möglichst groß und scharf, kein JPG-Rauschen (PNG ist besser). Feine Linien unter ca. 0,1 mm verschwinden beim Gravieren – dann Breite erhöhen. In XCS die SVG importieren, Ebene „gravieren“ als Füllung (Gravieren), Ebene „schneiden“ als Schneiden einstellen.</p>
      </div>
''' + s[j:]

rep('''$("#w_sch").hidden = b.dataset.w !== "sch"; });''', '''$("#w_sch").hidden = b.dataset.w !== "sch"; $("#w_vec").hidden = b.dataset.w !== "vec"; });''')
rep('''.wprev{display:flex;flex-direction:column;gap:var(--space-sm);min-width:0}''',
    '''.wprev{display:flex;flex-direction:column;gap:var(--space-sm);min-width:0}
.vpbox{position:relative;min-height:220px;display:grid;place-items:center;background:repeating-conic-gradient(var(--bg2) 0 25%,transparent 0 50%) 0 0/16px 16px;border-radius:12px;overflow:hidden}
.vpbox svg{display:block;width:100%;height:auto;max-height:520px}
.vpbox img{position:absolute;inset:0;width:100%;height:100%;object-fit:contain;opacity:.45;pointer-events:none}''')

# ---------- Kern: Maske → glatte Pfade (ersetzt die Treppen-Nachzeichnung des Logos)
rep('''    // Pixelbild → Vektorflächen: Graustufen, Schwelle, Umrisse wie beim QR-Code nachfahren (eine Fläche pro zusammenhängendem Bereich)
    const logoTrace = (url, thr, inv) => new Promise((res, rej) => { const im = new Image();''',
    r'''    // ---------- Pixelbild → glatte Vektorpfade (für „Bild → SVG“ und das Logo im Typenschild)
    const loadImg = (url) => new Promise((res, rej) => { const im = new Image(); im.onload = () => res(im); im.onerror = () => rej(new Error("Bild konnte nicht gelesen werden.")); im.src = url; });
    function vecMask(im, maxPx, thr, inv, auto) {
      const k = Math.min(1, maxPx / Math.max(im.naturalWidth, im.naturalHeight)), w = Math.max(1, Math.round(im.naturalWidth * k)), h = Math.max(1, Math.round(im.naturalHeight * k));
      const cv = document.createElement("canvas"); cv.width = w; cv.height = h; const g = cv.getContext("2d", { willReadFrequently: true }); g.fillStyle = "#fff"; g.fillRect(0, 0, w, h); g.drawImage(im, 0, 0, w, h);
      const px = g.getImageData(0, 0, w, h).data, L = new Uint8Array(w * h), hist = new Float64Array(256);
      for (let i = 0; i < w * h; i++) { const a = px[i * 4 + 3] / 255, l = (0.299 * px[i * 4] + 0.587 * px[i * 4 + 1] + 0.114 * px[i * 4 + 2]) * a + 255 * (1 - a); L[i] = l; hist[L[i]]++; }
      let T = thr / 100 * 255;
      if (auto) { let sum = 0, sB = 0, wB = 0, best = -1; for (let t = 0; t < 256; t++) sum += t * hist[t]; // Otsu
        for (let t = 0; t < 256; t++) { wB += hist[t]; if (!wB) continue; const wF = w * h - wB; if (!wF) break; sB += t * hist[t]; const mB = sB / wB, mF = (sum - sB) / wF, v = wB * wF * (mB - mF) ** 2; if (v > best) { best = v; T = t + 0.5; } } }
      const dark = new Uint8Array(w * h); let n = 0; for (let i = 0; i < w * h; i++) { dark[i] = (L[i] < T) !== !!inv ? 1 : 0; n += dark[i]; }
      return { w, h, dark, n, thr: Math.round(T / 255 * 100) };
    }
    function despeckle(m, w, h, minA) { // zusammenhängende Flecken (und Löcher) kleiner als minA Pixel umdrehen
      if (!(minA > 0)) return; const seen = new Uint8Array(w * h), st = [], comp = [];
      for (let i0 = 0; i0 < w * h; i0++) { if (seen[i0]) continue; const v = m[i0]; let edge = false; comp.length = 0; st.push(i0); seen[i0] = 1;
        while (st.length) { const i = st.pop(); comp.push(i); const x = i % w, y = (i / w) | 0; if (x === 0 || y === 0 || x === w - 1 || y === h - 1) edge = true;
          if (x > 0 && !seen[i - 1] && m[i - 1] === v) { seen[i - 1] = 1; st.push(i - 1); } if (x < w - 1 && !seen[i + 1] && m[i + 1] === v) { seen[i + 1] = 1; st.push(i + 1); }
          if (y > 0 && !seen[i - w] && m[i - w] === v) { seen[i - w] = 1; st.push(i - w); } if (y < h - 1 && !seen[i + w] && m[i + w] === v) { seen[i + w] = 1; st.push(i + w); } }
        if (comp.length < minA && (v === 1 || !edge)) for (const i of comp) m[i] = 1 - v; }
    }
    function dpClosed(P, tol) { // Douglas-Peucker für geschlossene Linienzüge
      if (P.length < 5) return P; let far = 0, fd = -1; for (let i = 1; i < P.length; i++) { const d = (P[i][0] - P[0][0]) ** 2 + (P[i][1] - P[0][1]) ** 2; if (d > fd) { fd = d; far = i; } }
      const keep = new Uint8Array(P.length); keep[0] = keep[far] = 1;
      const run = (a, b) => { const st = [[a, b]]; while (st.length) { const [i, j] = st.pop(); const A = P[i], B = P[j % P.length], dx = B[0] - A[0], dy = B[1] - A[1], l = Math.hypot(dx, dy) || 1e-9; let mi = -1, md = tol;
        for (let k = i + 1; k < j; k++) { const C = P[k % P.length], d = Math.abs(dx * (A[1] - C[1]) - dy * (A[0] - C[0])) / l; if (d > md) { md = d; mi = k; } } if (mi > 0) { keep[mi % P.length] = 1; st.push([i, mi], [mi, j]); } } };
      run(0, far); run(far, P.length); return P.filter((_, i) => keep[i]);
    }
    function vecLoops(dark, w, h, sm) { // Maske → Liste geschlossener Linienzüge (Pixel, y nach unten), geglättet
      const N = Math.max(w, h), grid = { size: N, getModule: (c, r) => c < w && r < h && dark[r * w + c] === 1 }, { regions } = qrRegions(grid, false, 0), loops = [];
      const tol = [0, 0.45, 0.7, 1.1][sm] || 0;
      for (const rg of regions) for (const L0 of [rg.outer, ...rg.holes]) { const L = L0.map(([x, y]) => [x, N - y]);
        if (!sm) { loops.push(L); continue; }
        const D = []; for (let i = 0; i < L.length; i++) { const a = L[i], b = L[(i + 1) % L.length], dx = Math.sign(b[0] - a[0]), dy = Math.sign(b[1] - a[1]), len = Math.abs(b[0] - a[0]) + Math.abs(b[1] - a[1]);
          if (len <= 1.01) D.push([(a[0] + b[0]) / 2, (a[1] + b[1]) / 2]); else { D.push([a[0] + dx * 0.5, a[1] + dy * 0.5]); D.push([b[0] - dx * 0.5, b[1] - dy * 0.5]); } }
        let Q = D; for (let it = 0; it < [0, 1, 2, 3][sm] && Q.length > 8; it++) { const n = Q.length; Q = Q.map((p, i) => { const a = Q[(i - 1 + n) % n], b = Q[(i + 1) % n], ux = p[0] - a[0], uy = p[1] - a[1], vx = b[0] - p[0], vy = b[1] - p[1];
          const c = (ux * vx + uy * vy) / ((Math.hypot(ux, uy) * Math.hypot(vx, vy)) || 1); return c < 0.2 ? p : [(a[0] + 2 * p[0] + b[0]) / 4, (a[1] + 2 * p[1] + b[1]) / 4]; }); } // Treppen weich ausgleichen, echte Ecken (> ca. 80°) bleiben
        const S = dpClosed(Q, tol); if (S.length >= 3) loops.push(S); }
      return loops;
    }
    function loopD(P, s, sm, f = (v) => +v.toFixed(3)) { // Linienzug → Pfad; mit Glättung als Bézier-Kurven, scharfe Ecken bleiben Ecken
      const X = (p) => f(p[0] * s) + " " + f(p[1] * s), n = P.length; if (!sm || n < 4) return "M" + P.map(X).join("L") + "Z";
      const corner = P.map((p, i) => { const a = P[(i - 1 + n) % n], b = P[(i + 1) % n], ux = p[0] - a[0], uy = p[1] - a[1], vx = b[0] - p[0], vy = b[1] - p[1], c = (ux * vx + uy * vy) / ((Math.hypot(ux, uy) * Math.hypot(vx, vy)) || 1); return c < [1, 0.55, 0.45, 0.3][sm]; });
      const tan = P.map((p, i) => { const a = P[(i - 1 + n) % n], b = P[(i + 1) % n], la = Math.hypot(p[0] - a[0], p[1] - a[1]), lb = Math.hypot(b[0] - p[0], b[1] - p[1]), tx = b[0] - a[0], ty = b[1] - a[1], tl = Math.hypot(tx, ty) || 1, m = Math.min(la, lb) * 0.5; return [tx / tl * m, ty / tl * m]; });
      let d = "M" + X(P[0]);
      for (let i = 0; i < n; i++) { const a = P[i], b = P[(i + 1) % n], j = (i + 1) % n;
        if (corner[i] && corner[j]) { d += "L" + X(b); continue; }
        const c1 = corner[i] ? a : [a[0] + tan[i][0] * 0.67, a[1] + tan[i][1] * 0.67], c2 = corner[j] ? b : [b[0] - tan[j][0] * 0.67, b[1] - tan[j][1] * 0.67];
        d += "C" + X(c1) + " " + X(c2) + " " + X(b); }
      return d + "Z";
    }
    const logoTrace = (url, thr, inv) => loadImg(url).then((im) => { const M = vecMask(im, 1000, thr, inv, false);
      if (!M.n || M.n === M.w * M.h) throw new Error(M.n ? "Das ganze Bild ist dunkel – Schwelle senken." : "Im Bild ist nichts Dunkles – Schwelle erhöhen.");
      despeckle(M.dark, M.w, M.h, 12); const d = vecLoops(M.dark, M.w, M.h, 2).map((L) => loopD(L, 1, 2, (v) => +v.toFixed(2))).join("");
      return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${M.w} ${M.h}"><path fill-rule="evenodd" d="${d}"/></svg>`; });
    const logoTraceOld = (url, thr, inv) => new Promise((res, rej) => { const im = new Image();''')

# ---------- Werkzeug „Bild → SVG“
rep('''    $("#w_seg").addEventListener("click", (e) =>''', r'''    // ---------- Werkzeug „Bild → SVG“
    const VDEF = { auto: true, inv: false, thr: 50, sm: "2", spk: 20, wmm: 80, res: "1000", out: "fill" };
    TS.vec = { ...VDEF, ...(TS.vec || {}) }; let vImg = null, vName = "Bild", vRes = null;
    function vecForm() { const f = $("#v_form"), V = TS.vec; Object.entries(V).forEach(([k, v]) => { const el = f.elements[k]; if (!el) return; if (el.type === "checkbox") el.checked = !!v; else el.value = v; }); $("#v_thrv").textContent = V.thr + " %"; $("#v_thrl").querySelector("input").disabled = !!V.auto; }
    function vecRender() {
      const V = TS.vec, info = $("#v_info"), box = $("#v_prev"); ["v_svg", "v_logo", "v_orig"].forEach((id) => { $("#" + id).disabled = !vImg; }); if (!vImg) return;
      const t0 = performance.now(), M = vecMask(vImg, +V.res, V.thr, V.inv, V.auto); if (V.auto) { V.thr = M.thr; $("#v_thrv").textContent = M.thr + " % (automatisch)"; $("#v_thrl").querySelector("input").value = M.thr; }
      if (!M.n || M.n === M.w * M.h) { box.innerHTML = `<p class="knote">${M.n ? "Das ganze Bild ist dunkel – Schwelle senken oder „Umkehren“." : "Im Bild ist nichts Dunkles – Schwelle erhöhen oder „Umkehren“."}</p>`; info.innerHTML = ""; vRes = null; return; }
      despeckle(M.dark, M.w, M.h, Math.round(num(V.spk)));
      const sm = +V.sm, loops = vecLoops(M.dark, M.w, M.h, sm), wmm = Math.max(1, num(V.wmm)), k = wmm / M.w, hmm = M.h * k;
      const d = loops.map((L) => loopD(L, k, sm)).join(""), nodes = loops.reduce((a, L) => a + L.length, 0);
      const fill = V.out !== "cut" ? `<g id="gravieren" fill="#000" fill-rule="evenodd"><path d="${d}"/></g>` : "", cut = V.out !== "fill" ? `<g id="schneiden" fill="none" stroke="#ff0000" stroke-width="0.1"><path d="${d}"/></g>` : "";
      const svg = (prev) => `<svg xmlns="http://www.w3.org/2000/svg" width="${+wmm.toFixed(2)}mm" height="${+hmm.toFixed(2)}mm" viewBox="0 0 ${+wmm.toFixed(3)} ${+hmm.toFixed(3)}">${fill}${prev && cut ? cut.replace('stroke-width="0.1"', 'stroke-width="1.2" vector-effect="non-scaling-stroke"') : cut}</svg>`;
      vRes = { svg, d, w: M.w, h: M.h, k };
      box.innerHTML = svg(true).replace("<svg ", '<svg role="img" aria-label="Vorschau Vektor" ') + ($("#v_orig").getAttribute("aria-pressed") === "true" ? `<img src="${vImg.src}" alt="">` : "");
      const px = wmm / M.w, msgs = [["ok", `${loops.length} ${loops.length === 1 ? "Umriss" : "Umrisse"}, ${nodes} Punkte · ${n1(wmm, 1)} × ${n1(hmm, 1)} mm · 1 Pixel = ${n1(px, 3)} mm · ${Math.round(performance.now() - t0)} ms`]];
      if (px > 0.12) msgs.push(["warn", `Ein Pixel ist ${n1(px, 2)} mm groß – bei dieser Breite werden Kanten grob. Höhere Auflösung wählen oder ein größeres Bild laden.`]);
      if (nodes > 60000) msgs.push(["warn", "Sehr viele Punkte – XCS wird langsam. Glättung erhöhen, Flecken entfernen oder Auflösung senken; Fotos besser als Bitmap gravieren."]);
      if (V.out !== "fill") msgs.push(["", "Umriss schneiden: Innere Umrisse (Löcher) werden mit ausgeschnitten – in XCS innere Konturen zuerst schneiden lassen, damit das Teil nicht verrutscht (Kapitel 10.12)."]);
      info.innerHTML = msgs.map(([c, t]) => `<p class="kmsg ${c}">${t}</p>`).join("");
    }
    { let tm = 0; $("#v_form").addEventListener("input", (e) => { const el = e.target; if (!el.name) return; TS.vec[el.name] = el.type === "checkbox" ? el.checked : el.type === "number" ? num(el.value) : el.value;
      if (el.name === "thr") $("#v_thrv").textContent = el.value + " %"; if (el.name === "auto") vecForm(); saveTS(); clearTimeout(tm); tm = setTimeout(vecRender, el.type === "range" ? 120 : 30); }); }
    $("#v_file").addEventListener("change", async (e) => { const f = e.target.files[0]; e.target.value = ""; if (!f) return; if (!/^image\//.test(f.type)) { toast("Bitte PNG, JPG oder WebP laden."); return; }
      const url = await new Promise((r) => { const fr = new FileReader(); fr.onload = () => r(fr.result); fr.readAsDataURL(f); });
      try { vImg = await loadImg(url); } catch (err) { toast(err.message); return; } vName = f.name.replace(/\.[^.]+$/, ""); $("#v_name").textContent = `${f.name} · ${vImg.naturalWidth} × ${vImg.naturalHeight} px`; vecRender(); });
    $("#v_orig").addEventListener("click", (e) => { const b = e.currentTarget; b.setAttribute("aria-pressed", b.getAttribute("aria-pressed") === "true" ? "false" : "true"); vecRender(); });
    $("#v_svg").addEventListener("click", () => { if (!vRes) return; offerFile(fileSafe(vName) + ".svg", `<?xml version="1.0" encoding="UTF-8"?>\n` + vRes.svg(false), "image/svg+xml"); });
    $("#v_logo").addEventListener("click", () => { if (!vRes) return; TS.sch.logo = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${vRes.w} ${vRes.h}"><path fill-rule="evenodd" d="${vRes.d.replace(/-?\d+(\.\d+)?/g, (v) => +(+v / vRes.k).toFixed(2))}"/></svg>`; TS.sch.logoRaw = ""; saveTS(); schForm(); schRender(); toast("Als Logo ins Typenschild übernommen."); });
    vecForm();
    $("#w_seg").addEventListener("click", (e) =>''')

rep('''TS = { qr: { ...TS.qr, ...v.qr }, sch: v.sch || {} };''', '''TS = { qr: { ...TS.qr, ...v.qr }, sch: v.sch || {}, vec: v.vec };''')
open(path, "w", encoding="utf-8").write(s)
print("Bild → SVG:", path)
