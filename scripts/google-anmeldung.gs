/**
 * Google-Anmeldung für das Handbuch 3D-Druck & Laser (Google Apps Script, läuft im Google-Konto des Verantwortlichen).
 *
 * Das Skript prüft ein Google-Konto und gibt dafür ein festes Geheimnis zurück, das nur zu diesem Konto gehört.
 * Mit dem Geheimnis öffnet die Anmeldeseite ein normales Benutzerkonto („g-…“). Ob jemand hineinkommt, entscheidet
 * allein die Freigabe in der index.html (scripts/benutzer.py freigeben / entfernen) – das Skript kennt weder den
 * Seitenschlüssel noch den Inhalt.
 *
 * Skripteigenschaften (Projekteinstellungen):
 *   GOOGLE_CLIENT_ID  OAuth-Client-ID (endet auf .apps.googleusercontent.com) – Pflicht
 *   ADMIN             E-Mail für Anfragen (leer = Besitzer des Skripts)
 *   DOMAIN            nur Konten dieser Domain zulassen, z. B. firma.de (leer = alle Google-Konten dürfen anfragen)
 *   MASTER            wird beim ersten Aufruf automatisch erzeugt – NICHT ändern oder löschen, sonst sind alle
 *                     Google-Konten ungültig und müssen neu freigegeben werden
 * Bereitstellen: Web-App, „Ausführen als: Ich“, „Zugriff: Jeder“.
 */
const P = PropertiesService.getScriptProperties();
const MAX_PRO_TAG = 30; // Schutz vor Spam: höchstens so viele Anfrage-Mails pro Tag

function doPost(e) {
  try {
    const d = JSON.parse(e.postData.contents), id = pruefe_(d.cred);
    if (!id) return json_({ ok: false, msg: "Die Google-Anmeldung konnte nicht bestätigt werden. Bitte noch einmal versuchen." });
    const dom = (P.getProperty("DOMAIN") || "").trim().toLowerCase();
    if (dom && id.email.split("@")[1].toLowerCase() !== dom) return json_({ ok: false, msg: "Für " + id.email + " ist kein Zugang vorgesehen (nur Konten von " + dom + ")." });
    const u = "g-" + hex_(hmac_("u|" + id.sub)).slice(0, 16), s = Utilities.base64EncodeWebSafe(hmac_("s|" + id.sub)).replace(/=+$/, "");
    if (d.t === "anfrage") return json_(anfrage_(id, u, String(d.code || "")));
    return json_({ ok: true, u: u, s: s, name: id.name, email: id.email });
  } catch (err) { return json_({ ok: false, msg: "Technischer Fehler bei der Anmeldung." }); }
}
function doGet() { return ContentService.createTextOutput("Google-Anmeldung Handbuch 3D-Druck & Laser: bereit."); }

// Google-Anmeldetoken prüfen: echt, für diese Seite ausgestellt, E-Mail bestätigt, nicht abgelaufen
function pruefe_(cred) {
  if (!cred || String(cred).length > 4000) return null;
  const r = UrlFetchApp.fetch("https://oauth2.googleapis.com/tokeninfo?id_token=" + encodeURIComponent(cred), { muteHttpExceptions: true });
  if (r.getResponseCode() !== 200) return null;
  const j = JSON.parse(r.getContentText()), cid = P.getProperty("GOOGLE_CLIENT_ID");
  if (!cid || j.aud !== cid || String(j.email_verified) !== "true" || !/^(https:\/\/)?accounts\.google\.com$/.test(j.iss) || Number(j.exp) * 1000 < Date.now() || !j.sub) return null;
  return { sub: String(j.sub), email: String(j.email), name: clean_(j.name || j.email, 60) };
}

// Erste Anmeldung: Konto-Code an den Verantwortlichen mailen (je Konto höchstens einmal am Tag)
function anfrage_(id, u, code) {
  const soll = id.name + " (" + id.email + ")";
  let j; try { const raw = code.slice(7).replace(/-/g, "+").replace(/_/g, "/"); j = JSON.parse(Utilities.newBlob(Utilities.base64Decode(raw + "===".slice((raw.length + 3) % 4))).getDataAsString("UTF-8")); } catch (e) { j = null; }
  if (code.indexOf("SU3DL1.") !== 0 || code.length > 1500 || !j || j.u !== u || j.n !== soll) return { ok: false, msg: "Die Anfrage war unvollständig – bitte noch einmal mit Google anmelden." };
  const lock = LockService.getScriptLock(); lock.waitLock(10000);
  try {
    const heute = Utilities.formatDate(new Date(), "Europe/Berlin", "yyyy-MM-dd"), kq = "q_" + u;
    if (P.getProperty(kq) === heute) return { ok: true, state: "wartet" };
    const kz = "z_" + heute, n = Number(P.getProperty(kz) || 0);
    if (n >= MAX_PRO_TAG) return { ok: false, msg: "Heute sind schon sehr viele Anfragen eingegangen – bitte morgen noch einmal versuchen oder den Verantwortlichen direkt ansprechen." };
    P.setProperty(kq, heute); P.setProperty(kz, String(n + 1));
    P.getKeys().forEach(function (k) { if ((k.indexOf("z_") === 0 && k !== kz) || (k.indexOf("q_") === 0 && P.getProperty(k) !== heute)) P.deleteProperty(k); });
  } finally { lock.releaseLock(); }
  MailApp.sendEmail({ to: admin_(), subject: "Handbuch 3D-Druck & Laser: Zugang für " + soll,
    body: soll + " möchte sich mit dem Google-Konto anmelden.\n\nFreigeben (im Ordner des Repos):\n\npython scripts/benutzer.py freigeben " + code + "\n\ndanach committen und pushen. Wieder entziehen: python scripts/benutzer.py entfernen " + u + "\n\nNicht freigeben? Dann einfach nichts tun." });
  return { ok: true, state: "neu" };
}

function master_() {
  let m = P.getProperty("MASTER");
  if (!m) { m = Utilities.base64Encode(Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, Utilities.getUuid() + Utilities.getUuid() + Utilities.getUuid() + Date.now())) + Utilities.getUuid(); P.setProperty("MASTER", m); }
  return m;
}
function hmac_(t) { return Utilities.computeHmacSha256Signature(t, master_()); }
function hex_(bytes) { return bytes.map(function (x) { return ((x + 256) % 256).toString(16).padStart(2, "0"); }).join(""); }
function admin_() { return P.getProperty("ADMIN") || Session.getEffectiveUser().getEmail(); }
function clean_(v, n) { return String(v || "").replace(/[\r\n\t]+/g, " ").trim().slice(0, n); }
function json_(o) { return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON); }

// Einmal von Hand ausführen: fragt die Berechtigungen ab, legt MASTER an und schickt eine Test-Mail
function testEinrichtung() {
  if (!P.getProperty("GOOGLE_CLIENT_ID")) throw new Error("Skripteigenschaft GOOGLE_CLIENT_ID fehlt.");
  master_(); UrlFetchApp.fetch("https://oauth2.googleapis.com/tokeninfo?id_token=x", { muteHttpExceptions: true });
  MailApp.sendEmail(admin_(), "Handbuch 3D-Druck & Laser: Google-Anmeldung eingerichtet", "Die Einrichtung funktioniert. Anfragen kommen an diese Adresse.");
}
