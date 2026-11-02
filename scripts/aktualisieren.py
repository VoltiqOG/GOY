"""Verschlüsselte index.html entschlüsseln, Patches einspielen, wieder verschlüsseln.

Aufruf:  python scripts/aktualisieren.py index.html scripts/patch_a.py [scripts/patch_b.py ...]
         python scripts/aktualisieren.py index.html --nur-entschluesseln quelle.html
Das Passwort wird abgefragt (nicht angezeigt, nirgends gespeichert). Es bleibt
dasselbe Passwort; Salt und IV werden neu erzeugt. Verfahren wie die Anmeldeseite:
PBKDF2-SHA256 (600 000 Runden) → AES-256-GCM über die gzip-komprimierte Seite.
Benötigt: pip install cryptography
"""
import base64, getpass, gzip, hashlib, os, re, subprocess, sys, tempfile
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

RE = re.compile(r'const SALT = "([^"]*)", ITER = (\d+), IV = "([^"]*)", DATA = "([^"]*)"')


def main():
    gate_path, rest = sys.argv[1], sys.argv[2:]
    gate = open(gate_path, encoding="utf-8").read()
    m = RE.search(gate)
    if not m:
        sys.exit("In der Datei steht keine verschlüsselte Seite.")
    salt, it, iv, data = base64.b64decode(m[1]), int(m[2]), base64.b64decode(m[3]), base64.b64decode(m[4])
    pw = os.environ.get("SEITEN_PASSWORT") or getpass.getpass("Passwort der Seite: ")
    key = hashlib.pbkdf2_hmac("sha256", pw.encode("utf-8"), salt, it, 32)
    try:
        src = gzip.decompress(AESGCM(key).decrypt(iv, data, None))
    except Exception:
        sys.exit("Passwort falsch – nichts geändert.")
    if rest[:1] == ["--nur-entschluesseln"]:
        open(rest[1], "wb").write(src); print("Entschlüsselt nach", rest[1]); return
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "quelle.html"); open(p, "wb").write(src)
        for patch in rest:
            subprocess.run([sys.executable, patch, p], check=True)
        src = open(p, "rb").read()
    salt2, iv2 = os.urandom(16), os.urandom(12)
    key2 = hashlib.pbkdf2_hmac("sha256", pw.encode("utf-8"), salt2, it, 32)
    ct = AESGCM(key2).encrypt(iv2, gzip.compress(src, 9), None)
    b = lambda x: base64.b64encode(x).decode()
    out = RE.sub(lambda _: f'const SALT = "{b(salt2)}", ITER = {it}, IV = "{b(iv2)}", DATA = "{b(ct)}"', gate, count=1)
    open(gate_path, "w", encoding="utf-8").write(out)
    print("Neu verschlüsselt:", gate_path)


if __name__ == "__main__":
    main()
