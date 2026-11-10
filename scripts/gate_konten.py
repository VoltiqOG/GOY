"""Anmeldeseite: Gestaltung für Benutzerkonten (Benutzername, Konto anlegen, Konto-Code). Einmalig vor „benutzer.py einrichten“.

Aufruf: python scripts/gate_konten.py index.html
"""
import sys

p = sys.argv[1]
s = open(p, encoding="utf-8").read()
MARK = "/* Konten */"
if MARK in s:
    raise SystemExit("schon angepasst")
i = s.find("</style>")
css = MARK + '''
section>p{margin:0 0 18px}
label{margin-top:12px}form>label:first-child{margin-top:0}
input[type=text],textarea{width:100%;font:inherit;font-size:17px;padding:12px 14px;border-radius:12px;border:1.5px solid transparent;background:rgba(118,118,128,.12);color:var(--ink);transition:border-color .2s,box-shadow .2s,background-color .2s}
input[type=text]:focus,textarea:focus{outline:none;border-color:var(--acc);background:var(--card);box-shadow:0 0 0 4px color-mix(in srgb,var(--acc) 22%,transparent)}
textarea{font:12.5px/1.45 ui-monospace,"SF Mono",Menlo,Consolas,monospace;resize:none;word-break:break-all;margin-bottom:12px}
form button{margin-top:18px}.r{margin:14px 0 0}
.alt{display:flex;gap:10px;justify-content:center;align-items:center;margin-top:20px;font-size:14.5px;color:var(--muted)}
.link{width:auto;background:none!important;color:var(--acc)!important;padding:0;font-weight:500;margin:0;filter:none!important}
.meter{height:4px;border-radius:4px;background:rgba(118,118,128,.16);margin-top:8px;overflow:hidden}
.meter i{display:block;height:100%;width:0;border-radius:4px;transition:width .3s,background-color .3s}
.meter .lo{background:#ff3b30}.meter .mid{background:#ff9f0a}.meter .hi{background:#34c759}
.okp{color:var(--ink);font-size:15px}
#rmsg{min-height:22px;margin:12px 0 0;font-size:14px;color:var(--err)}
.opt{font-weight:400;color:var(--muted)}
'''
s = s[:i] + css + s[i:]
open(p, "w", encoding="utf-8").write(s)
print("Anmeldeseite (Konten) gestaltet:", p)
