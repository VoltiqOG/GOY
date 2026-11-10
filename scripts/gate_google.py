"""Anmeldeseite: „Mit Google anmelden“ ergänzen (zusätzlich zu Benutzername + Passwort).

Aufruf: python scripts/gate_google.py index.html                       Code einbauen (einmalig, bleibt aus bis zur Einrichtung)
        python scripts/gate_google.py index.html CLIENT_ID WEBAPP_URL  einschalten: OAuth-Client-ID und Apps-Script-URL eintragen
        python scripts/gate_google.py index.html aus                   wieder ausschalten

So funktioniert es: Das Apps Script (scripts/google-anmeldung.gs) prüft das Google-Konto und gibt dafür ein festes,
nur für dieses Konto geltendes Geheimnis zurück. Damit öffnet die Seite ein ganz normales Benutzerkonto („g-…“).
Freigeben, Entfernen und Schlüsselwechsel laufen wie bei allen Konten über scripts/benutzer.py.
"""
import re, sys

HTML = '''    <div id="gbox" hidden>
      <div id="gbtn"></div>
      <div id="gmsg" role="status" aria-live="polite"></div>
      <div class="or">oder mit Benutzername</div>
    </div>
'''
JS = r'''
  // ---------- Anmeldung mit Google: Das Apps Script prüft das Google-Konto und liefert das Geheimnis für dessen Konto
  const GCID = "", GAUTH = "";
  const post = async (o) => (await fetch(GAUTH, { method: "POST", body: JSON.stringify(o) })).json();
  async function googleLogin(r) {
    const gm = $("gmsg"); gm.className = ""; gm.textContent = "Konto wird geprüft …";
    try {
      const j = await post({ t: "id", cred: r.credential });
      if (!j.ok) { gm.className = "err"; gm.textContent = j.msg || "Anmeldung mit Google nicht möglich."; return; }
      if (USERS[await uid(j.u)]) { gm.className = "ok"; gm.textContent = "Freigegeben – wird geöffnet …"; const { K, name } = await unlock(j.u, j.s); store(K, name, $("keep").checked); await open(K); return; }
      const a = await post({ t: "anfrage", cred: r.credential, code: await makeCode(j.name + " (" + j.email + ")", j.u, j.s) });
      gm.className = a.ok ? "ok" : "err";
      gm.textContent = !a.ok ? (a.msg || "Die Anfrage konnte nicht gesendet werden.") : a.state === "wartet" ? `Deine Anfrage für ${j.email} liegt schon beim Verantwortlichen. Sobald er sie freigegeben hat, klappt die Anmeldung.`
        : `Hallo ${j.name}, dein Google-Konto ${j.email} ist noch nicht freigegeben. Die Anfrage ist an den Verantwortlichen gegangen – danach meldest du dich einfach wieder mit Google an.`;
    } catch (err) { gm.className = "err"; gm.textContent = "Anmeldung über Google hat nicht geklappt – Internetverbindung prüfen oder Benutzername und Passwort nutzen."; }
  }
  if (GCID && GAUTH) {
    $("gbox").hidden = false;
    const sc = document.createElement("script"); sc.src = "https://accounts.google.com/gsi/client"; sc.async = true;
    sc.onload = () => { google.accounts.id.initialize({ client_id: GCID, callback: googleLogin, ux_mode: "popup", auto_select: false });
      google.accounts.id.renderButton($("gbtn"), { theme: matchMedia("(prefers-color-scheme: dark)").matches ? "filled_black" : "outline", size: "large", text: "signin_with", shape: "pill", locale: "de", width: 300 }); };
    sc.onerror = () => { $("gmsg").textContent = "Google-Anmeldung nicht erreichbar – bitte Benutzername und Passwort nutzen."; };
    document.head.append(sc);
  }
'''
CSS = '''/* Google */
#gbox{margin:0 0 18px}#gbtn{min-height:44px;display:flex;justify-content:center}#gmsg{min-height:20px;margin-top:10px;font-size:14px;color:var(--muted);text-align:center}#gmsg.ok{color:#1d7f37}#gmsg.err{color:var(--err)}
.or{display:flex;align-items:center;gap:10px;margin:16px 0 4px;font-size:13px;color:var(--muted)}.or::before,.or::after{content:"";flex:1;height:1px;background:var(--line)}
@media (prefers-color-scheme:dark){#gmsg.ok{color:#30d158}}
'''
RE_CFG = re.compile(r'const GCID = "[^"]*", GAUTH = "[^"]*";')


def einbauen(s):
    if "const GCID" in s:
        return s
    def rep(a, b):
        nonlocal s
        if s.count(a) != 1:
            raise SystemExit("Stelle nicht eindeutig: " + a[:70])
        s = s.replace(a, b)
    rep('''    <form id="f" autocomplete="on">''', HTML + '''    <form id="f" autocomplete="on">''')
    # Konto-Code als eigene Funktion (auch für Google-Konten)
    rep('''      const kp = await crypto.subtle.generateKey({ name: "ECDH", namedCurve: "P-256" }, true, ["deriveBits"]);
      const pk8 = await crypto.subtle.exportKey("pkcs8", kp.privateKey), pub = await crypto.subtle.exportKey("raw", kp.publicKey);
      const salt = crypto.getRandomValues(new Uint8Array(16)), iv = crypto.getRandomValues(new Uint8Array(12));
      const ct = await crypto.subtle.encrypt({ name: "AES-GCM", iv }, await kek(p1, salt), pk8), w = new Uint8Array(12 + ct.byteLength); w.set(iv); w.set(new Uint8Array(ct), 12);
      const json = JSON.stringify({ v: 1, n: name, u: user, s: toB64(salt), w: toB64(w), p: toB64(pub) });
      $("code").value = "SU3DL1." + toB64(enc.encode(json)).replace(/\\+/g, "-").replace(/\\//g, "_").replace(/=+$/, "");''',
        '''      $("code").value = await makeCode(name, user, p1);''')
    rep('''  // Ansichten\n''', '''  // Konto-Code: Schlüsselpaar erzeugen, privater Teil mit dem Passwort verschlüsselt
  async function makeCode(name, user, pw) {
    const kp = await crypto.subtle.generateKey({ name: "ECDH", namedCurve: "P-256" }, true, ["deriveBits"]);
    const pk8 = await crypto.subtle.exportKey("pkcs8", kp.privateKey), pub = await crypto.subtle.exportKey("raw", kp.publicKey);
    const salt = crypto.getRandomValues(new Uint8Array(16)), iv = crypto.getRandomValues(new Uint8Array(12));
    const ct = await crypto.subtle.encrypt({ name: "AES-GCM", iv }, await kek(pw, salt), pk8), w = new Uint8Array(12 + ct.byteLength); w.set(iv); w.set(new Uint8Array(ct), 12);
    const json = JSON.stringify({ v: 1, n: name, u: user, s: toB64(salt), w: toB64(w), p: toB64(pub) });
    return "SU3DL1." + toB64(enc.encode(json)).replace(/\\+/g, "-").replace(/\\//g, "_").replace(/=+$/, "");
  }
''' + JS + '''
  // Ansichten\n''')
    if "/* Google */" not in s and "</style>" in s:
        i = s.find("</style>"); s = s[:i] + CSS + s[i:]
    return s


def main():
    p, rest = sys.argv[1], sys.argv[2:]
    s = einbauen(open(p, encoding="utf-8").read())
    if rest == ["aus"]:
        s = RE_CFG.sub('const GCID = "", GAUTH = "";', s, count=1); print("Google-Anmeldung ausgeschaltet.")
    elif len(rest) == 2:
        cid, url = rest
        if not cid.endswith(".apps.googleusercontent.com") or not re.fullmatch(r"https://script\.google\.com/macros/s/[\w-]+/exec", url):
            raise SystemExit("Erwartet: CLIENT_ID (endet auf .apps.googleusercontent.com) und die Web-App-URL (https://script.google.com/macros/s/…/exec).")
        s = RE_CFG.sub(lambda _: f'const GCID = "{cid}", GAUTH = "{url}";', s, count=1); print("Google-Anmeldung eingeschaltet.")
    else:
        print("Google-Anmeldung eingebaut (noch aus).")
    open(p, "w", encoding="utf-8").write(s)


if __name__ == "__main__":
    main()
