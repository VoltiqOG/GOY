"""Kostenrechner: Aufschlüsselung „Kosten pro Teil“ nur auf Wunsch (Schalter, Standard aus, wird gemerkt).

Aufruf: python patch_kosten_pro_teil.py <unverschluesselte index.html>
"""
import sys

path = sys.argv[1]
s = open(path, encoding="utf-8").read()


def rep(a, b):
    global s
    if a not in s:
        raise SystemExit("Stelle nicht gefunden: " + a[:90])
    s = s.replace(a, b, 1)


rep('''        <details class="sp-card sp-rec" open><summary><h4>Aufschlüsselung pro Teil</h4>''',
    '''        <button class="kbtn sm ghost sp-pttog" type="button" data-act="pt" aria-expanded="${st.ptOn ? "true" : "false"}">${st.ptOn ? "Kosten pro Teil ausblenden" : "Kosten pro Teil anzeigen"}</button>
        ${st.ptOn ? `<details class="sp-card sp-rec" open><summary><h4>Aufschlüsselung pro Teil</h4>''')
rep('''          ${tip ? `<p class="knote">${tip}</p>` : ""}</details>''',
    '''          ${tip ? `<p class="knote">${tip}</p>` : ""}</details>` : ""}''')
rep('''      const bx = box.querySelector('[data-act="apx"]');''',
    '''      box.querySelector('[data-act="pt"]').addEventListener("click", () => { st.ptOn = !st.ptOn; save(); calcAll(); });
      const bx = box.querySelector('[data-act="apx"]');''')
rep('''.sp-rec summary::-webkit-details-marker{display:none}''',
    '''.sp-rec summary::-webkit-details-marker{display:none}
.sp-pttog{justify-self:start;align-self:flex-start}''')

open(path, "w", encoding="utf-8").write(s)
print("Kosten pro Teil optional:", path)
