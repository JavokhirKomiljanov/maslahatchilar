# -*- coding: utf-8 -*-
"""Build the Uzbek 'advisors' guide: data/advisors.json -> build/guide.html -> PDF (Chrome headless) -> PNG pages (PyMuPDF).
Usage: python tools/render.py [--data data/advisors.json] [--out <basename>] [--png]
Needs Google Chrome (or set CHROME=<path>) and `pip install -r tools/requirements.txt`.
Font: drop InterTight.ttf / InterTight-Italic.ttf into tools/assets/ for the exact look; otherwise Inter Tight loads from Google Fonts.
Flow layout: Chrome paginates; cards never split; page footer stamped by PyMuPDF.
"""
import json, sys, os, html, subprocess, shutil, re, argparse
from urllib.parse import urlparse

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
ASSETS = os.path.join(TOOLS, 'assets')
CHROME = os.environ.get('CHROME') or next((c for c in [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
] + [shutil.which(n) or '' for n in ('google-chrome', 'chromium', 'chromium-browser', 'chrome')] if c and os.path.exists(c)), None)
PW, PH = 1080, 1920            # px
MT, MR, MB, ML = 88, 84, 110, 84

ap = argparse.ArgumentParser()
ap.add_argument('--data', default=os.path.join(ROOT, 'data', 'advisors.json'))
ap.add_argument('--out', default='Maslahatchilar-UZ')
ap.add_argument('--png', action='store_true', help='also export every page as PNG into build/<out>-PNG')
a = ap.parse_args()

data = json.load(open(a.data, encoding='utf-8'))
intro = data['intro']
people = [p for p in data['people'] if p.get('profile')]

def e(s):
    return html.escape(str(s or ''), quote=False)

def dom(url):
    try:
        d = urlparse(url).netloc
        return d[4:] if d.startswith('www.') else d
    except Exception:
        return url

def para(s, cls=''):
    parts = [x.strip() for x in re.split(r'\n\s*\n|\n', str(s or '')) if x.strip()]
    c = f' class="{cls}"' if cls else ''
    return ''.join(f'<p{c}>{e(x)}</p>' for x in parts)

FONT_TTF = os.path.join(ASSETS, 'InterTight.ttf')
if os.path.exists(FONT_TTF):
    F = ASSETS.replace(os.sep, '/')
    FONT_CSS = (f"@font-face{{font-family:'IT';src:url('file:///{F}/InterTight.ttf');font-weight:100 900}}"
                f"@font-face{{font-family:'IT';src:url('file:///{F}/InterTight-Italic.ttf');font-weight:100 900;font-style:italic}}")
else:
    FONT_CSS = ("@import url('https://fonts.googleapis.com/css2?family=Inter+Tight:ital,wght@0,100..900;1,100..900&display=block');"
                )
CSS = FONT_CSS + f"""
@page{{size:{PW}px {PH}px;margin:{MT}px {MR}px {MB}px {ML}px}}
*{{box-sizing:border-box}}
html{{background:#141414}}
html,body{{margin:0;padding:0}}
body{{font-family:'IT','Inter Tight','Segoe UI',sans-serif;color:#F3F3F1;-webkit-print-color-adjust:exact;print-color-adjust:exact;font-size:34px;line-height:1.35;width:{PW-ML-MR}px}}
.sec{{break-before:page}}
.sec:first-child{{break-before:auto}}
.fixed{{height:{PH-MT-MB}px;display:flex;flex-direction:column}}
.kicker{{color:#00C896;font-weight:600;font-size:26px;letter-spacing:.14em;text-transform:uppercase;margin:0 0 22px;break-after:avoid}}
h1{{font-size:112px;line-height:.98;font-weight:800;letter-spacing:-.03em;margin:0 0 28px}}
h2{{font-size:72px;line-height:1.02;font-weight:800;letter-spacing:-.025em;margin:0 0 26px;break-after:avoid}}
h3{{font-size:44px;line-height:1.1;font-weight:700;letter-spacing:-.015em;margin:0 0 12px}}
p{{margin:0 0 18px}}
.lead{{font-size:40px;line-height:1.3;color:#C9C9C4}}
.muted{{color:#8F8F8A}}
.num{{font-size:220px;font-weight:800;line-height:.85;color:#00C896;letter-spacing:-.05em;margin:0 0 30px}}
.tag{{display:inline-block;border:2px solid #2E2E2C;border-radius:999px;padding:8px 22px;font-size:26px;margin:0 12px 12px 0;color:#DADAD6}}
.card{{background:#1F1F1E;border-radius:26px;padding:30px 32px;margin:0 0 22px;break-inside:avoid}}
.card h3{{font-size:38px;margin-bottom:8px}}
.card .x{{font-size:30px;color:#C9C9C4;margin:0}}
.q{{font-size:31px;line-height:1.38;font-style:italic;color:#F3F3F1;margin:14px 0 6px;padding-left:22px;border-left:5px solid #00C896}}
.q.big{{font-size:37px;font-style:normal;font-weight:500;margin-top:0}}
.tr{{font-size:26px;color:#9A9A95;margin:0 0 6px;padding-left:27px}}
.src{{font-size:22px;color:#00C896;padding-left:27px;margin:0}}
.tl{{list-style:none;margin:0 0 30px;padding:0}}
.tl li{{display:flex;gap:26px;margin:0 0 14px;font-size:31px;line-height:1.3;break-inside:avoid}}
.tl b{{flex:0 0 235px;color:#00C896;font-weight:700}}
.rules li{{margin:0 0 14px;font-size:32px;line-height:1.32;break-inside:avoid}}
ol,ul{{padding-left:44px;margin:0 0 30px}}
.prompt{{background:#FFFFFF;color:#141414;border-radius:28px;padding:40px 44px;font-size:29px;line-height:1.38;white-space:pre-wrap;font-weight:500;-webkit-box-decoration-break:clone;box-decoration-break:clone}}
.prompt.small{{font-size:25px;line-height:1.34;padding:34px 38px}}
.prompt.xs{{font-size:23px;line-height:1.3;padding:32px 36px}}
.copyhint{{font-size:26px;color:#00C896;font-weight:600;margin:0 0 16px}}
.sources li{{font-size:23px;line-height:1.3;margin:0 0 12px;color:#DADAD6;overflow-wrap:anywhere;break-inside:avoid}}
.sources li span{{color:#8F8F8A;word-break:break-all}}
.cover-names{{margin-top:auto}}
.cover-names div{{font-size:52px;font-weight:700;line-height:1.15;margin:0 0 10px;letter-spacing:-.02em}}
.cover-names small{{display:block;font-size:28px;font-weight:400;color:#9A9A95;margin:0 0 14px}}
.spacer{{flex:1}}
.bar{{height:10px;width:180px;background:#00C896;border-radius:6px;margin:0 0 40px}}
.steps li{{font-size:34px;line-height:1.35;margin:0 0 20px;break-inside:avoid}}
.note{{font-size:28px;color:#9A9A95}}
"""

secs = []
def add(inner, fixed=False):
    secs.append(f'<section class="sec{" fixed" if fixed else ""}">{inner}</section>')

T = intro['title']

# cover
names = ''.join(f'<div>{e(p["profile"]["name"])}<small>{e(p["profile"]["tagline"])}</small></div>' for p in people)
add(f'<p class="kicker">Bepul qo’llanma · 2026</p><h1>{e(T)}</h1><p class="lead">{e(intro["subtitle"])}</p>'
    f'<div class="cover-names"><p class="kicker">Ichida</p>{names}</div>', fixed=True)

# intro + how to use
add(f'<p class="kicker">Bu nima</p><div class="bar"></div>{para(intro["intro"], "lead")}'
    f'<p class="kicker" style="margin-top:50px">Qanday ishlatiladi</p><ol class="steps">{"".join(f"<li>{e(s)}</li>" for s in intro["how_to_use"])}</ol>')

for idx, pp in enumerate(people, 1):
    P = pp['profile']; nm = P['name']
    comps = ''.join(f'<span class="tag">{e(c["name"])}</span>' for c in P['companies'])
    add(f'<p class="num">0{idx}</p><h2>{e(nm)}</h2><p class="lead">{e(P["tagline"])}</p><div class="bar"></div>{para(P["bio"])}'
        f'<div class="spacer"></div><p class="kicker">Kompaniyalari</p><div>{comps}</div>', fixed=True)
    cl = ''.join(f'<li><b>{e(c.get("years") or "")}</b><span><strong>{e(c["name"])}</strong> — {e(c["what"])}</span></li>' for c in P['companies'])
    tl = ''.join(f'<li><b>{e(t["when"])}</b><span>{e(t["event"])}</span></li>' for t in P['timeline'])
    add(f'<p class="kicker">{e(nm)} · Yo’li</p><h2>Qisqa tarix</h2><ul class="tl">{tl}</ul>'
        f'<p class="kicker">Kompaniyalar</p><ul class="tl">{cl}</ul>')
    cards = ''
    for n, r in enumerate(P['principles'], 1):
        qo = r.get('quote_original')
        qq = f'<p class="q">{e(qo)}</p><p class="src">{e(dom(r.get("source_url","")))}</p>' if qo else ''
        cards += f'<div class="card"><h3><span class="muted">{n}.</span> {e(r["title"])}</h3><p class="x">{e(r["explain"])}</p>{qq}</div>'
    add(f'<p class="kicker">{e(nm)} · Prinsiplar</p><h2>Qanday fikrlaydi</h2>{cards}')
    cards = ''.join(f'<div class="card"><h3>{e(v["topic"])}</h3><p class="x">{e(v["stance"])}</p>'
                    f'<p class="src" style="padding-left:0;margin-top:8px">{e(dom(v.get("source_url","")))}</p></div>' for v in P['views'])
    add(f'<p class="kicker">{e(nm)} · Qarashlari</p><h2>Mavzular bo’yicha</h2>{cards}')
    cards = ''
    for q in P['quotes']:
        tr = f'<p class="tr">Tarjima: {e(re.sub(r"^(Tarjima:\s*)+", "", q["translation_uz"]))}</p>' if q.get('translation_uz') and q.get('lang') != 'uz' else ''
        meta = ' · '.join(x for x in [q.get('source_title') or dom(q.get('source_url','')), q.get('date') or ''] if x)
        cards += f'<div class="card"><p class="q big">«{e(q["text"])}»</p>{tr}<p class="src">{e(meta)}</p></div>'
    add(f'<p class="kicker">{e(nm)} · O’z so’zlari</p><h2>Iqtiboslar</h2>{cards}')
    rules = ''.join(f'<li>{e(r)}</li>' for r in P['decision_rules'])
    add(f'<p class="kicker">{e(nm)} · Uslub</p><h2>Qanday gapiradi</h2>{para(P["how_he_talks"])}'
        f'<p class="kicker" style="margin-top:40px">Qaror qoidalari</p><ul class="rules">{rules}</ul>')
    L = len(P['advisor_prompt'])
    add(f'<p class="kicker">{e(nm)} · Maslahatchi</p><h2>Prompt — nusxa oling</h2><p class="copyhint">ChatGPT / Claude ga joylashtiring va savolingizni yozing</p>'
        f'<div class="prompt{" xs" if L>2600 else " small" if L>1300 else ""}">{e(P["advisor_prompt"])}</div>')
    exq = ''.join(f'<li>{e(x)}</li>' for x in P['example_questions'])
    srcs = ''.join(f'<li>{e(s["title"])}<br><span>{e(s["url"])}</span></li>' for s in P['sources'])
    add(f'<p class="kicker">{e(nm)} · Savollar</p><h2>Undan nimani so’rash mumkin</h2><ol class="steps">{exq}</ol>'
        f'<p class="kicker">Manbalar</p><ol class="sources">{srcs}</ol>')

add(f'<p class="kicker">Universal prompt</p><h2>Istalgan bob uchun</h2><div class="prompt">{e(intro["universal_prompt"])}</div>'
    f'<p class="kicker" style="margin-top:50px">Eslatma</p>{para(intro["disclaimer"], "note")}<div class="bar" style="margin-top:30px"></div>{para(intro["closing"], "lead")}')

doc = f'<!doctype html><html lang="uz"><head><meta charset="utf-8"><title>{e(T)}</title><style>{CSS}</style></head><body>{"".join(secs)}</body></html>'
os.makedirs(os.path.join(ROOT, 'build'), exist_ok=True)
hp = os.path.join(ROOT, 'build', 'guide.html')
open(hp, 'w', encoding='utf-8').write(doc)

raw = os.path.join(ROOT, 'build', 'guide-raw.pdf')
if not CHROME:
    sys.exit('Google Chrome topilmadi. CHROME=<path> qilib ko’rsating.')
r = subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-pdf-header-footer', '--run-all-compositor-stages-before-draw',
                    '--virtual-time-budget=10000', f'--print-to-pdf={raw}', 'file:///' + hp.replace(os.sep, '/')], capture_output=True, text=True)
if not os.path.exists(raw):
    print(r.stderr[-2000:]); sys.exit(1)

import fitz
d = fitz.open(raw)
n = len(d)
S = 0.75  # px -> pt
FN = 'IT' if os.path.exists(FONT_TTF) else 'helv'
for i, pg in enumerate(d, 1):
    pg.draw_rect(pg.rect, color=None, fill=(0.0784, 0.0784, 0.0784), overlay=False)
    if os.path.exists(FONT_TTF):
        pg.insert_font(fontname='IT', fontfile=FONT_TTF)
    y = (PH - 52) * S
    pg.insert_text((ML * S, y), T, fontname=FN, fontsize=22 * S, color=(0.48, 0.48, 0.46))
    lbl = f'{i} / {n}'
    w = fitz.get_text_length(lbl, fontname=FN, fontsize=22 * S) if False else len(lbl) * 22 * S * 0.5
    pg.insert_text(((PW - MR) * S - w, y), lbl, fontname=FN, fontsize=22 * S, color=(0.48, 0.48, 0.46))
pdf = os.path.join(ROOT, a.out + '.pdf')
d.save(pdf, garbage=3, deflate=True)
print(f'PDF: {pdf}  pages={n}')
txt = os.path.join(ROOT, a.out + '-promptlar.txt')
NL = chr(10)
with open(txt, 'w', encoding='utf-8') as f:
    f.write(T + ' - promptlar' + NL + intro['subtitle'] + NL + NL)
    f.write('UNIVERSAL PROMPT (istalgan bob uchun)' + NL + '=' * 60 + NL + intro['universal_prompt'] + NL + NL)
    for i, pp in enumerate(people, 1):
        P = pp['profile']
        f.write('0%d. %s - %s' % (i, P['name'], P['tagline']) + NL + '=' * 60 + NL + P['advisor_prompt'] + NL + NL)
        f.write('Savol namunalari:' + NL + NL.join('- ' + q for q in P['example_questions']) + NL + NL + NL)
    f.write('ESLATMA' + NL + intro['disclaimer'] + NL)
print('TXT: ' + txt)
if a.png:
    pngdir = os.path.join(ROOT, 'build', a.out + '-PNG')
    shutil.rmtree(pngdir, ignore_errors=True); os.makedirs(pngdir)
    d2 = fitz.open(pdf)
    for i, pg in enumerate(d2, 1):
        pix = pg.get_pixmap(dpi=96)
        pix.save(os.path.join(pngdir, f'{i:02d}.png'))
    print(f'PNG: {pngdir}  {len(d2)} files  {pix.width}x{pix.height}')
