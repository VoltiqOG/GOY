"""Anmeldeseite: „Mit Google anmelden“ (Freigabe pro Google-Konto über das Apps Script).

Aufruf: python patch_gate_google.py index.html
Ändert nur die unverschlüsselte Anmeldeseite, nicht das Handbuch selbst.
Danach in index.html GCID (OAuth-Client-ID) und AUTH (Web-App-URL) eintragen –
solange beide leer sind, bleibt die Seite wie bisher (nur Passwort).
"""
import sys

path = sys.argv[1]
s = open(path, encoding="utf-8").read()
if "id=\"gbox\"" in s:
    sys.exit("Google-Anmeldung ist schon eingebaut.")


def rep(a, b):
    global s
    if a not in s:
        raise SystemExit("Stelle nicht gefunden: " + a[:90])
    s = s.replace(a, b, 1)


rep('''#rmsg{min-height:20px;''', '''#gbox{margin:0 0 18px}#gbtn{min-height:44px;display:flex;justify-content:center}#gmsg{min-height:20px;margin-top:10px;font-size:14px}#gmsg.ok{color:#1e7a3c}#gmsg.err{color:var(--err)}
.or{display:flex;align-items:center;gap:10px;margin:16px 0 14px;font-size:13px;color:var(--muted)}.or::before,.or::after{content:"";flex:1;height:1px;background:var(--line)}
@media (prefers-color-scheme:dark){#gmsg.ok{color:#6ee7a0}}
#rmsg{min-height:20px;''')

rep('''  <p>Diese Seite ist nur für den internen Gebrauch. Bitte Passwort eingeben.</p>''',
    '''  <p id="intro">Diese Seite ist nur für den internen Gebrauch. Bitte Passwort eingeben.</p>
  <div id="gbox" hidden>
    <div id="gbtn"></div>
    <div id="gmsg" role="status" aria-live="polite"></div>
    <div class="or">oder mit Passwort</div>
  </div>''')

rep('''  const SALT =''', '''  // ---------- Anmeldung mit Google: Das Apps Script prüft das Google-Konto und gibt nur freigegebenen Konten den Schlüssel
  const GCID = "", AUTH = "";
  async function googleLogin(r) {
    const gm = document.getElementById("gmsg"); gm.className = ""; gm.textContent = "Konto wird geprüft …";
    try {
      const res = await fetch(AUTH, { method: "POST", body: JSON.stringify({ t: "google", cred: r.credential }) }), j = await res.json();
      if (j.ok && j.pw) { gm.className = "ok"; gm.textContent = "Freigegeben – wird geöffnet …"; const raw = await derive(j.pw); store(raw, document.getElementById("keep").checked); await open(raw); return; }
      gm.className = j.state === "fehler" ? "err" : "ok";
      gm.textContent = j.state === "angefragt" ? `Hallo ${j.name || ""}, dein Konto ${j.email} ist noch nicht freigegeben. Die Anfrage ist an den Verantwortlichen gegangen – du bekommst eine E-Mail, sobald du dich anmelden kannst.`
        : j.state === "wartet" ? `Deine Anfrage für ${j.email} liegt noch beim Verantwortlichen. Du bekommst eine E-Mail, sobald sie freigegeben ist.`
        : j.state === "gesperrt" ? `Für ${j.email} ist kein Zugang vorgesehen. Bei Fragen den Verantwortlichen ansprechen.`
        : (j.msg || "Anmeldung nicht möglich.");
    } catch (err) { gm.className = "err"; gm.textContent = "Anmeldung über Google hat nicht geklappt – Internetverbindung prüfen oder das Passwort nutzen."; }
  }
  if (GCID && AUTH) {
    document.getElementById("gbox").hidden = false; document.getElementById("intro").textContent = "Diese Seite ist nur für den internen Gebrauch. Melde dich mit deinem Google-Konto an – beim ersten Mal wird dein Zugang beim Verantwortlichen angefragt.";
    const sc = document.createElement("script"); sc.src = "https://accounts.google.com/gsi/client"; sc.async = true;
    sc.onload = () => { google.accounts.id.initialize({ client_id: GCID, callback: googleLogin, ux_mode: "popup", auto_select: false });
      google.accounts.id.renderButton(document.getElementById("gbtn"), { theme: matchMedia("(prefers-color-scheme: dark)").matches ? "filled_black" : "outline", size: "large", text: "signin_with", shape: "rectangular", locale: "de", width: 300 }); };
    sc.onerror = () => { document.getElementById("gmsg").textContent = "Google-Anmeldung nicht erreichbar – bitte das Passwort nutzen."; };
    document.head.append(sc);
  }
  const SALT =''')

# googleLogin nutzt derive/open/store – die stehen weiter unten im selben Block; als Funktionsausdrücke (const) erst nach ihrer Definition aufrufbar.
# Der Knopf wird aber erst nach dem Laden des Google-Skripts klickbar, dann sind sie längst definiert.
open(path, "w", encoding="utf-8").write(s)
print("Google-Anmeldung eingebaut:", path)
