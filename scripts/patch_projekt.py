"""Kostenrechner: Preise pro Projekt statt pro Teil (Einzelfertigung).

Aufruf: python patch_projekt.py <unverschluesselte index.html>
- 3D-Druck: das Projekt = die Druckplatte mit allen Teilen; Serie und Laser: der ganze Auftrag
- Hero, „Du behältst“, Mindestpreis, Wunschpreis-Regler, Mini-Leiste und Aufschlüsselung als Projektsumme
- Staffelpreise (nur Serie) zeigen weiter Stückpreis und Auftrag
"""
import sys

path = sys.argv[1]
s = open(path, encoding="utf-8").read()


def rep(a, b, n=1):
    global s
    if s.count(a) != n:
        raise SystemExit(f"Stelle {s.count(a)}× statt {n}× gefunden: " + a[:90])
    s = s.replace(a, b)


rep('''    const PL = (k) => k === "p" && !st.pser, MUL = (k, c) => (PL(k) ? c.stk : 1);''',
    '''    const PL = (k) => k === "p" && !st.pser, MUL = (k, c) => c.stk; // alles als Summe für das Projekt / den Auftrag
    const PROJ = (k) => (PL(k) ? "für das Projekt" : "für den Auftrag");''')
rep('''const mu = MUL(k, c), u = PL(k) ? "für die Platte" : "pro Teil", sk = c.sk * mu;''', '''const mu = MUL(k, c), u = PROJ(k), sk = c.sk * mu;''')
rep('''<span>${pl ? `netto für die Druckplatte (${c.stk} ${c.stk === 1 ? "Teil" : "Teile"})` : "netto pro Teil"}, Preisgruppe ${esc(prof().name)}</span>''',
    '''<span>netto · ${pl ? "ganzes Projekt" : "ganzer Auftrag"} (${c.stk} ${k === "p" && pl ? (c.stk === 1 ? "Teil" : "Teile") : "Stk."}), Preisgruppe ${esc(prof().name)}</span>''')
rep('''<div class="sp-sub">${pl ? `brutto ${eur.format(c.br * mu)}${c.stk > 1 ? ` · ${eur.format(c.vk)} pro Teil` : ""}` : `brutto ${eur.format(c.br)} · Auftrag ${c.stk} Stk.: ${eur.format(c.vk * c.stk)} netto`}${''',
    '''<div class="sp-sub">brutto ${eur.format(c.br * mu)}${!pl && k === "p" && c.stk > 1 ? ` · Stückpreis ${eur.format(c.vk)}` : ""}${''')
rep('''aria-label="Wunschpreis netto ${pl ? "für die Platte" : "pro Teil"}">''', '''aria-label="Wunschpreis netto ${PROJ(k)}">''')
rep('''${st.ptOn ? "Kosten pro Teil ausblenden" : "Kosten pro Teil anzeigen"}</button>''', '''${st.ptOn ? "Kostenaufschlüsselung ausblenden" : "Kostenaufschlüsselung anzeigen"}</button>''')
rep('''<summary><h4>Aufschlüsselung pro Teil</h4><span>${eur.format(c.hk)} Herstellkosten</span></summary>''',
    '''<summary><h4>Aufschlüsselung ${PROJ(k)}</h4><span>${eur.format(c.hk * mu)} Herstellkosten</span></summary>''')
rep('''<dl>${lines.map((l) => row(...l)).join("")}${row("+ Gemeinkosten", c.gkb)}${row("+ Versand / Verpackung", c.vs)}${row("Selbstkosten = Mindestpreis", c.sk, "sum min")}${row(gl, c.gwb)}${row("Verkaufspreis netto", c.vk, "sum")}</dl>''',
    '''<dl>${lines.filter(([a]) => !(pl && /^Probedruck/.test(a))).map(([a, v, cl]) => row(a, v * mu, cl)).join("")}${row("+ Gemeinkosten", c.gkb * mu)}${row("+ Versand / Verpackung", c.vs * mu)}${row("Selbstkosten = Mindestpreis", c.sk * mu, "sum min")}${row(gl, c.gwb * mu)}${row("Verkaufspreis netto", c.vk * mu, "sum")}</dl>''')
rep('''<small>Verkaufen für${PL(k) ? " (Platte)" : ""}</small>''', '''<small>Verkaufen für (${PL(k) ? "Projekt" : "Auftrag"})</small>''')
# Angebotstext: Summen fürs Projekt, Stückpreis nur in der Serie
rep('''      return [...head, `Herstellkosten ${eur.format(c.hk)} · Selbstkosten (Mindestpreis) ${eur.format(c.sk)} pro Teil`, `Verkaufspreis netto ${eur.format(c.vk)} pro Teil · brutto ${eur.format(c.br)}`, `${k === "p" && !st.pser ? "Druckplatte" : "Auftrag"}: ${eur.format(c.vk * c.stk)} netto / ${eur.format(c.br * c.stk)} brutto`].join("\\n");''',
    '''      const n = c.stk, pr = k === "p" && !st.pser;
      return [...head, `Herstellkosten ${eur.format(c.hk * n)} · Selbstkosten (Mindestpreis) ${eur.format(c.sk * n)}`, `${pr ? "Projekt" : "Auftrag"}: ${eur.format(c.vk * n)} netto / ${eur.format(c.br * n)} brutto`, ...(pr ? [] : [`Stückpreis netto ${eur.format(c.vk)}`])].join("\\n");''')
rep('''`${st.pser ? `Stückzahl ${c.stk}` : `1 Druckplatte mit ${c.stk} ${c.stk === 1 ? "Teil" : "Teilen"}`} · Drucker''',
    '''`${st.pser ? `Stückzahl ${c.stk}` : `Projekt: 1 Druckplatte mit ${c.stk} ${c.stk === 1 ? "Teil" : "Teilen"}`} · Drucker''')
rep('''`Material ${eur.format(c.mat)} · Maschine ${eur.format(c.mas)} · Strom ${eur.format(c.strom)} · Verschleiß ${eur.format(c.ver)} · Laser ${eur.format(c.las)} · Arbeit ${eur.format(c.lo)} · Zukauf ${eur.format(c.zk)} · Probedrucke ${eur.format(c.prb)}`''',
    '''`Material ${eur.format(c.mat * c.stk)} · Maschine ${eur.format(c.mas * c.stk)} · Strom ${eur.format(c.strom * c.stk)} · Verschleiß ${eur.format(c.ver * c.stk)} · Laser ${eur.format(c.las * c.stk)} · Arbeit ${eur.format(c.lo * c.stk)} · Zukauf ${eur.format(c.zk * c.stk)} · Probedrucke ${eur.format(c.prb * c.stk)}`''')
rep('''`Material ${eur.format(c.mat)} · Maschine ${eur.format(c.mas)} · Strom ${eur.format(c.strom)} · Arbeit ${eur.format(c.lo)} · Zukauf ${eur.format(c.zk)} · Testläufe ${eur.format(c.prb)}`''',
    '''`Material ${eur.format(c.mat * c.stk)} · Maschine ${eur.format(c.mas * c.stk)} · Strom ${eur.format(c.strom * c.stk)} · Arbeit ${eur.format(c.lo * c.stk)} · Zukauf ${eur.format(c.zk * c.stk)} · Testläufe ${eur.format(c.prb * c.stk)}`''')
# Hinweis über dem Formular
rep('''`<b>Eine Druckplatte</b> mit ${n} ${n === 1 ? "Teil" : "Teilen"} (Feld „Teile pro Druckplatte“) – Preis für die ganze Platte. Für Stückzahlen und Staffelpreise: Reiter <a href="#rechner-serie">Serie</a>.`''',
    '''`<b>Projekt (Einzelfertigung):</b> eine Druckplatte mit ${n} ${n === 1 ? "Teil" : "Teilen"} (Feld „Teile pro Druckplatte“) – alle Preise für das ganze Projekt. Für Stückzahlen und Staffelpreise: Reiter <a href="#rechner-serie">Serie</a>.`''')
rep('''`<b>Serie:</b> Stückzahl, Probedrucke und Staffelpreise – Preise pro Teil. Für eine einzelne Druckplatte den Reiter <a href="#rechner">3D-Druck</a> nehmen.`''',
    '''`<b>Serie:</b> Stückzahl, Probedrucke und Staffelpreise – oben die Summe für den Auftrag, der Stückpreis steht darunter und in der Staffel. Für Einzelfertigung den Reiter <a href="#rechner">3D-Druck</a> nehmen.`''')

open(path, "w", encoding="utf-8").write(s)
print("Rechner pro Projekt:", path)
