"""Seite: Konto-Menü (angemeldet als …, Passwort ändern, Abmelden) in Navigation und Fußzeile.

Aufruf: python patch_konto.py <unverschluesselte index.html>
"""
import sys

path = sys.argv[1]
s = open(path, encoding="utf-8").read()


def rep(a, b, n=1):
    global s
    if s.count(a) != n:
        raise SystemExit(f"Stelle {s.count(a)}× statt {n}× gefunden: " + a[:90])
    s = s.replace(a, b)


rep('''<button class="ib" id="menu" type="button" aria-label="Inhaltsverzeichnis">''',
    '''<div class="acct" id="acct"><button class="ib" id="acctb" type="button" aria-label="Konto" aria-haspopup="true" aria-expanded="false" title="Konto"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="8" r="3.6"/><path d="M4.5 20c1-3.6 4-5.4 7.5-5.4s6.5 1.8 7.5 5.4"/></svg></button>
      <div class="acctm" id="acctm" hidden><div class="acctn"><small>Angemeldet als</small><b id="acctname">–</b></div><button type="button" data-acct="pw">Passwort ändern</button><button type="button" data-acct="out">Abmelden</button></div></div>
    <button class="ib" id="menu" type="button" aria-label="Inhaltsverzeichnis">''')
rep('''<span>Technische Daten nach Herstellerangaben. Es gilt die Betriebsanleitung des Herstellers.</span></div></footer>''',
    '''<span>Technische Daten nach Herstellerangaben. Es gilt die Betriebsanleitung des Herstellers.</span><span class="acctf">Angemeldet als <b id="acctname2">–</b> · <button type="button" data-acct="pw">Passwort ändern</button> · <button type="button" data-acct="out">Abmelden</button></span></div></footer>''')
rep("</style>", '''
@media screen{
.acct{position:relative;display:flex}
.acctm{position:absolute;right:0;top:calc(100% + 10px);z-index:60;min-width:220px;padding:8px;border-radius:16px;background:var(--color-paper-2);box-shadow:0 0 0 1px color-mix(in srgb,var(--color-ink) 8%,transparent),0 18px 40px -12px rgba(0,0,0,.3);display:grid;gap:2px}
.acctn{padding:8px 12px 10px;border-bottom:1px solid var(--color-rule);margin-bottom:4px;display:grid}
.acctn small{font-size:12px;color:var(--color-muted)}.acctn b{font-weight:600;overflow-wrap:anywhere}
.acctm button{all:unset;box-sizing:border-box;width:100%;padding:9px 12px;border-radius:10px;font:500 14.5px/1.3 var(--font-body);color:var(--color-ink);cursor:pointer}
.acctm button:hover,.acctm button:focus-visible{background:var(--ap-fill,var(--color-paper-3))}
.acctm button[data-acct="out"]{color:var(--color-bad)}
.acctf button{all:unset;cursor:pointer;color:var(--color-cool)}.acctf button:hover{text-decoration:underline}
@media (prefers-reduced-motion:no-preference){.acctm:not([hidden]){animation:acctIn .25s cubic-bezier(.28,.11,.32,1)}@keyframes acctIn{from{opacity:0;transform:translateY(-6px) scale(.97)}to{opacity:1;transform:none}}}
}
@media print{.acct,.acctf{display:none!important}}
</style>''')
JS = r'''<script>
(function () {
  var d = document, SK = "su3dl-k2", SU = "su3dl-user", m = d.getElementById("acctm"), b = d.getElementById("acctb"); if (!m || !b) return;
  var name = ""; try { name = sessionStorage.getItem(SU) || localStorage.getItem(SU) || ""; } catch (e) {}
  ["acctname", "acctname2"].forEach(function (id) { var el = d.getElementById(id); if (el) el.textContent = name || "–"; });
  function show(on) { m.hidden = !on; b.setAttribute("aria-expanded", on ? "true" : "false"); }
  b.addEventListener("click", function (e) { e.stopPropagation(); show(m.hidden); });
  d.addEventListener("click", function (e) { if (!m.hidden && !m.contains(e.target)) show(false); });
  d.addEventListener("keydown", function (e) { if (e.key === "Escape" && !m.hidden) { show(false); b.focus(); } });
  d.addEventListener("click", function (e) {
    var t = e.target.closest && e.target.closest("[data-acct]"); if (!t) return;
    try {
      if (t.dataset.acct === "out") { [SK, SU].forEach(function (k) { sessionStorage.removeItem(k); localStorage.removeItem(k); }); }
      else sessionStorage.setItem("su3dl-konto", "1");
    } catch (err) {}
    location.hash = ""; location.reload();
  });
})();
</script>
'''
i = s.rfind("</body>")
s = s[:i] + JS + s[i:]
open(path, "w", encoding="utf-8").write(s)
print("Konto-Menü:", path)
