"""Kopfleiste auf dem Handy fest oben (position: fixed statt sticky – hält auch in iOS-Safari/Samsung Internet).

Aufruf: python patch_nav_fest.py <unverschluesselte index.html>
"""
import sys

path = sys.argv[1]
s = open(path, encoding="utf-8").read()
a = '''@media (max-width:520px){.qleg{font-size:12.5px}.qvbtn button{padding:5px 8px}}
</style>'''
if s.count(a) != 1:
    raise SystemExit("Stelle nicht gefunden")
s = s.replace(a, '''@media (max-width:520px){.qleg{font-size:12.5px}.qvbtn button{padding:5px 8px}}
@media screen and (max-width:900px){
  .nav{position:fixed;top:0;left:0;right:0;height:calc(var(--navh) + env(safe-area-inset-top,0px));padding-top:env(safe-area-inset-top,0px);box-sizing:border-box;-webkit-transform:translateZ(0);transform:translateZ(0)}
  body{padding-top:calc(var(--navh) + env(safe-area-inset-top,0px))}
}
</style>''')
open(path, "w", encoding="utf-8").write(s)
print("Kopfleiste fest:", path)
