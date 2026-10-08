# -*- coding: utf-8 -*-
"""Generate the repo pages from data/advisors.json.
Usage: python tools/build_site.py
Writes: README.md, SAVOLLAR.md, advisors/*.md, prompts/*.txt, docs/index.html (GitHub Pages site).
The PDF and the all-in-one prompts TXT come from tools/render.py."""
import json, os, re, html
from urllib.parse import urlparse
DST = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OWNER, REPO = 'JavokhirKomiljanov', 'maslahatchilar'
SITE = f'https://{OWNER.lower()}.github.io/{REPO}/'
GH = f'https://github.com/{OWNER}/{REPO}'
RAW = f'https://raw.githubusercontent.com/{OWNER}/{REPO}/main'
TXT = 'Maslahatchilar-UZ-promptlar.txt'

d = json.load(open(os.path.join(DST, 'data', 'advisors.json'), encoding='utf-8'))
intro, people = d['intro'], d['people']
NOTE = 'Bu loyihaning shu tadbirkorlarga aloqasi yo’q, ular buni tasdiqlamagan.'
for sub in ('advisors', 'prompts', 'docs'):
    os.makedirs(os.path.join(DST, sub), exist_ok=True)

def dom(u):
    n = urlparse(u or '').netloc
    return n[4:] if n.startswith('www.') else n
def w(rel, text):
    open(os.path.join(DST, rel), 'w', encoding='utf-8', newline='\n').write(text)
def q(text):
    return '\n'.join('> ' + l for l in str(text).split('\n'))
untr = lambda s: re.sub(r'^(Tarjima:\s*)+', '', s or '')

for pp in people:
    P, s = pp['profile'], pp['slug']
    w(f'prompts/{s}.txt', P['advisor_prompt'].strip() + '\n')
    L = [f"# {P['name']}", '', f"> {P['tagline']}", '', P['bio'], '',
         '## Prompt — nusxa oling', '', 'ChatGPT yoki Claude’ga tashlang va savolingizni yozing.', '', '```text', P['advisor_prompt'].strip(), '```', '',
         f"Faqat matn: [`prompts/{s}.txt`]({RAW}/prompts/{s}.txt)", '',
         '## Undan nimani so’rash mumkin', ''] + [f'- {x}' for x in P['example_questions']] + ['', '## Prinsiplar', '']
    for i, r in enumerate(P['principles'], 1):
        L += [f"### {i}. {r['title']}", '', r['explain'], '']
        if r.get('quote_original'):
            L += [q('«' + r['quote_original'] + '»') + (f"  \n> — [{dom(r.get('source_url'))}]({r['source_url']})" if r.get('source_url') else ''), '']
    L += ['## Mavzular bo’yicha qarashlari', '']
    for v in P['views']:
        L += [f"**{v['topic']}.** {v['stance']}" + (f" ([manba]({v['source_url']}))" if v.get('source_url') else ''), '']
    L += ['## O’z so’zlari', '']
    for x in P['quotes']:
        b = q('«' + x['text'] + '»')
        if x.get('translation_uz') and x.get('lang') != 'uz': b += '  \n> Tarjima: ' + untr(x['translation_uz'])
        meta = ', '.join(t for t in [f"[{x.get('source_title') or dom(x['source_url'])}]({x['source_url']})", x.get('date') or ''] if t)
        L += [b + '  \n> — ' + meta, '']
    L += ['## Qanday gapiradi', '', P['how_he_talks'], '', '## Qaror qoidalari', ''] + [f'- {x}' for x in P['decision_rules']]
    L += ['', '## Qisqa tarix', '', '| Qachon | Nima bo’lgan |', '|---|---|'] + [f"| {t['when']} | {t['event'].replace('|', '/')} |" for t in P['timeline']]
    L += ['', '## Kompaniyalar', ''] + [f"- **{c['name']}**" + (f" ({c['years']})" if c.get('years') else '') + f" — {c['what']}" for c in P['companies']]
    L += ['', '## Manbalar', ''] + [f"{i}. [{x['title']}]({x['url']})" for i, x in enumerate(P['sources'], 1)]
    L += ['', '---', '', intro['disclaimer'].replace('\n', ' ') + ' ' + NOTE, '', f'[← Barcha maslahatchilar]({GH}#maslahatchilar)', '']
    w(f'advisors/{s}.md', '\n'.join(L))

R = [f"# {intro['title']}", '', f"**{intro['subtitle']}**", '', f'**Ochish: {SITE}**', '', intro['intro'].replace('\n', ' '), '',
     '## Maslahatchilar', '', '| Kim | Nima bilan mashhur | Profil | Prompt |', '|---|---|---|---|']
for pp in people:
    P, s = pp['profile'], pp['slug']
    R.append(f"| **{P['name']}** | {P['tagline'].replace('|', '/')} | [o’qish](advisors/{s}.md) | [matn]({RAW}/prompts/{s}.txt) |")
R += ['', '## Tayyor savollar', '',
      'Har bir maslahatchiga beriladigan savol namunalari: **[SAVOLLAR.md](SAVOLLAR.md)**. Promptni tashlang, keyin shu savollardan birini bering yoki o’zingizga moslang.', '',
      f'Barcha promptlar va savollar bitta faylda: [{TXT}]({RAW}/{TXT})']
R += ['', '## Qanday ishlatiladi', ''] + [f'{i}. {x}' for i, x in enumerate(intro['how_to_use'], 1)]
R += ['', 'Tez yo’l: [saytni oching](' + SITE + '), maslahatchini tanlang va «ChatGPT’da ochish» tugmasini bosing.', '',
      '## Universal prompt', '', '```text', intro['universal_prompt'], '```', '',
      '## PDF', '', f'[Maslahatchilar-UZ.pdf](Maslahatchilar-UZ.pdf) — to’liq qo’llanma, telefon formati.', '',
      '## Claude Code uchun', '',
      'Claude Code ishlatsangiz, maslahatchilarni buyruq qilib qo’ying: [`claude-skill/maslahatchi`](claude-skill/maslahatchi/SKILL.md) papkasini `~/.claude/skills/` ichiga nusxalang.', '',
      '```text', '/maslahatchi isaev Savdom ikki oydan beri tushyapti, nimadan boshlay?',
      '/maslahatchi kengash Kredit olib ikkinchi filial ochsammi?   # to’rttasi birga javob beradi',
      '/maslahatchi savollar                                        # tayyor savollar', '```', '',
      '## Kod', '',
      'Hamma narsa bitta fayldan yig’iladi: [`data/advisors.json`](data/advisors.json). Profil matnini shu yerda o’zgartirasiz, sahifalar va PDF qayta yig’iladi.', '',
      '```bash', 'pip install -r tools/requirements.txt',
      'python tools/build_site.py   # README, SAVOLLAR.md, advisors/, prompts/, docs/ (sayt)',
      'python tools/render.py       # PDF va promptlar TXT (Google Chrome kerak)', '```', '',
      'Yangi tadbirkor qo’shish uchun `data/advisors.json` ichidagi `people` ro’yxatiga xuddi shu tuzilmada yangi profil qo’shing va ikkala skriptni ishga tushiring. '
      'Qoida bitta: har bir iqtibos manbasi bilan, o’ylab topilgan gap yo’q.', '',
      '## Eslatma', '', intro['disclaimer'].replace('\n', ' ') + ' ' + NOTE, '']
w('README.md', '\n'.join(R))

S = ['# Tayyor savollar', '',
     'Avval maslahatchining promptini ChatGPT yoki Claude’ga tashlang. Keyin quyidagi savollardan birini bering. '
     'Savolni o’z vaziyatingizga moslang va raqamlarni qo’shing: aylanma, jamoa soni, muammo nimada.', '',
     f'Tez yo’l: [saytda]({SITE}) «ChatGPT’da ochish» tugmasini bosing, prompt o’zi tushadi.', '']
for i, pp in enumerate(people, 1):
    P, s = pp['profile'], pp['slug']
    S += [f"## {i}. {P['name']}", '', f"_{P['tagline']}_", '',
          f"Prompt: [matn]({RAW}/prompts/{s}.txt) · [to’liq profil](advisors/{s}.md)", ''] + [f'- {x}' for x in P['example_questions']] + ['']
S += ['---', '', intro['disclaimer'].replace('\n', ' ') + ' ' + NOTE, '', '[← Bosh sahifa](README.md)', '']
w('SAVOLLAR.md', '\n'.join(S))
w('.gitignore', 'research/\nbuild/\ntools/assets/\n__pycache__/\n*.log\n')

data = [{'slug': pp['slug'], 'name': pp['profile']['name'], 'tagline': pp['profile']['tagline'], 'prompt': pp['profile']['advisor_prompt'].strip(),
         'questions': pp['profile']['example_questions']} for pp in people]
e = lambda s: html.escape(str(s), quote=True)
steps = ''.join(f'<li>{e(x)}</li>' for x in intro['how_to_use'])
page = f"""<!doctype html><html lang="uz"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(intro['title'])} — AI maslahatchilar</title><meta name="description" content="{e(intro['subtitle'])}">
<meta property="og:title" content="{e(intro['title'])}"><meta property="og:description" content="{e(intro['subtitle'])}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@400;500;600;800&display=swap" rel="stylesheet">
<style>
:root{{--bg:#141414;--fg:#f3f3f1;--mut:#9a9a95;--card:#1f1f1e;--line:#2e2e2c;--acc:#00c896}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--fg);font:17px/1.45 'Inter Tight','Segoe UI',system-ui,sans-serif}}
main{{max-width:760px;margin:0 auto;padding:40px 16px 72px}}
.k{{color:var(--acc);font-weight:600;font-size:13px;letter-spacing:.14em;text-transform:uppercase;margin:0 0 10px}}
h1{{font-size:clamp(44px,11vw,76px);line-height:1;font-weight:800;letter-spacing:-.03em;margin:0 0 14px}}
h2{{font-size:28px;line-height:1.1;font-weight:800;letter-spacing:-.02em;margin:0 0 6px}}
.lead{{font-size:20px;color:#c9c9c4;margin:0 0 28px}}
.card{{background:var(--card);border-radius:20px;padding:22px;margin:0 0 16px}}
.tag{{color:var(--mut);margin:0 0 14px;font-size:16px}}
.btns{{display:flex;flex-wrap:wrap;gap:8px}}
button,a.b{{font:600 15px/1 'Inter Tight',system-ui,sans-serif;border-radius:999px;padding:13px 18px;border:1.5px solid var(--line);background:transparent;color:var(--fg);cursor:pointer;text-decoration:none;display:inline-block}}
button.p,a.p{{background:var(--acc);border-color:var(--acc);color:#0b1f19}}
button:hover,a.b:hover{{border-color:var(--acc)}}
details{{margin-top:14px}}summary{{cursor:pointer;color:var(--mut);font-size:15px}}
pre{{white-space:pre-wrap;background:#fff;color:#141414;border-radius:14px;padding:16px;font:500 14px/1.45 'Inter Tight',system-ui,sans-serif;margin:12px 0 0}}
ul.q{{margin:10px 0 0;padding-left:20px;color:#c9c9c4;font-size:15px}}ol{{padding-left:22px;margin:0}}li{{margin:0 0 8px}}
.note{{color:var(--mut);font-size:14px;margin-top:28px}}a{{color:var(--acc)}}
</style></head><body><main>
<p class="k">Bepul qo’llanma · 2026</p><h1>{e(intro['title'])}</h1><p class="lead">{e(intro['subtitle'])}</p>
<div id="list"></div>
<div class="card"><p class="k">Qanday ishlatiladi</p><ol>{steps}</ol></div>
<div class="btns"><a class="b p" href="{GH}/raw/main/Maslahatchilar-UZ.pdf">PDF yuklab olish</a><a class="b" href="{GH}/blob/main/SAVOLLAR.md">Tayyor savollar</a><a class="b" href="{GH}">GitHub’da ochish</a></div>
<p class="note">{e(intro['disclaimer'].replace(chr(10), ' '))} {e(NOTE)}</p>
</main>
<script id="d" type="application/json">{json.dumps(data, ensure_ascii=False).replace('</', '<\\/')}</script>
<script>
const A=JSON.parse(document.getElementById('d').textContent),GH={json.dumps(GH)};
const START="\\n\\nTayyor bo’lsang, o’zingni qisqa tanishtir va mening vaziyatimni so’ra.";
const el=(t,c,x)=>{{const n=document.createElement(t);if(c)n.className=c;if(x!=null)n.textContent=x;return n}};
A.forEach((a,i)=>{{
  const c=el('div','card');c.append(el('p','k','0'+(i+1)),el('h2','',a.name),el('p','tag',a.tagline));
  const b=el('div','btns');
  const cp=el('button','p','Promptni nusxalash');
  cp.onclick=async()=>{{try{{await navigator.clipboard.writeText(a.prompt)}}catch(e){{const t=document.createElement('textarea');t.value=a.prompt;document.body.append(t);t.select();document.execCommand('copy');t.remove()}}cp.textContent='Nusxalandi';setTimeout(()=>cp.textContent='Promptni nusxalash',1800)}};
  const g=el('a','b','ChatGPT’da ochish');g.href='https://chatgpt.com/?q='+encodeURIComponent(a.prompt+START);g.target='_blank';g.rel='noopener';
  const k=el('a','b','Claude’da ochish');k.href='https://claude.ai/new?q='+encodeURIComponent(a.prompt+START);k.target='_blank';k.rel='noopener';
  const f=el('a','b','To’liq profil');f.href=GH+'/blob/main/advisors/'+a.slug+'.md';f.target='_blank';f.rel='noopener';
  b.append(cp,g,k,f);c.append(b);
  const d=el('details');d.append(el('summary','','Promptni ko’rish va savol namunalari'));d.append(el('pre','',a.prompt));
  const u=el('ul','q');a.questions.forEach(x=>u.append(el('li','',x)));d.append(u);c.append(d);
  document.getElementById('list').append(c);
}});
</script></body></html>"""
w('docs/index.html', page)
print('built', DST, [f for f in sorted(os.listdir(DST)) if not f.startswith('.git') or f == '.gitignore'], 'site', SITE)
