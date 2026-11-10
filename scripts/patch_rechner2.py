"""Rechner und Werkzeuge überarbeitet: Rechnung berichtigt, Unpassendes entfernt, Stammdaten gegliedert.

Aufruf: python patch_rechner2.py <unverschluesselte index.html>  (nach patch_apple.py)
Rechnung
- Laserzeit im 3D-Druck-Rechner zählt als Arbeitszeit (Aufsicht), wie im Laser-Rechner
- Strompreis wird wie alle Stammdatenpreise netto gerechnet, wenn „Bruttopreise“ eingestellt ist
- Runden im Projekt gilt für den Projektpreis (nicht je Teil × Anzahl)
- Projekt (Einzelfertigung) rechnet ohne Probedrucke – die Auswahl „Woher kommt das Modell?“ zeigt sie dort nicht mehr
- Kennzahl „Gewinn pro Druck-/Laserstunde“ entfernt (bei kurzen Laserzeiten sinnlos) → „deine Arbeitszeit“;
  „pro Stunde deiner Arbeit“ rechnet mit den echten Stunden, auch wenn die Preisgruppe keine Arbeitszeit berechnet
- Angebotspreis: ein Feld in der Karte „Anderer Preis“ (Regler oder genau eintippen), das zweite Feld im Formular entfällt;
  ein übernommener Angebotspreis steht im kopierten Angebot
Aufgeräumt
- Zahlenblock-Knöpfe in den Feldern nur noch auf Touch-Geräten
- Stammdaten in aufklappbare Gruppen, häufigste zuerst; Tabelle Lasermaterialien repariert
- Werkzeuge: Meldungen sortiert (Fehler → Warnung → OK → Hinweise), leere Kästen weg, Schritt-Nummer „1“ ohne Folgeschritte weg
- QR-Code: Standardmaße ohne Fehlermeldung (Code 42 mm, Platte 3,2 mm)
- Materialkarten: Kennwerte in zwei Reihen, Fußzeile einheitlich
"""
import sys

path = sys.argv[1]
s = open(path, encoding="utf-8").read()


def rep(a, b, n=1):
    global s
    if s.count(a) != n:
        raise SystemExit(f"Stelle {s.count(a)}× statt {n}× gefunden: " + a[:100])
    s = s.replace(a, b)


# ---------------- Rechnung
# Strom netto
rep('''const kwh = (m) => num(st.mas[m][5]) * num(st.mas[m][6]);''', '''const kwh = (m) => num(st.mas[m][5]) * num(st.mas[m][6]) / bdiv();''')
rep('''const laserFull = () => rateM("f1") + filterRate() + (num(st.mas.f1[5]) + num(st.las.absKw)) * num(st.mas.f1[6]);''',
    '''const laserKwh = () => (num(st.mas.f1[5]) + num(st.las.absKw)) * num(st.mas.f1[6]) / bdiv();
    const laserFull = () => rateM("f1") + filterRate() + laserKwh();''')
rep('''const strom = hL * (num(st.mas.f1[5]) + num(L.absKw)) * num(st.mas.f1[6]) * ld;''', '''const strom = hL * laserKwh() * ld;''')
rep('''hL * (rateM("f1") + filterRate()) + hL * (num(st.mas.f1[5]) + num(L.absKw)) * num(st.mas.f1[6]) + (L.aufsicht ? hL * lohn : 0))''',
    '''hL * (rateM("f1") + filterRate()) + hL * laserKwh() + (L.aufsicht ? hL * lohn : 0))''')
rep('''+ Strom ${eur.format((num(st.mas.f1[5]) + num(st.las.absKw)) * num(st.mas.f1[6]))}/h''', '''+ Strom ${eur.format(laserKwh())}/h''')

# Runden: im Projekt auf den Projektpreis
rep('''function pricing(hk, stk, versand) {''', '''function pricing(hk, stk, versand, tot) {''')
rep('''const r = num(z.rund), vkr = r > 0 ? Math.ceil(Math.round(vk0 / r * 1e9) / 1e9) * r : vk0;''',
    '''const r = num(z.rund), up = (v) => Math.ceil(Math.round(v / r * 1e9) / 1e9) * r, vkr = r > 0 ? (tot ? up(vk0 * stk) / stk : up(vk0)) : vk0;''')

# Arbeitsstunden als eigene Größe; Laserzeit im 3D-Druck = Aufsicht
rep('''const lo = (num(I.p_ez) / stk + (none ? 0 : num(I.p_bz) / 60 / pp) + num(I.p_na) / T / 60) * lohn;''',
    '''const hw = num(I.p_ez) / stk + (none ? 0 : num(I.p_bz) / 60 / pp) + num(I.p_na) / T / 60 + (st.las.aufsicht ? num(I.p_l) / T / 60 : 0), lo = hw * lohn;''')
rep('''return { stk, mat, mas, strom, ver, las, lo, zk, prb, prbA, nPrb, hk, ...pricing(hk, stk, num(I.p_vs)) };''',
    '''return { stk, mat, mas, strom, ver, las, lo, hw, zk, prb, prbA, nPrb, hk, ...pricing(hk, stk, num(I.p_vs), !st.pser) };''')
rep('''const lo = (num(I.l_setup) / 60 / stk + num(I.l_ez) / stk + (num(I.l_hand) + num(I.l_na)) / 60 + (L.aufsicht ? hL : 0)) * lohn;''',
    '''const hw = num(I.l_setup) / 60 / stk + num(I.l_ez) / stk + (num(I.l_hand) + num(I.l_na)) / 60 + (L.aufsicht ? hL : 0), lo = hw * lohn;''')
rep('''return { stk, T, mat, mas, strom, lo, zk, prb, prbA, nPrb, hk, ...pricing(hk, stk, num(I.l_vs)) };''',
    '''return { stk, T, mat, mas, strom, lo, hw, zk, prb, prbA, nPrb, hk, ...pricing(hk, stk, num(I.l_vs)) };''')
rep('''<small>falls das Teil zusätzlich gelasert wird</small>''', '''<small>falls das Teil zusätzlich gelasert wird – zählt auch als Arbeitszeit (Aufsicht)</small>''')

# Kennzahlen
rep('''const lohn = num(ZP().lohn), hw = lohn > 0 ? c.lo / lohn : 0, hM = hoursOf(k, c);
      return { keep: c.gwb * MUL(k, c), keepPct: c.vk > 0 ? c.gwb / c.vk : 0, perPrint: perH(c.gwb, hM), perWork: hw > 0 ? perH(c.gwb + c.lo, hw) : "–" };''',
    '''const hw = c.hw || 0;
      return { keep: c.gwb * MUL(k, c), keepPct: c.vk > 0 ? c.gwb / c.vk : 0, work: hw > 0 ? fmtDur(hw * MUL(k, c)).replace(/(\\d)([dhm])/g, "$1 $2").replace(/m\\b/g, "min") : "–", perWork: hw > 0 ? perH(c.gwb + c.lo, hw) : "–" };''')
rep('''<div><b data-h="perPrint">${H.perPrint}</b><span>Gewinn pro ${k === "p" ? "Druckstunde" : "Laserstunde"}</span></div>''',
    '''<div><b>${H.work}</b><span>deine Arbeitszeit${num(ZP().lohn) > 0 ? "" : " (nicht berechnet)"}</span></div>''')
rep('''<div><b data-h="perWork">${H.perWork}</b><span>pro Stunde deiner Arbeit</span></div>''',
    '''<div><b data-h="perWork">${H.perWork}</b><span>Lohn + Gewinn je Arbeitsstunde</span></div>''')
rep('''box.querySelector('[data-h="perPrint"]').textContent = H2.perPrint; box.querySelector('[data-h="perWork"]').textContent = H2.perWork;''',
    '''box.querySelector('[data-h="perWork"]').textContent = H2.perWork;''')
rep('''const g = price - sk, mar = price > 0 ? g / price : 0, hM = hoursOf(k, c) * mu, cls = g < 0 ? "bad" : mar < 0.1 ? "warn" : "ok";''',
    '''const g = price - sk, mar = price > 0 ? g / price : 0, hW = (c.hw || 0) * mu, cls = g < 0 ? "bad" : mar < 0.1 ? "warn" : "ok";''')
rep('''· Marge ${pct(mar)} · ${perH(g, hM)} ${k === "p" ? "Druckzeit" : "Laserzeit"}${mar < 0.1 ? " – sehr knapp" : ""}`''',
    '''· Marge ${pct(mar)}${hW > 0 ? ` · ${perH(g + c.lo * mu, hW)} je Arbeitsstunde` : ""}${mar < 0.1 ? " – sehr knapp" : ""}`''')

# Projekt: keine Probedrucke in der Herkunfts-Auswahl
rep('''<small>legt die einmalige Zeit und die ${k === "p" ? "Probedrucke" : "Testläufe"} fest (Richtwerte, unten änderbar)</small>''',
    '''<small>${k === "p" && !st.pser ? "legt die einmalige Arbeitszeit fest (Richtwert, unten änderbar)" : `legt die einmalige Zeit und die ${k === "p" ? "Probedrucke" : "Testläufe"} fest (Richtwerte, unten änderbar)`}</small>''')
rep('''<em><span>≈ ${n1(pr[0], 2)} h</span><span>· ${num(pr[1])} ${prbWord(k, num(pr[1]))}</span></em>''',
    '''<em><span>≈ ${n1(pr[0], 2)} h</span>${k === "p" && !st.pser ? "" : `<span>· ${num(pr[1])} ${prbWord(k, num(pr[1]))}</span>`}</em>''')
rep('''st.pser = ser; projScale(ser ? 1 / pp : pp); projLabels(); calcP(); }''', '''st.pser = ser; projScale(ser ? 1 / pp : pp); projLabels(); buildSrc("p"); calcP(); }''')

# Angebotspreis: Regler + genaues Feld in einer Karte
rep('''<div class="sp-th"><h4>Was bleibt bei einem anderen Preis?</h4><output data-o="try">${ap > 0 ? eur.format(tv) : ""}</output></div>
          <input type="range" min="${tmin}" max="${tmax}" step="${tstep}" value="${tv}" data-r="try" aria-label="Wunschpreis netto ${PROJ(k)}">''',
    '''<div class="sp-th"><h4>${ap > 0 ? "Dein Angebotspreis" : "Anderer Preis?"}</h4><label class="sp-tryn"><input type="number" min="0" step="0.5" inputmode="decimal" data-r="tryn" value="${ap > 0 ? tv : ""}" placeholder="${n1(tv, 2)}" aria-label="Preis netto ${PROJ(k)} genau eingeben"><span>€ netto</span></label></div>
          <input type="range" min="${tmin}" max="${tmax}" step="${tstep}" value="${tv}" data-r="try" aria-label="Wunschpreis netto ${PROJ(k)}">''')
rep('''"Regler ziehen: zeigt sofort, was bei einem anderen Preis übrig bleibt – etwa wenn der Kunde handelt."''',
    '''"Regler ziehen oder Betrag eintippen: zeigt sofort, was bei diesem Preis übrig bleibt – etwa wenn der Kunde handelt oder ein Festpreis vorgegeben ist."''')
rep('''const rt = box.querySelector('[data-r="try"]'), ot = box.querySelector('[data-o="try"]'), res = box.querySelector('[data-o="tryres"]');
      rt.addEventListener("input", () => { const v = num(rt.value), T = tryText(k, c, v); ot.textContent = eur.format(v); res.className = `sp-tryres ${T.cls}`; res.innerHTML = T.html; });
      box.querySelector('[data-act="ap"]').addEventListener("click", () => { $(`#${k}_ap`).value = +(num(rt.value) / (PL(k) ? 1 : MUL(k, c))).toFixed(2); recalc(); toast("Angebotspreis übernommen."); });''',
    '''const rt = box.querySelector('[data-r="try"]'), tn = box.querySelector('[data-r="tryn"]'), res = box.querySelector('[data-o="tryres"]');
      let tcur = num(rt.value);
      const tshow = (v) => { tcur = v; const T = tryText(k, c, v); res.className = `sp-tryres ${T.cls}`; res.innerHTML = T.html; };
      rt.addEventListener("input", () => { const v = num(rt.value); tn.value = v; tshow(v); });
      tn.addEventListener("input", () => { if (tn.value === "") return; const v = Math.max(0, num(tn.value)); if (v > num(rt.max)) rt.max = Math.ceil(v * 1.2); rt.value = v; rt.dispatchEvent(new Event("change", { bubbles: true })); tshow(v); });
      tn.addEventListener("keydown", (e) => { if (e.key === "Enter" && tn.value !== "") { e.preventDefault(); box.querySelector('[data-act="ap"]').click(); } });
      box.querySelector('[data-act="ap"]').addEventListener("click", () => { $(`#${k}_ap`).value = +(tcur / (PL(k) ? 1 : MUL(k, c))).toFixed(2); recalc(); toast("Angebotspreis übernommen."); });''')
rep('''<button class="kbtn sm" type="button" data-act="ap">Als Angebotspreis übernehmen</button>''', '''<button class="kbtn sm" type="button" data-act="ap">${ap > 0 ? "Preis ändern" : "Als Angebotspreis übernehmen"}</button>''')
# im kopierten Angebot
rep('''const n = c.stk, pr = k === "p" && !st.pser;
      return [...head,''', '''const n = c.stk, pr = k === "p" && !st.pser, apT = num(I[`${k}_ap`]) * (pr ? 1 : n), mwF = 1 + num(st.zus.mwst) / 100;
      if (apT > 0) head.push(`Angebotspreis: ${eur.format(apT)} netto / ${eur.format(apT * mwF)} brutto (kalkuliert ${eur.format(c.vk * n)}, ${apT - c.sk * n < 0 ? "Verlust" : "Gewinn"} beim Angebotspreis ${eur.format(Math.abs(apT - c.sk * n))})`);
      return [...head,''')

rep(''' · Zukauf ${eur.format(c.zk * c.stk)} · Probedrucke ${eur.format(c.prb * c.stk)}`, `Herkunft: ${srcName("p", I.p_src)}`]''',
    ''' · Zukauf ${eur.format(c.zk * c.stk)}${st.pser ? ` · Probedrucke ${eur.format(c.prb * c.stk)}` : ""}`, `Herkunft: ${srcName("p", I.p_src)}`]''')

# QR: Standardmaße ohne Fehlermeldung
rep('''const QRSTD = { ecc: "L", pw: 50, ph: 50, pt: 3, size: 42.5,''', '''const QRSTD = { ecc: "L", pw: 50, ph: 50, pt: 3.2, size: 42,''')
rep('''TS = { qr: { ...TS.qr, ...v.qr }, sch: v.sch || {}, vec: v.vec, vk: v.vk, pr: v.pr };''',
    '''TS = { qr: { ...TS.qr, ...v.qr }, sch: v.sch || {}, vec: v.vec, vk: v.vk, pr: v.pr }; if (num(TS.qr.size) === 42.5 && num(TS.qr.pw) === 50 && num(TS.qr.ph) === 50 && num(TS.qr.quiet) === 2) TS.qr.size = 42;''')
rep('''["auto", "Touch: beim Antippen · PC: Knopf im Feld"]''', '''["auto", "nur auf Touch-Geräten (empfohlen)"]''')

CSS = r'''
/* ================= Rechner 2: aufgeräumt ================= */
@media screen{
@media (hover:hover) and (pointer:fine){.app:not(.np-always) .npbtn{display:none!important}}
.kf:has(#p_ap),.kf:has(#l_ap){display:none!important}
.sp-th{align-items:center;gap:var(--space-sm)}
.sp-tryn{display:inline-flex;align-items:center;gap:8px;margin:0;font-size:13px;color:var(--color-muted);white-space:nowrap}
.sp-tryn input{width:7.2em;font:600 17px/1.2 var(--font-body);text-align:right;color:var(--color-ink);background:var(--ap-fill);border:1.5px solid transparent;border-radius:10px;padding:7px 10px;font-variant-numeric:tabular-nums;-moz-appearance:textfield;transition:border-color .2s var(--ap-ease),box-shadow .2s var(--ap-ease),background-color .2s var(--ap-ease)}
.sp-tryn input::-webkit-outer-spin-button,.sp-tryn input::-webkit-inner-spin-button{-webkit-appearance:none;margin:0}
.sp-tryn input:focus{outline:none;border-color:var(--color-accent);background:var(--color-paper-2);box-shadow:0 0 0 4px color-mix(in srgb,var(--color-accent) 22%,transparent)}
.sp-tryres.hint+.sp-tryb [data-act="ap"]{display:none}
.sp-tryb{display:flex;gap:8px;flex-wrap:wrap}
.sp-kpis b{font-weight:600;letter-spacing:-.02em}

/* Stammdaten in Gruppen */
.kst>summary{font-weight:600;letter-spacing:-.02em}
.kgrp{border-top:1px solid var(--color-rule);padding:0}
.kst .kgrp>summary{list-style:none;cursor:pointer;display:flex;justify-content:flex-start;align-items:baseline;gap:12px;padding:14px 2px;font:600 15.5px/1.3 var(--font-body);letter-spacing:-.012em}
.kgrp>summary::-webkit-details-marker{display:none}
.kgrp>summary small{font:400 13px/1.3 var(--font-body);color:var(--color-muted);flex:1;min-width:0}
.kst .kgrp>summary::after{content:""!important;font-size:0;flex:none;width:8px;height:8px;border-right:2px solid var(--color-muted);border-bottom:2px solid var(--color-muted);transform:rotate(45deg) translateY(-3px);transition:transform .3s var(--ap-ease)}
.kst .kgrp[open]>summary::after{transform:rotate(225deg) translateY(-2px)}
.kgrp>summary:hover{color:var(--color-accent)}
.kgrp>.ktab{margin:0 0 var(--space-md)}
.kst .pricebar{margin-bottom:var(--space-sm)}
.ktab td.pair{display:table-cell;white-space:nowrap;min-width:150px}
.ktab td.pair input{display:inline-block;width:calc(50% - 4px)}
.ktab td.pair input+input{margin-left:6px}
@media (prefers-reduced-motion:no-preference){.kgrp[open]>.ktab{animation:apUp .4s var(--ap-ease) both}}

/* Werkzeuge: Meldungen sortiert, Leeres weg */
.kinfo:empty,.kinfo:not(:has(*)){display:none}
.kinfo{display:flex;flex-direction:column;gap:6px}
.kinfo>*{margin:0}
.kinfo>:not(.kmsg){order:-4}
.kinfo>.kmsg.err{order:-3}.kinfo>.kmsg.warn{order:-2}.kinfo>.kmsg.ok{order:-1}
.kinfo>.kmsg:not(.err):not(.warn):not(.ok){font-size:13.5px;color:var(--color-muted)}
.kinfo>.kmsg.err,.kinfo>.kmsg.warn,.kinfo>.kmsg.ok{padding:9px 12px;border-radius:12px;font-weight:500}
.kinfo>.kmsg.err{background:var(--badbg)}.kinfo>.kmsg.warn{background:var(--warnbg)}.kinfo>.kmsg.ok{background:var(--okbg)}
#pane-m .ksech .kstep,#pane-c .ksech .kstep,#pane-w .ksech .kstep{display:none}

/* Materialkarten */
.mspec div.w{grid-column:span 1}
.mcard footer{flex-wrap:nowrap;align-items:flex-end}
.mcard footer .kbtn{flex:none;padding:8px 14px;font-size:13px}
}
'''
rep("</style>", CSS + "</style>")

JS = r'''<script>
(function () {
  var d = document, kst = d.getElementById("kst"); if (!kst) return;
  // Stammdaten: jede Überschrift mit ihrer Tabelle wird eine aufklappbare Gruppe; das Häufigste zuerst
  var hint = { "Lohn": "Stundensatz, Fehldruckquote, MwSt., Runden", "Preisgruppen": "Arbeitszeit, Gemeinkosten und Gewinn je Kundengruppe", "Filamente": "Preis je Rolle, Düsenverschleiß", "Lasermaterialien": "Plattenpreis, Geschwindigkeiten", "Maschinen": "Anschaffung, Laufzeit, Strom → Stundensatz", "Laser:": "Filter, Verschnitt, Aufsicht", "Richtwerte": "einmalige Zeit und Probedrucke je Herkunft" };
  var order = ["Lohn", "Preisgruppen", "Filamente", "Lasermaterialien", "Maschinen", "Laser:", "Richtwerte"], grp = {};
  [].slice.call(kst.querySelectorAll(":scope > h4")).forEach(function (h) {
    var tab = h.nextElementSibling; if (!tab || !tab.classList.contains("ktab")) return;
    var t = h.textContent.trim(), key = order.filter(function (k) { return t.indexOf(k) === 0; })[0] || t;
    var g = d.createElement("details"); g.className = "kgrp"; var sm = d.createElement("summary");
    sm.innerHTML = "<span></span><small></small>"; sm.firstChild.textContent = t.replace(/\s*\(.*\)$/, ""); sm.lastChild.textContent = hint[key] || "";
    kst.insertBefore(g, h); g.appendChild(sm); g.appendChild(tab); h.remove(); grp[key] = g;
  });
  var anchor = kst.querySelector(":scope > .krow");
  order.forEach(function (k) { if (grp[k] && anchor) kst.insertBefore(grp[k], anchor); });
  // „Werte anpassen“ und Sprünge in die Stammdaten öffnen die passende Gruppe
  d.addEventListener("click", function (e) {
    var b = e.target.closest && e.target.closest("#kprof_edit"); if (b && grp["Preisgruppen"]) grp["Preisgruppen"].open = true;
  }, true);
  kst.addEventListener("toggle", function () { if (kst.open && !kst.querySelector(".kgrp[open]") && grp["Lohn"]) grp["Lohn"].open = true; });
})();
</script>
'''
i = s.rfind("</body>")
s = s[:i] + JS + s[i:]

open(path, "w", encoding="utf-8").write(s)
print("Rechner 2:", path)
