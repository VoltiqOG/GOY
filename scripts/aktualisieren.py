"""Verschlüsselte index.html entschlüsseln, Patches einspielen, wieder verschlüsseln.

Aufruf:  python scripts/aktualisieren.py index.html scripts/patch_a.py [scripts/patch_b.py ...]
         python scripts/aktualisieren.py index.html --nur-entschluesseln quelle.html
Anmelden mit dem eigenen Konto (abgefragt oder SEITEN_BENUTZER / SEITEN_PASSWORT). Der Seitenschlüssel und
alle Konten bleiben unverändert, nur der Inhalt wird mit neuem IV neu verschlüsselt (siehe scripts/benutzer.py).
Benötigt: pip install cryptography
"""
import os, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from benutzer import Seite


def main():
    gate_path, rest = sys.argv[1], sys.argv[2:]
    s = Seite(gate_path).anmelden()
    src = s.inhalt()
    if rest[:1] == ["--nur-entschluesseln"]:
        open(rest[1], "wb").write(src); print("Entschlüsselt nach", rest[1]); return
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "quelle.html"); open(p, "wb").write(src)
        for patch in rest:
            subprocess.run([sys.executable, patch, p], check=True)
        src = open(p, "rb").read()
    s.setze_inhalt(src); s.speichern()
    print("Neu verschlüsselt:", gate_path)


if __name__ == "__main__":
    main()
