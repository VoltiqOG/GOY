"""Benutzerkonten der Seite verwalten.

Die Seite läuft ohne Server: Der Inhalt ist verschlüsselt, und jedes Konto trägt den
Seitenschlüssel einzeln eingepackt in der index.html. Passwörter stehen nirgends.

    python scripts/konten.py liste
    python scripts/konten.py freigeben SU3DL1.xxxx [--ersetzen]
    python scripts/konten.py anlegen m.mustermann "Max Mustermann"
    python scripts/konten.py rechte m.mustermann doku,qr
    python scripts/konten.py entfernen m.mustermann
    python scripts/konten.py schluessel

Anmelden mit dem eigenen Konto: Abfrage oder SEITEN_BENUTZER / SEITEN_PASSWORT.
Dasselbe geht in der Seite unter Konto-Menü → „Konten verwalten“.
Benötigt: pip install cryptography
"""

import argparse
import base64
import getpass
import gzip
import hashlib
import json
import os
import re
import secrets
import sys
import unicodedata

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

PBKDF2_RUNDEN = 600_000
KURVE = ec.SECP256R1()
RECHTE = ["doku", "rechner", "material", "pruefen", "qr", "sch", "vec", "vk", "pr"]
BENUTZERNAME = re.compile(r"[a-z0-9._-]{3,30}")

# Die Daten stehen als einzelne Zeilen in der index.html (siehe scripts/anmeldeseite.html).
ZEILE_KONTEN = re.compile(r"const USERS = (\{.*?\});\n")
ZEILE_INHALT = re.compile(r'const IV = "([^"]*)", DATA = "([^"]*)"')
ZEILE_ANFRAGEN = re.compile(r"const REQ = (\{.*?\});\n")
ZEILE_KANAL = re.compile(r'const NTFY = "([^"]*)";')

WOERTER = (
    "apfel birke dachs eimer falke gabel hafen insel jacke kabel lampe mauer nagel ofen pinsel "
    "quelle regal sense tasse ufer vogel wolke zange anker bogen draht feder gitter hobel kante "
    "leiste mutter niete platte riemen schiene welle zahn"
).split()


def b64(daten):
    return base64.b64encode(daten).decode()


def roh(text):
    return base64.b64decode(text)


# ---------------------------------------------------------------- Kryptografie


def konto_id(benutzername):
    """Benutzernamen stehen nicht im Klartext in der Datei, nur dieser Hash."""
    name = str(benutzername or "").strip().lower()
    return hashlib.sha256(("su3dl|" + name).encode()).digest()[:16].hex()


def passwort_schluessel(passwort, salt):
    passwort = unicodedata.normalize("NFC", passwort).encode()
    return hashlib.pbkdf2_hmac("sha256", passwort, salt, PBKDF2_RUNDEN, 32)


def versiegeln(schluessel, daten):
    iv = os.urandom(12)
    return iv + AESGCM(schluessel).encrypt(iv, daten, None)


def oeffnen(schluessel, paket):
    return AESGCM(schluessel).decrypt(paket[:12], paket[12:], None)


def oeffentlich(punkt):
    return ec.EllipticCurvePublicKey.from_encoded_point(KURVE, punkt)


def punkt(schluessel):
    return schluessel.public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)


def als_pkcs8(privat):
    return privat.private_bytes(
        serialization.Encoding.DER,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )


def gemeinsamer_schluessel(privat, gegen):
    geheimnis = privat.exchange(ec.ECDH(), gegen)
    return HKDF(hashes.SHA256(), 32, None, b"su3dl-k").derive(geheimnis)


def einpacken(seitenschluessel, empfaenger_punkt):
    """Seitenschlüssel für einen öffentlichen Schlüssel einpacken."""
    einmal = ec.generate_private_key(KURVE)
    schluessel = gemeinsamer_schluessel(einmal, oeffentlich(empfaenger_punkt))
    return punkt(einmal.public_key()), versiegeln(schluessel, seitenschluessel)


def schluesselpaar(passwort):
    """Neues Konto: (Salt, privater Schlüssel mit dem Passwort versiegelt, öffentlicher Schlüssel)."""
    privat = ec.generate_private_key(KURVE)
    salt = os.urandom(16)
    versiegelt = versiegeln(passwort_schluessel(passwort, salt), als_pkcs8(privat))
    return salt, versiegelt, punkt(privat.public_key())


# ---------------------------------------------------------------------- Seite


class Seite:
    def __init__(self, pfad="index.html"):
        self.pfad = pfad
        self.html = open(pfad, encoding="utf-8").read()
        treffer = ZEILE_KONTEN.search(self.html)
        if not treffer:
            sys.exit(f"{pfad} enthält keine Kontenliste.")
        self.konten = json.loads(treffer[1])
        treffer = ZEILE_ANFRAGEN.search(self.html)
        self.anfragen = json.loads(treffer[1]) if treffer else {}
        treffer = ZEILE_KANAL.search(self.html)
        self.kanal = treffer[1] if treffer else ""
        self.schluessel = None

    # --- anmelden

    def anmelden(self):
        benutzer = os.environ.get("SEITEN_BENUTZER") or input("Dein Benutzername: ")
        passwort = os.environ.get("SEITEN_PASSWORT") or getpass.getpass("Dein Passwort: ")
        konto = self.konten.get(konto_id(benutzer))
        try:
            privat = serialization.load_der_private_key(
                oeffnen(passwort_schluessel(passwort, roh(konto["s"])), roh(konto["w"])), None
            )
            schluessel = gemeinsamer_schluessel(privat, oeffentlich(roh(konto["e"])))
            self.schluessel = oeffnen(schluessel, roh(konto["k"]))
        except Exception:
            sys.exit("Benutzername oder Passwort falsch – nichts geändert.")
        return self

    # --- Inhalt

    def inhalt(self):
        iv, daten = ZEILE_INHALT.search(self.html).groups()
        return gzip.decompress(AESGCM(self.schluessel).decrypt(roh(iv), roh(daten), None))

    def setze_inhalt(self, quelltext):
        iv = os.urandom(12)
        daten = AESGCM(self.schluessel).encrypt(iv, gzip.compress(quelltext, 9), None)
        zeile = f'const IV = "{b64(iv)}", DATA = "{b64(daten)}"'
        self.html = ZEILE_INHALT.sub(lambda _: zeile, self.html, count=1)

    # --- Konten

    def angaben(self, konto):
        """(Name, Benutzername, Rechte) – in der Datei mit dem Seitenschlüssel versiegelt."""
        try:
            teile = oeffnen(self.schluessel, roh(konto["n"])).decode().split("\t")
        except Exception:
            return "?", "?", ["*"]
        teile += ["?", "*"][len(teile) - 1 :]
        rechte = [r for r in teile[2].split(",") if r] or ["*"]
        if konto.get("a") and "admin" not in rechte:
            rechte.append("admin")
        return teile[0], teile[1], rechte

    def setze_angaben(self, konto, name, benutzer, rechte):
        rechte = list(dict.fromkeys(rechte))
        klartext = "\t".join([name.replace("\t", " "), benutzer, ",".join(rechte)])
        konto["n"] = b64(versiegeln(self.schluessel, klartext.encode()))
        if "admin" in rechte:
            konto["a"] = 1
        else:
            konto.pop("a", None)

    def neues_konto(self, benutzer, name, salt, privat_versiegelt, pub, rechte=("*",)):
        einmal, paket = einpacken(self.schluessel, pub)
        konto = {
            "s": b64(salt),
            "w": b64(privat_versiegelt),
            "p": b64(pub),
            "e": b64(einmal),
            "k": b64(paket),
        }
        self.setze_angaben(konto, name, benutzer, list(rechte))
        self.konten[konto_id(benutzer)] = konto

    def schluessel_wechseln(self):
        """Neuer Seitenschlüssel: Inhalt neu verschlüsseln und für alle Konten neu einpacken."""
        quelltext = self.inhalt()
        angaben = {i: self.angaben(k) for i, k in self.konten.items()}
        anfrage_privat = None
        if self.anfragen.get("w"):
            anfrage_privat = oeffnen(self.schluessel, roh(self.anfragen["w"]))

        self.schluessel = os.urandom(32)
        for i, konto in self.konten.items():
            einmal, paket = einpacken(self.schluessel, roh(konto["p"]))
            konto["e"], konto["k"] = b64(einmal), b64(paket)
            self.setze_angaben(konto, *angaben[i])
        if anfrage_privat:
            self.anfragen["w"] = b64(versiegeln(self.schluessel, anfrage_privat))
        self.setze_inhalt(quelltext)

    def anfragen_einrichten(self):
        """Schlüssel und Kanal, über die neue Anfragen die Verwalter erreichen."""
        if not self.anfragen.get("p"):
            privat = ec.generate_private_key(KURVE)
            self.anfragen = {
                "p": b64(punkt(privat.public_key())),
                "w": b64(versiegeln(self.schluessel, als_pkcs8(privat))),
            }
        if not self.kanal:
            self.kanal = "https://ntfy.sh/su3dl-" + secrets.token_hex(16)

    def speichern(self):
        def zeile(name, wert):
            return f"const {name} = " + json.dumps(wert, separators=(",", ":"), sort_keys=True) + ";\n"

        self.html = ZEILE_KONTEN.sub(lambda _: zeile("USERS", self.konten), self.html, count=1)
        self.html = ZEILE_ANFRAGEN.sub(lambda _: zeile("REQ", self.anfragen), self.html, count=1)
        self.html = ZEILE_KANAL.sub(lambda _: f'const NTFY = "{self.kanal}";', self.html, count=1)
        open(self.pfad, "w", encoding="utf-8").write(self.html)


# ---------------------------------------------------------------- Konto-Code


def lese_code(code):
    """Konto-Code aus „Konto anlegen“ → (Benutzername, Name, Salt, privater Schlüssel, öffentlicher Schlüssel)."""
    code = re.sub(r"\s+", "", code)
    if not code.startswith("SU3DL1."):
        sys.exit("Das ist kein Konto-Code (er beginnt mit SU3DL1.).")
    daten = code[7:].replace("-", "+").replace("_", "/")
    try:
        j = json.loads(roh(daten + "=" * (-len(daten) % 4)))
        benutzer = str(j["u"]).strip().lower()
        name = str(j["n"]).strip()[:80]
        salt, privat, pub = roh(j["s"]), roh(j["w"]), roh(j["p"])
        oeffentlich(pub)
    except Exception:
        sys.exit("Der Konto-Code ist beschädigt oder unvollständig – bitte neu kopieren lassen.")
    if not BENUTZERNAME.fullmatch(benutzer) or len(salt) != 16 or len(privat) < 100:
        sys.exit("Der Konto-Code enthält ungültige Angaben.")
    return benutzer, name, salt, privat, pub


def pruefe_rechte(text):
    rechte = [r for r in text.split(",") if r]
    unbekannt = [r for r in rechte if r not in RECHTE + ["*", "admin"]]
    if unbekannt or not rechte:
        sys.exit("Erlaubt: * (alles) oder eine Liste aus " + ", ".join(RECHTE) + "; dazu admin.")
    return rechte


# -------------------------------------------------------------------- Befehle


def liste(seite, _):
    zeilen = sorted((seite.angaben(k) for k in seite.konten.values()), key=lambda a: a[0].lower())
    for name, benutzer, rechte in zeilen:
        print(f"  {benutzer:<24} {name:<34} {','.join(rechte)}")
    print(f"{len(zeilen)} Konten")


def freigeben(seite, args):
    benutzer, name, salt, privat, pub = lese_code(args.code)
    altes = seite.konten.get(konto_id(benutzer))
    if altes and not args.ersetzen:
        sys.exit(
            f"Den Benutzernamen „{benutzer}“ gibt es schon (Konto von {seite.angaben(altes)[0]}).\n"
            "Neues Passwort für dieselbe Person: noch einmal mit --ersetzen.\n"
            "Vorher nachfragen, ob der Code wirklich von ihr kommt."
        )
    rechte = seite.angaben(altes)[2] if altes else ["*"]
    seite.neues_konto(benutzer, name, salt, privat, pub, rechte)
    seite.speichern()
    print(f"Freigegeben: {name} ({benutzer})" + (" – Passwort ersetzt" if altes else ""))


def anlegen(seite, args):
    benutzer = args.benutzer.strip().lower()
    if not BENUTZERNAME.fullmatch(benutzer):
        sys.exit("Benutzername: 3–30 Zeichen, nur a–z, 0–9, Punkt, Minus, Unterstrich.")
    if konto_id(benutzer) in seite.konten:
        sys.exit("Den Benutzernamen gibt es schon.")
    passwort = "-".join(secrets.choice(WOERTER) for _ in range(4)) + f"-{secrets.randbelow(90) + 10}"
    seite.neues_konto(benutzer, args.name, *schluesselpaar(passwort))
    seite.speichern()
    print(f"Angelegt: {args.name}\n  Benutzername:  {benutzer}\n  Startpasswort: {passwort}")
    print("Das Passwort wird nur jetzt angezeigt.")


def rechte(seite, args):
    konto = seite.konten.get(konto_id(args.benutzer))
    if not konto:
        sys.exit("Dieses Konto gibt es nicht.")
    name, benutzer, _ = seite.angaben(konto)
    seite.setze_angaben(konto, name, benutzer, pruefe_rechte(args.rechte))
    seite.speichern()
    print(f"Rechte von {name}: {','.join(seite.angaben(konto)[2])}")


def entfernen(seite, args):
    i = konto_id(args.benutzer)
    if i not in seite.konten:
        sys.exit("Dieses Konto gibt es nicht.")
    if len(seite.konten) == 1:
        sys.exit("Das letzte Konto kann nicht entfernt werden.")
    name = seite.angaben(seite.konten.pop(i))[0]
    seite.schluessel_wechseln()
    seite.speichern()
    print(f"Entfernt: {name}. Der Seitenschlüssel ist gewechselt – alle melden sich einmal neu an.")


def schluessel(seite, _):
    seite.schluessel_wechseln()
    seite.speichern()
    print("Seitenschlüssel gewechselt – alle melden sich einmal neu an.")


def anfragen(seite, _):
    seite.anfragen_einrichten()
    seite.speichern()
    print("Anfragen eingerichtet. Kanal:", seite.kanal)


def main():
    parser = argparse.ArgumentParser(description="Benutzerkonten der Seite verwalten")
    parser.add_argument("--datei", default="index.html")
    befehle = parser.add_subparsers(dest="befehl", required=True)

    befehle.add_parser("liste", help="alle Konten").set_defaults(tu=liste)
    p = befehle.add_parser("freigeben", help="Konto-Code freischalten")
    p.add_argument("code")
    p.add_argument("--ersetzen", action="store_true", help="vorhandenes Konto: neues Passwort")
    p.set_defaults(tu=freigeben)
    p = befehle.add_parser("anlegen", help="Konto mit Startpasswort anlegen")
    p.add_argument("benutzer")
    p.add_argument("name")
    p.set_defaults(tu=anlegen)
    p = befehle.add_parser("rechte", help="Rechte setzen, z. B. doku,qr oder *,admin")
    p.add_argument("benutzer")
    p.add_argument("rechte")
    p.set_defaults(tu=rechte)
    p = befehle.add_parser("entfernen", help="Konto löschen und Seitenschlüssel wechseln")
    p.add_argument("benutzer")
    p.set_defaults(tu=entfernen)
    befehle.add_parser("schluessel", help="nur den Seitenschlüssel wechseln").set_defaults(tu=schluessel)
    befehle.add_parser("anfragen", help="Anfragen/Benachrichtigung einrichten").set_defaults(tu=anfragen)

    args = parser.parse_args()
    args.tu(Seite(args.datei).anmelden(), args)


if __name__ == "__main__":
    main()
