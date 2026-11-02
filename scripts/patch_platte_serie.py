"""Kostenrechner: Reiter „3D-Druck“ rechnet eine einzelne Druckplatte, neuer Reiter „Serie“ für Stückzahlen.

Aufruf: python patch_platte_serie.py <unverschluesselte index.html>
- 3D-Druck (Standard): Auftrag = eine Platte mit „Teile pro Druckplatte“ Teilen. Preis, „Du behältst“,
  Mindestpreis und der Wunschpreis-Regler gelten für die ganze Platte. Ohne Stückzahl, Probedrucke, Staffel.
- Serie: wie bisher – Stückzahl, Probedrucke anteilig, Preise pro Teil, Staffelpreise.
Beide Reiter nutzen dasselbe Formular und dieselben Eingaben (Werte pro Teil, aus der 3MF automatisch).
"""
import sys

path = sys.argv[1]
s = open(path, encoding="utf-8").read()


def rep(a, b, n=1):
    global s
    if s.count(a) != n:
        raise SystemExit(f"Stelle {s.count(a)}× statt {n}× gefunden: " + a[:90])
    s = s.replace(a, b)


# ---------- Reiter
rep('''        <button role="tab" id="tab-p" aria-controls="pane-p" aria-selected="true">3D-Druck</button>''',
    '''        <button role="tab" id="tab-p" aria-controls="pane-p" aria-selected="true">3D-Druck</button>
        <button role="tab" id="tab-s" aria-controls="pane-p" aria-selected="false">Serie</button>''')
rep('''const tabs = { p: $("#tab-p"), l: $("#tab-l"),''', '''const tabs = { p: $("#tab-p"), s: $("#tab-s"), l: $("#tab-l"),''')
rep('''const TABHASH = { p: "#rechner", l:''', '''const TABHASH = { p: "#rechner", s: "#rechner-serie", l:''')
rep('''    function selectTab(t) { const ord = "plmcw", was = st.tab || "p"; app.style.setProperty("--dx", `${ord.indexOf(t) < ord.indexOf(was) ? -24 : 24}px`); st.tab = t; ["p", "l", "m", "c", "w"].forEach((k) => { const on = k === t; tabs[k].setAttribute("aria-selected", on); tabs[k].tabIndex = on ? 0 : -1; $(`#pane-${k}`).hidden = !on; }); placeInd(); if (t === "p") redraw();''',
    '''    function selectTab(t) { const ord = "pslmcw", was = st.tab || "p"; app.style.setProperty("--dx", `${ord.indexOf(t) < ord.indexOf(was) ? -24 : 24}px`); st.tab = t;
      if (t === "p" || t === "s") { const ser = t === "s"; $("#pane-p").classList.toggle("ser", ser); if (!!st.pser !== ser) { st.pser = ser; calcP(); } }
      ["p", "s", "l", "m", "c", "w"].forEach((k) => { const on = k === t; tabs[k].setAttribute("aria-selected", on); tabs[k].tabIndex = on ? 0 : -1; });
      ["p", "l", "m", "c", "w"].forEach((k) => { $(`#pane-${k}`).hidden = !(k === t || (k === "p" && t === "s")); }); placeInd(); { const bar = $(".apptabs"), b = tabs[t]; if (bar && b && bar.scrollWidth > bar.clientWidth) bar.scrollLeft = Math.max(0, b.offsetLeft - (bar.clientWidth - b.offsetWidth) / 2); } if (t === "p" || t === "s") redraw();''')
rep('''const order = ["p", "l", "m", "c", "w"], i = order.indexOf(st.tab || "p"), t = order[(i + (e.key === "ArrowRight" ? 1 : 4)) % 5];''',
    '''const order = ["p", "s", "l", "m", "c", "w"], i = order.indexOf(st.tab || "p"), t = order[(i + (e.key === "ArrowRight" ? 1 : 5)) % 6];''')
rep('''if (h === "rechner") openApp("p"); else''', '''if (h === "rechner") openApp("p"); else if (h === "rechner-serie") openApp("s"); else''')
rep('''if (!app || app.hidden || (st.tab || "p") !== "p") return;''', '''if (!app || app.hidden || !["p", "s"].includes(st.tab || "p")) return;''')
rep('''$$("#tab-p, #tab-l")''', '''$$("#tab-p, #tab-s, #tab-l")''')

# ---------- Formular: Stückzahl und Probedrucke nur in der Serie
rep('''            <div class="kf"><label for="p_stk">''', '''            <p class="pmode" id="p_mode"></p>
            <div class="kf ser-only"><label for="p_stk">''')
rep('''            <div class="kf"><label for="p_prb">''', '''            <div class="kf ser-only"><label for="p_prb">''')
rep('''.sp-rec summary::-webkit-details-marker{display:none}''',
    '''.sp-rec summary::-webkit-details-marker{display:none}
#pane-p:not(.ser) .ser-only{display:none}
.pmode{grid-column:1/-1;margin:0;padding:10px 14px;border-radius:12px;background:var(--bg2);color:var(--fg2);font-size:14px;line-height:1.45}.pmode b{color:var(--fg)}.pmode a{color:inherit;font-weight:600;text-decoration:underline;text-underline-offset:2px}
.apptabs{min-width:0;max-width:100%;overflow-x:auto;scrollbar-width:none;-webkit-overflow-scrolling:touch}.apptabs::-webkit-scrollbar{display:none}''')

# ---------- Rechnung
rep('''      const nPrb = Math.max(0, Math.round(num(I.p_prb)));''', '''      const nPrb = st.pser ? Math.max(0, Math.round(num(I.p_prb))) : 0; // Probedrucke nur in der Serie''')
rep('''matOk(); const c = pCost(st.p.p_stk); lastP = c;''',
    '''matOk(); const c = pCost(st.pser ? st.p.p_stk : st.p.p_pp); lastP = c;
      { const m = $("#p_mode"), n = c.stk; if (m) m.innerHTML = st.pser ? `<b>Serie:</b> Stückzahl, Probedrucke und Staffelpreise – Preise pro Teil. Für eine einzelne Druckplatte den Reiter <a href="#rechner">3D-Druck</a> nehmen.`
        : `<b>Eine Druckplatte</b> mit ${n} ${n === 1 ? "Teil" : "Teilen"} (Feld „Teile pro Druckplatte“) – Preis für die ganze Platte. Für Stückzahlen und Staffelpreise: Reiter <a href="#rechner-serie">Serie</a>.`; }''')

# Faktor: in der Plattenansicht werden Preise für die ganze Platte gezeigt
rep('''    function heroNums(k, c) {
      const lohn = num(ZP().lohn), hw = lohn > 0 ? c.lo / lohn : 0, hM = hoursOf(k, c);
      return { keep: c.gwb,''',
    '''    const PL = (k) => k === "p" && !st.pser, MUL = (k, c) => (PL(k) ? c.stk : 1);
    function heroNums(k, c) {
      const lohn = num(ZP().lohn), hw = lohn > 0 ? c.lo / lohn : 0, hM = hoursOf(k, c);
      return { keep: c.gwb * MUL(k, c),''')
rep('''    function tryText(k, c, price) {
      const g = price - c.sk, mar = price > 0 ? g / price : 0, hM = hoursOf(k, c), cls = g < 0 ? "bad" : mar < 0.1 ? "warn" : "ok";
      return { cls, html: g < 0 ? `<b>Verlust ${eur.format(-g)}</b> pro Teil – der Mindestpreis liegt bei ${eur.format(c.sk)}`
        : `Du behältst <b>${eur.format(g)}</b> pro Teil ·''',
    '''    function tryText(k, c, price) {
      const mu = MUL(k, c), u = PL(k) ? "für die Platte" : "pro Teil", sk = c.sk * mu;
      const g = price - sk, mar = price > 0 ? g / price : 0, hM = hoursOf(k, c) * mu, cls = g < 0 ? "bad" : mar < 0.1 ? "warn" : "ok";
      return { cls, html: g < 0 ? `<b>Verlust ${eur.format(-g)}</b> ${u} – der Mindestpreis liegt bei ${eur.format(sk)}`
        : `Du behältst <b>${eur.format(g)}</b> ${u} ·''')

rep('''      const tmax = Math.max(10, Math.ceil(Math.max(c.vk * 2.5, c.sk * 3, ap * 1.2) / 5) * 5), tmin = Math.max(0, Math.floor(c.sk * 0.5)),''',
    '''      const mu = MUL(k, c), pl = PL(k);
      const tmax = Math.max(10, Math.ceil(Math.max(c.vk * mu * 2.5, c.sk * mu * 3, ap * mu * 1.2) / 5) * 5), tmin = Math.max(0, Math.floor(c.sk * mu * 0.5)),''')
rep('''      const tv = ap > 0 ? ap : c.vk, T = tryText(k, c, tv);''', '''      const tv = +((ap > 0 ? ap : c.vk) * mu).toFixed(2), T = tryText(k, c, tv);''')
rep('''<span>netto pro Teil, Preisgruppe ${esc(prof().name)}</span>''',
    '''<span>${pl ? `netto für die Druckplatte (${c.stk} ${c.stk === 1 ? "Teil" : "Teile"})` : "netto pro Teil"}, Preisgruppe ${esc(prof().name)}</span>''')
rep('''<b class="sp-price">${eur.format(c.vk)}</b>''', '''<b class="sp-price">${eur.format(c.vk * mu)}</b>''')
rep('''<div><b>${eur.format(c.sk)}</b><span>Mindestpreis</span></div>''', '''<div><b>${eur.format(c.sk * mu)}</b><span>Mindestpreis</span></div>''')
rep('''<div class="sp-sub">brutto ${eur.format(c.br)} · Auftrag ${c.stk} Stk.: ${eur.format(c.vk * c.stk)} netto${''',
    '''<div class="sp-sub">${pl ? `brutto ${eur.format(c.br * mu)}${c.stk > 1 ? ` · ${eur.format(c.vk)} pro Teil` : ""}` : `brutto ${eur.format(c.br)} · Auftrag ${c.stk} Stk.: ${eur.format(c.vk * c.stk)} netto`}${''')
rep('''aria-label="Wunschpreis netto pro Teil">''', '''aria-label="Wunschpreis netto ${pl ? "für die Platte" : "pro Teil"}">''')
rep('''        <div class="sp-card kstaf"><h4>Staffelpreise netto</h4>${staffelChart(k, cost, c.stk)}<div class="ktab"><table><thead><tr><th>Stückzahl</th><th>pro Teil</th><th>Auftrag</th></tr></thead><tbody>${staf}</tbody></table></div></div>''',
    '''        ${pl ? "" : `<div class="sp-card kstaf"><h4>Staffelpreise netto</h4>${staffelChart(k, cost, c.stk)}<div class="ktab"><table><thead><tr><th>Stückzahl</th><th>pro Teil</th><th>Auftrag</th></tr></thead><tbody>${staf}</tbody></table></div></div>`}''')
rep('''      bindChart(k); bindHero(k, c);''', '''      if (!pl) bindChart(k); bindHero(k, c);''')
rep('''tweenTo(box.querySelector(".sp-price"), lastVK[k], c.vk);''', '''tweenTo(box.querySelector(".sp-price"), lastVK[k], c.vk * mu);''')
rep('''if (lastVK[k] !== undefined && Math.abs(lastVK[k] - c.vk) > 0.004)''', '''if (lastVK[k] !== undefined && Math.abs(lastVK[k] - c.vk * mu) > 0.004)''')
rep('''      lastVK[k] = c.vk; lastKeep[k] = H.keep;''', '''      lastVK[k] = c.vk * mu; lastKeep[k] = H.keep;''')
rep('''box.querySelector(".sp-price").textContent = eur.format(c2.vk);''', '''box.querySelector(".sp-price").textContent = eur.format(c2.vk * MUL(k, c2));''')
rep('''lastVK[k] = c2.vk; lastKeep[k] = H2.keep;''', '''lastVK[k] = c2.vk * MUL(k, c2); lastKeep[k] = H2.keep;''')
rep('''$(`#${k}_ap`).value = +num(rt.value).toFixed(2);''', '''$(`#${k}_ap`).value = +(num(rt.value) / MUL(k, c)).toFixed(2);''')
rep('''<span><small>Verkaufen für</small><b>${eur.format(c.vk)}</b></span>''', '''<span><small>Verkaufen für${PL(k) ? " (Platte)" : ""}</small><b>${eur.format(c.vk * MUL(k, c))}</b></span>''')
rep('''`Stückzahl ${c.stk} · Drucker ${drName[I.p_dr]}''', '''`${st.pser ? `Stückzahl ${c.stk}` : `1 Druckplatte mit ${c.stk} ${c.stk === 1 ? "Teil" : "Teilen"}`} · Drucker ${drName[I.p_dr]}''')
rep('''`Auftrag: ${eur.format(c.vk * c.stk)} netto / ${eur.format(c.br * c.stk)} brutto`]''',
    '''`${k === "p" && !st.pser ? "Druckplatte" : "Auftrag"}: ${eur.format(c.vk * c.stk)} netto / ${eur.format(c.br * c.stk)} brutto`]''')

open(path, "w", encoding="utf-8").write(s)
print("3D-Druck = eine Platte, Reiter Serie:", path)
