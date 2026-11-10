"""Benutzerkonten der Anmeldeseite verwalten (läuft ohne Server, alles steckt verschlüsselt in der index.html).

Aufruf (im Ordner des Repos):
  python scripts/benutzer.py liste
  python scripts/benutzer.py freigeben SU3DL1.xxxxx            Konto-Code aus „Konto anlegen“ freischalten
  python scripts/benutzer.py freigeben SU3DL1.xxxxx --ersetzen  … auch wenn es den Benutzernamen schon gibt (neues Passwort)
  python scripts/benutzer.py anlegen m.mustermann "Max Mustermann"   Konto mit zufälligem Startpasswort anlegen
  python scripts/benutzer.py entfernen m.mustermann            Konto löschen UND Seitenschlüssel wechseln
  python scripts/benutzer.py schluessel                        nur den Seitenschlüssel wechseln (alle müssen sich neu anmelden)
  python scripts/benutzer.py einrichten leon "Leon"            einmalig: Umstellung vom gemeinsamen Passwort auf Konten

Anmelden zum Verwalten: eigenes Konto, abgefragt oder über die Umgebungsvariablen SEITEN_BENUTZER / SEITEN_PASSWORT.
Danach die geänderte index.html committen und pushen.

Verfahren
- Die Seite ist mit einem zufälligen Seitenschlüssel K verschlüsselt (AES-256-GCM über die gzip-komprimierte Seite).
- Jedes Konto hat ein Schlüsselpaar (ECDH P-256). Der private Schlüssel liegt mit dem Passwort verschlüsselt vor
  (PBKDF2-SHA256, 600 000 Runden → AES-256-GCM). K ist für jeden öffentlichen Schlüssel eingepackt
  (ECDH mit Einmal-Schlüssel → HKDF-SHA256 → AES-256-GCM).
- Passwörter stehen nirgends, auch nicht als Hash. Der Verantwortliche kennt sie nicht; beim Freigeben und beim
  Schlüsselwechsel braucht er nur die öffentlichen Schlüssel.
- Konto entfernen wechselt K: Das entfernte Konto und alle Geräte mit „angemeldet bleiben“ kommen nicht mehr an neue Stände.
Benötigt: pip install cryptography
"""
import base64, getpass, gzip, hashlib, json, os, re, secrets, sys
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

ITER = 600000
RE_USERS = re.compile(r"const USERS = (\{.*?\});\n")
RE_DATA = re.compile(r'const IV = "([^"]*)", DATA = "([^"]*)"')
RE_ALT = re.compile(r'const SALT = "([^"]*)", ITER = (\d+), IV = "([^"]*)", DATA = "([^"]*)"')
b = lambda x: base64.b64encode(x).decode()
d = base64.b64decode


def norm(u):
    return str(u or "").strip().lower()


def uid(u):
    return hashlib.sha256(("su3dl|" + norm(u)).encode()).digest()[:16].hex()


def kek(pw, salt):
    import unicodedata
    return hashlib.pbkdf2_hmac("sha256", unicodedata.normalize("NFC", pw).encode(), salt, ITER, 32)


def seal(key, data):
    iv = os.urandom(12)
    return iv + AESGCM(key).encrypt(iv, data, None)


def unseal(key, blob):
    return AESGCM(key).decrypt(blob[:12], blob[12:], None)


def wrap_key(K, pub_raw):
    """K für einen öffentlichen Schlüssel einpacken → (Einmal-Schlüssel, Paket)."""
    pub = ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256R1(), pub_raw)
    eph = ec.generate_private_key(ec.SECP256R1())
    wk = HKDF(hashes.SHA256(), 32, None, b"su3dl-k").derive(eph.exchange(ec.ECDH(), pub))
    e = eph.public_key().public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)
    return e, seal(wk, K)


def unlock(users, user, pw):
    e = users.get(uid(user))
    if not e:
        raise ValueError("Benutzername oder Passwort falsch.")
    try:
        priv = serialization.load_der_private_key(unseal(kek(pw, d(e["s"])), d(e["w"])), None)
        eph = ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256R1(), d(e["e"]))
        wk = HKDF(hashes.SHA256(), 32, None, b"su3dl-k").derive(priv.exchange(ec.ECDH(), eph))
        return unseal(wk, d(e["k"]))
    except Exception:
        raise ValueError("Benutzername oder Passwort falsch.")


class Seite:
    def __init__(self, pfad="index.html"):
        self.pfad = pfad
        self.html = open(pfad, encoding="utf-8").read()
        m = RE_USERS.search(self.html)
        if not m:
            sys.exit("Die Seite ist noch nicht auf Benutzerkonten umgestellt (erst „einrichten“).")
        self.users = json.loads(m[1])
        self.K = None

    def anmelden(self):
        user = os.environ.get("SEITEN_BENUTZER") or input("Dein Benutzername: ")
        pw = os.environ.get("SEITEN_PASSWORT") or getpass.getpass("Dein Passwort: ")
        try:
            self.K = unlock(self.users, user, pw)
        except ValueError as e:
            sys.exit(str(e) + " – nichts geändert.")
        return self

    def inhalt(self):
        m = RE_DATA.search(self.html)
        return gzip.decompress(AESGCM(self.K).decrypt(d(m[1]), d(m[2]), None))

    def setze_inhalt(self, src):
        iv = os.urandom(12)
        ct = AESGCM(self.K).encrypt(iv, gzip.compress(src, 9), None)
        self.html = RE_DATA.sub(lambda _: f'const IV = "{b(iv)}", DATA = "{b(ct)}"', self.html, count=1)

    def klar(self, e):
        try:
            return unseal(self.K, d(e["n"])).decode()
        except Exception:
            return "?\t?"

    def name(self, e):
        return self.klar(e).split("\t")[0]

    def user(self, e):
        return (self.klar(e).split("\t") + ["?"])[1]

    def konto(self, user, name, salt, w, pub, admin=False):
        e, k = wrap_key(self.K, pub)
        ent = {"s": b(salt), "w": b(w), "p": b(pub), "e": b(e), "k": b(k), "n": b(seal(self.K, (name.replace("\t", " ") + "\t" + norm(user)).encode()))}
        if admin:
            ent["a"] = 1
        self.users[uid(user)] = ent

    def schluessel_wechseln(self):
        src = self.inhalt()
        namen = {i: self.klar(e) for i, e in self.users.items()}
        self.K = os.urandom(32)
        for i, e in self.users.items():
            eph, k = wrap_key(self.K, d(e["p"]))
            e["e"], e["k"], e["n"] = b(eph), b(k), b(seal(self.K, namen[i].encode()))
        self.setze_inhalt(src)

    def speichern(self):
        self.html = RE_USERS.sub(lambda _: "const USERS = " + json.dumps(self.users, separators=(",", ":"), sort_keys=True) + ";\n", self.html, count=1)
        open(self.pfad, "w", encoding="utf-8").write(self.html)


def neues_konto(pw):
    """Schlüsselpaar wie im Browser: (salt, verschlüsselter privater Schlüssel, öffentlicher Schlüssel)."""
    priv = ec.generate_private_key(ec.SECP256R1())
    pk8 = priv.private_bytes(serialization.Encoding.DER, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
    pub = priv.public_key().public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)
    salt = os.urandom(16)
    return salt, seal(kek(pw, salt), pk8), pub


def lese_code(code):
    code = re.sub(r"\s+", "", code)
    if not code.startswith("SU3DL1."):
        sys.exit("Das ist kein Konto-Code (er beginnt mit SU3DL1.).")
    raw = code[7:].replace("-", "+").replace("_", "/")
    try:
        j = json.loads(d(raw + "=" * (-len(raw) % 4)))
        user, name, salt, w, pub = norm(j["u"]), str(j["n"]).strip()[:60], d(j["s"]), d(j["w"]), d(j["p"])
        ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256R1(), pub)
    except Exception:
        sys.exit("Der Konto-Code ist beschädigt oder unvollständig – bitte neu kopieren lassen.")
    if not re.fullmatch(r"[a-z0-9._-]{3,30}", user) or len(salt) != 16 or len(w) < 100:
        sys.exit("Der Konto-Code enthält ungültige Angaben.")
    return user, name, salt, w, pub


def main():
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    cmd, pfad = a[0], "index.html"
    if cmd == "einrichten":
        html = open(pfad, encoding="utf-8").read()
        m = RE_ALT.search(html)
        if not m:
            sys.exit("Keine Seite mit gemeinsamem Passwort gefunden (schon umgestellt?).")
        alt = os.environ.get("SEITEN_PASSWORT_ALT") or getpass.getpass("Bisheriges gemeinsames Passwort: ")
        try:
            src = gzip.decompress(AESGCM(hashlib.pbkdf2_hmac("sha256", alt.encode(), d(m[1]), int(m[2]), 32)).decrypt(d(m[3]), d(m[4]), None))
        except Exception:
            sys.exit("Passwort falsch – nichts geändert.")
        user, name = norm(a[1]), a[2]
        pw = os.environ.get("SEITEN_PASSWORT") or getpass.getpass(f"Neues Passwort für {user}: ")
        kopf = html[:html.index("<body>")]
        body = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "anmeldeseite_body.html"), encoding="utf-8").read()
        open(pfad, "w", encoding="utf-8").write(kopf + body)
        s = Seite(pfad); s.K = os.urandom(32)
        s.konto(user, name, *neues_konto(pw), admin=True); s.setze_inhalt(src); s.speichern()
        print(f"Umgestellt. Erstes Konto: {user} (Verwalter). Das gemeinsame Passwort gilt nicht mehr.")
        return
    s = Seite(pfad).anmelden()
    if cmd == "liste":
        for i, e in sorted(s.users.items(), key=lambda x: s.name(x[1]).lower()):
            print(f"  {s.user(e):<24} {s.name(e):<30} {'Verwalter' if e.get('a') else ''}")
        print(f"{len(s.users)} Konto/Konten. (Namen und Benutzernamen stehen nur verschlüsselt in der Datei.)")
        return
    if cmd == "freigeben":
        user, name, salt, w, pub = lese_code(a[1])
        alt = s.users.get(uid(user))
        if alt and "--ersetzen" not in a:
            sys.exit(f"Den Benutzernamen „{user}“ gibt es schon (Konto von {s.name(alt)}).\nWenn dieselbe Person ein neues Passwort setzen will: noch einmal mit --ersetzen. Vorher bei der Person nachfragen, ob der Code wirklich von ihr kommt!")
        s.konto(user, name, salt, w, pub, admin=bool(alt and alt.get("a")))
        s.speichern(); print(f"Freigegeben: {name} ({user}){' – altes Passwort ersetzt' if alt else ''}. Jetzt committen und pushen.")
    elif cmd == "anlegen":
        user, name = norm(a[1]), a[2]
        if not re.fullmatch(r"[a-z0-9._-]{3,30}", user):
            sys.exit("Benutzername: 3–30 Zeichen, nur a–z, 0–9, Punkt, Minus, Unterstrich.")
        if uid(user) in s.users:
            sys.exit("Den Benutzernamen gibt es schon.")
        pw = a[3] if len(a) > 3 else "-".join(secrets.choice(WOERTER) for _ in range(4)) + "-" + str(secrets.randbelow(90) + 10)
        s.konto(user, name, *neues_konto(pw), admin="--verwalter" in a)
        s.speichern(); print(f"Angelegt: {name}\n  Benutzername: {user}\n  Startpasswort: {pw}\nDas Passwort wird nur jetzt angezeigt. Die Person sollte es im Konto-Menü unter „Passwort ändern“ ersetzen.")
    elif cmd == "entfernen":
        i = uid(a[1])
        if i not in s.users:
            sys.exit("Dieses Konto gibt es nicht.")
        if len(s.users) == 1:
            sys.exit("Das letzte Konto kann nicht entfernt werden.")
        name = s.name(s.users.pop(i)); s.schluessel_wechseln(); s.speichern()
        print(f"Entfernt: {name}. Seitenschlüssel gewechselt – alle anderen melden sich einmal neu an (Passwörter bleiben).")
    elif cmd == "schluessel":
        s.schluessel_wechseln(); s.speichern(); print("Seitenschlüssel gewechselt – alle melden sich einmal neu an.")
    else:
        sys.exit(__doc__)


WOERTER = "apfel birke dachs eimer falke gabel hafen insel jacke kabel lampe mauer nagel ofen pinsel quelle regal sense tasse ufer vogel wolke zange anker bogen draht feder gitter hobel kante leiste mutter niete platte riemen schiene träger welle zahn".split()

if __name__ == "__main__":
    main()
