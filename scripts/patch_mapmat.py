"""3MF-Filamentzuordnung: neue Materialien eigene Zeile (PA6-GF lief bisher auf den PA6-CF-Preis).

Aufruf: python patch_mapmat.py <unverschluesselte index.html>
PA6-GF → PA6-GF, PC FR → PC FR, TPU for AMS (AMS/68D) → TPU for AMS, ABS-S/Support for ABS → Support for ABS,
PLA-S/PETG-S → Support for PLA. Fehlt die Zeile in den Stammdaten, greift wie bisher die nächstpassende.
"""
import sys

path = sys.argv[1]
s = open(path, encoding="utf-8").read()
a = '''      if (idx === "GFA01") return pick("PLA Matt"); if (idx === "GFA02") return pick("PLA Metall");'''
if s.count(a) != 1:
    raise SystemExit("Stelle nicht gefunden")
s = s.replace(a, '''      if (t.startsWith("PA6") && t.includes("GF") && pick("PA6-GF")) return "PA6-GF";
      if (t.startsWith("PC") && t.includes("FR") && pick("PC FR")) return "PC FR";
      if (t.startsWith("TPU") && (t.includes("AMS") || t.includes("68D")) && pick("TPU for AMS")) return "TPU for AMS";
      if ((t === "ABS-S" || (t.includes("SUPPORT") && t.includes("ABS"))) && pick("Support for ABS")) return "Support for ABS";
      if (t === "PLA-S" || t === "PETG-S") return pick("Support for PLA");
''' + a)
b = '''    buildStamm(); projMigrate(); fillForm("p");'''
if s.count(b) != 1:
    raise SystemExit("Startzeile nicht gefunden")
s = s.replace(b, '''    if (st.multi) st.multi.forEach((m) => { const nm = mapMat(m.type, m.idx), was = { "PA6-GF": "PA6-CF", "PC FR": "PC", "TPU for AMS": "TPU 95A HF", "Support for ABS": "ABS", "Support for PLA": "PLA Basic" }[nm]; if (nm && was && m.mat === was) m.mat = nm; }); // alte Zuordnung aus gespeicherter 3MF korrigieren
    if (st.multi && st.multi.length) { const main = st.multi.slice().sort((a, b) => b.g - a.g)[0]; if (main) st.p.p_mat = main.mat; }
''' + b)
open(path, "w", encoding="utf-8").write(s)
print("Filamentzuordnung:", path)
