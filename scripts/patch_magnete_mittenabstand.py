"""QR-Werkzeug: Magnetposition über den Mittenabstand (Magnetmitte zu Magnetmitte) waagerecht und senkrecht;
der Wert wird je zur Hälfte symmetrisch zur Plattenmitte aufgeteilt. Aufruf über scripts/aktualisieren.py"""
import sys
p = sys.argv[1]; s = open(p, encoding="utf-8").read()
if "mdx:" in s: sys.exit("schon eingespielt")
def R(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:90], s.count(a)); s = s.replace(a, b)
R('mpo: 10, mpx: 16, mpy: 21 }, sch: {} };', 'mpo: 10, mpx: 16, mpy: 21, mdx: 32, mdy: 42 }, sch: {} };')
R('''      const cl = (v, a, b) => Math.min(b, Math.max(a, v)), ax = Math.abs(q.mpx || 0), ay = Math.abs(q.mpy || 0),''',
  '''      const cl = (v, a, b) => Math.min(b, Math.max(a, v)), ax = Math.abs(q.mdx || 0) / 2, ay = Math.abs(q.mdy || 0) / 2,''')
R('''q._mpm = 1; } }''', '''q._mpm = 1; }
      if (q._mpm2 !== 1) { q.mdx = +(2 * (q.mpx || 0)).toFixed(1); q.mdy = +(2 * (q.mpy || 0)).toFixed(1); q._mpm2 = 1; } } // halbe Abstände → Mittenabstand''')
R('''            <label>Abstand Mitte ↔ Magnet waagerecht (mm)<input name="mpx" type="number" step="0.1" min="0"></label>
            <label>Abstand Mitte ↔ Magnet senkrecht (mm)<input name="mpy" type="number" step="0.1" min="0"></label>''',
  '''            <label>Mittenabstand Magnete waagerecht (mm)<input name="mdx" type="number" step="0.1" min="0"></label>
            <label>Mittenabstand Magnete senkrecht (mm)<input name="mdy" type="number" step="0.1" min="0"></label>''')
R('''["mps", "mpd", "mpx", "mpy"].forEach''', '''["mps", "mpd", "mdx", "mdy"].forEach''')
R('symmetrisch zur Plattenmitte: Abstand von der senkrechten Mittelebene nach links/rechts und von der waagerechten nach oben/unten (Mittelpunkt der Tasche).',
  'symmetrisch zur Plattenmitte. Eingegeben wird der <b>Mittenabstand</b> von Magnetmitte zu Magnetmitte – je die Hälfte liegt links/rechts bzw. oben/unten der Mitte (z. B. 30 mm → ±15 mm).')
R('''symmetrisch zur Plattenmitte: ±${n1((M.pos[1][0] - M.pos[0][0]) / 2, 1)} mm waagerecht, ±${n1((M.pos[2][1] - M.pos[0][1]) / 2, 1)} mm senkrecht (Mittenabstand ${n1(M.pos[1][0] - M.pos[0][0], 1)} × ${n1(M.pos[2][1] - M.pos[0][1], 1)} mm,''',
  '''Mittenabstand ${n1(M.pos[1][0] - M.pos[0][0], 1)} × ${n1(M.pos[2][1] - M.pos[0][1], 1)} mm, symmetrisch zur Plattenmitte (je ±${n1((M.pos[1][0] - M.pos[0][0]) / 2, 2)} / ±${n1((M.pos[2][1] - M.pos[0][1]) / 2, 2)} mm,''')
R('''Mitte ±${n1((M.pos[1][0] - M.pos[0][0]) / 2, 1)} / ±${n1((M.pos[2][1] - M.pos[0][1]) / 2, 1)} mm`''', '''Mittenabstand ${n1(M.pos[1][0] - M.pos[0][0], 1)} × ${n1(M.pos[2][1] - M.pos[0][1], 1)} mm`''')
# Hinweis, wenn der Mittenabstand nicht auf die Platte passt (Taschen würden an den Rand geschoben)
R('''      const pos = [[xL, yU], [xR, yU], [xL, yO], [xR, yO]];''', '''      const pos = [[xL, yU], [xR, yU], [xL, yO], [xR, yO]], clipped = Math.abs(xR - xL - 2 * ax) > 1e-6 || Math.abs(yO - yU - 2 * ay) > 1e-6;''')
R('''return { d, r, z0: 0, z1: depth, cover: q.pt - depth, limited, e: Math.min(xL, yU), pos,''', '''return { d, r, z0: 0, z1: depth, cover: q.pt - depth, limited, clipped, e: Math.min(xL, yU), pos,''')
R('''      msgs.push(["", `4 Magnettaschen <b>Ø''', '''      if (M.clipped) msgs.push(["err", `Mittenabstand größer als die Platte erlaubt – die Taschen wurden an den Rand gesetzt. Höchstens ${n1(q.pw - M.d, 1)} × ${n1(q.ph - M.d, 1)} mm eingeben.`]);
      msgs.push(["", `4 Magnettaschen <b>Ø''')
open(p, "w", encoding="utf-8").write(s); print("Mittenabstand:", p)
