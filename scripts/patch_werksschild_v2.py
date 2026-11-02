"""Werksschild näher am Firmenschild (Fotos vom 02.11.): Aufbau und Proportionen angepasst.

Aufruf (nach patch_werksschild.py): python patch_werksschild_v2.py <unverschluesselte index.html>
- Kopf: Logo groß oben, Anschrift links darunter, Service-Block rechts eine Zeile tiefer
- Die obere Kante des ersten Kastens läuft als dünne Linie über die ganze Breite
- Links 5 Kästen mit Beschriftung davor; rechts 4 Felder, um eine Zeile nach unten versetzt,
  das letzte (Kom.) auf Höhe der Website-Zeile
- CE rechts im freien Bereich über dem ersten rechten Feld
- Website schmal (gestaucht) und fett, unter der linken Spalte
- Standard ohne Befestigungslöcher, Striche oben und unten über die volle Breite
"""
import sys

path = sys.argv[1]
s = open(path, encoding="utf-8").read()


def cut(start, end, new):
    global s
    i = s.find(start)
    j = s.find(end, i)
    if i < 0 or j < 0:
        raise SystemExit("Abschnitt nicht gefunden: " + start[:60])
    s = s[:i] + new + s[j:]


def rep(a, b):
    global s
    if a not in s:
        raise SystemExit("Stelle nicht gefunden: " + a[:90])
    s = s.replace(a, b, 1)


cut('''      // oben und unten ein kräftiger Strich über die volle Breite innerhalb des Rands''', '''      const svg = (prev) => { const C = (k) => (prev ? SCOL[colOf(k)].view : SCOL[colOf(k)].hex);''', r'''      // oben und unten ein kräftiger Strich über die volle Breite (bei Löchern davor endend)
      head.push(`M${f3(mx)} ${f3(m)}H${f3(W - mx)}V${f3(m + t)}H${f3(mx)}Z`, `M${f3(mx)} ${f3(H - m - t)}H${f3(W - mx)}V${f3(H - m)}H${f3(mx)}Z`);
      const top = m + t, bot = H - m - t, U = bot - top, Y = (f) => top + U * f;   // Lage als Anteil der Höhe zwischen den Strichen
      // Logo: groß, oben mittig
      const lgX = W * 0.16, lgW = W * 0.68, lgY = Y(0.04), lgH = U * 0.27; let logo = null;
      if (S.logo) { logo = svgFit(S.logo, lgX, lgY, lgW, lgH, "logo"); if (!logo) msgs.push(["err", "Die Logo-Datei ist keine gültige SVG."]); else if (logo.hasImg) msgs.push(["warn", "Das Logo enthält ein eingebettetes Pixelbild – das wurde entfernt. Bitte ein Vektor-Logo nehmen (Pixelbild in Inkscape oder XCS vektorisieren)."]); }
      else msgs.push(["warn", "Kein Logo geladen – gestrichelter Platzhalter (wird nicht gelasert). Logo als SVG laden; am besten einfarbig, Schrift in Pfade umgewandelt."]);
      // Anschrift links, Service rechts eine Zeile tiefer
      const ca = Math.max(1.4, Math.min(3, U * 0.032)), lh = 1.55, aY = Y(0.36), rx = W * 0.47;
      const L = [V.hersteller, V.adresse, V.telfax].filter((x) => String(x || "").trim()), R = [V.hotline ? "Service-Hotline   " + V.hotline : "", V.mail].filter((x) => String(x || "").trim());
      const cL = Math.min(ca, ...L.map((x) => fit(x, ca, false, rx - mx - 3))), cR = Math.min(ca, ...R.map((x) => fit(x, ca, false, W - mx - rx)));
      L.forEach((x, i) => head.push(cmdsToD(textCmds(x, mx, aY + cL + i * cL * lh, cL, false))));
      R.forEach((x, i) => head.push(cmdsToD(textCmds(x, rx, aY + cR + (i + 2) * cR * lh, cR, false))));
      // Felder: Raster aus 6 Zeilen; Zeile 6 ist die Website-Zeile
      const y0 = Math.max(aY + (L.length) * cL * lh + 1.5, aY + (R.length + 2) * cR * lh + 1.2), rows = 6, pitch = (bot - 0.8 - y0) / rows, bh = pitch * 0.74, rt = 0.25;
      const lc = Math.max(1.4, Math.min(3, pitch * 0.3)), vc0 = Math.max(1.4, Math.min(3.6, bh * 0.55));
      if (pitch < 4) msgs.push(["err", `Zu wenig Höhe für die Felder (Zeile ${n1(pitch, 1)} mm) – Schild höher machen.`]);
      const labL = WSL.map((_, i) => String(S["wsL" + i] || "")), labR = WSR.map((_, i) => String(S["wsRL" + i] || ""));
      const lw = Math.max(0, ...labL.map((x) => textWidth(x, lc, false))), rw = Math.max(0, ...labR.map((x) => textWidth(x, lc, false)));
      const bx = mx + (lw ? lw + 2 : 0), bx2 = W * 0.42, rlx = W * 0.45, rbx = Math.max(W * 0.66, rlx + (rw ? rw + 2 : 0)), rbx2 = W - mx;
      const rowY = (i) => y0 + pitch * i + (pitch - bh) / 2;
      const box = (x1, x2, yy, label, lx, value, name, topLine) => {
        if (label) fld.push(cmdsToD(textCmds(label, lx, yy + (bh + lc) / 2, lc, false)));
        fld.push(ringRect(x1, yy, x2 - x1, bh, rt));
        if (topLine) fld.push(`M${f3(x2)} ${f3(yy)}H${f3(W - mx)}V${f3(yy + rt)}H${f3(x2)}Z`); // obere Kante läuft über die ganze Breite
        if (S.wsfill && String(value || "").trim()) { const vw = x2 - x1 - 3, vc = fit(value, vc0, false, vw);
          if (textWidth(value, vc, false) > vw + 0.01) msgs.push(["err", `„${esc(name)}“ passt nicht in den Kasten – kürzen.`]);
          vals.push(cmdsToD(textCmds(value, x1 + 1.5, yy + (bh + vc) / 2, vc, false))); }
        if (x2 - x1 < 12) msgs.push(["warn", `Kasten „${esc(name)}“ ist sehr schmal – Beschriftung kürzen oder Schild breiter.`]); };
      for (let i = 0; i < 5; i++) box(bx, bx2, rowY(i), labL[i], mx, S["wsV" + i], labL[i] || "Feld " + (i + 1), i === 0);
      for (let i = 0; i < 4; i++) box(rbx, rbx2, rowY(i + 2), labR[i], rlx, S["wsRV" + i], labR[i] || "Feld " + (i + 6), false);
      // Website: gestaucht und fett, unter der linken Spalte (Zeile 6)
      const web = String(V.web || "").trim().toUpperCase(), sq = 0.78, wcx = (mx + bx2) / 2;
      let webD = "", webT = "";
      if (web) { const cw = fit(web, Math.min(3.4, pitch * 0.5), true, (bx2 - mx) / sq); webD = cmdsToD(textCmds(web, wcx, rowY(5) + (bh + cw) / 2, cw, true, "middle")); webT = `matrix(${sq} 0 0 1 ${f3(wcx * (1 - sq))} 0)`; }
      // CE rechts über dem ersten rechten Feld
      const ceH = Math.max(5, Math.min(10, pitch * 1.3)), ceW = ceH * 1.4, ce = ceGroup(W - mx - ceW - 1, rowY(0) + (pitch * 2 - ceH) / 2 + 0.6, ceH);
      if (!S.ce) msgs.push(["warn", "Keine CE-Vorlage geladen – blau gestrichelter Platzhalter. Offizielle CE-Datei der EU laden (Höhe ≥ 5 mm)."]);
      msgs.push(["", "Maschinenverordnung (EU) 2023/1230, Anhang III 1.7.3: Name und Anschrift des Herstellers, Bezeichnung, CE, Baureihe oder Typ, Seriennummer (falls vorhanden) und Baujahr gehören auf das Schild – die Feldbeschriftungen entsprechend wählen."]);
      // Schnitt
      if (S.outline) cut.push("M" + roundRect(0, 0, W, H, S.rad).map(([a, b]) => f3(a) + " " + f3(H - b)).join("L") + "Z");
      hp.forEach(([a, b]) => cut.push(`M${f3(a + S.hd / 2)} ${f3(b)}A${f3(S.hd / 2)} ${f3(S.hd / 2)} 0 1 0 ${f3(a - S.hd / 2)} ${f3(b)}A${f3(S.hd / 2)} ${f3(S.hd / 2)} 0 1 0 ${f3(a + S.hd / 2)} ${f3(b)}Z`));
      if (!msgs.some((x) => x[0] === "err")) msgs.unshift(["ok", "Werksschild passt – Logo, Felder und Text liegen innerhalb des Rands."]);
      if (S.color) msgs.push(["warn", "Farbmarkierung: Kapitel 10.11 – für Schilder an Maschinen in der Recyclinghalle oder außen keine Farben, dort schwarz markieren."]);
''')

# Website als eigener, gestauchter Pfad in der Kopf-Ebene
rep('''          grp("kopf", "c_kopf", head) + lg +''',
    '''          grp("kopf", "c_kopf", head) + (webD ? `<g id="website" fill="${C("c_kopf")}"><path transform="${webT}" d="${webD}"/></g>` : "") + lg +''')

# Vorlage „Werksschild“: Standard ohne Löcher, Format wie das Firmenschild
rep('''if (el.name === "preset" && el.value === "ws" && S.w <= 100) { S.w = 150; S.h = 95; S.holes = 4; }''',
    '''if (el.name === "preset" && el.value === "ws" && S.w <= 100) { S.w = 150; S.h = 110; S.holes = 0; }''')

open(path, "w", encoding="utf-8").write(s)
print("Werksschild v2:", path)
