"""Anmeldeseite in der index.html durch die aktuelle Vorlage (scripts/anmeldeseite_body.html) ersetzen.
Kopf (CSS), Konten, verschlüsselter Inhalt und Einstellungen (Google, Anfragen) bleiben erhalten.

Aufruf: python scripts/gate_neu.py index.html
"""
import os, re, sys

p = sys.argv[1]
alt = open(p, encoding="utf-8").read()
neu = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "anmeldeseite_body.html"), encoding="utf-8").read()
KEEP = [r"const USERS = \{.*?\};\n", r'const IV = "[^"]*", DATA = "[^"]*"', r"const REQ = \{.*?\};\n", r'const NTFY = "[^"]*";', r'const GCID = "[^"]*", GAUTH = "[^"]*";']
for rx in KEEP:
    m = re.search(rx, alt)
    if m:
        if not re.search(rx, neu):
            raise SystemExit("Vorlage ohne " + rx)
        neu = re.sub(rx, lambda _: m[0], neu, count=1)
open(p, "w", encoding="utf-8").write(alt[:alt.index("<body>")] + neu)
print("Anmeldeseite erneuert:", p)
