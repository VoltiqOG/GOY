"""Seite: Rechte je Konto (was jemand sieht) und Kontenverwaltung für Verwalter direkt in der Seite.

Aufruf: python patch_verwaltung.py <unverschluesselte index.html>   (nach patch_konto.py)
- Rechte: Handbuch, Kostenrechner, Materialien, Modell prüfen und jedes Werkzeug einzeln; Verwalter als eigenes Recht.
  Die Anmeldeseite legt die Rechte des Kontos in sessionStorage („su3dl-rights“), die Seite blendet den Rest aus.
  Das ist Sichtbarkeit, kein Kopierschutz: Der Inhalt ist nach der Anmeldung im Browser vollständig vorhanden.
- Verwaltung (Konto-Menü → „Konten verwalten“): Anfragen sehen und freigeben, Konto-Code einfügen, Rechte per Haken,
  Konto entfernen (wechselt den Seitenschlüssel). Gespeichert wird als Commit über die GitHub-API – dafür braucht der
  Verwalter ein eigenes Token (nur dieses Repository, „Contents: Read and write“), das nur in seinem Browser liegt.
- Benachrichtigung: Punkt am Konto-Symbol und Hinweis, sobald Anfragen vorliegen (verschlüsselt über den Kanal aus NTFY).
"""
import sys

path = sys.argv[1]
s = open(path, encoding="utf-8").read()


def rep(a, b, n=1):
    global s
    if s.count(a) != n:
        raise SystemExit(f"Stelle {s.count(a)}× statt {n}× gefunden: " + a[:90])
    s = s.replace(a, b)


rep('''<button type="button" data-acct="pw">Passwort ändern</button><button type="button" data-acct="out">Abmelden</button></div></div>''',
    '''<button type="button" id="admopen" hidden>Konten verwalten <span class="admn" id="admn" hidden></span></button><button type="button" data-acct="pw">Passwort ändern</button><button type="button" data-acct="out">Abmelden</button></div></div>''')
rep('''<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="8" r="3.6"/>''',
    '''<span class="admdot" id="admdot" hidden></span><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="8" r="3.6"/>''')

DLG = '''<dialog id="adm" class="adm" aria-labelledby="admt">
  <div class="admbox">
    <header><h2 id="admt">Konten verwalten</h2><button type="button" class="ib" id="admx" aria-label="Schließen">✕</button></header>
    <div class="admbody">
      <section id="adm_tok" hidden>
        <h3>Einmalig: Speichern erlauben</h3>
        <p>Änderungen an Konten werden in die Seite auf GitHub geschrieben. Dafür braucht dieser Browser ein GitHub-Token von dir: <a href="https://github.com/settings/personal-access-tokens/new" target="_blank" rel="noopener">Fine-grained Token anlegen</a> → Repository access: <b>Only select repositories</b> → <b id="adm_repo"></b> → Permissions → Repository → <b>Contents: Read and write</b>. Das Token bleibt nur in diesem Browser.</p>
        <div class="admrow"><input type="password" id="adm_tokin" placeholder="github_pat_…" autocomplete="off" spellcheck="false"><button type="button" class="kbtn pri" id="adm_toksave">Token speichern</button></div>
        <label class="admchk"><input type="checkbox" id="adm_tokkeep" checked> auf diesem Gerät merken</label>
      </section>
      <p class="admmsg" id="adm_msg" role="status" aria-live="polite"></p>
      <section id="adm_req">
        <h3>Anfragen <span class="admcount" id="adm_reqn"></span></h3>
        <div id="adm_reql"></div>
        <details class="admpaste"><summary>Konto-Code von Hand einfügen</summary>
          <textarea id="adm_code" rows="3" placeholder="SU3DL1.…" spellcheck="false"></textarea><button type="button" class="kbtn" id="adm_codeadd">Code prüfen</button></details>
      </section>
      <section>
        <h3>Konten <span class="admcount" id="adm_usern"></span></h3>
        <div id="adm_users"></div>
      </section>
    </div>
    <footer><span id="adm_dirty"></span><button type="button" class="kbtn ghost" id="adm_reset">Verwerfen</button><button type="button" class="kbtn pri" id="adm_save" disabled>Speichern</button></footer>
  </div>
</dialog>
'''
i = s.rfind("</body>")
s = s[:i] + DLG + s[i:]

rep("</style>", r'''
@media screen{
/* Rechte: ausblenden, was das Konto nicht nutzen darf */
html.no-rechner #tab-p,html.no-rechner #tab-s,html.no-rechner #tab-l,html.no-rechner .tgrid li:has(a[href="#rechner"]),html.no-rechner .tgrid li:has(a[href="#rechner-laser"]),
html.no-material #tab-m,html.no-material .tgrid li:has(a[href="#rechner-material"]),
html.no-pruefen #tab-c,html.no-pruefen .tgrid li:has(a[href="#rechner-pruefen"]),
html.no-qr #w_seg [data-w="qr"],html.no-qr .tgrid li:has(a[href$="-qr"]),html.no-sch #w_seg [data-w="sch"],html.no-sch .tgrid li:has(a[href$="-sch"]),
html.no-vec #w_seg [data-w="vec"],html.no-vec .tgrid li:has(a[href$="-vec"]),html.no-vk #w_seg [data-w="vk"],html.no-vk .tgrid li:has(a[href$="-vk"]),
html.no-pr #w_seg [data-w="pr"],html.no-pr .tgrid li:has(a[href$="-pr"]),
html.no-werkzeuge #tab-w,html.no-app .calcbtn,html.no-app #werkzeuge,html.no-app .hero .cta a[href="#werkzeuge"],
html.no-doku #kapitel,html.no-doku #sicherheit,html.no-doku #maschinen,html.no-doku #ablauf,html.no-doku #schnellstart,html.no-doku #handbuch,html.no-doku .nl,html.no-doku #sb,html.no-doku #menu,html.no-doku .hero .cta a[href^="#kapitel"],html.no-doku .totop,html.no-doku .prog{display:none!important}
html.no-rechner .apptabs #tab-l::after{display:none}

.admdot{position:absolute;top:5px;right:5px;width:9px;height:9px;border-radius:50%;background:var(--color-bad);box-shadow:0 0 0 2px var(--color-paper)}
#acctb{position:relative}
.admn{display:inline-block;min-width:20px;padding:1px 6px;border-radius:980px;background:var(--color-bad);color:#fff;font-size:12px;font-weight:600;text-align:center;margin-left:6px}
dialog.adm{width:min(860px,calc(100vw - 24px));max-height:min(88vh,900px);padding:0;border-radius:24px;background:var(--color-paper);color:var(--color-ink);box-shadow:0 40px 90px -30px rgba(0,0,0,.5);overflow:hidden}
dialog.adm[open]{display:flex}
.admbox{display:flex;flex-direction:column;width:100%;min-height:0}
.admbox>header{display:flex;align-items:center;justify-content:space-between;padding:18px 22px;border-bottom:1px solid var(--color-rule)}
.admbox>header h2{margin:0;font:600 21px/1.2 var(--font-display);letter-spacing:-.02em}
.admbody{overflow:auto;padding:6px 22px 18px;flex:1;min-height:0}
.admbody h3{font:600 16px/1.3 var(--font-body);margin:18px 0 10px;display:flex;align-items:center;gap:8px}
.admbody p{margin:0 0 10px;font-size:14.5px;color:var(--color-ink-2)}
.admcount{font:500 12.5px/1 var(--font-body);color:var(--color-muted);background:var(--ap-fill,var(--color-paper-3));padding:4px 8px;border-radius:980px}
.admmsg{margin:12px 0 0!important;padding:10px 14px;border-radius:12px;font-weight:500;line-height:1.4}
.admmsg:empty{display:none}.admmsg.ok{background:var(--okbg);color:var(--ok)}.admmsg.err{background:var(--badbg);color:var(--bad)}.admmsg.info{background:var(--ap-fill,var(--color-paper-3));color:var(--color-ink-2)}
.admrow{display:flex;gap:8px;flex-wrap:wrap}
.admrow input,.admpaste textarea{flex:1;min-width:200px;font:15px/1.4 var(--font-body);padding:10px 12px;border-radius:12px;border:1.5px solid transparent;background:var(--ap-fill,var(--color-paper-3));color:var(--color-ink)}
.admrow input:focus,.admpaste textarea:focus{outline:none;border-color:var(--color-accent);background:var(--color-paper-2)}
.admpaste textarea{display:block;width:100%;margin:10px 0 8px;font:12.5px/1.4 ui-monospace,Menlo,Consolas,monospace;resize:vertical}
.admpaste summary{cursor:pointer;font-size:14px;color:var(--color-cool)}
.admchk{display:flex;gap:8px;align-items:center;font-size:13.5px;color:var(--color-muted);margin-top:8px}
.admcard{background:var(--color-paper-2);border-radius:18px;padding:14px 16px;margin-bottom:10px;box-shadow:0 1px 2px rgba(0,0,0,.04),0 8px 22px -14px rgba(0,0,0,.18)}
.admcard.neu{box-shadow:inset 0 0 0 2px var(--color-accent)}.admcard.weg{opacity:.5}
.admhead{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.admhead b{font-weight:600;font-size:16px}.admhead small{color:var(--color-muted);font-size:13px}
.admhead .sp{flex:1}
.admtag{font-size:12px;font-weight:600;padding:3px 8px;border-radius:980px;background:var(--color-accent-soft);color:var(--color-accent)}
.admtag.warn{background:var(--warnbg);color:var(--warn)}
.admrights{display:flex;flex-wrap:wrap;gap:6px;margin-top:12px}
.admrights label{display:inline-flex;align-items:center;gap:6px;padding:6px 11px;border-radius:980px;background:var(--ap-fill,var(--color-paper-3));font-size:13.5px;cursor:pointer;user-select:none;transition:background-color .2s,color .2s}
.admrights label:has(input:checked){background:var(--color-accent);color:#fff}
.admrights label:has(input:disabled){opacity:.55;cursor:not-allowed}
.admrights label.adm-a:has(input:checked){background:var(--color-ink);color:var(--color-paper)}
.admrights input{position:absolute;opacity:0;pointer-events:none}
.admrights .grp{flex-basis:100%;font-size:12px;color:var(--color-muted);margin-top:4px}
.admbtn{all:unset;cursor:pointer;font-size:13.5px;font-weight:500;padding:6px 12px;border-radius:980px;color:var(--color-cool)}
.admbtn:hover{background:var(--ap-fill,var(--color-paper-3))}.admbtn.bad{color:var(--color-bad)}.admbtn.pri{background:var(--color-accent);color:#fff}
.admempty{font-size:14px;color:var(--color-muted);padding:4px 0 8px}
.admbox>footer{display:flex;align-items:center;gap:10px;padding:14px 22px;border-top:1px solid var(--color-rule);background:var(--color-paper-2)}
.admbox>footer span{flex:1;font-size:14px;color:var(--color-muted)}
@media (max-width:600px){dialog.adm{max-height:94vh;border-radius:20px}.admbody{padding:4px 14px 14px}.admbox>header,.admbox>footer{padding:14px}}
}
@media print{dialog.adm{display:none!important}}
</style>''')

JS = r'''<script>
(function () {
  "use strict";
  var d = document, root = d.documentElement, $ = function (id) { return d.getElementById(id); };
  var SK = "su3dl-k2", SI = "su3dl-uid", SR = "su3dl-rights", REPO = "VoltiqOG/GOY", BRANCH = "main", FILE = "index.html";
  var ALL = ["doku", "rechner", "material", "pruefen", "qr", "sch", "vec", "vk", "pr"], TOOLS = ["qr", "sch", "vec", "vk", "pr"];
  var LAB = { doku: "Handbuch", rechner: "Kostenrechner", material: "Materialien", pruefen: "Modell prüfen", qr: "QR-Code", sch: "Typenschild", vec: "Bild → SVG", vk: "Visitenkarte", pr: "Präger" };
  var gs = function (k) { try { return sessionStorage.getItem(k) || localStorage.getItem(k); } catch (e) { return null; } };

  // ---------- Rechte anwenden
  var rs = (gs(SR) || "*").split(","), isAdmin = rs.indexOf("admin") >= 0, has = function (r) { return rs.indexOf("*") >= 0 || rs.indexOf(r) >= 0; };
  ALL.forEach(function (r) { if (!has(r)) root.classList.add("no-" + r); });
  if (!TOOLS.some(has)) root.classList.add("no-werkzeuge");
  var HASH = { rechner: "rechner", material: "rechner-material", pruefen: "rechner-pruefen" }, first = null;
  ["rechner", "material", "pruefen"].concat(TOOLS).forEach(function (r) { if (!first && has(r)) first = HASH[r] || "rechner-werkzeuge-" + r; });
  if (!first) root.classList.add("no-app");
  function need(h) { if (!/^rechner/.test(h)) return null; if (h === "rechner-material") return "material"; if (h === "rechner-pruefen") return "pruefen"; var m = /^rechner-werkzeuge(?:-(\w+))?$/.exec(h); if (m) return m[1] || "werkzeuge"; return "rechner"; }
  function guard() {
    var h = location.hash.slice(1), n = need(h);
    if (n && n !== "werkzeuge" && !has(n)) { location.replace("#" + (first || "")); return; }
    if (n === "werkzeuge" && !TOOLS.some(has)) { location.replace("#" + (first || "")); return; }
    if (n && TOOLS.indexOf(n) < 0 && n !== "werkzeuge") return;
    setTimeout(function () { var on = d.querySelector('#w_seg button[aria-pressed="true"]'); if (on && !has(on.dataset.w)) { var b = TOOLS.filter(has)[0]; if (b) d.querySelector('#w_seg [data-w="' + b + '"]').click(); } }, 0);
  }
  if (rs.indexOf("*") < 0) {
    addEventListener("hashchange", function () { setTimeout(guard, 0); }); setTimeout(guard, 0);
    d.addEventListener("click", function (e) { if (e.target.closest && e.target.closest(".apptabs,#w_seg")) setTimeout(guard, 0); });
    var cb = $("calcbtn"); if (cb && first) cb.setAttribute("href", "#" + first);
    if (!has("doku") && first && !location.hash) location.replace("#" + first);
  }
  if (!isAdmin) return;

  // ---------- Verwaltung (nur Verwalter)
  var enc = new TextEncoder(), dec = new TextDecoder(), EC = { name: "ECDH", namedCurve: "P-256" }, CS = crypto.subtle;
  var b64 = function (t) { return Uint8Array.from(atob(t), function (c) { return c.charCodeAt(0); }); };
  var toB64 = function (u) { var a = new Uint8Array(u), t = ""; for (var i = 0; i < a.length; i += 0x8000) t += String.fromCharCode.apply(null, a.subarray(i, i + 0x8000)); return btoa(t); };
  var esc = function (t) { return String(t).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); };
  var aes = function (raw, use) { return CS.importKey("raw", raw, "AES-GCM", false, use); };
  async function seal(key, data) { var iv = crypto.getRandomValues(new Uint8Array(12)), ct = new Uint8Array(await CS.encrypt({ name: "AES-GCM", iv: iv }, key, data)), o = new Uint8Array(12 + ct.length); o.set(iv); o.set(ct, 12); return o; }
  var unseal = function (key, blob) { return CS.decrypt({ name: "AES-GCM", iv: blob.slice(0, 12) }, key, blob.slice(12)); };
  async function hk(bits, use) { return CS.deriveKey({ name: "HKDF", hash: "SHA-256", salt: new Uint8Array(32), info: enc.encode("su3dl-k") }, await CS.importKey("raw", bits, "HKDF", false, ["deriveKey"]), { name: "AES-GCM", length: 256 }, false, [use]); }
  async function wrapKey(Kraw, pubB64) { var eph = await CS.generateKey(EC, true, ["deriveBits"]), bits = await CS.deriveBits({ name: "ECDH", public: await CS.importKey("raw", b64(pubB64), EC, false, []) }, eph.privateKey, 256);
    return { e: toB64(await CS.exportKey("raw", eph.publicKey)), k: toB64(await seal(await hk(bits, "encrypt"), Kraw)) }; }
  async function uid(u) { return Array.from(new Uint8Array(await CS.digest("SHA-256", enc.encode("su3dl|" + String(u).trim().toLowerCase())))).slice(0, 16).map(function (x) { return x.toString(16).padStart(2, "0"); }).join(""); }
  function parseCode(code) { code = String(code || "").replace(/\s+/g, ""); if (code.indexOf("SU3DL1.") !== 0) return null;
    try { var raw = code.slice(7).replace(/-/g, "+").replace(/_/g, "/"), j = JSON.parse(dec.decode(b64(raw + "=".repeat((4 - raw.length % 4) % 4))));
      if (!/^[a-z0-9._-]{3,30}$/.test(j.u) || b64(j.s).length !== 16 || b64(j.w).length < 100 || b64(j.p).length !== 65) return null;
      return { n: String(j.n).replace(/\t/g, " ").trim().slice(0, 80), u: j.u, s: j.s, w: j.w, p: j.p }; } catch (e) { return null; } }

  var RX = { users: /const USERS = (\{.*?\});\n/, req: /const REQ = (\{.*?\});\n/, ntfy: /const NTFY = "([^"]*)";/, data: /const IV = "([^"]*)", DATA = "([^"]*)"/ };
  var S = null; // geladener Stand: { text, sha, users, req, ntfy, K (raw), key, list:[…], reqs:[…] }
  var tok = function () { return gs("su3dl-ghtok") || ""; };
  var msg = function (cls, t) { var m = $("adm_msg"); m.className = "admmsg " + cls; m.textContent = t || ""; };
  async function gh(path, opt) { var r = await fetch("https://api.github.com/repos/" + REPO + path, Object.assign({ headers: { Authorization: "Bearer " + tok(), Accept: "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28" } }, opt || {}));
    if (!r.ok) { var e = new Error(r.status === 401 ? "Das GitHub-Token ist ungültig oder abgelaufen." : r.status === 403 || r.status === 404 ? "Das Token hat keinen Schreibzugriff auf " + REPO + " (Contents: Read and write)." : r.status === 409 || r.status === 422 ? "Die Seite wurde inzwischen von jemand anderem geändert – bitte neu laden." : "GitHub antwortet mit Fehler " + r.status + "."); e.status = r.status; throw e; }
    return r.json(); }
  async function parse(text, sha) {
    var Kraw = b64(gs(SK)).buffer, key = await aes(Kraw, ["encrypt", "decrypt"]), users = JSON.parse(RX.users.exec(text)[1]);
    var st = { text: text, sha: sha, users: users, req: JSON.parse((RX.req.exec(text) || [0, "{}"])[1]), ntfy: (RX.ntfy.exec(text) || [0, ""])[1], K: Kraw, key: key, list: [] };
    for (var id in users) { var e = users[id], t; try { t = dec.decode(await unseal(key, b64(e.n))).split("\t"); } catch (err) { throw new Error("Dein Gerät hat einen älteren Schlüssel als die Seite – bitte ab- und wieder anmelden."); }
      var r = (t[2] || "*").split(",").filter(Boolean); if (e.a && r.indexOf("admin") < 0) r.push("admin");
      st.list.push({ id: id, e: e, name: t[0], user: t[1] || "?", rights: r, orig: r.slice().sort().join(), neu: false, weg: false }); }
    st.list.sort(function (a, b) { return a.name.localeCompare(b.name, "de"); });
    return st;
  }
  async function loadSite() { var r = await fetch(location.pathname + "?v=" + Date.now(), { cache: "no-store" }); return r.text(); }
  async function loadGit() { var m = await gh("/contents/" + FILE + "?ref=" + BRANCH), blob = await gh("/git/blobs/" + m.sha); return { text: dec.decode(b64(blob.content.replace(/\s+/g, ""))), sha: m.sha }; }

  // Anfragen aus dem Benachrichtigungskanal lesen (verschlüsselt für den Anfrage-Schlüssel) und lokal merken
  var RQ = "su3dl-req", IGN = "su3dl-req-x";
  var lsj = function (k, f) { try { return JSON.parse(localStorage.getItem(k)) || f; } catch (e) { return f; } };
  async function pollReq(st) {
    var known = lsj(RQ, {}), ign = lsj(IGN, []);
    if (st.ntfy && st.req.w) { try {
      var priv = await CS.importKey("pkcs8", await unseal(st.key, b64(st.req.w)), EC, false, ["deriveBits"]);
      var r = await fetch(st.ntfy + "/json?poll=1&since=12h", { cache: "no-store" }), lines = (await r.text()).split("\n");
      for (var i = 0; i < lines.length; i++) { if (!lines[i].trim()) continue; var m; try { m = JSON.parse(lines[i]); } catch (e) { continue; }
        if (m.event !== "message" || String(m.message).indexOf("SU3DLR1.") !== 0) continue;
        try { var raw = b64(m.message.slice(8)), bits = await CS.deriveBits({ name: "ECDH", public: await CS.importKey("raw", raw.slice(0, 65), EC, false, []) }, priv, 256);
          var code = dec.decode(await unseal(await hk(bits, "decrypt"), raw.slice(65))), c = parseCode(code);
          if (c && !known[c.p]) known[c.p] = { code: code, t: (m.time || Date.now() / 1000) * 1000 }; } catch (e) {} }
    } catch (e) {} }
    var out = [], ps = {}; for (var id in st.users) ps[st.users[id].p] = 1;
    for (var p in known) { if (ps[p] || ign.indexOf(p) >= 0 || Date.now() - known[p].t > 45 * 864e5) { delete known[p]; continue; } var c2 = parseCode(known[p].code); if (c2) { c2.t = known[p].t; c2.code = known[p].code; out.push(c2); } }
    try { localStorage.setItem(RQ, JSON.stringify(known)); } catch (e) {}
    out.sort(function (a, b) { return b.t - a.t; }); st.reqs = out; return out;
  }
  function badge(n) { $("admdot").hidden = !n; var b = $("admn"); b.hidden = !n; b.textContent = n || ""; }

  // ---------- Oberfläche
  var dlg = $("adm"), dirty = function () { return S ? S.list.filter(function (x) { return x.neu || x.weg || x.rights.slice().sort().join() !== x.orig; }).length : 0; };
  function rightsHtml(x, i) { var star = x.rights.indexOf("*") >= 0, me = x.id === gs(SI);
    var chk = function (r, lab, cls, dis) { return '<label class="' + (cls || "") + '"><input type="checkbox" data-i="' + i + '" data-r="' + r + '"' + ((r === "admin" ? x.rights.indexOf("admin") >= 0 : star || x.rights.indexOf(r) >= 0) ? " checked" : "") + (dis ? " disabled" : "") + ">" + lab + "</label>"; };
    return '<div class="admrights"><span class="grp">Darf sehen und nutzen</span>' + ["doku", "rechner", "material", "pruefen"].map(function (r) { return chk(r, LAB[r], "", x.weg); }).join("") + '<span class="grp">Werkzeuge</span>' + TOOLS.map(function (r) { return chk(r, LAB[r], "", x.weg); }).join("") + '<span class="grp">Verwaltung</span>' + chk("admin", "Verwalter", "adm-a", x.weg || me) + "</div>"; }
  function render() {
    if (!S) return; var me = gs(SI);
    $("adm_users").innerHTML = S.list.map(function (x, i) { return '<div class="admcard' + (x.neu ? " neu" : "") + (x.weg ? " weg" : "") + '"><div class="admhead"><b>' + esc(x.name) + "</b><small>" + esc(x.user) + "</small>" + (x.id === me ? '<span class="admtag">du</span>' : "") + (x.neu ? '<span class="admtag">' + (x.ersetzt ? "neues Passwort" : "neu") + "</span>" : "") + (x.weg ? '<span class="admtag warn">wird entfernt</span>' : "") + '<span class="sp"></span>' +
      (x.id === me ? "" : x.weg || x.neu ? '<button type="button" class="admbtn" data-undo="' + i + '">Rückgängig</button>' : '<button type="button" class="admbtn bad" data-del="' + i + '">Entfernen</button>') + "</div>" + rightsHtml(x, i) + "</div>"; }).join("");
    $("adm_usern").textContent = S.list.filter(function (x) { return !x.weg; }).length;
    var rq = (S.reqs || []).filter(function (c) { return !S.list.some(function (x) { return x.neu && x.code === c.code; }); });
    $("adm_reql").innerHTML = rq.length ? rq.map(function (c) { var ex = S.list.filter(function (x) { return x.user === c.u && !x.neu; })[0];
      return '<div class="admcard"><div class="admhead"><b>' + esc(c.n) + "</b><small>" + esc(c.u) + " · " + new Date(c.t).toLocaleString("de-DE", { dateStyle: "short", timeStyle: "short" }) + "</small>" + (ex ? '<span class="admtag warn">neues Passwort für ' + esc(ex.name) + " – vorher nachfragen</span>" : "") + '<span class="sp"></span><button type="button" class="admbtn bad" data-ign="' + esc(c.p) + '">Ablehnen</button><button type="button" class="admbtn pri" data-ok="' + esc(c.p) + '">' + (ex ? "Passwort ersetzen" : "Freigeben") + "</button></div></div>"; }).join("") : '<p class="admempty">Keine offenen Anfragen.</p>';
    $("adm_reqn").textContent = rq.length; $("adm_reqn").hidden = !rq.length; badge(rq.length);
    var n = dirty(); $("adm_dirty").textContent = n ? n + (n === 1 ? " Änderung" : " Änderungen") + " – noch nicht gespeichert" : ""; $("adm_save").disabled = !n || !tok(); $("adm_reset").hidden = !n;
    $("adm_tok").hidden = !!tok(); $("adm_repo").textContent = REPO;
  }
  async function addCode(c) {
    if (!c) { msg("err", "Das ist kein gültiger Konto-Code."); return; }
    var id = await uid(c.u), old = S.list.filter(function (x) { return x.id === id; })[0];
    if (old && old.neu) { msg("info", "Dieses Konto ist schon vorgemerkt."); return; }
    var x = { id: id, e: { s: c.s, w: c.w, p: c.p }, name: c.n, user: c.u, rights: old ? old.rights.slice() : ["*"], orig: "", neu: true, weg: false, code: c.code, ersetzt: old || null };
    if (old) S.list.splice(S.list.indexOf(old), 1, x); else S.list.unshift(x);
    msg("info", (old ? "Neues Passwort für " : "Konto für ") + c.n + " vorgemerkt – Rechte wählen und speichern."); render();
  }
  async function open() {
    if (!dlg.open) dlg.showModal(); msg("info", "Wird geladen …");
    try { var f = tok() ? await loadGit() : { text: await loadSite(), sha: null }; S = await parse(f.text, f.sha); await pollReq(S); msg("", ""); if (!tok()) msg("info", "Zum Speichern einmalig ein GitHub-Token hinterlegen (unten erklärt). Ansehen geht auch ohne."); render(); }
    catch (e) { msg("err", e.message || "Laden hat nicht geklappt."); if (e.status === 401) { try { localStorage.removeItem("su3dl-ghtok"); sessionStorage.removeItem("su3dl-ghtok"); } catch (x) {} render(); } }
  }
  async function save() {
    var b = $("adm_save"); b.disabled = true; msg("info", "Wird gespeichert …");
    try {
      var cur = await loadGit(); if (S.sha && cur.sha !== S.sha) { msg("err", "Die Seite wurde inzwischen geändert (z. B. neuer Inhalt). Die Liste wird neu geladen – bitte Änderungen noch einmal vornehmen."); await open(); return; }
      var admins = S.list.filter(function (x) { return !x.weg && x.rights.indexOf("admin") >= 0; }); if (!admins.length) { msg("err", "Mindestens ein Verwalter muss bleiben."); render(); return; }
      var rot = S.list.some(function (x) { return x.weg; }), Kraw = S.K, key = S.key, text = cur.text, req = S.req;
      if (rot) { // Konto entfernt: neuer Seitenschlüssel, Inhalt neu verschlüsseln
        var m = RX.data.exec(text), plain = await CS.decrypt({ name: "AES-GCM", iv: b64(m[1]) }, S.key, b64(m[2]));
        Kraw = crypto.getRandomValues(new Uint8Array(32)).buffer; key = await aes(Kraw, ["encrypt", "decrypt"]);
        var iv = crypto.getRandomValues(new Uint8Array(12)), ct = await CS.encrypt({ name: "AES-GCM", iv: iv }, key, plain);
        text = text.replace(RX.data, function () { return 'const IV = "' + toB64(iv) + '", DATA = "' + toB64(ct) + '"'; });
        if (req.w) req = { p: req.p, w: toB64(await seal(key, await unseal(S.key, b64(req.w)))) };
      }
      var users = {};
      for (var i = 0; i < S.list.length; i++) { var x = S.list[i]; if (x.weg) continue;
        var r = x.rights.indexOf("*") >= 0 ? ["*"].concat(x.rights.indexOf("admin") >= 0 ? ["admin"] : []) : x.rights.slice();
        var e = { s: x.e.s, w: x.e.w, p: x.e.p }; if (rot || x.neu) { var wk = await wrapKey(Kraw, x.e.p); e.e = wk.e; e.k = wk.k; } else { e.e = x.e.e; e.k = x.e.k; }
        e.n = toB64(await seal(key, enc.encode([x.name, x.user, r.join(",")].join("\t")))); if (r.indexOf("admin") >= 0) e.a = 1; users[x.id] = e; }
      var ids = Object.keys(users).sort(), sorted = {}; ids.forEach(function (k) { var o = {}; Object.keys(users[k]).sort().forEach(function (f) { o[f] = users[k][f]; }); sorted[k] = o; });
      text = text.replace(RX.users, function () { return "const USERS = " + JSON.stringify(sorted) + ";\n"; });
      if (RX.req.test(text)) text = text.replace(RX.req, function () { return "const REQ = " + JSON.stringify(req) + ";\n"; });
      var names = S.list.filter(function (x) { return x.neu || x.weg; }).length, res = await gh("/contents/" + FILE, { method: "PUT", body: JSON.stringify({ message: "Konten geändert (Verwaltung in der Seite)", content: toB64(enc.encode(text)), sha: cur.sha, branch: BRANCH }) });
      if (rot) { try { sessionStorage.setItem(SK, toB64(Kraw)); if (localStorage.getItem(SK)) localStorage.setItem(SK, toB64(Kraw)); } catch (e2) {} }
      var ign = lsj(IGN, []); try { localStorage.setItem(IGN, JSON.stringify(ign.slice(-200))); } catch (e3) {}
      S = await parse(text, res.content.sha); await pollReq(S); render();
      msg("ok", "Gespeichert. In etwa einer Minute ist die Änderung für alle aktiv." + (rot ? " Der Seitenschlüssel wurde gewechselt – alle anderen melden sich einmal neu an." : ""));
    } catch (e) { msg("err", e.message || "Speichern hat nicht geklappt."); render(); }
  }

  $("admopen").hidden = false; $("admopen").addEventListener("click", function () { $("acctm").hidden = true; open(); });
  $("admx").addEventListener("click", function () { if (dirty() && !confirmClose()) return; dlg.close(); });
  var closeArmed = 0; function confirmClose() { if (Date.now() - closeArmed < 4000) return true; closeArmed = Date.now(); msg("info", "Es gibt ungespeicherte Änderungen – zum Verwerfen noch einmal auf ✕ klicken."); return false; }
  dlg.addEventListener("cancel", function (e) { if (dirty() && !confirmClose()) e.preventDefault(); });
  $("adm_toksave").addEventListener("click", function () { var v = $("adm_tokin").value.trim(); if (!/^(github_pat_|ghp_)[\w]+$/.test(v)) { msg("err", "Das sieht nicht wie ein GitHub-Token aus (beginnt mit github_pat_)."); return; }
    try { sessionStorage.setItem("su3dl-ghtok", v); if ($("adm_tokkeep").checked) localStorage.setItem("su3dl-ghtok", v); } catch (e) {} $("adm_tokin").value = ""; var keep = S ? S.list : null; open().then(function () { if (keep && S) { /* vorgemerkte Änderungen behalten */ keep.forEach(function (x) { if (x.neu && !S.list.some(function (y) { return y.id === x.id && y.neu; })) { var o = S.list.filter(function (y) { return y.id === x.id; })[0]; if (o) S.list.splice(S.list.indexOf(o), 1, x); else S.list.unshift(x); } }); render(); } }); });
  $("adm_codeadd").addEventListener("click", function () { var c = parseCode($("adm_code").value); if (c) { c.code = $("adm_code").value.replace(/\s+/g, ""); $("adm_code").value = ""; } addCode(c); });
  $("adm_reset").addEventListener("click", function () { open(); });
  $("adm_save").addEventListener("click", save);
  dlg.addEventListener("click", function (e) {
    var t = e.target; if (!S || !t.closest) return; var b;
    if ((b = t.closest("[data-del]"))) { var x = S.list[+b.dataset.del]; x.weg = true; msg("info", x.name + " wird beim Speichern entfernt. Dabei wechselt der Seitenschlüssel: Alle anderen melden sich einmal neu an."); render(); }
    else if ((b = t.closest("[data-undo]"))) { var y = S.list[+b.dataset.undo]; if (y.neu) { if (y.ersetzt) S.list.splice(+b.dataset.undo, 1, y.ersetzt); else S.list.splice(+b.dataset.undo, 1); } else y.weg = false; msg("", ""); render(); }
    else if ((b = t.closest("[data-ok]"))) { var c = (S.reqs || []).filter(function (q) { return q.p === b.dataset.ok; })[0]; addCode(c); }
    else if ((b = t.closest("[data-ign]"))) { var ign = lsj(IGN, []); ign.push(b.dataset.ign); try { localStorage.setItem(IGN, JSON.stringify(ign)); } catch (e2) {} S.reqs = (S.reqs || []).filter(function (q) { return q.p !== b.dataset.ign; }); render(); }
  });
  dlg.addEventListener("change", function (e) { var t = e.target; if (!S || !t.dataset || !t.dataset.r) return; var x = S.list[+t.dataset.i], r = t.dataset.r;
    if (r === "admin") { if (t.checked) x.rights.push("admin"); else x.rights = x.rights.filter(function (q) { return q !== "admin"; }); }
    else { var adm = x.rights.indexOf("admin") >= 0, set = x.rights.indexOf("*") >= 0 ? ALL.slice() : x.rights.filter(function (q) { return q !== "admin"; });
      if (t.checked) { if (set.indexOf(r) < 0) set.push(r); } else set = set.filter(function (q) { return q !== r; });
      x.rights = (ALL.every(function (q) { return set.indexOf(q) >= 0; }) ? ["*"] : ALL.filter(function (q) { return set.indexOf(q) >= 0; })).concat(adm ? ["admin"] : []); }
    render(); });

  // Beim Öffnen der Seite nach Anfragen sehen (Punkt am Konto-Symbol + Hinweis)
  setTimeout(async function () { try { var st = await parse(await loadSite(), null), rq = await pollReq(st); badge(rq.length);
    if (rq.length) { var t = $("toast"); if (t) { t.textContent = rq.length === 1 ? "Neue Konto-Anfrage von " + rq[0].n + " – Konto-Menü → Konten verwalten" : rq.length + " neue Konto-Anfragen – Konto-Menü → Konten verwalten"; t.classList.add("show"); setTimeout(function () { t.classList.remove("show"); }, 6000); } } } catch (e) {} }, 1500);
})();
</script>
'''
i = s.rfind("</body>")
s = s[:i] + JS + s[i:]
open(path, "w", encoding="utf-8").write(s)
print("Verwaltung:", path)
