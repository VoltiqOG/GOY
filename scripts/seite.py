"""Inhalt der verschlüsselten Seite bearbeiten.

    python scripts/seite.py auspacken quelle.html     Inhalt entschlüsselt in eine Datei schreiben
    python scripts/seite.py einpacken quelle.html     bearbeitete Datei wieder verschlüsseln
    python scripts/seite.py anmeldeseite              Anmeldeseite aus scripts/anmeldeseite.html erneuern
    python scripts/seite.py google CLIENT_ID URL      „Mit Google anmelden“ einschalten (oder: google aus)

Ablauf für eine Änderung: auspacken → quelle.html bearbeiten → einpacken → committen und pushen.
quelle.html gehört nicht ins Repository (steht in .gitignore).
"""

import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from konten import Seite  # noqa: E402

VORLAGE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "anmeldeseite.html")
ZEILE_GOOGLE = re.compile(r'const GCID = "[^"]*", GAUTH = "[^"]*";')

# Diese Zeilen der index.html bleiben erhalten, wenn die Anmeldeseite erneuert wird.
DATENZEILEN = [
    r"const USERS = \{.*?\};\n",
    r'const IV = "[^"]*", DATA = "[^"]*"',
    r"const REQ = \{.*?\};\n",
    r'const NTFY = "[^"]*";',
    r'const GCID = "[^"]*", GAUTH = "[^"]*";',
]


def auspacken(args):
    seite = Seite(args.datei).anmelden()
    open(args.quelle, "wb").write(seite.inhalt())
    print("Entschlüsselt nach", args.quelle)


def einpacken(args):
    seite = Seite(args.datei).anmelden()
    seite.setze_inhalt(open(args.quelle, "rb").read())
    seite.speichern()
    print("Neu verschlüsselt:", args.datei)


def anmeldeseite(args):
    alt = open(args.datei, encoding="utf-8").read()
    neu = open(VORLAGE, encoding="utf-8").read()
    for muster in DATENZEILEN:
        treffer = re.search(muster, alt)
        if not treffer:
            sys.exit(f"In {args.datei} fehlt eine Datenzeile: {muster}")
        neu, anzahl = re.subn(muster, lambda _: treffer[0], neu, count=1)
        if anzahl != 1:
            sys.exit(f"In der Vorlage fehlt eine Datenzeile: {muster}")
    open(args.datei, "w", encoding="utf-8").write(neu)
    print("Anmeldeseite erneuert:", args.datei)


def google(args):
    html = open(args.datei, encoding="utf-8").read()
    if args.werte == ["aus"]:
        client_id, url = "", ""
    elif len(args.werte) == 2:
        client_id, url = args.werte
        if not client_id.endswith(".apps.googleusercontent.com"):
            sys.exit("Die Client-ID endet auf .apps.googleusercontent.com")
        if not re.fullmatch(r"https://script\.google\.com/macros/s/[\w-]+/exec", url):
            sys.exit("Die Web-App-URL hat die Form https://script.google.com/macros/s/…/exec")
    else:
        sys.exit("Erwartet: CLIENT_ID und WEB-APP-URL – oder „aus“.")
    zeile = f'const GCID = "{client_id}", GAUTH = "{url}";'
    html = ZEILE_GOOGLE.sub(lambda _: zeile, html, count=1)
    open(args.datei, "w", encoding="utf-8").write(html)
    print("Google-Anmeldung", "eingeschaltet." if client_id else "ausgeschaltet.")


def main():
    parser = argparse.ArgumentParser(description="Inhalt der verschlüsselten Seite bearbeiten")
    parser.add_argument("--datei", default="index.html")
    befehle = parser.add_subparsers(dest="befehl", required=True)

    p = befehle.add_parser("auspacken", help="Inhalt entschlüsseln")
    p.add_argument("quelle")
    p.set_defaults(tu=auspacken)
    p = befehle.add_parser("einpacken", help="Inhalt wieder verschlüsseln")
    p.add_argument("quelle")
    p.set_defaults(tu=einpacken)
    befehle.add_parser("anmeldeseite", help="Anmeldeseite aus der Vorlage erneuern").set_defaults(
        tu=anmeldeseite
    )
    p = befehle.add_parser("google", help="Google-Anmeldung ein- oder ausschalten")
    p.add_argument("werte", nargs="+")
    p.set_defaults(tu=google)

    args = parser.parse_args()
    args.tu(args)


if __name__ == "__main__":
    main()
