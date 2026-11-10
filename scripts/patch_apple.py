"""Komplette Design-Überarbeitung: ruhige, helle Gestaltung mit Systemschrift, Glasleiste, weichen Karten und Bewegung.

Aufruf: python patch_apple.py <unverschluesselte index.html>  (als letzter Design-Patch)
- Farb-, Schrift- und Radius-Token neu (hell und dunkel), Akzent Blau, Warnfarbe getrennt vom Akzent
- Navigation und Rechner-Kopf als Milchglas, Knöpfe als Pillen, Karten ohne harte Rahmen
- Startseite: zentrierter Kopf, Abschnitte mit Einblend-Bewegung beim Scrollen (nur ohne „Bewegung reduzieren“)
- Rechner: Segment-Umschalter, Eingabefelder mit Fokusring, Regler im iOS-Stil, große Preisanzeige
- Doppeltes entfernt: „Was bleibt bei einem anderen Preis?“ wiederholt nicht mehr Preis und Gewinn der Hauptanzeige
"""
import re
import sys

path = sys.argv[1]
s = open(path, encoding="utf-8").read()


def rep(a, b, n=1):
    global s
    if s.count(a) != n:
        raise SystemExit(f"Stelle {s.count(a)}× statt {n}× gefunden: " + a[:90])
    s = s.replace(a, b)


# Schrift: Systemschrift (San Francisco auf Apple-Geräten), sonst Inter
rep('''<link href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible+Mono:wght@400;500&family=Host+Grotesk:wght@400;500&display=swap" rel="stylesheet">''',
    '''<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">''')

CSS = r'''
/* ================= Gestaltung 4.0 – ruhig, hell, mit Bewegung ================= */
@media screen{
:root{
  --font-display:-apple-system,BlinkMacSystemFont,"SF Pro Display","Inter","Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
  --font-body:-apple-system,BlinkMacSystemFont,"SF Pro Text","Inter","Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
  --font-outlier:var(--font-body);--ap-mono:ui-monospace,"SF Mono",SFMono-Regular,Menlo,Consolas,monospace;
  --radius-card:20px;--radius-pill:12px;--tracking-display:-.025em;--display-weight:600;
  --ap-ease:cubic-bezier(.28,.11,.32,1);--ap-spring:cubic-bezier(.2,.9,.25,1.12);--navh:56px;--container:1240px;--section-gap:120px;--section-gap-s:104px;
  --text-display:clamp(3rem,6.2vw + .5rem,6rem);--text-section:clamp(2.1rem,3vw + 1rem,3.5rem);
  --color-paper:#f5f5f7;--color-paper-2:#ffffff;--color-paper-3:#ebebef;
  --color-ink:#1d1d1f;--color-ink-2:#3a3a3c;--color-muted:#6e6e73;
  --color-rule:#e2e2e7;--color-rule-soft:#ececf0;--color-rule-2:#c9c9cf;
  --color-accent:#0071e3;--color-accent-ink:#ffffff;--color-accent-soft:#e6f1fd;--color-focus:#0071e3;
  --color-cool:#0066cc;--color-cool-soft:#e8f2fe;
  --color-ok:#1d7f37;--color-ok-soft:#e7f6ea;--color-bad:#d70015;--color-bad-soft:#fdeaec;
  --color-deep:#1d1d1f;--color-deep-2:#2c2c2e;--color-deep-ink:#f5f5f7;--color-deep-muted:#a1a1a6;--color-deep-rule:#3a3a3c;--color-deep-bad:#ff6961;
  --color-plate:#ffffff;--color-scrim:rgba(0,0,0,.36);--color-scrim-strong:rgba(0,0,0,.82);--color-shade:rgba(0,0,0,.12);
  --color-grund:#5856d6;--color-druck:#0071e3;--color-slicer:#0b7f8c;--color-konstr:#1d7f37;--color-laser:#c2410c;--color-orga:#8944ab;--color-safety:#d70015;
  --warn:#b25000;--warnbg:#fff3e2;--onfill:#ffffff;
  --ap-alt:#ffffff;--ap-glass:rgba(245,245,247,.72);--ap-fill:rgba(118,118,128,.12);--ap-fill-2:rgba(118,118,128,.2);
  --ap-shadow:0 1px 2px rgba(0,0,0,.04),0 10px 30px -14px rgba(0,0,0,.14);--ap-shadow-up:0 2px 4px rgba(0,0,0,.05),0 24px 48px -18px rgba(0,0,0,.24);
}
:root[data-theme="dark"]{
  --color-paper:#000000;--color-paper-2:#1c1c1e;--color-paper-3:#2c2c2e;
  --color-ink:#f5f5f7;--color-ink-2:#d1d1d6;--color-muted:#a1a1a6;
  --color-rule:#2f2f32;--color-rule-soft:#262628;--color-rule-2:#48484a;
  --color-accent:#0a84ff;--color-accent-ink:#ffffff;--color-accent-soft:#0b2a4a;--color-focus:#0a84ff;
  --color-cool:#2997ff;--color-cool-soft:#0b2a4a;
  --color-ok:#30d158;--color-ok-soft:#0f2b17;--color-bad:#ff453a;--color-bad-soft:#331512;
  --color-deep:#1c1c1e;--color-deep-2:#2c2c2e;--color-deep-ink:#f5f5f7;--color-deep-muted:#a1a1a6;--color-deep-rule:#3a3a3c;
  --color-plate:#f5f5f7;--color-scrim:rgba(0,0,0,.6);--color-shade:rgba(0,0,0,.5);
  --color-grund:#7d7aff;--color-druck:#409cff;--color-slicer:#40c8e0;--color-konstr:#30d158;--color-laser:#ff9f0a;--color-orga:#bf5af2;--color-safety:#ff453a;
  --warn:#ff9f0a;--warnbg:#33240c;--onfill:#ffffff;
  --ap-alt:#0d0d0f;--ap-glass:rgba(22,22,24,.72);--ap-fill:rgba(118,118,128,.24);--ap-fill-2:rgba(118,118,128,.36);
  --ap-shadow:0 0 0 1px rgba(255,255,255,.06);--ap-shadow-up:0 0 0 1px rgba(255,255,255,.14),0 24px 48px -18px rgba(0,0,0,.8);
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --color-paper:#000000;--color-paper-2:#1c1c1e;--color-paper-3:#2c2c2e;
  --color-ink:#f5f5f7;--color-ink-2:#d1d1d6;--color-muted:#a1a1a6;
  --color-rule:#2f2f32;--color-rule-soft:#262628;--color-rule-2:#48484a;
  --color-accent:#0a84ff;--color-accent-ink:#ffffff;--color-accent-soft:#0b2a4a;--color-focus:#0a84ff;
  --color-cool:#2997ff;--color-cool-soft:#0b2a4a;
  --color-ok:#30d158;--color-ok-soft:#0f2b17;--color-bad:#ff453a;--color-bad-soft:#331512;
  --color-deep:#1c1c1e;--color-deep-2:#2c2c2e;--color-deep-ink:#f5f5f7;--color-deep-muted:#a1a1a6;--color-deep-rule:#3a3a3c;
  --color-plate:#f5f5f7;--color-scrim:rgba(0,0,0,.6);--color-shade:rgba(0,0,0,.5);
  --color-grund:#7d7aff;--color-druck:#409cff;--color-slicer:#40c8e0;--color-konstr:#30d158;--color-laser:#ff9f0a;--color-orga:#bf5af2;--color-safety:#ff453a;
  --warn:#ff9f0a;--warnbg:#33240c;--onfill:#ffffff;
  --ap-alt:#0d0d0f;--ap-glass:rgba(22,22,24,.72);--ap-fill:rgba(118,118,128,.24);--ap-fill-2:rgba(118,118,128,.36);
  --ap-shadow:0 0 0 1px rgba(255,255,255,.06);--ap-shadow-up:0 0 0 1px rgba(255,255,255,.14),0 24px 48px -18px rgba(0,0,0,.8);
}}

body{font-size:17px;line-height:1.5;letter-spacing:-.011em;font-variant-numeric:tabular-nums}
code,kbd,pre,samp,.code{font-family:var(--ap-mono)}
::selection{background:color-mix(in srgb,var(--color-accent) 26%,transparent)}
:focus-visible{outline:2px solid var(--color-focus);outline-offset:3px}
h1,h2,h3,h4{font-weight:600}

/* ---------- Navigation: Milchglas */
.nav{background:var(--ap-glass);-webkit-backdrop-filter:saturate(180%) blur(20px);backdrop-filter:saturate(180%) blur(20px);border-bottom:1px solid color-mix(in srgb,var(--color-ink) 9%,transparent)}
.brand{font-weight:600;font-size:18px;letter-spacing:-.022em}
.nav .wrap{max-width:1400px}
.nl{gap:2px;font-size:13.5px}
.nl a{color:color-mix(in srgb,var(--color-ink) 78%,transparent);padding:7px 10px;border-radius:980px;transition:color .2s var(--ap-ease),background-color .2s var(--ap-ease)}
.nl a:hover{color:var(--color-ink);background:var(--ap-fill)}
.sbtn{height:34px;border-radius:980px;border-color:transparent;background:var(--ap-fill);font-size:13.5px;transition:background-color .2s var(--ap-ease)}
.sbtn:hover{background:var(--ap-fill-2);border-color:transparent}
.sbtn kbd{border:0;background:color-mix(in srgb,var(--color-ink) 8%,transparent);border-radius:6px}
.calcbtn{height:34px;border-radius:980px;font-weight:500;font-size:13.5px;padding:0 15px 0 12px;transition:transform .2s var(--ap-ease),background-color .2s var(--ap-ease)}
.calcbtn:active,.btn:active{transform:scale(.97)}
.ib{border-radius:50%;transition:background-color .2s var(--ap-ease)}
.ib:hover{background:var(--ap-fill);border-color:transparent}
.prog{height:2px;background:linear-gradient(90deg,var(--color-accent),#5ac8fa)}

/* ---------- Knöpfe */
.btn{border-radius:980px;min-height:46px;padding:0 24px;font-size:17px;font-weight:400;letter-spacing:-.015em;transition:transform .2s var(--ap-ease),background-color .2s var(--ap-ease),color .2s var(--ap-ease),border-color .2s var(--ap-ease)}
.btn.ghost{border-color:var(--color-accent);color:var(--color-accent)}
.btn.ghost:hover{background:var(--color-accent);border-color:var(--color-accent);color:var(--color-accent-ink)}
.more,.go{color:var(--color-cool)}
.more:not(.ext)::after,.go::after,.flowx a::after{content:" ›";display:inline-block;margin-left:.2em;transition:transform .25s var(--ap-ease)}
.more:hover::after,a:hover>.qt .go::after,.flowx a:hover::after{transform:translateX(3px)}
.more,.flowx a{text-decoration:none!important}
.more:hover,.flowx a:hover{text-decoration:underline!important;text-underline-offset:3px}

/* ---------- Kopf der Startseite */
.hero{text-align:center;border-bottom:0;padding-block:clamp(56px,9vw,112px) var(--space-2xl);background:linear-gradient(180deg,var(--ap-alt),var(--color-paper))}
.hero-grid{grid-template-columns:minmax(0,1fr);justify-items:center;gap:clamp(32px,5vw,64px)}
.hero h1{font-weight:700;letter-spacing:-.04em;line-height:1.03;max-width:none}
.hero .lead{max-width:30em;margin-inline:auto;font-size:clamp(1.2rem,1vw + 1rem,1.7rem);line-height:1.3;letter-spacing:-.02em;color:var(--color-muted);font-weight:500}
.cta{justify-content:center;margin-top:var(--space-lg)}
.heroimg{width:100%;max-width:1040px}
.heroimg img{max-height:560px;margin-inline:auto;border-radius:28px}
.meta{border:0;background:transparent;border-radius:0;max-width:880px;margin-inline:auto;text-align:center;border-top:1px solid var(--color-rule)}
.meta>div,.meta.meta>div{border:0!important;padding:var(--space-md) var(--space-sm) 0}
.meta dt{font-size:12px;letter-spacing:0}
.meta dd{font-size:15px;font-weight:500}

/* ---------- Abschnitte */
.sec.alt{background:var(--ap-alt);border-block:0}
.band{background:#000;color:#f5f5f7}
.sh{grid-template-columns:minmax(0,1fr);row-gap:14px;max-width:860px;margin-bottom:var(--space-2xl)}
.sh h2{letter-spacing:-.03em;line-height:1.06}
.sh p{color:var(--color-muted);font-size:clamp(1.15rem,.6vw + 1rem,1.45rem);line-height:1.35;letter-spacing:-.015em;font-weight:500;max-width:36em}

/* ---------- Werkzeugkarten */
.tgrid{gap:var(--space-md)}
.tcard{border:0;background:var(--color-paper-2);border-radius:22px;padding:22px;box-shadow:var(--ap-shadow);column-gap:var(--space-md);transition:transform .45s var(--ap-ease),box-shadow .45s var(--ap-ease)}
.tcard:hover{transform:translateY(-4px) scale(1.012);box-shadow:var(--ap-shadow-up);border-color:transparent}
.tcard .ti{width:46px;height:46px;border-radius:13px;background:color-mix(in srgb,var(--a,var(--color-ink)) 13%,transparent)}
.tcard .tt{font-size:17px;letter-spacing:-.018em}
.tcard .td{font-size:14px}

/* ---------- Kapitelübersicht */
.cfilt button{border-color:transparent;background:var(--ap-fill);font-weight:500;padding:9px 16px;transition:background-color .2s var(--ap-ease),color .2s var(--ap-ease),transform .2s var(--ap-ease)}
.cfilt button:hover{background:var(--ap-fill-2)}
.cfilt button:active{transform:scale(.96)}
.cfilt button[aria-pressed="true"]{background:var(--color-ink);color:var(--color-paper);border-color:transparent}
.cc{border-radius:14px;transition:background-color .25s var(--ap-ease),transform .25s var(--ap-ease)}
.cc:hover{background:var(--color-paper-2)}
.cc .cct{letter-spacing:-.015em}

/* ---------- Maschinen, Schnellstart, Regeln, Ablauf */
.trio{border:0!important;background:none!important;gap:var(--space-md)!important;border-radius:0!important;overflow:visible!important}
.mc{background:var(--color-paper-2);border:0!important;border-radius:26px;box-shadow:var(--ap-shadow);overflow:hidden;transition:transform .5s var(--ap-ease),box-shadow .5s var(--ap-ease)}
.mc:hover{transform:translateY(-4px);box-shadow:var(--ap-shadow-up)}
.mc .mi img{transition:transform .8s var(--ap-ease)}
.mc:hover .mi img{transform:scale(1.035)}
.mc h3,.qc h3{letter-spacing:-.022em;font-weight:600}
.qc{border:0!important;background:var(--color-paper-2);border-radius:26px;box-shadow:var(--ap-shadow);overflow:hidden;transition:transform .5s var(--ap-ease),box-shadow .5s var(--ap-ease)}
.qc:hover{transform:translateY(-4px);box-shadow:var(--ap-shadow-up)}
.qc .qi img{transition:transform .8s var(--ap-ease)}
.qc:hover .qi img{transform:scale(1.03)}
.rule h3{font-weight:600;letter-spacing:-.02em}
.flow li.key{--color-accent:#ff9f0a}

/* ---------- Handbuch */
.chh h1,.content h2,.content h3{letter-spacing:-.022em;font-weight:600}
.call{border:0;border-radius:18px}
.glance{border:0!important;border-radius:20px}
.toc>ol>li>a,.toc li li a{border-radius:10px;transition:background-color .2s var(--ap-ease)}
.fig img,.fig .zoom{border-radius:16px}
.totop{border-radius:50%;border:0;background:var(--ap-glass);-webkit-backdrop-filter:saturate(180%) blur(20px);backdrop-filter:saturate(180%) blur(20px);box-shadow:var(--ap-shadow-up)}
.toast{border-radius:980px;background:color-mix(in srgb,#1d1d1f 86%,transparent);-webkit-backdrop-filter:blur(20px);backdrop-filter:blur(20px);color:#f5f5f7}
dialog::backdrop,.scrim{-webkit-backdrop-filter:blur(6px);backdrop-filter:blur(6px)}

/* ---------- Rechner & Werkzeuge */
.appbar{background:var(--ap-glass);-webkit-backdrop-filter:saturate(180%) blur(20px);backdrop-filter:saturate(180%) blur(20px);border-bottom:1px solid color-mix(in srgb,var(--color-ink) 9%,transparent)}
.appbar-in{height:56px}
.app{--apph:calc(56px + env(safe-area-inset-top,0px))}
.apptitle h2{font-weight:600;font-size:18px;letter-spacing:-.022em}
.appicon{border-radius:9px;width:30px;height:30px;background:linear-gradient(180deg,#2b95ff,#0071e3)}
.appicon svg{width:17px;height:17px}
.apptabs{background:var(--ap-fill);border-radius:11px;padding:3px}
.apptabs button{font-weight:500;font-size:13.5px;padding:8px 16px;border-radius:9px;letter-spacing:-.01em}
.apptabs button[aria-selected="true"]{font-weight:600}
.tabind{top:3px;bottom:3px;left:3px;border-radius:9px;background:var(--color-paper-2);box-shadow:0 3px 8px rgba(0,0,0,.12),0 1px 1px rgba(0,0,0,.06);transition:transform .4s var(--ap-ease),width .4s var(--ap-ease)}
:root[data-theme="dark"] .tabind{background:#636366}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .tabind{background:#636366}}
.appclose{background:var(--ap-fill)}
.appclose:hover{background:var(--ap-fill-2)}
.wseg{background:var(--ap-fill)!important;border-radius:11px!important;padding:3px!important;border:0!important}
.wseg button{border-radius:9px!important;font-weight:500;transition:background-color .25s var(--ap-ease),color .25s var(--ap-ease),box-shadow .25s var(--ap-ease)}
.wseg button[aria-pressed="true"]{background:var(--color-paper-2)!important;color:var(--color-ink)!important;font-weight:600;box-shadow:0 3px 8px rgba(0,0,0,.12),0 1px 1px rgba(0,0,0,.06)}
:root[data-theme="dark"] .wseg button[aria-pressed="true"]{background:#636366!important}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .wseg button[aria-pressed="true"]{background:#636366!important}}

.kin,.kres .sp-card,.sp-card,.kprof,.mcard,.kst,.wform,.ksrcb{border:0;box-shadow:var(--ap-shadow)}
.kprof,.sp-card,.mcard{border-radius:22px}
.kin{border-radius:24px}
.kin h3,.kres h3,.ksrch h3,.ksech h3{font-weight:600;letter-spacing:-.022em}
.kstep{border:0;background:var(--color-ink);color:var(--color-paper-2);font-weight:600;font-size:.74em;width:1.75em;height:1.75em}
.kf label,.wform label{font-weight:500;letter-spacing:-.005em}
.kin input,.kin select,.kst input,.wform input:not([type=checkbox]):not([type=range]):not([type=file]),.wform select,.wform textarea{background:var(--ap-fill);border:1.5px solid transparent;border-radius:12px;transition:border-color .2s var(--ap-ease),box-shadow .2s var(--ap-ease),background-color .2s var(--ap-ease)}
.kin input:focus,.kin select:focus,.kst input:focus,.wform input:not([type=checkbox]):not([type=range]):focus,.wform select:focus{outline:none;border-color:var(--color-accent);background:var(--color-paper-2);box-shadow:0 0 0 4px color-mix(in srgb,var(--color-accent) 22%,transparent)}
.kbtn{border-radius:980px;background:var(--ap-fill);font-weight:500;padding:11px 20px;transition:transform .2s var(--ap-ease),background-color .2s var(--ap-ease),filter .2s}
.kbtn:hover{filter:none;background:var(--ap-fill-2)}
.kbtn.pri,#q_step,#s_svg,#v_svg,#k_svg{background:var(--color-accent);color:#fff}
.kbtn.pri:hover,#q_step:hover,#s_svg:hover,#v_svg:hover,#k_svg:hover{background:color-mix(in srgb,var(--color-accent) 88%,#000);filter:none}
.kbtn.ghost{box-shadow:none;background:transparent;color:var(--color-accent)}
.kbtn.ghost:hover{background:color-mix(in srgb,var(--color-accent) 10%,transparent)}
.kbtn:disabled{opacity:.4;cursor:not-allowed}
.kprof-g>*{border-radius:14px!important;transition:transform .2s var(--ap-ease),background-color .2s var(--ap-ease),box-shadow .2s var(--ap-ease)}
.kprof-g>*:active,.ksrcb:active{transform:scale(.98)}
.ksrcb{border-radius:20px;transition:transform .3s var(--ap-ease),box-shadow .3s var(--ap-ease),background-color .3s var(--ap-ease)!important}
.ksrcb:hover{box-shadow:var(--ap-shadow-up)}
.ksrcb[aria-checked="true"]{box-shadow:inset 0 0 0 2px var(--color-accent),var(--ap-shadow);background:color-mix(in srgb,var(--color-accent) 7%,var(--color-paper-2))}
.ksrcb[aria-checked="true"]::after{background:var(--color-accent)}
.kdz,.kpaste{border-radius:20px!important}

.sp-hero{border-radius:26px;border:0;padding:26px 26px 22px;background:radial-gradient(120% 140% at 0% 0%,#2e2e33 0%,#1d1d1f 46%,#141416 100%);box-shadow:0 24px 50px -24px rgba(0,0,0,.55)}
.sp-price{font-family:var(--font-display);font-weight:600;font-size:clamp(44px,5.4vw,64px);letter-spacing:-.04em;line-height:1}
.sp-kpis>div{border-radius:14px!important;border:0!important;background:rgba(255,255,255,.08)!important}
.sp-keep em{border-radius:980px!important}

/* Regler im iOS-Stil */
.app input[type=range]{-webkit-appearance:none;appearance:none;background:transparent;height:30px;cursor:pointer}
.app input[type=range]::-webkit-slider-runnable-track{height:5px;border-radius:5px;background:var(--ap-fill-2)}
.app input[type=range]::-moz-range-track{height:5px;border-radius:5px;background:var(--ap-fill-2)}
.app input[type=range]::-moz-range-progress{height:5px;border-radius:5px;background:var(--color-accent)}
.app input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:24px;height:24px;margin-top:-9.5px;border-radius:50%;background:#fff;border:0;box-shadow:0 .5px 4px rgba(0,0,0,.14),0 3px 8px rgba(0,0,0,.2);transition:transform .2s var(--ap-ease)}
.app input[type=range]::-moz-range-thumb{width:24px;height:24px;border-radius:50%;background:#fff;border:0;box-shadow:0 .5px 4px rgba(0,0,0,.14),0 3px 8px rgba(0,0,0,.2)}
.app input[type=range]:active::-webkit-slider-thumb{transform:scale(1.12)}
.sp-hero input[type=range]::-webkit-slider-runnable-track{background:rgba(255,255,255,.22)}
.sp-hero input[type=range]::-moz-range-track{background:rgba(255,255,255,.22)}
.sp-tryres.hint{background:var(--ap-fill);color:var(--color-muted)}
.sp-tryres.hint+.sp-tryb [data-act="ap"]{display:none}
.app input[type=range]{--ap-p:0%}
.app input[type=range]::-webkit-slider-runnable-track{background:linear-gradient(90deg,var(--ap-on,var(--color-accent)) var(--ap-p),var(--ap-fill-2) var(--ap-p))}
.sp-hero input[type=range]{--ap-on:#fff}
.sp-hero input[type=range]::-webkit-slider-runnable-track{background:linear-gradient(90deg,#fff var(--ap-p),rgba(255,255,255,.22) var(--ap-p))}
.sp-hero input[type=range]::-moz-range-progress{background:#fff}
.sp-tryres{border-radius:14px!important}
.kmsg{border-radius:14px}
.wpbox,.prbox,.vpbox,.vkbox{border-radius:20px!important}
.mchip,.kchip,.chip,.badge{border-radius:980px}

/* ---------- Bewegung (nur wenn nicht „Bewegung reduzieren“) */
@media (prefers-reduced-motion:no-preference){
  @keyframes apUp{from{opacity:0;transform:translateY(26px)}to{opacity:1;transform:none}}
  @keyframes apZoom{from{opacity:0;transform:scale(.965) translateY(18px)}to{opacity:1;transform:none}}
  .hero h1{animation:apUp .9s var(--ap-ease) both}
  .hero .lead{animation:apUp .9s .08s var(--ap-ease) both}
  .hero .cta{animation:apUp .9s .16s var(--ap-ease) both}
  .heroimg{animation:apZoom 1.2s .2s var(--ap-ease) both}
  .hero .meta{animation:apUp .9s .4s var(--ap-ease) both}
  html.ap-rv .ap-r{opacity:0;transform:translateY(28px);transition:opacity .8s var(--ap-ease) var(--ap-d,0ms),transform .8s var(--ap-ease) var(--ap-d,0ms)}
  html.ap-rv .ap-r.ap-in{opacity:1;transform:none}
  html.ap-rv .ap-r.ap-done{transition:transform .45s var(--ap-ease),box-shadow .45s var(--ap-ease),background-color .25s var(--ap-ease)}
  .pane:not([hidden])>*{animation:apUp .55s var(--ap-ease) both}
  .pane:not([hidden])>*:nth-child(2){animation-delay:.04s}.pane:not([hidden])>*:nth-child(3){animation-delay:.08s}.pane:not([hidden])>*:nth-child(4){animation-delay:.12s}.pane:not([hidden])>*:nth-child(n+5){animation-delay:.16s}
  .sp-hero.chg{animation:apPulse .5s var(--ap-ease)}
  @keyframes apPulse{0%{transform:scale(1)}40%{transform:scale(1.012)}100%{transform:scale(1)}}
}

@media (max-width:900px){
  :root{--section-gap:80px;--section-gap-s:72px}
  .hero{padding-block:calc(var(--navh) + 40px) var(--space-xl)}
  .btn{font-size:16px;min-height:44px;padding:0 20px}
  .calcbtn{width:36px;height:36px;padding:0}
  .tcard{padding:16px;border-radius:18px}
  .tcard .ti{width:38px;height:38px;border-radius:11px}
  .tcard .tt{font-size:15px}
  .apptabs button{padding:8px 11px;font-size:13px}
  .sp-hero{padding:20px;border-radius:22px}
  .meta.meta{text-align:left}
}
}
'''

rep("</style>", CSS + "</style>")

# Doppelte Anzeige: „anderer Preis“ zeigt erst nach dem Ziehen ein Ergebnis (sonst steht dasselbe wie in der Hauptanzeige)
rep('''<p class="sp-tryres ${T.cls}" data-o="tryres">${T.html}</p>''',
    '''<p class="sp-tryres ${ap > 0 ? T.cls : "hint"}" data-o="tryres">${ap > 0 ? T.html : "Regler ziehen: zeigt sofort, was bei einem anderen Preis übrig bleibt – etwa wenn der Kunde handelt."}</p>''')
rep('''<div class="sp-th"><h4>Was bleibt bei einem anderen Preis?</h4><output data-o="try">${eur.format(tv)}</output></div>''',
    '''<div class="sp-th"><h4>Was bleibt bei einem anderen Preis?</h4><output data-o="try">${ap > 0 ? eur.format(tv) : ""}</output></div>''')

# Einblenden beim Scrollen
JS = r'''<script>
(function () {
  var d = document, root = d.documentElement;
  // Regler: gefüllte Spur
  function fill(r) { var mn = +r.min || 0, mx = +r.max || 100; r.style.setProperty("--ap-p", (mx > mn ? ((+r.value - mn) / (mx - mn)) * 100 : 0).toFixed(2) + "%"); }
  function fillAll() { d.querySelectorAll(".app input[type=range]").forEach(fill); }
  d.addEventListener("input", function (e) { if (e.target && e.target.type === "range") fill(e.target); setTimeout(fillAll, 0); }, true);
  d.addEventListener("change", function () { setTimeout(fillAll, 0); }, true);
  var app = d.querySelector(".app"); if (app && "MutationObserver" in window) { var ft = 0; new MutationObserver(function () { clearTimeout(ft); ft = setTimeout(fillAll, 30); }).observe(app, { childList: true, subtree: true }); }
  fillAll();
  if (!("IntersectionObserver" in window) || matchMedia("(prefers-reduced-motion: reduce)").matches || matchMedia("print").matches) return;
  var sel = ".sec .sh, .tgrid>li, .cfilt, ol.cards>li, .rules>li, .band .more, .trio>.mc, .flow>li, .flowx, .qs>.qc, .chh, .glance, .pnav";
  var els = [].slice.call(d.querySelectorAll(sel)), vh = innerHeight;
  if (!els.length) return;
  var io = new IntersectionObserver(function (en) {
    var k = 0;
    en.forEach(function (e) {
      if (!e.isIntersecting) return;
      var t = e.target; io.unobserve(t);
      t.style.setProperty("--ap-d", Math.min(k++, 8) * 55 + "ms"); t.classList.add("ap-in");
      setTimeout(function () { t.classList.add("ap-done"); t.style.removeProperty("--ap-d"); }, 1500);
    });
  }, { rootMargin: "0px 0px -6% 0px", threshold: 0.01 });
  els.forEach(function (el) { var r = el.getBoundingClientRect(); if (r.top < vh * 0.92 && r.bottom > 0) return; el.classList.add("ap-r"); io.observe(el); });
  root.classList.add("ap-rv");
  // Sprünge über Anker, Suche oder Kapitelfilter: nichts darf unsichtbar bleiben
  addEventListener("hashchange", function () { setTimeout(function () { els.forEach(function (el) { var r = el.getBoundingClientRect(); if (r.top < innerHeight && r.bottom > 0) el.classList.add("ap-in", "ap-done"); }); }, 60); });
  d.addEventListener("click", function (e) { if (e.target.closest && e.target.closest(".cfilt")) d.querySelectorAll("ol.cards>li.ap-r").forEach(function (el) { el.classList.add("ap-in", "ap-done"); }); });
})();
</script>
'''
i = s.rfind("</body>")
if i < 0:
    raise SystemExit("</body> nicht gefunden")
s = s[:i] + JS + s[i:]

open(path, "w", encoding="utf-8").write(s)
print("Gestaltung 4.0:", path)
