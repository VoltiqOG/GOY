"""Kostenrechner, Reiter 3D-Druck (Projekt): Eingaben für das ganze Projekt statt pro Teil.

Aufruf: python patch_projekt_eingaben.py <unverschluesselte index.html>
- Filament, Druckzeit, Nacharbeit, Zukaufteile, Laserzeit und Angebotspreis gelten im Reiter 3D-Druck für das
  ganze Projekt (die Platte), im Reiter Serie wie bisher pro Teil. Beim Wechsel der Reiter werden die Felder
  umgerechnet (× / ÷ Teile pro Platte); die 3MF trägt im Projekt die Plattenwerte direkt ein.
- Gespeicherte Werte (bisher pro Teil) werden einmalig umgerechnet.
"""
import sys

path = sys.argv[1]
s = open(path, encoding="utf-8").read()


def rep(a, b, n=1):
    global s
    if s.count(a) != n:
        raise SystemExit(f"Stelle {s.count(a)}× statt {n}× gefunden: " + a[:90])
    s = s.replace(a, b)


# Rechnung: im Projekt sind die Felder Summen → auf ein Teil umrechnen
rep('''      const I = st.p, z = ZP(), stk = Math.max(1, Math.round(num(stkIn))), pp = Math.max(1, Math.round(num(I.p_pp)));
      const q = Math.min(num(z.fehl), 90) / 100, fd = 1 / (1 - q), d = bdiv(), lohn = num(z.lohn), dr = I.p_dr, none = dr === "none", h = num(I.p_h);''',
    '''      const I = st.p, z = ZP(), stk = Math.max(1, Math.round(num(stkIn))), pp = Math.max(1, Math.round(num(I.p_pp))), T = st.pser ? 1 : pp; // T: Projektsumme → pro Teil
      const q = Math.min(num(z.fehl), 90) / 100, fd = 1 / (1 - q), d = bdiv(), lohn = num(z.lohn), dr = I.p_dr, none = dr === "none", h = num(I.p_h) / T;''')
rep('''      else { matB = num(I.p_g) / 1000 * pkg(I.p_mat); wear = num(filRow(I.p_mat)[3]); }
      const mat = none ? 0 : matB * fd, mas = none ? 0 : h * rateM(dr) * fd, strom = none ? 0 : h * kwh(dr) * fd, ver = none ? 0 : h * wear / d * fd;
      const las = num(I.p_l) / 60 * laserFull();
      const lo = (num(I.p_ez) / stk + (none ? 0 : num(I.p_bz) / 60 / pp) + num(I.p_na) / 60) * lohn;''',
    '''      else { matB = num(I.p_g) / T / 1000 * pkg(I.p_mat); wear = num(filRow(I.p_mat)[3]); }
      const mat = none ? 0 : matB * fd, mas = none ? 0 : h * rateM(dr) * fd, strom = none ? 0 : h * kwh(dr) * fd, ver = none ? 0 : h * wear / d * fd;
      const las = num(I.p_l) / T / 60 * laserFull();
      const lo = (num(I.p_ez) / stk + (none ? 0 : num(I.p_bz) / 60 / pp) + num(I.p_na) / T / 60) * lohn;''')
rep('''      const zk = num(I.p_zk), hk = mat + mas''', '''      const zk = num(I.p_zk) / T, hk = mat + mas''')

# Hilfen: Felder umrechnen, Beschriftung je Reiter
rep('''    function selectTab(t) {''', '''    const PROJF = ["p_g", "p_h", "p_na", "p_zk", "p_l", "p_ap"], PD = (n) => (st.pser ? n : 1);
    function projScale(f) { PROJF.forEach((id) => { const el = document.getElementById(id); if (!el || el.value === "" || !(num(el.value) > 0)) return; el.value = +(num(el.value) * f).toFixed(id === "p_h" ? 4 : 2); }); readForm("p"); }
    function projMigrate() { if (st.projIn) return; st.projIn = 1; if (st.pser) return; const pp = Math.max(1, Math.round(num(st.p.p_pp))); PROJF.forEach((id) => { if (num(st.p[id]) > 0) st.p[id] = +(num(st.p[id]) * pp).toFixed(id === "p_h" ? 4 : 2); }); }
    function projLabels() {
      const P = !st.pser, L = (id, a, b) => { const l = document.querySelector(`label[for="${id}"]`); if (l) l.textContent = P ? a : b; }, S = (id, a, b) => { const e = document.getElementById(id); const sm = e && e.closest(".kf") && e.closest(".kf").querySelector("small"); if (sm && sm.firstChild && sm.firstChild.nodeType === 3) sm.firstChild.textContent = P ? a : b; };
      L("p_g", "Filament – ganzes Projekt", "Filament pro Teil"); S("p_g", "inkl. Stützen, Brim, Spülmenge (Slicer: ganze Platte)", "inkl. Stützen, Brim, Spülmenge");
      L("p_h_t", "Druckzeit – ganzes Projekt", "Druckzeit pro Teil"); S("p_h", "Druckzeit der ganzen Platte aus dem Slicer", "Plattenzeit ÷ Teile pro Platte");
      L("p_na", "Nacharbeit – ganzes Projekt", "Nacharbeit pro Teil"); L("p_zk", "Zukaufteile – ganzes Projekt", "Zukaufteile pro Teil"); L("p_l", "Laserzeit – ganzes Projekt", "Laserzeit pro Teil");
      L("p_ap", "Dein Angebotspreis netto für das Projekt (optional)", "Dein Angebotspreis netto pro Teil (optional)"); L("p_pp", "Teile im Projekt (auf der Platte)", "Teile pro Druckplatte"); S("p_vs", "für das ganze Projekt", "je Auftrag, auf die Stückzahl verteilt");
    }
    function selectTab(t) {''')
rep('''if (!!st.pser !== ser) { st.pser = ser; calcP(); } }''',
    '''if (!!st.pser !== ser) { const pp = Math.max(1, Math.round(num($("#p_pp").value))); readForm("p"); st.pser = ser; projScale(ser ? 1 / pp : pp); projLabels(); calcP(); } }''')
# Laden / Zurücksetzen: einmalig umrechnen
rep('''    buildStamm(); fillForm("p"); fillForm("l"); calcAll();''', '''    buildStamm(); projMigrate(); fillForm("p"); fillForm("l"); projLabels(); calcAll();''')
rep('''buildStamm(); fillForm("p"); fillForm("l"); clearStates("p");''', '''buildStamm(); st.projIn = 0; projMigrate(); fillForm("p"); fillForm("l"); projLabels(); clearStates("p");''')
# 3MF: im Projekt die Plattenwerte direkt eintragen
rep('''      $("#p_g").value = +(g / parts).toFixed(2); setState("p_g", "file"); $("#p_h").value = +(t / 3600 / parts).toFixed(3); setState("p_h", "file");''',
    '''      $("#p_g").value = +(g / PD(parts)).toFixed(2); setState("p_g", "file"); $("#p_h").value = +(t / 3600 / PD(parts)).toFixed(3); setState("p_h", "file");''', 2)
rep('''        $("#p_g").value = +(tot / parts).toFixed(2); setState("p_g", "file");
        $("#p_h").value = +(pl.time / 3600 / parts).toFixed(3);''', '''        $("#p_g").value = +(tot / PD(parts)).toFixed(2); setState("p_g", "file");
        $("#p_h").value = +(pl.time / 3600 / PD(parts)).toFixed(3);''')
rep('''          $("#p_g").value = +(est / n).toFixed(2); setState("p_g", "est");
          $("#p_h").value = +(hP / n).toFixed(3);''', '''          $("#p_g").value = +(est / PD(n)).toFixed(2); setState("p_g", "est");
          $("#p_h").value = +(hP / PD(n)).toFixed(3);''')
rep('''$("#p_g").value = +(st.plate.g / pp).toFixed(2); $("#p_h").value = +(st.plate.h / pp).toFixed(3);''',
    '''$("#p_g").value = +(st.plate.g / PD(pp)).toFixed(2); $("#p_h").value = +(st.plate.h / PD(pp)).toFixed(3);''')
# Plattenzeit-Zusatz nur in der Serie
rep('''o.textContent = h > 0 && st.plate ? ` (Platte ${fmtDur(st.plate.h)})` : "";''', '''o.textContent = h > 0 && st.plate && st.pser ? ` (Platte ${fmtDur(st.plate.h)})` : "";''')
# Angebotspreis: im Projekt als Summe
rep('''ap = num(I[`${k}_ap`]), z = ZP()''', '''ap = num(I[`${k}_ap`]) / (PL(k) ? Math.max(1, c.stk) : 1), z = ZP()''')
rep('''$(`#${k}_ap`).value = +(num(rt.value) / MUL(k, c)).toFixed(2);''', '''$(`#${k}_ap`).value = +(num(rt.value) / (PL(k) ? 1 : MUL(k, c))).toFixed(2);''')

open(path, "w", encoding="utf-8").write(s)
print("Eingaben pro Projekt:", path)
