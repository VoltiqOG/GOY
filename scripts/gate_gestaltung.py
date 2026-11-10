"""Anmeldeseite (unverschlüsselter Rahmen der index.html) an die Gestaltung 4.0 anpassen.

Aufruf: python scripts/gate_gestaltung.py index.html   (direkt auf die verschlüsselte Datei, der Inhalt bleibt unberührt)
"""
import sys

p = sys.argv[1]
s = open(p, encoding="utf-8").read()
MARK = "/* Gestaltung 4.0 */"
if MARK in s:
    raise SystemExit("schon angepasst")
i = s.find("</style>")
if i < 0:
    raise SystemExit("</style> nicht gefunden")
css = MARK + '''
:root{--bg:#f5f5f7;--card:#fff;--ink:#1d1d1f;--muted:#6e6e73;--line:#e2e2e7;--acc:#0071e3;--err:#d70015}
@media (prefers-color-scheme:dark){:root{--bg:#000;--card:#1c1c1e;--ink:#f5f5f7;--muted:#a1a1a6;--line:#2f2f32;--acc:#0a84ff;--err:#ff453a}}
body{font:17px/1.47 -apple-system,BlinkMacSystemFont,"SF Pro Text","Inter","Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;letter-spacing:-.011em;-webkit-font-smoothing:antialiased}
main{max-width:400px;border:0;border-radius:28px;padding:36px 32px 28px;box-shadow:0 1px 2px rgba(0,0,0,.04),0 30px 60px -24px rgba(0,0,0,.22)}
.k{letter-spacing:0;text-transform:none;font-weight:600;font-size:13px}
h1{font-size:32px;font-weight:700;letter-spacing:-.035em;line-height:1.08;margin:6px 0 8px}
p{font-size:15px}label{font-weight:500}
input[type=password],#rf input:not([type=checkbox]){border:1.5px solid transparent;background:rgba(118,118,128,.12);border-radius:12px;padding:12px 14px;transition:border-color .2s,box-shadow .2s,background-color .2s}
input[type=password]:focus,#rf input:not([type=checkbox]):focus{outline:none;border-color:var(--acc);background:var(--card);box-shadow:0 0 0 4px color-mix(in srgb,var(--acc) 22%,transparent)}
button{border-radius:980px;font-weight:500;padding:13px;color:#fff!important;transition:transform .2s cubic-bezier(.28,.11,.32,1),filter .2s}
button:hover{filter:brightness(1.06)}button:active{transform:scale(.98)}
.link{color:var(--acc)!important;text-decoration:none;border-radius:0}.link:hover{text-decoration:underline}
@media (prefers-reduced-motion:no-preference){@keyframes gIn{from{opacity:0;transform:translateY(18px) scale(.98)}to{opacity:1;transform:none}}main{animation:gIn .7s cubic-bezier(.28,.11,.32,1) both}}
'''
s = s[:i] + css + s[i:]
s = s.replace("</style>\n</style>", "</style>", 1)
open(p, "w", encoding="utf-8").write(s)
print("Anmeldeseite angepasst:", p)
