"""Rechner-Overlay aufgeräumt: einheitliche Akzentfarbe, weniger Knöpfe oben, kompakte Auswahl, klare Aktionen.

Aufruf: python patch_overlay.py <unverschluesselte index.html>
- Titel „Rechner & Werkzeuge“; Reiter optisch in Rechnen | Wissen & Werkzeuge getrennt
- Preisquelle („Bambu-Preise laden“) von oben in die Stammdaten verschoben; Stammdaten nur bei den Rechnern
- „Woher kommt das Modell?“ als kompakte Karten mit Symbol links, Auswahl in Akzentfarbe statt Blau mit Haken
- Preisgruppen: „Zurücksetzen“ nur, wenn es etwas zurückzusetzen gibt
- leere 3D-Vorschau ausgeblendet, bis ein Modell geladen ist
- Ergebnis: „Angebot kopieren“ als Hauptknopf direkt unter dem Preis, Aufschlüsselung als zweiter Knopf daneben;
  Download-Knöpfe der Werkzeuge in Akzentfarbe
"""
import sys

path = sys.argv[1]
s = open(path, encoding="utf-8").read()


def rep(a, b, n=1):
    global s
    if s.count(a) != n:
        raise SystemExit(f"Stelle {s.count(a)}× statt {n}× gefunden: " + a[:90])
    s = s.replace(a, b)


rep('<h2 id="app-title">Kostenrechner</h2>', '<h2 id="app-title">Rechner &amp; Werkzeuge</h2>')
# alter Rechner-Teaser auf der Startseite ist durch „Werkzeuge“ ersetzt
i = s.index('<section class="sec band2" id="rechner-teaser">'); j = s.index('</section>', i) + len('</section>')
s = s[:i] + s[j:].lstrip("\n")
s = s.replace('#werkzeuge{padding-bottom:', '#werkzeuge{padding-top:calc(var(--section-gap) * .8);padding-bottom:', 1)
# Preisquelle in die Stammdaten
pb = '''    <div class="pricebar" id="pricebar"><span class="pdot" aria-hidden="true"></span><span id="pricetxt">Preise: Stammdaten</span><button class="kbtn sm" type="button" id="priceupd">Bambu-Preise laden</button></div>
'''
rep(pb, '')
rep('''      <summary>Stammdaten anpassen (Preise, Maschinen, Zuschläge)</summary>''',
    '''      <summary>Stammdaten anpassen (Preise, Maschinen, Zuschläge)</summary>
''' + pb.replace("    <div", "      <div"))
# Reiter-Zustand fürs CSS
rep('''      ["p", "s", "l", "m", "c", "w"].forEach((k) => { const on = k === t;''', '''      app.dataset.tab = t; ["p", "s", "l", "m", "c", "w"].forEach((k) => { const on = k === t;''')
# Aktionen im Ergebnis: Angebot kopieren nach oben, neben die Aufschlüsselung
rep('''        <button class="kbtn sm ghost sp-pttog" type="button" data-act="pt" aria-expanded="${st.ptOn ? "true" : "false"}">${st.ptOn ? "Kostenaufschlüsselung ausblenden" : "Kostenaufschlüsselung anzeigen"}</button>''',
    '''        <div class="kact"><button class="kbtn pri" type="button" data-copy="${k}">Angebot kopieren</button><button class="kbtn ghost sp-pttog" type="button" data-act="pt" aria-expanded="${st.ptOn ? "true" : "false"}">${st.ptOn ? "Aufschlüsselung ausblenden" : "Kostenaufschlüsselung"}</button></div>''')
rep('''        <div class="krow"><button class="kbtn" type="button" data-copy="${k}">Angebot kopieren</button></div><textarea class="kcopytxt" readonly hidden aria-label="Angebotstext"></textarea>`;''',
    '''        <textarea class="kcopytxt" readonly hidden aria-label="Angebotstext"></textarea>`;''')

CSS = '''
/* ---------- Overlay aufgeräumt */
.apptabs #tab-l{margin-right:12px}
.apptabs #tab-l::after{content:"";position:absolute;right:-7px;top:22%;bottom:22%;width:1px;background:var(--line2);pointer-events:none}
.apptabs [role=tab]{position:relative}
.app:is([data-tab="c"],[data-tab="w"]) #kst{display:none}
#kst .pricebar{margin:var(--space-sm) 0 var(--space-md)}
#kprof_reset:disabled{display:none}
/* Auswahl einheitlich in der Akzentfarbe */
.ksrcb[aria-checked="true"]{box-shadow:inset 0 0 0 2px var(--color-accent);background:var(--color-accent-soft)}
.ksrcb[aria-checked="true"]::after{display:none}
.ksrcb:focus-visible{outline-color:var(--color-accent)}
/* Modellherkunft kompakt: Symbol links, Text rechts */
.ksrcb{display:grid;grid-template-columns:auto minmax(0,1fr);column-gap:var(--space-sm);row-gap:2px;align-items:start;padding:var(--space-sm) var(--space-md)}
.ksrcb .ksi{grid-row:1/4;margin:2px 0 0}
.ksrcb b{padding-right:0}
.ksrcb .kss{margin-bottom:var(--space-2xs)}
.ksrcb em{justify-self:start;margin-top:2px}
.ksrcb[aria-checked="true"] .ksi{color:var(--color-accent)}
/* leere 3D-Vorschau erst zeigen, wenn ein Modell da ist; Ablagefläche dann kompakt über die ganze Breite */
.kfile.empty{grid-template-columns:minmax(0,1fr)}.kfile.empty .kview{display:none}
.kfile.empty .kdz{display:grid;grid-template-columns:auto minmax(0,1fr);column-gap:var(--space-md);row-gap:2px;align-items:center;justify-items:start;text-align:left;padding:var(--space-md) var(--space-lg);min-height:0}
.kfile.empty .kdz svg{grid-row:1/3;width:30px;height:30px;margin:0}
/* Aktionen */
.sp-try input[type=range],.sp-sl input{accent-color:var(--color-accent)}
@media (max-width:600px){.ksrcg{grid-template-columns:minmax(0,1fr);gap:var(--space-xs)}.ksrcb{grid-template-columns:auto minmax(0,1fr) auto}.ksrcb .ksi{grid-row:1/3}.ksrcb em{grid-column:3;grid-row:1/3;align-self:center;flex-direction:column;align-items:flex-end;margin:0}.ksrcb .kss{margin:0}.ksrcb b,.ksrcb .kss{hyphens:manual}}
.kbtn.pri,#q_step,#s_svg,#v_svg,#k_svg{background:var(--color-accent);color:var(--color-paper-2);box-shadow:none}
.kbtn.pri:hover,#q_step:hover,#s_svg:hover,#v_svg:hover,#k_svg:hover{filter:brightness(1.06)}
.kact{display:flex;flex-wrap:wrap;gap:var(--space-xs);margin:var(--space-2xs) 0}
.kact .kbtn{flex:1 1 auto;justify-content:center;text-align:center;padding:12px 18px}
.sp-pttog{justify-self:auto;align-self:auto}
@media (max-width:600px){.kact .kbtn{flex-basis:100%}}
'''
rep('''/* ---------- Werkzeuge auf der Startseite */''', CSS + '''/* ---------- Werkzeuge auf der Startseite */''')

rep('''</body>''', '''<script>
[["p_hint", "p_view"], ["l_hint", "l_view"]].forEach(([hi, vi]) => { // leere Vorschau ausblenden, bis ein Modell/eine Zeichnung geladen ist
  const h = document.getElementById(hi), v = document.getElementById(vi); if (!h || !v) return; const f = v.parentElement;
  const u = () => f.classList.toggle("empty", !h.hidden && /^Hier erscheint/.test(h.textContent.trim()));
  new MutationObserver(u).observe(h, { attributes: true, childList: true, characterData: true, subtree: true }); u();
});
</script>
</body>''')
open(path, "w", encoding="utf-8").write(s)
print("Overlay:", path)
