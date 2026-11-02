/**
 * Zugang zum Handbuch 3D-Druck & Laser (SU-3DL-001)
 *
 * Zwei Wege, beide mit Freigabe durch den Verantwortlichen:
 *   A) Mit Google anmelden: Beim ersten Mal geht automatisch eine Anfrage an dich.
 *      Nach „Freigeben“ öffnet sich die Seite für dieses Google-Konto bei jeder Anmeldung.
 *   B) Formular „Zugang anfragen“: Nach „Freigeben“ bekommt die Person das Passwort per E-Mail.
 * Freigegebene Konten verwaltest du über den Link „Zugänge verwalten“ in jeder Anfrage-Mail.
 *
 * Skripteigenschaften (Projekteinstellungen → Skripteigenschaften):
 *   PASSWORT          das Passwort der Seite (steht nur hier, nicht im Code)
 *   SEITE             Adresse der Seite, z. B. https://voltiqog.github.io/goy/
 *   GOOGLE_CLIENT_ID  OAuth-Client-ID (Typ Webanwendung) – nur für die Google-Anmeldung
 *   ADMIN             (optional) E-Mail für Anfragen; sonst dein Google-Konto
 *   DOMAIN            (optional) nur Konten dieser Domain zulassen, z. B. firma.de
 * Einrichtung: siehe README „Zugang einrichten“.
 */

const PROPS = PropertiesService.getScriptProperties();
const MAX_PRO_TAG = 20;          // Schutz vor Spam: höchstens so viele Anfragen pro Tag
const GUELTIG_TAGE = 14;         // offene Anfragen verfallen danach

// ---------- POST: Formular-Anfrage oder Google-Anmeldung
function doPost(e) {
  const body = e && e.postData && e.postData.contents;
  if (body && body.trim().charAt(0) === "{") {
    let j = {}; try { j = JSON.parse(body); } catch (x) {}
    if (j.t === "google") return json_(googleAnmelden_(String(j.cred || "")));
    return json_({ state: "fehler", msg: "Unbekannte Anfrage." });
  }
  const p = (e && e.parameter) || {};
  if (p.website) return text_("ok");                       // Honigtopf-Feld: Bots füllen es aus
  const name = clean_(p.name, 80), mail = clean_(p.email, 120).toLowerCase(), grund = clean_(p.reason, 500);
  if (!name || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(mail)) return text_("ok");
  neueAnfrage_({ name, mail, grund, via: "formular" });
  return text_("ok");
}

// Google-Anmeldung: ID-Token bei Google prüfen, dann Konto nachschlagen
function googleAnmelden_(cred) {
  const cid = PROPS.getProperty("GOOGLE_CLIENT_ID");
  if (!cid) return { state: "fehler", msg: "Google-Anmeldung ist noch nicht eingerichtet (GOOGLE_CLIENT_ID fehlt)." };
  if (!cred) return { state: "fehler", msg: "Kein Anmeldenachweis von Google." };
  const res = UrlFetchApp.fetch("https://oauth2.googleapis.com/tokeninfo?id_token=" + encodeURIComponent(cred), { muteHttpExceptions: true });
  if (res.getResponseCode() !== 200) return { state: "fehler", msg: "Google hat die Anmeldung nicht bestätigt. Bitte erneut versuchen." };
  const t = JSON.parse(res.getContentText());
  const okIss = t.iss === "accounts.google.com" || t.iss === "https://accounts.google.com";
  if (t.aud !== cid || !okIss || String(t.email_verified) !== "true" || Number(t.exp) * 1000 < Date.now())
    return { state: "fehler", msg: "Anmeldenachweis ungültig oder abgelaufen." };
  const mail = String(t.email || "").toLowerCase(), name = clean_(t.name || t.given_name || mail, 80);
  const dom = (PROPS.getProperty("DOMAIN") || "").toLowerCase().replace(/^@/, "");
  if (dom && mail.split("@")[1] !== dom) return { state: "gesperrt", email: mail };
  if (PROPS.getProperty("user_" + mail)) {
    const pw = PROPS.getProperty("PASSWORT");
    if (!pw) return { state: "fehler", msg: "Beim Verantwortlichen fehlt die Einstellung PASSWORT." };
    const u = JSON.parse(PROPS.getProperty("user_" + mail)); u.zuletzt = Date.now(); PROPS.setProperty("user_" + mail, JSON.stringify(u));
    return { ok: true, pw, name, email: mail };
  }
  if (PROPS.getProperty("nein_" + mail)) return { state: "gesperrt", email: mail };
  const pend = PROPS.getProperty("pend_" + mail);
  if (pend && anfrage_(pend)) return { state: "wartet", name, email: mail };
  return neueAnfrage_({ name, mail, grund: "", via: "google" }) ? { state: "angefragt", name, email: mail } : { state: "fehler", msg: "Gerade gehen zu viele Anfragen ein – bitte später erneut versuchen." };
}

function neueAnfrage_(r) {
  const lock = LockService.getScriptLock(); lock.waitLock(10000);
  let id;
  try {
    aufraeumen_();
    const tag = Utilities.formatDate(new Date(), "Europe/Berlin", "yyyy-MM-dd"), n = Number(PROPS.getProperty("tag_" + tag) || 0);
    if (n >= MAX_PRO_TAG) return false;
    PROPS.setProperty("tag_" + tag, String(n + 1));
    id = Utilities.getUuid(); r.t = Date.now();
    PROPS.setProperty("anf_" + id, JSON.stringify(r)); PROPS.setProperty("pend_" + r.mail, id);
  } finally { lock.releaseLock(); }
  const url = ScriptApp.getService().getUrl();
  MailApp.sendEmail({
    to: admin_(), replyTo: r.mail,
    subject: "Zugangsanfrage Handbuch 3D-Druck & Laser: " + r.name,
    htmlBody:
      "<p><b>" + esc_(r.name) + "</b> (" + esc_(r.mail) + ") möchte Zugang zum Handbuch 3D-Druck &amp; Laser" + (r.via === "google" ? " – angemeldet mit dem Google-Konto." : " – über das Formular.") + "</p>" +
      (r.grund ? "<p>Wofür: " + esc_(r.grund) + "</p>" : "") +
      '<p><a href="' + url + "?a=ja&id=" + id + '" style="display:inline-block;padding:10px 18px;background:#9a5a0b;color:#fff;border-radius:6px;text-decoration:none;font-weight:600">Freigeben</a> ' +
      '&nbsp; <a href="' + url + "?a=nein&id=" + id + '">Ablehnen</a></p>' +
      "<p style=\"color:#666;font-size:13px\">Nach dem Klick fragt die Seite noch einmal nach. " + (r.via === "google" ? "Danach kann sich das Konto mit Google anmelden" : "Danach geht das Passwort per E-Mail raus") + ". Die Anfrage verfällt nach " + GUELTIG_TAGE + " Tagen.<br>" +
      '<a href="' + url + "?a=liste&k=" + adminKey_() + '">Zugänge verwalten</a> (Link nicht weitergeben)</p>',
  });
  return true;
}

// ---------- GET: Bestätigungsseite für Freigeben/Ablehnen oder Verwaltung.
// Die eigentliche Aktion passiert erst per Knopfdruck, damit Virenscanner,
// die Links in E-Mails vorab öffnen, nichts versehentlich auslösen.
function doGet(e) {
  const p = (e && e.parameter) || {};
  if (p.a === "liste") {
    const t = HtmlService.createTemplate(LISTE_HTML); t.k = String(p.k || ""); t.ok = t.k === adminKey_(); t.L = t.ok ? liste_() : null;
    return t.evaluate().setTitle("Zugänge verwalten").addMetaTag("viewport", "width=device-width,initial-scale=1");
  }
  const a = p.a === "nein" ? "nein" : "ja", id = String(p.id || ""), t = HtmlService.createTemplate(SEITE_HTML);
  t.a = a; t.id = id; t.r = anfrage_(id);
  return t.evaluate().setTitle("Zugangsanfrage").addMetaTag("viewport", "width=device-width,initial-scale=1");
}

// Knopf auf der Bestätigungsseite
function entscheiden(id, a) {
  const r = anfrage_(id);
  if (!r) return "Diese Anfrage gibt es nicht mehr (schon erledigt oder verfallen).";
  const seite = PROPS.getProperty("SEITE") || "", pw = PROPS.getProperty("PASSWORT");
  if (a === "ja" && r.via !== "google" && !pw) return "Fehler: In den Skripteigenschaften fehlt PASSWORT.";
  PROPS.deleteProperty("anf_" + id); PROPS.deleteProperty("pend_" + r.mail);
  if (a !== "ja") { if (r.via === "google") PROPS.setProperty("nein_" + r.mail, JSON.stringify({ name: r.name, t: Date.now() })); return "Abgelehnt. " + r.name + " bekommt keine Nachricht."; }
  PROPS.setProperty("user_" + r.mail, JSON.stringify({ name: r.name, t: Date.now(), via: r.via }));
  MailApp.sendEmail({
    to: r.mail, replyTo: admin_(), subject: "Dein Zugang zum Handbuch 3D-Druck & Laser",
    htmlBody: "<p>Hallo " + esc_(r.name) + ",</p><p>deine Anfrage wurde freigegeben.</p>" +
      (seite ? '<p>Seite: <a href="' + esc_(seite) + '">' + esc_(seite) + "</a></p>" : "") +
      (r.via === "google" ? "<p>Melde dich dort mit <b>„Mit Google anmelden“</b> und dem Konto " + esc_(r.mail) + " an.</p>"
        : "<p>Passwort: <b style=\"font-family:monospace;font-size:16px\">" + esc_(pw) + "</b></p><p>Bitte das Passwort nicht weitergeben.</p>") +
      "<p>Die Seite ist nur für den internen Gebrauch.</p>",
  });
  return "Freigegeben. " + r.name + (r.via === "google" ? " kann sich jetzt mit Google anmelden (" + r.mail + ")." : " bekommt das Passwort an " + r.mail + ".");
}

// Verwaltung: Zugang entziehen, Sperre aufheben, Anfrage löschen
function verwalten(k, was, mail) {
  if (k !== adminKey_()) return "Kein Zugriff.";
  mail = String(mail || "").toLowerCase();
  if (was === "entziehen") { PROPS.deleteProperty("user_" + mail); PROPS.setProperty("nein_" + mail, JSON.stringify({ name: mail, t: Date.now() })); return mail + ": Zugang entzogen. Ab der nächsten Anmeldung gesperrt – bereits angemeldete Geräte bleiben offen, bis du das Passwort der Seite änderst."; }
  if (was === "entsperren") { PROPS.deleteProperty("nein_" + mail); return mail + ": Sperre aufgehoben – bei der nächsten Anmeldung kommt eine neue Anfrage."; }
  if (was === "freigeben") { PROPS.deleteProperty("nein_" + mail); PROPS.setProperty("user_" + mail, JSON.stringify({ name: mail, t: Date.now(), via: "google" })); return mail + ": freigegeben."; }
  return "Unbekannte Aktion.";
}

// ---------- Hilfsfunktionen
function liste_() {
  const all = PROPS.getProperties(), L = { user: [], nein: [], offen: [] };
  Object.keys(all).forEach((k) => {
    try {
      if (k.indexOf("user_") === 0) L.user.push(Object.assign({ mail: k.slice(5) }, JSON.parse(all[k])));
      else if (k.indexOf("nein_") === 0) L.nein.push(Object.assign({ mail: k.slice(5) }, JSON.parse(all[k])));
      else if (k.indexOf("anf_") === 0) L.offen.push(JSON.parse(all[k]));
    } catch (x) {}
  });
  const d = (t) => (t ? Utilities.formatDate(new Date(t), "Europe/Berlin", "dd.MM.yyyy") : "–");
  L.user.forEach((u) => { u.seit = d(u.t); u.letzt = d(u.zuletzt); }); L.nein.forEach((u) => { u.seit = d(u.t); }); L.offen.forEach((u) => { u.seit = d(u.t); });
  return L;
}
function adminKey_() { let k = PROPS.getProperty("ADMIN_KEY"); if (!k) { k = Utilities.getUuid().replace(/-/g, ""); PROPS.setProperty("ADMIN_KEY", k); } return k; }
function anfrage_(id) {
  if (!/^[0-9a-f-]{36}$/i.test(String(id))) return null;
  const s = PROPS.getProperty("anf_" + id);
  return s ? JSON.parse(s) : null;
}
function aufraeumen_() {
  const grenze = Date.now() - GUELTIG_TAGE * 864e5, heute = Utilities.formatDate(new Date(), "Europe/Berlin", "yyyy-MM-dd");
  const all = PROPS.getProperties();
  Object.keys(all).forEach((k) => {
    if (k.indexOf("anf_") === 0) { try { const r = JSON.parse(all[k]); if (r.t < grenze) { PROPS.deleteProperty(k); if (r.mail) PROPS.deleteProperty("pend_" + r.mail); } } catch (x) { PROPS.deleteProperty(k); } }
    else if (k.indexOf("tag_") === 0 && k !== "tag_" + heute) PROPS.deleteProperty(k);
  });
}
function admin_() { return PROPS.getProperty("ADMIN") || Session.getEffectiveUser().getEmail(); }
function clean_(v, n) { return String(v || "").replace(/[\r\n\t]+/g, " ").trim().slice(0, n); }
function esc_(s) { return String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])); }
function text_(s) { return ContentService.createTextOutput(s); }
function json_(o) { return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON); }

// Einmal im Editor ausführen: prüft die Einstellungen und schickt dir eine Test-Mail mit dem Verwaltungslink
function testEinrichtung() {
  const fehlt = ["PASSWORT", "SEITE"].filter((k) => !PROPS.getProperty(k));
  if (fehlt.length) throw new Error("In den Skripteigenschaften fehlt: " + fehlt.join(", "));
  UrlFetchApp.fetch("https://oauth2.googleapis.com/tokeninfo?id_token=x", { muteHttpExceptions: true }); // Berechtigung für Abrufe einholen
  const url = ScriptApp.getService().getUrl();
  MailApp.sendEmail({ to: admin_(), subject: "Test: Zugang Handbuch", htmlBody: "<p>Die Einrichtung funktioniert. Anfragen gehen an diese Adresse.</p>" +
    (PROPS.getProperty("GOOGLE_CLIENT_ID") ? "<p>Google-Anmeldung: eingerichtet.</p>" : "<p>Google-Anmeldung: GOOGLE_CLIENT_ID fehlt noch.</p>") +
    (url ? '<p><a href="' + url + "?a=liste&k=" + adminKey_() + '">Zugänge verwalten</a> (nach dem Bereitstellen)</p>' : "<p>Verwaltungslink kommt mit der ersten Anfrage (erst bereitstellen).</p>") });
  Logger.log("Test-Mail an " + admin_() + " gesendet.");
}

const CSS = `<style>body{margin:0;font:16px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif;background:#f6f4ef;color:#1c1b19;display:grid;place-items:center;min-height:100vh;padding:20px;box-sizing:border-box}
main{max-width:620px;width:100%;background:#fff;border:1px solid #dcd8cf;border-radius:10px;padding:24px}h1{font-size:22px;margin:0 0 8px;font-weight:600}h2{font-size:17px;margin:20px 0 8px;font-weight:600}p{margin:0 0 14px;color:#4a4842}
button{font:inherit;font-weight:600;padding:12px 18px;border-radius:6px;border:1px solid #9a5a0b;background:#9a5a0b;color:#fff;cursor:pointer;width:100%}button.nein,button.s{background:#fff;color:#1c1b19;border-color:#9b978f}
button.s{width:auto;padding:6px 12px;font-size:14px}button:disabled{opacity:.6;cursor:wait}#m{margin-top:14px;font-weight:600}
table{width:100%;border-collapse:collapse;font-size:14px}td,th{text-align:left;padding:8px 6px;border-top:1px solid #e6e2d9;vertical-align:middle}th{color:#6b6862;font-weight:500}</style>`;

const SEITE_HTML = `<!doctype html><html lang="de"><head><base target="_top">${CSS}</head><body><main>
<? if (!r) { ?><h1>Anfrage nicht gefunden</h1><p>Sie wurde schon bearbeitet oder ist verfallen.</p>
<? } else { ?><h1><?= a === "ja" ? "Zugang freigeben?" : "Anfrage ablehnen?" ?></h1>
<p><b><?= r.name ?></b><br><?= r.mail ?><br><?= r.via === "google" ? "Anmeldung mit Google" : "über das Formular" ?></p><? if (r.grund) { ?><p>Wofür: <?= r.grund ?></p><? } ?>
<p><?= a === "ja" ? (r.via === "google" ? "Das Konto kann sich danach mit Google anmelden." : "Die Person bekommt das Passwort per E-Mail.") : (r.via === "google" ? "Das Konto wird gesperrt (in der Verwaltung wieder aufhebbar)." : "Die Person bekommt keine Nachricht.") ?></p>
<button id="b" class="<?= a ?>"><?= a === "ja" ? "Ja, freigeben" : "Ja, ablehnen" ?></button><p id="m" role="status"></p>
<script>const b=document.getElementById("b"),m=document.getElementById("m");b.onclick=()=>{b.disabled=true;google.script.run.withSuccessHandler((t)=>{m.textContent=t;b.remove();}).withFailureHandler((e)=>{m.textContent="Fehler: "+e.message;b.disabled=false;}).entscheiden(<?!= JSON.stringify(id) ?>,<?!= JSON.stringify(a) ?>);};</script>
<? } ?></main></body></html>`;

const LISTE_HTML = `<!doctype html><html lang="de"><head><base target="_top">${CSS}</head><body><main>
<? if (!ok) { ?><h1>Kein Zugriff</h1><p>Den Verwaltungslink findest du in jeder Anfrage-Mail.</p><? } else { ?>
<h1>Zugänge verwalten</h1><p id="m" role="status"></p>
<h2>Freigegeben (<?= L.user.length ?>)</h2><table><tr><th>Konto</th><th>seit</th><th>zuletzt</th><th></th></tr>
<? L.user.forEach(function (u) { ?><tr><td><?= u.name ?><br><small><?= u.mail ?></small></td><td><?= u.seit ?></td><td><?= u.letzt ?></td><td><button class="s" data-w="entziehen" data-m="<?= u.mail ?>">Entziehen</button></td></tr><? }) ?></table>
<h2>Abgelehnt (<?= L.nein.length ?>)</h2><table><? L.nein.forEach(function (u) { ?><tr><td><?= u.name ?><br><small><?= u.mail ?></small></td><td><?= u.seit ?></td><td><button class="s" data-w="freigeben" data-m="<?= u.mail ?>">Doch freigeben</button> <button class="s" data-w="entsperren" data-m="<?= u.mail ?>">Sperre aufheben</button></td></tr><? }) ?></table>
<h2>Offene Anfragen (<?= L.offen.length ?>)</h2><table><? L.offen.forEach(function (u) { ?><tr><td><?= u.name ?><br><small><?= u.mail ?></small></td><td><?= u.seit ?></td><td>über den Link in der Anfrage-Mail</td></tr><? }) ?></table>
<script>const m=document.getElementById("m");document.querySelectorAll("button[data-w]").forEach((b)=>b.onclick=()=>{b.disabled=true;google.script.run.withSuccessHandler((t)=>{m.textContent=t;b.closest("tr").style.opacity=.4;}).withFailureHandler((e)=>{m.textContent="Fehler: "+e.message;b.disabled=false;}).verwalten(<?!= JSON.stringify(k) ?>,b.dataset.w,b.dataset.m);});</script>
<? } ?></main></body></html>`;
