"""Design/Layout-Feinschliff: Werkzeug-Einstieg auf der Startseite, Kapitelfilter, Handy-Optimierungen.

Aufruf: python patch_design.py <unverschluesselte index.html>
- Startseite: Abschnitt „Werkzeuge“ mit Direktlinks (#rechner-werkzeuge-qr|sch|vk|vec usw.)
- Inhalt: Filter nach Bereich (Grundlagen, Sicherheit, 3D-Drucker, Slicer, Konstruktion, Laser, Organisation)
- Handy: Dokumentinfo in einer Zeile, Bewertungstabellen (Punkte) zweispaltig, Preisgruppen als Wischleiste,
  Reiterleiste im Rechner mit Verlauf am Rand, wenn sie weiter scrollt
"""
import sys

path = sys.argv[1]
s = open(path, encoding="utf-8").read()


def rep(a, b, n=1):
    global s
    if s.count(a) != n:
        raise SystemExit(f"Stelle {s.count(a)}× statt {n}× gefunden: " + a[:90])
    s = s.replace(a, b)


I = lambda d: f'<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">{d}</svg>'
TOOLS = [
    ("#rechner", "Kostenrechner 3D-Druck", "Projektpreis aus der geslicten 3MF – mit Preisgruppen", I('<rect x="5" y="3" width="14" height="18" rx="2"/><path d="M8 7h8M8 11h2M12 11h2M16 11h0M8 15h2M12 15h2M8 18h2M12 18h4"/>'), "a-druck"),
    ("#rechner-laser", "Kostenrechner Laser", "Laserzeit aus Fläche und Schnittlänge oder aus XCS", I('<path d="M12 3v6M9 6l3 3 3-3M4 21h16M7 21l5-8 5 8"/>'), "a-laser"),
    ("#rechner-pruefen", "Modell prüfen", "STEP/STL gegen die Konstruktionsregeln, Lage und Teilung", I('<path d="M12 3l8 4v5c0 4.5-3.4 8.3-8 9-4.6-.7-8-4.5-8-9V7z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>'), "a-konstr"),
    ("#rechner-material", "Materialien vergleichen", "Temperaturen, Drucker, Preis – mit Eigenschafts-Sechseck", I('<path d="M12 3l7.8 4.5v9L12 21l-7.8-4.5v-9z"/><path d="M12 8l3.5 2v4L12 16l-3.5-2v-4z"/>'), "a-druck"),
    ("#rechner-werkzeuge-qr", "QR-Code-Platte", "zum Drucken, mit Magnettaschen – STL und STEP", I('<rect x="4" y="4" width="6" height="6" rx="1"/><rect x="14" y="4" width="6" height="6" rx="1"/><rect x="4" y="14" width="6" height="6" rx="1"/><path d="M14 14h2v2h-2zM18 14h2M14 18h2M18 18h2v2"/>'), "a-konstr"),
    ("#rechner-werkzeuge-sch", "Typenschild", "Werksschild mit Logo und CE-Zeichen für den Laser", I('<rect x="3" y="6" width="18" height="12" rx="2"/><path d="M6 10h6M6 14h4M15 10h3M15 14h3"/>'), "a-laser"),
    ("#rechner-werkzeuge-vk", "Visitenkarte", "zum Gravieren auf Alu, Edelstahl oder Holz – mit QR", I('<rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="8.5" cy="10.5" r="2"/><path d="M5.5 16c.6-1.6 1.7-2.5 3-2.5s2.4.9 3 2.5M14 9h4M14 12h4M14 15h3"/>'), "a-laser"),
    ("#rechner-werkzeuge-vec", "Bild → SVG", "PNG/JPG zu glatten Vektoren für Gravur und Schnitt", I('<rect x="3" y="4" width="8" height="8" rx="1"/><path d="M5 10l2-2 2 2"/><path d="M13 8h3M15 6l2 2-2 2"/><path d="M14 20c1-4 3-6 7-6M14 20h2M21 14v2"/>'), "a-grund"),
]
tools_html = '''<section class="sec" id="werkzeuge">
  <div class="wrap">
    <div class="sh"><h2>Werkzeuge</h2><p>Rechnen, prüfen und Dateien erzeugen – direkt im Browser, ohne Installation. Ergebnisse als SVG, STEP, STL oder Angebotstext.</p></div>
    <ul class="tgrid">''' + "".join(f'<li><a class="tcard {c}" href="{h}"><span class="ti">{ic}</span><span class="tt">{t}</span><span class="td">{d}</span></a></li>' for h, t, d, ic, c in TOOLS) + '''</ul>
  </div>
</section>

'''
rep('<section class="sec" id="kapitel">', tools_html + '<section class="sec" id="kapitel">')

# Kapitelfilter
AREAS = ["Grundlagen", "Sicherheit", "3D-Drucker", "Slicer", "Konstruktion", "Laser", "Organisation"]
rep('''<div class="sh"><h2>Inhalt</h2><p>Vom ersten Druck bis zum fertigen Bauteil: 20 Kapitel, farbig nach Bereich. Fang vorne an oder spring direkt hin.</p></div>
    <ol class="cards">''',
    '''<div class="sh"><h2>Inhalt</h2><p>Vom ersten Druck bis zum fertigen Bauteil: 20 Kapitel, farbig nach Bereich. Fang vorne an oder spring direkt hin.</p></div>
    <div class="cfilt" role="group" aria-label="Kapitel nach Bereich filtern"><button type="button" aria-pressed="true" data-a="">Alle</button>''' + "".join(f'<button type="button" aria-pressed="false" data-a="{a}">{a}</button>' for a in AREAS) + '''</div>
    <ol class="cards">''')

CSS = '''
/* ---------- Werkzeuge auf der Startseite */
.tgrid{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:var(--space-sm)}
.tcard{display:grid;grid-template-columns:auto minmax(0,1fr);grid-template-rows:auto auto;column-gap:var(--space-sm);row-gap:2px;height:100%;box-sizing:border-box;padding:var(--space-md);border:1px solid var(--color-rule-2);border-radius:var(--radius-card);background:var(--color-paper-2);color:var(--color-ink);text-decoration:none;transition:border-color var(--dur-micro) var(--ease-out),transform var(--dur-micro) var(--ease-out),box-shadow var(--dur-micro) var(--ease-out)}
.tcard:hover{border-color:var(--a,var(--color-ink));transform:translateY(-1px);box-shadow:0 6px 18px -10px rgba(0,0,0,.35)}
.tcard:focus-visible{outline:2px solid var(--a,var(--color-ink));outline-offset:2px}
.tcard .ti{grid-row:1/3;width:40px;height:40px;display:grid;place-items:center;border-radius:10px;color:var(--a,var(--color-ink));background:color-mix(in srgb,var(--a,var(--color-ink)) 12%,transparent)}
.tcard .ti svg{width:22px;height:22px}
.tcard .tt{font-weight:600;font-size:16px;line-height:1.3;align-self:end}.tcard .td{font-size:13.5px;line-height:1.4;color:var(--color-muted)}
.tcard.a-druck{--a:var(--color-druck)}.tcard.a-laser{--a:var(--color-laser)}.tcard.a-konstr{--a:var(--color-konstr)}.tcard.a-grund{--a:var(--color-grund)}
@media (max-width:1100px){.tgrid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media (max-width:560px){.tgrid{gap:var(--space-xs)}.tcard{grid-template-columns:minmax(0,1fr);padding:var(--space-sm)}.tcard .ti{grid-row:auto;width:34px;height:34px;margin-bottom:4px}.tcard .tt{font-size:15px;align-self:start}.tcard .td{display:none}}
#werkzeuge{padding-bottom:calc(var(--section-gap) * .4)}#werkzeuge+#kapitel{padding-top:calc(var(--section-gap) * .6)}
/* ---------- Kapitelfilter */
.cfilt{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 var(--space-lg)}
.cfilt button{font:500 14px/1 var(--f-text,inherit);padding:8px 14px;border-radius:999px;border:1px solid var(--color-rule-2);background:transparent;color:var(--color-ink);cursor:pointer;transition:background-color var(--dur-micro) var(--ease-out)}
.cfilt button:hover{background:var(--color-paper-2)}.cfilt button[aria-pressed="true"]{background:var(--color-ink);color:var(--color-paper);border-color:var(--color-ink)}
.cards li[hidden]{display:none}
@media (max-width:640px){.cfilt{flex-wrap:nowrap;overflow-x:auto;scrollbar-width:none;margin-inline:calc(-1 * var(--gutter,16px));padding-inline:var(--gutter,16px)}.cfilt::-webkit-scrollbar{display:none}.cfilt button{flex:0 0 auto}}
/* ---------- Handy: Dokumentinfo kompakt */
@media (max-width:640px){
  .meta.meta{grid-template-columns:repeat(3,minmax(0,1fr))}
  .meta.meta .m-wide{grid-column:1/-1}
  .meta>div{border-left:1px solid var(--color-rule);border-top:1px solid var(--color-rule);padding:var(--space-xs) var(--space-sm) var(--space-sm)}
  .meta>div.m-wide{border-top:0;border-left:0;border-bottom:0}.meta.meta>div:nth-child(2){grid-column:auto;border-left:0;border-bottom:0}.meta.meta>div:nth-child(3){border-left:1px solid var(--color-rule)}
  .meta dd{font-size:14px}
}
/* ---------- Handy: Bewertungstabellen (Punkte) zweispaltig */
@media (max-width:640px){
  .tw table:not(.blank):has(.dots) tr{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);column-gap:var(--space-md)}
  .tw table:not(.blank):has(.dots) td{grid-template-columns:minmax(0,1fr) auto;align-items:center;gap:var(--space-xs)}
  .tw table:not(.blank):has(.dots) td:first-child{grid-column:1/-1}
  .tw table:not(.blank):has(.dots) td:nth-last-child(-n+2){border-bottom:0}
}
/* ---------- Rechner am Handy: Preisgruppen als Wischleiste, Reiter mit Verlauf */
@media (max-width:600px){
  .kprof-g{display:flex;overflow-x:auto;scroll-snap-type:x proximity;scrollbar-width:none;padding-bottom:2px}
  .kprof-g::-webkit-scrollbar{display:none}
  .kprof-g .kpb{flex:0 0 46%;scroll-snap-align:start;min-height:0}
}
.apptabs.fr{-webkit-mask-image:linear-gradient(90deg,#000 80%,transparent);mask-image:linear-gradient(90deg,#000 80%,transparent)}
.apptabs.fl{-webkit-mask-image:linear-gradient(270deg,#000 80%,transparent);mask-image:linear-gradient(270deg,#000 80%,transparent)}
.apptabs.fl.fr{-webkit-mask-image:linear-gradient(90deg,transparent,#000 15%,#000 85%,transparent);mask-image:linear-gradient(90deg,transparent,#000 15%,#000 85%,transparent)}
'''
rep('''@media screen and (max-width:900px){
  .nav{position:fixed;''', CSS + '''@media screen and (max-width:900px){
  .nav{position:fixed;''')

rep('<a class="btn ghost" href="#kapitel">Alle Kapitel ansehen</a>', '<a class="btn ghost" href="#kapitel">Alle Kapitel ansehen</a><a class="btn ghost" href="#werkzeuge">Werkzeuge</a>')
# Direktlinks in die Werkzeuge + Filter + Reiter-Verlauf
rep('''else if (h === "rechner-werkzeuge") openApp("w"); else closeApp(); }''',
    '''else if (h === "rechner-werkzeuge") openApp("w"); else if (/^rechner-werkzeuge-(qr|sch|vk|vec)$/.test(h)) { openApp("w"); const b = document.querySelector(`#w_seg [data-w="${h.split("-").pop()}"]`); if (b) b.click(); } else closeApp(); }''')
rep('''</body>''', '''<script>
(() => { // Kapitelfilter auf der Startseite
  const f = document.querySelector(".cfilt"); if (!f) return;
  f.addEventListener("click", (e) => { const b = e.target.closest("button[data-a]"); if (!b) return; const a = b.dataset.a;
    f.querySelectorAll("button").forEach((x) => x.setAttribute("aria-pressed", x === b ? "true" : "false"));
    document.querySelectorAll("#kapitel .cards li").forEach((li) => { const t = li.querySelector(".ccb"); li.hidden = !!a && !(t && t.textContent.trim() === a); }); });
})();
(() => { // Preisgruppen am Handy: gewählte Gruppe in den sichtbaren Bereich schieben
  const g = document.getElementById("kprof_g"); if (!g) return;
  const show = () => { if (g.scrollWidth <= g.clientWidth + 2) return; const b = g.querySelector('[aria-checked="true"]'); if (b) g.scrollLeft = Math.max(0, b.offsetLeft - g.offsetLeft - 8); };
  new MutationObserver(show).observe(g, { attributes: true, subtree: true, attributeFilter: ["aria-checked"], childList: true }); addEventListener("hashchange", () => setTimeout(show, 400)); setTimeout(show, 600);
})();
(() => { // Reiterleiste im Rechner: Verlauf am Rand, solange sie weiter scrollt
  const bar = document.querySelector(".apptabs"); if (!bar) return;
  const u = () => { bar.classList.toggle("fr", bar.scrollLeft + bar.clientWidth < bar.scrollWidth - 4); bar.classList.toggle("fl", bar.scrollLeft > 4); };
  bar.addEventListener("scroll", u, { passive: true }); addEventListener("resize", u); new MutationObserver(u).observe(document.body, { attributes: true, subtree: false }); setTimeout(u, 300); document.addEventListener("click", () => setTimeout(u, 350));
})();
</script>
</body>''')

open(path, "w", encoding="utf-8").write(s)
print("Design:", path)
