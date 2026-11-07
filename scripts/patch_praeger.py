"""Werkzeuge: Präger (3D-Druck) – Prägewalzen für den Makerspace.Online-Visitenkartenpräger und flache Prägeplatten.

Aufruf: python patch_praeger.py <unverschluesselte index.html>  (nach patch_visitenkarte.py und patch_design.py)
- Motiv: Text (bis 3 Zeilen) oder Bild (PNG/JPG/SVG, wird nachgezeichnet), Lage auf der Karte wählbar
- Walzen: Patrize (erhaben) und Matrize (vertieft, gespiegelt, um Papierdicke + Spiel aufgeweitet) als STL;
  Vierkant-Aufnahme für die Original-Zahnräder (13,1 mm), Matrize um eine halbe Zahnteilung (7,5°) versetzt,
  damit beide Markierkerben gleichzeitig vorne stehen; Maße aus der Original-3MF (Achsabstand 30,1 mm, Innenhöhe 80,3 mm)
- Platten: Patrize und Matrize als STEP, Passstifte Ø4/Ø5 (verdrehsicher), Kartenanschlag auf der Matrize
"""
import sys

path = sys.argv[1]
s = open(path, encoding="utf-8").read()


def rep(a, b, n=1):
    global s
    if s.count(a) != n:
        raise SystemExit(f"Stelle {s.count(a)}× statt {n}× gefunden: " + a[:90])
    s = s.replace(a, b)


rep('''<button type="button" data-w="vk" aria-pressed="false">Visitenkarte (Laser)</button></div>''',
    '''<button type="button" data-w="vk" aria-pressed="false">Visitenkarte (Laser)</button><button type="button" data-w="pr" aria-pressed="false">Präger (3D-Druck)</button></div>''')
rep('''$("#w_vk").hidden = b.dataset.w !== "vk"; if (b.dataset.w === "vk") vkRender(); });''',
    '''$("#w_vk").hidden = b.dataset.w !== "vk"; if (b.dataset.w === "vk") vkRender(); $("#w_pr").hidden = b.dataset.w !== "pr"; if (b.dataset.w === "pr") prRender(); b.scrollIntoView({ block: "nearest", inline: "nearest" }); });''')
rep('''/^rechner-werkzeuge-(qr|sch|vk|vec)$/''', '''/^rechner-werkzeuge-(qr|sch|vk|vec|pr)$/''')

UI = '''      <div id="w_pr" hidden>
        <div class="ksech"><span class="kstep">1</span><div><h3>Präger für Visitenkarten</h3><small>Text oder Bild rein, Patrize (erhaben) und Matrize (vertieft) drucken, Karte durchdrehen bzw. pressen. Walzen passen in den Makerspace.Online-Präger (Original-Gehäuse und -Zahnräder), Platten funktionieren ohne Gehäuse im Schraubstock.</small></div></div>
        <div class="wgrid">
          <form class="wform" id="e_form" autocomplete="off">
            <label class="wfull">Werkzeug<select name="mode"><option value="walze">Prägewalzen (Makerspace-Präger) – STL</option><option value="platte">Prägeplatten (flach, Schraubstock) – STEP</option></select></label>
            <label>Motiv<select name="src"><option value="text">Text</option><option value="bild">Bild / Logo</option></select></label>
            <label>Lage auf der Karte<select name="pos"><option value="mm">mittig</option><option value="om">oben mittig</option><option value="um">unten mittig</option><option value="ol">oben links</option><option value="or">oben rechts</option><option value="ul">unten links</option><option value="ur">unten rechts</option></select></label>
            <label class="wfull e_t">Zeile 1<input name="t1" maxlength="40"></label>
            <label class="e_t">Zeile 2<input name="t2" maxlength="40"></label>
            <label class="e_t">Zeile 3<input name="t3" maxlength="40"></label>
            <label class="e_t">Schrifthöhe (Versal, mm)<input name="cap" type="number" min="2" max="20" step="0.5"></label>
            <label class="wchk e_t"><input name="bold" type="checkbox"> fett (empfohlen)</label>
            <div class="wfull sce e_b"><span id="e_imgname">kein Bild geladen</span><label class="kbtn sm">Bild laden (PNG, JPG, SVG)<input type="file" id="e_file" accept="image/png,image/jpeg,image/webp,image/svg+xml,.svg" hidden></label><button type="button" class="kbtn sm ghost" id="e_logots">Logo vom Typenschild</button></div>
            <label class="e_b">Bildbreite (mm)<input name="iw" type="number" min="5" max="85" step="0.5"></label>
            <label class="wchk e_b"><input name="inv" type="checkbox"> Umkehren (helles Motiv)</label>
            <label class="wfull e_b">Schwelle hell/dunkel <b id="e_thrv"></b><input name="thr" type="range" min="5" max="95" step="1"></label>
            <label>Kartenformat<select name="fmt"><option value="85x55">85 × 55 mm</option><option value="90x50">90 × 50 mm</option><option value="86x54">85,6 × 54 mm</option></select></label>
            <label>Kartendicke (mm)<input name="t" type="number" min="0.1" max="0.8" step="0.05"></label>
            <label>Reliefhöhe (mm)<input name="h" type="number" min="0.3" max="1.2" step="0.05"></label>
            <label>Spiel Matrize (mm)<input name="c" type="number" min="0" max="0.5" step="0.05"></label>
            <details class="wfull e_more e_w"><summary>Maße des Präger-Gehäuses (vorbelegt aus der Original-3MF)</summary><div class="e_mg">
              <label>Achsabstand (mm)<input name="A" type="number" min="20" max="60" step="0.05"></label>
              <label>Walzenlänge (mm)<input name="L" type="number" min="20" max="120" step="0.1"></label>
              <label>Vierkant am Zahnrad (mm)<input name="sq" type="number" min="5" max="25" step="0.05"></label>
              <label>Spiel Vierkant (mm)<input name="sqs" type="number" min="0" max="0.8" step="0.05"></label>
              <label>Karte über Walzenunterkante (mm)<input name="z0" type="number" min="0" max="10" step="0.1"></label>
              <label>Netzauflösung<select name="res"><option value="0.35">0,35 mm – kleine Datei</option><option value="0.25">0,25 mm (empfohlen)</option><option value="0.18">0,18 mm – fein, große Datei</option></select></label>
            </div></details>
            <details class="wfull e_more e_p"><summary>Plattenmaße</summary><div class="e_mg">
              <label>Plattenstärke (mm)<input name="pb" type="number" min="2" max="10" step="0.5"></label>
              <label>Rand um die Karte (mm)<input name="pm" type="number" min="8" max="30" step="1"></label>
              <label class="wchk"><input name="stop" type="checkbox"> Kartenanschlag auf der Matrize</label>
            </div></details>
          </form>
          <div class="wprev"><div class="wpbox prbox" id="e_prev"></div>
            <div class="krow"><button type="button" class="kbtn pri e_w" id="e_m">Patrize-Walze (STL)</button><button type="button" class="kbtn pri e_w" id="e_f">Matrize-Walze (STL)</button><button type="button" class="kbtn pri e_p" id="e_pm">Patrize-Platte (STEP)</button><button type="button" class="kbtn pri e_p" id="e_pf">Matrize-Platte (STEP)</button><button type="button" class="kbtn ghost" id="e_reset">Beispiel laden</button></div><div class="kinfo" id="e_info"></div></div>
        </div>
        <ol class="knote e_w e_how"><li><b>Drucken:</b> Walzen stehend, ohne Stützen, 0,12–0,16 mm Schichthöhe, PETG oder PLA, 3 Wände. Die Kerbe oben ist die Markierung – Walzen nicht kopfüber einbauen.</li><li><b>Einbauen (Blick in die offene Seite):</b> Matrize links, Patrize rechts, jeweils auf die Vierkante der Original-Zahnräder.</li><li><b>Ausrichten:</b> Knopf drehen, bis beide Kerben nach vorne zeigen. Steht eine Kerbe schief, diese Walze mit ihren Zahnrädern herausheben und um einen Zahn versetzt wieder einsetzen.</li><li><b>Prägen:</b> Karte mit der Vorderseite nach links (zur Matrize), linke Kartenkante voraus bis an den Walzenspalt schieben, Unterkante auf den Zahnrädern – dann Knopf gleichmäßig durchdrehen.</li></ol>
        <ol class="knote e_p e_how"><li><b>Drucken:</b> beide Platten liegend, Motiv nach oben, 0,12 mm Schichthöhe, 100 % Füllung im Motivbereich (oder 4 Wände + 40 % Füllung).</li><li><b>Prägen:</b> Karte mit der Vorderseite nach unten auf die Matrize legen, an den Anschlag schieben, Patrize umdrehen und mit den Stiften (Ø4 und Ø5) aufsetzen.</li><li><b>Pressen:</b> im Schraubstock mit zwei Brettchen oder einer Hebelpresse – gleichmäßig, nicht ruckartig. Große Flächen brauchen viel Kraft: lieber Konturen und Schrift als volle Flächen.</li></ol>
      </div>
'''
rep('''      <div id="w_vec" hidden>''', UI + '''      <div id="w_vec" hidden>''')
rep('''.vpbox{position:relative;''', '''.prbox{padding:18px;display:grid;gap:14px;place-items:center;background:var(--bg2);border-radius:12px}.prbox svg{display:block;width:100%;max-width:560px;height:auto}
.prbox .prcap{font:600 12px/1.3 var(--f-text);color:var(--fg2);text-align:center;margin:0}
.e_more{border:1px solid var(--line);border-radius:12px;padding:10px 12px}.e_more summary{cursor:pointer;font-weight:600;font-size:14px}.e_mg{display:grid;grid-template-columns:1fr 1fr;gap:var(--space-sm);margin-top:10px}
.e_how{padding-left:20px;display:grid;gap:4px}.e_how li{margin:0}
@media (max-width:900px){.wseg{overflow-x:auto;scrollbar-width:none;max-width:100%}.wseg::-webkit-scrollbar{display:none}.wseg button{flex:0 0 auto;white-space:nowrap}}
@media (min-width:1101px){.tgrid.tgrid{grid-template-columns:repeat(3,minmax(0,1fr))}}@media (max-width:1100px){.tgrid>li:last-child:nth-child(odd){grid-column:1/-1}}
.vpbox{position:relative;''')

JS = r'''    // ---------- Präger (3D-Druck): Prägewalzen für den Makerspace-Präger und flache Prägeplatten
    // Walzen-Koordinaten: Achse Z nach oben, X zur anderen Walze; Patrize bei X = −A/2 (dreht im Uhrzeigersinn), Matrize bei X = +A/2.
    // Kartenpunkt u (mm hinter der Vorderkante) trifft die Patrize unter φ = u/R und die Matrize unter φ = 180° − u/R; Kerbe bei φ = 90° (nach vorne).
    const PRDEF = { mode: "walze", src: "text", t1: "MUSTERMANN", t2: "Konstruktion", t3: "", cap: 6, bold: true, img: "", imgName: "", thr: 50, inv: false, iw: 40, pos: "mm", fmt: "85x55", t: 0.35, h: 0.6, c: 0.15, A: 30.1, L: 59.6, sq: 13.1, sqs: 0.3, z0: 0.8, res: "0.25", pb: 3, pm: 12, stop: true };
    TS.pr = { ...PRDEF, ...(TS.pr || {}) };
    let prLoops = null, prLoopsKey = "";
    const prCard = () => (TS.pr.fmt === "90x50" ? [90, 50] : TS.pr.fmt === "86x54" ? [85.6, 53.98] : [85, 55]);
    function prForm() { const f = $("#e_form"), P = TS.pr; Object.entries(P).forEach(([k, v]) => { const el = f.elements[k]; if (!el) return; if (el.type === "checkbox") el.checked = !!v; else el.value = v; });
      const w = P.mode === "walze", tx = P.src === "text"; $("#w_pr").querySelectorAll(".e_w").forEach((e) => { e.hidden = !w; }); $("#w_pr").querySelectorAll(".e_p").forEach((e) => { e.hidden = w; });
      f.querySelectorAll(".e_t").forEach((e) => { e.hidden = !tx; }); f.querySelectorAll(".e_b").forEach((e) => { e.hidden = tx; });
      $("#e_thrv").textContent = P.thr + " %"; $("#e_imgname").textContent = P.img ? (P.imgName || "Bild") + " ✓" : "kein Bild geladen"; }
    async function prTrace() { const P = TS.pr, key = P.img.length + "|" + P.img.slice(-40) + "|" + P.thr + "|" + P.inv; if (prLoops && prLoopsKey === key) return prLoops;
      const im = await loadImg(P.img), M = vecMask(im, 1000, P.thr, P.inv, false); if (!M.n || M.n === M.w * M.h) throw new Error(M.n ? "Das ganze Bild ist dunkel – Schwelle senken." : "Im Bild ist nichts Dunkles – Schwelle erhöhen.");
      despeckle(M.dark, M.w, M.h, 12); let x0 = M.w, y0 = M.h, x1 = 0, y1 = 0; for (let y = 0; y < M.h; y++) for (let x = 0; x < M.w; x++) if (M.dark[y * M.w + x]) { if (x < x0) x0 = x; if (x > x1) x1 = x; if (y < y0) y0 = y; if (y > y1) y1 = y; }
      prLoops = { loops: vecLoops(M.dark, M.w, M.h, 2), x0, y0, w: x1 - x0 + 1, h: y1 - y0 + 1 }; prLoopsKey = key; return prLoops; }
    // Motiv als Pfad in Karten-mm (Ursprung oben links, y nach unten), so wie man die Vorderseite liest
    async function prMotif(msgs) {
      const P = TS.pr, [W, H] = prCard(), m = 5; let d = "", bw = 0, bh = 0, rule = "nonzero", place;
      const at = (bw0, bh0) => { const x = P.pos.endsWith("l") ? m : P.pos.endsWith("r") ? W - m - bw0 : (W - bw0) / 2, y = P.pos.startsWith("o") ? m : P.pos.startsWith("u") ? H - m - bh0 : (H - bh0) / 2; return [x, y]; };
      if (P.src === "text") { const L = [P.t1, P.t2, P.t3].map((x) => String(x || "").trim()).filter(Boolean), cap = Math.max(2, num(P.cap)), pitch = cap * 1.55;
        if (!L.length) { msgs.push(["warn", "Noch kein Text – Zeile 1 ausfüllen."]); return null; }
        bw = Math.max(...L.map((x) => textWidth(x, cap, P.bold))); bh = cap + (L.length - 1) * pitch; const [x, y] = at(bw, bh);
        d = L.map((x2, i) => cmdsToD(textCmds(x2, x + bw / 2, y + cap + i * pitch, cap, P.bold, "middle"))).join(""); place = [x, y];
        const bad = [...new Set(L.join("").split("").filter((ch) => !FCH.has(ch)))]; if (bad.length) msgs.push(["warn", `Diese Zeichen hat die eingebaute Schrift nicht (werden „?“): ${bad.map(esc).join(" ")}`]);
        if (cap < 4) msgs.push(["warn", `Schrift ${n1(cap, 1)} mm – zu klein zum Prägen, Buchstaben laufen zu. Ab 5 mm, fett.`]); else if (cap < 5 || !P.bold) msgs.push(["warn", "Geprägte Schrift wird erst ab ca. 5 mm Versalhöhe und fett sauber – dünne Striche verschwinden im Karton."]);
      } else { if (!P.img) { msgs.push(["warn", "Noch kein Bild geladen."]); return null; }
        let T; try { T = await prTrace(); } catch (e) { msgs.push(["err", esc(e.message)]); return null; }
        const s = Math.max(5, num(P.iw)) / T.w; bw = T.w * s; bh = T.h * s; const [x, y] = at(bw, bh); place = [x, y];
        d = T.loops.map((Lp) => loopD(Lp.map(([a, b]) => [a - T.x0 + x / s, b - T.y0 + y / s]), s, 2)).join(""); rule = "evenodd"; }
      if (place[0] < 3 - 1e-6 || place[1] < 3 - 1e-6 || place[0] + bw > W - 3 + 1e-6 || place[1] + bh > H - 3 + 1e-6) msgs.push(["warn", `Motiv ${n1(bw, 1)} × ${n1(bh, 1)} mm reicht bis an den Kartenrand (unter 3 mm) – kleiner machen, der Rand reißt sonst ein.`]);
      return { d, rule, bw, bh, W, H };
    }
    // Motiv rastern (Kantenglättung = Bedeckung 0…1); grow = Aufweitung in mm (Minkowski mit runden Ecken)
    function prRaster(M, ppm, grow) {
      const w = Math.ceil(M.W * ppm), h = Math.ceil(M.H * ppm), cv = document.createElement("canvas"); cv.width = w; cv.height = h;
      const g = cv.getContext("2d", { willReadFrequently: true }); g.setTransform(ppm, 0, 0, ppm, 0, 0); const p = new Path2D(M.d); g.fillStyle = g.strokeStyle = "#000"; g.fill(p, M.rule);
      if (grow > 0) { g.lineWidth = 2 * grow; g.lineJoin = g.lineCap = "round"; g.stroke(p); }
      const px = g.getImageData(0, 0, w, h).data, a = new Float32Array(w * h); for (let i = 0; i < w * h; i++) a[i] = px[i * 4 + 3] / 255; return { w, h, a, ppm };
    }
    const prAt = (R, u, v) => { const x = u * R.ppm - 0.5, y = v * R.ppm - 0.5, i = Math.floor(x), j = Math.floor(y), fx = x - i, fy = y - j, A = (ii, jj) => (ii < 0 || jj < 0 || ii >= R.w || jj >= R.h ? 0 : R.a[jj * R.w + ii]);
      return A(i, j) * (1 - fx) * (1 - fy) + A(i + 1, j) * fx * (1 - fy) + A(i, j + 1) * (1 - fx) * fy + A(i + 1, j + 1) * fx * fy; };
    const prCov = (R, u, v, g) => { let s = 0; for (const a of [-g / 3, 0, g / 3]) for (const b of [-g / 3, 0, g / 3]) s += prAt(R, u + a, v + b); return s / 9; };
    function prGeo() { const P = TS.pr, t = Math.max(0.05, num(P.t)), Rb = (num(P.A) - t) / 2; return { P, t, Rb, h: Math.max(0.2, num(P.h)), c: Math.max(0, num(P.c)), L: num(P.L), z0: num(P.z0), sqa: (num(P.sq) + num(P.sqs)) / 2, sqr: 3.06 + num(P.sqs) / 2 }; }
    // Walze als geschlossenes Dreiecksnetz → binäre STL
    function prRoller(M, fem) {
      const G = prGeo(), { Rb, L, z0 } = G, g = Math.max(0.15, +G.P.res || 0.25), [W, H] = [M.W, M.H], N = Math.max(96, Math.round(2 * Math.PI * Rb / g / 4) * 4), zc = 0.5, n = Math.max(4, Math.round((L - 2 * zc) / g));
      const R = prRaster(M, 12, fem ? G.t + G.c : 0), dep = fem ? -(G.h + 0.2) : G.h, psi = fem ? 7.5 * Math.PI / 180 : 0;
      const Z = [0]; for (let k = 0; k <= n; k++) Z.push(zc + (L - 2 * zc) * k / n); Z.push(L); const NZ = Z.length;
      const V = new Float32Array(NZ * N * 3 + 2 * N * 3);
      for (let i = 0; i < NZ; i++) { const z = Z[i], end = i === 0 || i === NZ - 1, v = H - (z - z0);
        for (let j = 0; j < N; j++) { const ph = 2 * Math.PI * j / N; let r = Rb;
          if (end) r = Rb - 0.4; else { let u = fem ? Rb * (Math.PI - ph) : Rb * ph; u = ((u % (2 * Math.PI * Rb)) + 2 * Math.PI * Rb) % (2 * Math.PI * Rb);
            if (v > -1 && v < H + 1 && u < W + 1) r += dep * prCov(R, u, v, g);
            if (z > L - 3.2) { const da = Math.abs(((ph - Math.PI / 2 + Math.PI) % (2 * Math.PI)) - Math.PI) * Rb; if (da < 0.9) r -= 0.6 * (1 - da / 0.9); } } // Kerbe vorne oben
          const k = (i * N + j) * 3; V[k] = r * Math.cos(ph); V[k + 1] = r * Math.sin(ph); V[k + 2] = z; } }
      const sd = (x, y) => { const qx = Math.abs(x) - (G.sqa - G.sqr), qy = Math.abs(y) - (G.sqa - G.sqr); return Math.hypot(Math.max(qx, 0), Math.max(qy, 0)) + Math.min(Math.max(qx, qy), 0) - G.sqr; };
      const IN = NZ * N; for (let j = 0; j < N; j++) { const b = 2 * Math.PI * j / N - psi, cx = Math.cos(b), cy = Math.sin(b); let lo = 0, hi = G.sqa * 1.6; for (let it = 0; it < 40; it++) { const mid = (lo + hi) / 2; if (sd(cx * mid, cy * mid) < 0) lo = mid; else hi = mid; }
        const ph = 2 * Math.PI * j / N, r = lo; for (const [o, z] of [[0, 0], [N, L]]) { const k = (IN + o + j) * 3; V[k] = r * Math.cos(ph); V[k + 1] = r * Math.sin(ph); V[k + 2] = z; } }
      const T = [], O = (i, j) => i * N + (j % N), I0 = (j) => IN + (j % N), I1 = (j) => IN + N + (j % N);
      for (let i = 0; i < NZ - 1; i++) for (let j = 0; j < N; j++) T.push(O(i, j), O(i, j + 1), O(i + 1, j + 1), O(i, j), O(i + 1, j + 1), O(i + 1, j));
      for (let j = 0; j < N; j++) { T.push(I0(j), I1(j + 1), I0(j + 1), I0(j), I1(j), I1(j + 1)); // Innenwand (Normale zur Achse)
        T.push(O(0, j), I0(j + 1), O(0, j + 1), O(0, j), I0(j), I0(j + 1)); // Boden (−Z)
        T.push(O(NZ - 1, j), O(NZ - 1, j + 1), I1(j + 1), O(NZ - 1, j), I1(j + 1), I1(j)); } // Deckel (+Z)
      const nt = T.length / 3, buf = new ArrayBuffer(84 + nt * 50), dv = new DataView(buf), hd = `Praegewalze ${fem ? "Matrize" : "Patrize"} – su3dl`; for (let i = 0; i < Math.min(80, hd.length); i++) dv.setUint8(i, hd.charCodeAt(i) & 127);
      dv.setUint32(80, nt, true); let o = 84;
      for (let t = 0; t < nt; t++) { const a = T[3 * t] * 3, b = T[3 * t + 1] * 3, c = T[3 * t + 2] * 3, ux = V[b] - V[a], uy = V[b + 1] - V[a + 1], uz = V[b + 2] - V[a + 2], vx = V[c] - V[a], vy = V[c + 1] - V[a + 1], vz = V[c + 2] - V[a + 2];
        let nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx; const l = Math.hypot(nx, ny, nz) || 1; dv.setFloat32(o, nx / l, true); dv.setFloat32(o + 4, ny / l, true); dv.setFloat32(o + 8, nz / l, true); o += 12;
        for (const q of [a, b, c]) { dv.setFloat32(o, V[q], true); dv.setFloat32(o + 4, V[q + 1], true); dv.setFloat32(o + 8, V[q + 2], true); o += 12; } o += 2; }
      return new Uint8Array(buf);
    }
    // Motiv-Konturen aus dem Raster (Karten-mm, y nach unten)
    function prLoopsOf(M, grow) { const ppm = 10, R = prRaster(M, ppm, grow), dark = new Uint8Array(R.w * R.h); for (let i = 0; i < dark.length; i++) dark[i] = R.a[i] >= 0.5 ? 1 : 0; despeckle(dark, R.w, R.h, 6);
      return vecLoops(dark, R.w, R.h, 2).map((Lp) => Lp.map(([x, y]) => [x / ppm, y / ppm])); }
    function prPlates(M, fem) {
      const G = prGeo(), P = G.P, B = Math.max(2, num(P.pb)), mg = Math.max(8, num(P.pm)), W = M.W + 2 * mg, H = M.H + 2 * mg, x0 = mg, y0 = mg, d = G.h + 0.2;
      const rect = [[0, 0], [W, 0], [W, H], [0, H]], pins = [[6, 6, 2], [W - 6, H - 6, 2.5]], solids = [];
      const map = (Lp) => Lp.map(([u, v]) => [fem ? x0 + M.W - u : x0 + u, y0 + M.H - v]);
      if (!fem) { solids.push({ name: "Patrize_Platte", color: [0.9, 0.9, 0.9], z0: 0, z1: B, outer: rect, outerC: roundRectSegs(0, 0, W, H, 0), holes: [] });
        pins.forEach(([x, y, r], i) => solids.push({ name: "Stift_" + (i + 1), color: [0.9, 0.9, 0.9], z0: B, z1: B + 5, outer: ccw(x, y, r, 48), outerC: { cx: x, cy: y, r }, holes: [] }));
        nestLoops(prLoopsOf(M, 0).map(map)).forEach((rg, i) => solids.push({ name: "Relief_" + (i + 1), color: [0.15, 0.15, 0.15], z0: B, z1: B + G.h, outer: rg.outer, holes: rg.holes }));
      } else { const hp = pins.map(([x, y, r]) => [W - x, y, r + 0.2]); // Stifte nach dem Umdrehen gespiegelt, 0,2 mm Spiel
        solids.push({ name: "Matrize_Platte", color: [0.9, 0.9, 0.9], z0: 0, z1: B, outer: rect, outerC: roundRectSegs(0, 0, W, H, 0), holes: hp.map(([x, y, r]) => circle(x, y, r, 48)), holesC: hp.map(([x, y, r]) => ({ cx: x, cy: y, r })) });
        nestLoops([rect, ...prLoopsOf(M, G.t + G.c).map(map), ...hp.map(([x, y, r]) => circle(x, y, r, 48))]).forEach((rg, i) => solids.push({ name: "Matrize_Lage_" + (i + 1), color: [0.9, 0.9, 0.9], z0: B, z1: B + d, outer: rg.outer, holes: rg.holes }));
        if (P.stop) { const fx = x0 + M.W + 0.3, fy = y0 - 0.3, fw = 3; // Anschlag an linker Kartenkante (liegt rechts, Karte mit der Vorderseite nach unten) und Unterkante
          solids.push({ name: "Anschlag", color: [0.2, 0.45, 0.85], z0: B + d, z1: B + d + Math.max(0.2, G.t * 0.8), outer: [[x0, fy - fw], [fx + fw, fy - fw], [fx + fw, y0 + M.H], [fx, y0 + M.H], [fx, fy], [x0, fy]], holes: [] }); } }
      return { solids, W, H };
    }
    // Vorschau: Karte (geprägt) und abgewickelte Walzen
    let prM = null, prTok = 0;
    async function prRender() {
      const tok = ++prTok, P = TS.pr, msgs = [], M = await prMotif(msgs); if (tok !== prTok) return; prM = M;
      const G = prGeo(), [W, H] = prCard(), U = 2 * Math.PI * G.Rb, w = P.mode === "walze";
      const card = `<svg viewBox="-2 -2 ${W + 4} ${H + 4}" role="img" aria-label="Vorschau geprägte Karte"><defs><filter id="e_emb" x="-5%" y="-5%" width="110%" height="110%"><feGaussianBlur in="SourceAlpha" stdDeviation="0.25"/><feOffset dx="-0.25" dy="-0.25" result="hi"/><feGaussianBlur in="SourceAlpha" stdDeviation="0.3"/><feOffset dx="0.35" dy="0.35" result="sh"/><feFlood flood-color="#fff" flood-opacity=".9"/><feComposite in2="hi" operator="in" result="h2"/><feFlood flood-color="#000" flood-opacity=".38"/><feComposite in2="sh" operator="in" result="s2"/><feMerge><feMergeNode in="s2"/><feMergeNode in="h2"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
        <rect width="${W}" height="${H}" rx="1.5" fill="#f4f1ea" stroke="#d6d1c4" stroke-width="0.2"/>${M ? `<path d="${M.d}" fill="#f4f1ea" fill-rule="${M.rule}" filter="url(#e_emb)"/>` : ""}</svg>`;
      let roll = "";
      if (w && M) { const top = f3(G.L - G.z0 - H), x0 = (U - W) / 2, frame = (x, title, mir) => { const mk = mir ? (U + W) / 2 - U / 4 : x0 + U / 4;
          return `<g transform="translate(${x} 0)"><rect width="${f3(U)}" height="${f3(G.L)}" fill="#e7e9ee" stroke="#9aa1ad" stroke-width="0.25"/><rect x="${f3(x0)}" y="${top}" width="${W}" height="${H}" fill="none" stroke="#3b82f6" stroke-width="0.2" stroke-dasharray="1 0.8"/>
          <g transform="${mir ? `translate(${f3((U + W) / 2)} ${top}) scale(-1 1)` : `translate(${f3(x0)} ${top})`}"><path d="${M.d}" fill="${mir ? "#8a93a3" : "#2b3240"}" fill-rule="${M.rule}"/></g><path d="M${f3(mk - 0.9)} 0L${f3(mk)} 2.6L${f3(mk + 0.9)} 0Z" fill="#e5484d"/><text x="${f3(U / 2)}" y="${f3(G.L + 6)}" font-size="4.2" text-anchor="middle" fill="currentColor">${title}</text></g>`; };
        roll = `<svg viewBox="-2 -2 ${f3(2 * U + 14)} ${f3(G.L + 12)}" role="img" aria-label="Walzen abgewickelt">${frame(0, "Patrize (rechts) – erhaben", false)}${frame(U + 10, "Matrize (links) – vertieft, gespiegelt", true)}</svg>`; }
      $("#e_prev").innerHTML = `<p class="prcap">So sieht die Karte nach dem Prägen aus</p>${card}${roll ? `<p class="prcap">Walzen abgewickelt (Blick von außen, rote Kerbe = vorne, blau = Karte)</p>${roll}` : ""}`;
      if (M) { if (w) { if (W > U - 4) msgs.push(["err", `Karte ${n1(W, 1)} mm ist länger als der Walzenumfang (${n1(U, 1)} mm).`]); if (H + G.z0 > G.L - 3.3) msgs.push(["warn", `Karte ${n1(H, 1)} mm hoch, Walze ${n1(G.L, 1)} mm – oben überdeckt sich das Motiv mit der Kerbe. Motiv nicht ganz oben platzieren.`]);
          msgs.unshift(["ok", `Walzen Ø ${n1(2 * G.Rb, 2)} mm (Umfang ${n1(U, 1)} mm), Länge ${n1(G.L, 1)} mm, Spalt ${n1(G.t, 2)} mm = Kartendicke. Relief ${n1(G.h, 2)} mm, Matrize ${n1(G.h + 0.2, 2)} mm tief und ${n1(G.t + G.c, 2)} mm aufgeweitet.`]);
          msgs.push(["", "Vierkant-Aufnahme durchgehend (spart Material, druckt ohne Stützen). Die Matrize hat den Vierkant um 7,5° (eine halbe Zahnteilung) gedreht – sonst können beide Kerben nie gleichzeitig vorne stehen."]); }
        else msgs.unshift(["ok", `Platten ${n1(W + 2 * num(P.pm), 1)} × ${n1(H + 2 * num(P.pm), 1)} mm. Relief ${n1(G.h, 2)} mm, Matrize ${n1(G.h + 0.2, 2)} mm tief, ${n1(G.t + G.c, 2)} mm aufgeweitet. Stifte Ø4 und Ø5 (verdrehsicher), Löcher +0,4 mm.`]);
        if (G.t > 0.45) msgs.push(["warn", "Dicker Karton (über 0,45 mm) prägt sich schwer und bricht an den Kanten – Relief eher 0,8 mm, Spiel 0,2 mm."]); }
      $("#e_info").innerHTML = msgs.map(([c, t]) => `<p class="kmsg ${c}">${t}</p>`).join("");
      ["#e_m", "#e_f", "#e_pm", "#e_pf"].forEach((id) => { $(id).disabled = !M; });
    }
    { let tm = 0; $("#e_form").addEventListener("input", (e) => { const el = e.target; if (!el.name) return; TS.pr[el.name] = el.type === "checkbox" ? el.checked : el.type === "number" ? num(el.value) : el.value;
      if (["mode", "src", "thr"].includes(el.name)) prForm(); saveTS(); clearTimeout(tm); tm = setTimeout(prRender, el.name === "thr" ? 250 : 80); }); }
    $("#e_file").addEventListener("change", async (e) => { const f = e.target.files[0]; e.target.value = ""; if (!f) return;
      const url = await new Promise((r) => { const fr = new FileReader(); fr.onload = () => r(fr.result); fr.readAsDataURL(f); });
      const sm = await new Promise((r) => { const im = new Image(); im.onload = () => { const k = Math.min(1, 1000 / Math.max(im.naturalWidth || 1000, im.naturalHeight || 1000)), c = document.createElement("canvas"); c.width = Math.max(1, Math.round((im.naturalWidth || 1000) * k)); c.height = Math.max(1, Math.round((im.naturalHeight || 1000) * k));
        const g = c.getContext("2d"); g.fillStyle = "#fff"; g.fillRect(0, 0, c.width, c.height); g.drawImage(im, 0, 0, c.width, c.height); r(c.toDataURL("image/png")); }; im.onerror = () => r(""); im.src = url; });
      if (!sm) { toast("Bild konnte nicht gelesen werden."); return; } Object.assign(TS.pr, { img: sm, imgName: f.name, src: "bild" }); saveTS(); prForm(); prRender(); });
    $("#e_logots").addEventListener("click", () => { const svg = TS.sch && TS.sch.logo; if (!svg) { toast("Im Typenschild ist noch kein Logo geladen."); return; }
      const url = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svg); loadImg(url).then((im) => { const k = 1000 / Math.max(im.naturalWidth || 1, im.naturalHeight || 1), c = document.createElement("canvas"); c.width = Math.round((im.naturalWidth || 1000) * k); c.height = Math.round((im.naturalHeight || 1000) * k);
        const g = c.getContext("2d"); g.fillStyle = "#fff"; g.fillRect(0, 0, c.width, c.height); g.drawImage(im, 0, 0, c.width, c.height); Object.assign(TS.pr, { img: c.toDataURL("image/png"), imgName: "Logo Typenschild", src: "bild" }); saveTS(); prForm(); prRender(); }).catch(() => toast("Logo konnte nicht gelesen werden.")); });
    $("#e_reset").addEventListener("click", () => { const { img, imgName } = TS.pr; TS.pr = { ...PRDEF, img, imgName }; saveTS(); prForm(); prRender(); });
    const prName = () => fileSafe(TS.pr.src === "text" ? TS.pr.t1 || "Text" : (TS.pr.imgName || "Bild").replace(/\.[a-z0-9]+$/i, ""));
    const prGo = async (fn) => { await prRender(); if (!prM) { toast("Erst Text eingeben oder ein Bild laden."); return; } toast("Wird berechnet …"); await new Promise((r) => setTimeout(r, 30)); fn(prM); };
    $("#e_m").addEventListener("click", () => prGo((M) => offerFile(`Praegewalze_Patrize_${prName()}.stl`, prRoller(M, false), "model/stl")));
    $("#e_f").addEventListener("click", () => prGo((M) => offerFile(`Praegewalze_Matrize_${prName()}.stl`, prRoller(M, true), "model/stl")));
    $("#e_pm").addEventListener("click", () => prGo((M) => { const nm = `Praegeplatte_Patrize_${prName()}`; offerFile(nm + ".step", stepFile(prPlates(M, false).solids, nm), "application/step"); }));
    $("#e_pf").addEventListener("click", () => prGo((M) => { const nm = `Praegeplatte_Matrize_${prName()}`; offerFile(nm + ".step", stepFile(prPlates(M, true).solids, nm), "application/step"); }));
    prForm();
'''
rep('''    // ---------- Werkzeug „Bild → SVG“''', JS + '''    // ---------- Werkzeug „Bild → SVG“''')
rep('''TS = { qr: { ...TS.qr, ...v.qr }, sch: v.sch || {}, vec: v.vec, vk: v.vk };''', '''TS = { qr: { ...TS.qr, ...v.qr }, sch: v.sch || {}, vec: v.vec, vk: v.vk, pr: v.pr };''')

# Startseite: Werkzeugkarte
i = s.find('<a class="tcard a-grund" href="#rechner-werkzeuge-vec">')
if i < 0:
    raise SystemExit("Werkzeugkarte Bild → SVG nicht gefunden")
j = s.find("</a>", i) + 4
card = ('<a class="tcard a-druck" href="#rechner-werkzeuge-pr"><span class="ti"><svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">'
        '<circle cx="8" cy="8" r="4.5"/><circle cx="16" cy="8" r="4.5"/><path d="M8 8h.01M16 8h.01"/><rect x="5" y="15" width="14" height="5" rx="1"/><path d="M9 17.5h6"/></svg></span>'
        '<span class="tt">Präger (3D-Druck)</span><span class="td">Text oder Logo als Prägewalzen oder Prägeplatten für Visitenkarten</span></a>')
card = "</li><li>" + card
s = s[:j] + card + s[j:]

open(path, "w", encoding="utf-8").write(s)
print("Präger:", path)
