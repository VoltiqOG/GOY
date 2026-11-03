"""QR-Werkzeug: Eckenradius der Platte als echte Kreisbögen im STEP (statt Vieleck), Schrift feiner aufgelöst.
Aufruf über scripts/aktualisieren.py index.html scripts/patch_eckenradien.py"""
import sys
def patch_js(s):
    def R(a, b, n=1):
        nonlocal s
        assert s.count(a) == n, (a[:80], s.count(a)); s = s.replace(a, b)
    # Kontur aus Strecken und Kreisbögen (exakt) im STEP
    R('''          if (!Array.isArray(pts)) { // exakter Kreis {cx, cy, r}''', '''          if (pts && pts.segs) { // Kontur aus Strecken und exakten Kreisbögen (z. B. Platte mit Eckenradius)
            const S = pts.segs, n = S.length, vb = [], vt = [], eb = [], et = [], ev = [];
            for (const g of S) { vb.push(add(`VERTEX_POINT('',${P3(g.a[0], g.a[1], s.z0)})`)); vt.push(add(`VERTEX_POINT('',${P3(g.a[0], g.a[1], s.z1)})`)); }
            const curve = (g, z) => g.c ? add(`CIRCLE('',${add(`AXIS2_PLACEMENT_3D('',${P3(g.c[0], g.c[1], z)},${D3(0, 0, g.ccw ? 1 : -1)},${D3(1, 0, 0)})`)},${f3(g.r)})`)
              : (() => { const dx = g.b[0] - g.a[0], dy = g.b[1] - g.a[1], l = Math.hypot(dx, dy); return add(`LINE('',${P3(g.a[0], g.a[1], z)},${add(`VECTOR('',${D3(dx / l, dy / l, 0)},${f3(l)})`)})`); })();
            for (let i = 0; i < n; i++) { const g = S[i];
              eb.push(add(`EDGE_CURVE('',${vb[i]},${vb[(i + 1) % n]},${curve(g, s.z0)},.T.)`)); et.push(add(`EDGE_CURVE('',${vt[i]},${vt[(i + 1) % n]},${curve(g, s.z1)},.T.)`));
              ev.push(add(`EDGE_CURVE('',${vb[i]},${vt[i]},${add(`LINE('',${P3(g.a[0], g.a[1], s.z0)},${add(`VECTOR('',${D3(0, 0, 1)},${f3(s.z1 - s.z0)})`)})`)},.T.)`)); }
            for (let i = 0; i < n; i++) { const g = S[i];
              const loop = add(`EDGE_LOOP('',(${add(`ORIENTED_EDGE('',*,*,${eb[i]},.T.)`)},${add(`ORIENTED_EDGE('',*,*,${ev[(i + 1) % n]},.T.)`)},${add(`ORIENTED_EDGE('',*,*,${et[i]},.F.)`)},${add(`ORIENTED_EDGE('',*,*,${ev[i]},.F.)`)}))`);
              let surf, sense = ".T.";
              if (g.c) { surf = add(`CYLINDRICAL_SURFACE('',${add(`AXIS2_PLACEMENT_3D('',${P3(g.c[0], g.c[1], s.z0)},${D3(0, 0, 1)},${D3(1, 0, 0)})`)},${f3(g.r)})`); sense = g.ccw ? ".T." : ".F."; }
              else { const dx = g.b[0] - g.a[0], dy = g.b[1] - g.a[1], l = Math.hypot(dx, dy); surf = add(`PLANE('',${add(`AXIS2_PLACEMENT_3D('',${P3(g.a[0], g.a[1], s.z0)},${D3(dy / l, -dx / l, 0)},${D3(dx / l, dy / l, 0)})`)})`); }
              faces.push(add(`ADVANCED_FACE('',(${add(`FACE_OUTER_BOUND('',${loop},.T.)`)}),${surf},${sense})`)); }
            L.push({ eb, et }); continue;
          }
          if (!Array.isArray(pts)) { // exakter Kreis {cx, cy, r}''')
    R('''        const [ox, oy] = s.outerC ? [s.outerC.cx + s.outerC.r, s.outerC.cy] : s.outer[0];''', '''        const [ox, oy] = s.outerC ? (s.outerC.segs ? s.outerC.segs[0].a : [s.outerC.cx + s.outerC.r, s.outerC.cy]) : s.outer[0];''')
    # Platte: Außenkontur mit echten Eckenradien
    R('''    const circle = (cx, cy, r, n = 32) =>''', '''    const roundRectSegs = (x, y, w, h, r) => { r = Math.max(0, Math.min(r, w / 2 - 0.01, h / 2 - 0.01));
      if (r < 0.05) return { segs: [[x, y, x + w, y], [x + w, y, x + w, y + h], [x + w, y + h, x, y + h], [x, y + h, x, y]].map(([a, b, c, d]) => ({ a: [a, b], b: [c, d] })) };
      const L = (a, b) => ({ a, b }), A = (a, b, c) => ({ a, b, c, r, ccw: true });
      return { segs: [L([x + r, y], [x + w - r, y]), A([x + w - r, y], [x + w, y + r], [x + w - r, y + r]), L([x + w, y + r], [x + w, y + h - r]), A([x + w, y + h - r], [x + w - r, y + h], [x + w - r, y + h - r]),
        L([x + w - r, y + h], [x + r, y + h]), A([x + r, y + h], [x, y + h - r], [x + r, y + h - r]), L([x, y + h - r], [x, y + r]), A([x, y + r], [x + r, y], [x + r, y + r])] }; };
    const circle = (cx, cy, r, n = 32) =>''')
    R('''      const M = qrMagnets(), outer = roundRect(0, 0, q.pw, q.ph, q.rad);''', '''      const M = qrMagnets(), outer = roundRect(0, 0, q.pw, q.ph, q.rad, 12), outerS = roundRectSegs(0, 0, q.pw, q.ph, q.rad);''')
    R('''({ name, color: [0.95, 0.95, 0.95], z0, z1, outer, holes:''', '''({ name, color: [0.95, 0.95, 0.95], z0, z1, outer, outerC: outerS, holes:''')
    # Schrift feiner auflösen (Kurven der Buchstaben)
    R('''nestLoops(cmdsToLoops(cmds, 5)).forEach((g, i) => solids.push({ name: "Text_" + (i + 1)''', '''nestLoops(cmdsToLoops(cmds, 8)).forEach((g, i) => solids.push({ name: "Text_" + (i + 1)''')
    return s
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
if "roundRectSegs" in s: sys.exit("schon eingespielt")
open(p, "w", encoding="utf-8").write(patch_js(s)); print("Eckenradien exakt:", p)
