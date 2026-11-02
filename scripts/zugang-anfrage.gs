/**
 * Zugangsanfragen für das Handbuch 3D-Druck & Laser (SU-3DL-001)
 *
 * Ablauf:
 *   1. Jemand füllt auf der Anmeldeseite „Zugang anfragen“ aus.
 *   2. Du bekommst eine E-Mail mit „Freigeben“ und „Ablehnen“.
 *   3. Bei „Freigeben“ bekommt die Person das Passwort per E-Mail.
 *
 * Einrichtung (einmalig, ca. 10 Minuten), siehe README „Zugangsanfragen einrichten“.
 * Skripteigenschaften (Projekteinstellungen → Skripteigenschaften):
 *   PASSWORT   das Passwort der Seite (steht nur hier, nicht im Code)
 *   SEITE      Adresse der Seite, z. B. https://voltiqog.github.io/goy/
 *   ADMIN      (optional) E-Mail, an die Anfragen gehen; sonst dein Google-Konto
 */

const PROPS = PropertiesService.getScriptProperties();
const MAX_PRO_TAG = 20;          // Schutz vor Spam: höchstens so viele Anfragen pro Tag
const GUELTIG_TAGE = 14;         // offene Anfragen verfallen danach

// ---------- Anfrage von der Anmeldeseite (Formular, POST)
function doPost(e) {
  const p = (e && e.parameter) || {};
  if (p.website) return text_("ok");                       // Honigtopf-Feld: Bots füllen es aus
  const name = clean_(p.name, 80), mail = clean_(p.email, 120), grund = clean_(p.reason, 500);
  if (!name || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(mail)) return text_("ok");

  const lock = LockService.getScriptLock();
  lock.waitLock(10000);
  let id;
  try {
    aufraeumen_();
    const tag = Utilities.formatDate(new Date(), "Europe/Berlin", "yyyy-MM-dd");
    const n = Number(PROPS.getProperty("tag_" + tag) || 0);
    if (n >= MAX_PRO_TAG) return text_("ok");
    PROPS.setProperty("tag_" + tag, String(n + 1));
    id = Utilities.getUuid();
    PROPS.setProperty("anf_" + id, JSON.stringify({ name, mail, grund, t: Date.now() }));
  } finally {
    lock.releaseLock();
  }

  const url = ScriptApp.getService().getUrl();
  MailApp.sendEmail({
    to: admin_(),
    replyTo: mail,
    subject: "Zugangsanfrage Handbuch 3D-Druck & Laser: " + name,
    htmlBody:
      "<p><b>" + esc_(name) + "</b> (" + esc_(mail) + ") möchte Zugang zum Handbuch 3D-Druck &amp; Laser.</p>" +
      (grund ? "<p>Wofür: " + esc_(grund) + "</p>" : "") +
      '<p><a href="' + url + "?a=ja&id=" + id + '" style="display:inline-block;padding:10px 18px;background:#9a5a0b;color:#fff;border-radius:6px;text-decoration:none;font-weight:600">Freigeben</a> ' +
      '&nbsp; <a href="' + url + "?a=nein&id=" + id + '">Ablehnen</a></p>' +
      "<p style=\"color:#666;font-size:13px\">Nach dem Klick fragt die Seite noch einmal nach. Erst dann geht das Passwort raus. Die Anfrage verfällt nach " + GUELTIG_TAGE + " Tagen.</p>",
  });
  return text_("ok");
}

// ---------- Link aus deiner E-Mail (GET): zeigt eine Bestätigungsseite.
// Die eigentliche Freigabe passiert erst per Knopfdruck, damit Virenscanner,
// die Links in E-Mails vorab öffnen, nichts versehentlich freigeben.
function doGet(e) {
  const p = (e && e.parameter) || {}, a = p.a === "nein" ? "nein" : "ja", id = String(p.id || "");
  const r = anfrage_(id);
  const t = HtmlService.createTemplate(SEITE_HTML);
  t.a = a; t.id = id; t.r = r;
  return t.evaluate().setTitle("Zugangsanfrage").addMetaTag("viewport", "width=device-width,initial-scale=1");
}

// Wird vom Knopf auf der Bestätigungsseite aufgerufen
function entscheiden(id, a) {
  const r = anfrage_(id);
  if (!r) return "Diese Anfrage gibt es nicht mehr (schon erledigt oder verfallen).";
  PROPS.deleteProperty("anf_" + id);
  if (a === "ja") {
    const pw = PROPS.getProperty("PASSWORT"), seite = PROPS.getProperty("SEITE") || "";
    if (!pw) { PROPS.setProperty("anf_" + id, JSON.stringify(r)); return "Fehler: In den Skripteigenschaften fehlt PASSWORT."; }
    MailApp.sendEmail({
      to: r.mail,
      replyTo: admin_(),
      subject: "Dein Zugang zum Handbuch 3D-Druck & Laser",
      htmlBody:
        "<p>Hallo " + esc_(r.name) + ",</p>" +
        "<p>deine Anfrage wurde freigegeben.</p>" +
        (seite ? '<p>Seite: <a href="' + esc_(seite) + '">' + esc_(seite) + "</a></p>" : "") +
        "<p>Passwort: <b style=\"font-family:monospace;font-size:16px\">" + esc_(pw) + "</b></p>" +
        "<p>Bitte das Passwort nicht weitergeben. Die Seite ist nur für den internen Gebrauch.</p>",
    });
    return "Freigegeben. " + r.name + " bekommt das Passwort an " + r.mail + ".";
  }
  return "Abgelehnt. " + r.name + " bekommt keine Nachricht.";
}

// ---------- Hilfsfunktionen
function anfrage_(id) {
  if (!/^[0-9a-f-]{36}$/i.test(id)) return null;
  const s = PROPS.getProperty("anf_" + id);
  return s ? JSON.parse(s) : null;
}
function aufraeumen_() {
  const grenze = Date.now() - GUELTIG_TAGE * 864e5, heute = Utilities.formatDate(new Date(), "Europe/Berlin", "yyyy-MM-dd");
  const all = PROPS.getProperties();
  Object.keys(all).forEach((k) => {
    if (k.indexOf("anf_") === 0) { try { if (JSON.parse(all[k]).t < grenze) PROPS.deleteProperty(k); } catch (x) { PROPS.deleteProperty(k); } }
    else if (k.indexOf("tag_") === 0 && k !== "tag_" + heute) PROPS.deleteProperty(k);
  });
}
function admin_() { return PROPS.getProperty("ADMIN") || Session.getEffectiveUser().getEmail(); }
function clean_(v, n) { return String(v || "").replace(/[\r\n\t]+/g, " ").trim().slice(0, n); }
function esc_(s) { return String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])); }
function text_(s) { return ContentService.createTextOutput(s); }

// Einmal im Editor ausführen: prüft die Einstellungen und schickt dir eine Test-Mail
function testEinrichtung() {
  const fehlt = ["PASSWORT", "SEITE"].filter((k) => !PROPS.getProperty(k));
  if (fehlt.length) throw new Error("In den Skripteigenschaften fehlt: " + fehlt.join(", "));
  MailApp.sendEmail(admin_(), "Test: Zugangsanfragen Handbuch", "Die Einrichtung funktioniert. Anfragen gehen an diese Adresse.");
  Logger.log("Test-Mail an " + admin_() + " gesendet. Verbleibende Mails heute: " + MailApp.getRemainingDailyQuota());
}

const SEITE_HTML = `<!doctype html><html lang="de"><head><base target="_top">
<style>body{margin:0;font:16px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif;background:#f6f4ef;color:#1c1b19;display:grid;place-items:center;min-height:100vh;padding:20px;box-sizing:border-box}
main{max-width:420px;width:100%;background:#fff;border:1px solid #dcd8cf;border-radius:10px;padding:24px}
h1{font-size:22px;margin:0 0 8px;font-weight:600}p{margin:0 0 14px;color:#4a4842}
button{font:inherit;font-weight:600;padding:12px 18px;border-radius:6px;border:1px solid #9a5a0b;background:#9a5a0b;color:#fff;cursor:pointer;width:100%}
button.nein{background:#fff;color:#1c1b19;border-color:#9b978f}button:disabled{opacity:.6;cursor:wait}#m{margin-top:14px;font-weight:600}</style></head><body><main>
<? if (!r) { ?><h1>Anfrage nicht gefunden</h1><p>Sie wurde schon bearbeitet oder ist verfallen.</p>
<? } else { ?><h1><?= a === "ja" ? "Zugang freigeben?" : "Anfrage ablehnen?" ?></h1>
<p><b><?= r.name ?></b><br><?= r.mail ?></p><? if (r.grund) { ?><p>Wofür: <?= r.grund ?></p><? } ?>
<p><?= a === "ja" ? "Die Person bekommt das Passwort per E-Mail." : "Die Person bekommt keine Nachricht." ?></p>
<button id="b" class="<?= a ?>"><?= a === "ja" ? "Ja, Passwort senden" : "Ja, ablehnen" ?></button><p id="m" role="status"></p>
<script>const b=document.getElementById("b"),m=document.getElementById("m");b.onclick=()=>{b.disabled=true;google.script.run.withSuccessHandler((t)=>{m.textContent=t;b.remove();}).withFailureHandler((e)=>{m.textContent="Fehler: "+e.message;b.disabled=false;}).entscheiden(<?!= JSON.stringify(id) ?>,<?!= JSON.stringify(a) ?>);};</script>
<? } ?></main></body></html>`;
