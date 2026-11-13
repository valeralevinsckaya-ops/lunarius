# Собирает страницы знаков зодиака из docs/signs_content.py в public/signs/<slug>.html + public/signs/index.html
import os, sys, html, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'docs'))
from signs_content import SIGNS
OUT = os.path.join(ROOT, 'public/signs'); os.makedirs(OUT, exist_ok=True)
METRIKA = open(os.path.join(ROOT, 'design/metrika.html'), encoding='utf-8').read()
FAVICON = '''<link rel="icon" href="/favicon-64.png" sizes="64x64" type="image/png">
<link rel="icon" href="/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="#FBF8F3">
'''
from pairs_content import SIGNS as PSIGNS
GEN = {x[0]: x[2] for x in PSIGNS}
ELEM_COLOR = {'Огонь': '#F2768A', 'Земля': '#D9A93E', 'Воздух': '#5E8BF2', 'Вода': '#6E56CF'}
NAME2SLUG = {s['name']: s['slug'] for s in SIGNS}
ORDER = [s['slug'] for s in SIGNS]
def pair_links(me, names):
    out = []
    for n in [x.strip() for x in names.split(',')]:
        a, b = sorted([me, NAME2SLUG[n]], key=ORDER.index)
        out.append(f'<a href="/compat/{a}-{b}" style="color:inherit;text-decoration:none;border-bottom:1px solid rgba(91,68,189,.4)">{n}</a>')
    return ', '.join(out)

HEAD = '''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="https://lunarius.ru{path}">
''' + FAVICON + '''<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Oswald:wght@400;500;600;700&family=Manrope:wght@400;500;600;700&family=Noto+Sans+Symbols&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box}}
body{{margin:0;font-family:'Manrope',sans-serif;color:#2A2340;line-height:1.65;background:#FBF8F3;background-image:radial-gradient(1000px 700px at 100% 0%,rgba(242,180,120,.6),transparent 60%),radial-gradient(1000px 800px at 0% 25%,rgba(197,178,247,.65),transparent 60%),radial-gradient(900px 700px at 70% 80%,rgba(242,118,138,.3),transparent 60%),radial-gradient(800px 600px at 10% 100%,rgba(94,139,242,.25),transparent 60%);background-attachment:fixed}}
a{{color:#5B44BD}}
.wrap{{max-width:1200px;margin:0 auto;padding:0 24px 96px}}
header{{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:16px;padding:28px 0}}
.logo{{display:flex;align-items:center;gap:10px;text-decoration:none;color:#2A2340}}
.logo b{{font-family:'Oswald',sans-serif;font-size:26px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;line-height:1;display:block}}
.logo span{{font-size:11px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:#5B44BD;margin-top:4px;display:block}}
nav{{display:flex;flex-wrap:wrap;gap:28px;font-size:15px;font-weight:600}}nav a{{color:#2A2340;text-decoration:none}}
.glass{{background:linear-gradient(135deg,rgba(255,255,255,.78) 0%,rgba(255,255,255,.52) 55%,rgba(255,255,255,.68) 100%);backdrop-filter:blur(30px) saturate(170%);-webkit-backdrop-filter:blur(30px) saturate(170%);border:1.5px solid rgba(255,255,255,.98);box-shadow:inset 0 1px 0 #fff,inset 0 24px 48px rgba(255,255,255,.3),0 36px 80px rgba(62,44,143,.2),0 4px 10px rgba(62,44,143,.08);border-radius:36px}}
.crumbs{{font-size:13px;color:#6B6380;margin:8px 0 20px}}.crumbs a{{color:#5B44BD;text-decoration:none}}
.hero{{display:grid;grid-template-columns:minmax(0,420px) minmax(0,1fr);gap:40px;align-items:center;padding:36px 44px}}
.hero img{{width:100%;aspect-ratio:4/5;object-fit:cover;object-position:50% 20%;border-radius:32px;display:block}}
.sym{{font-family:'Noto Sans Symbols','Segoe UI Symbol',sans-serif;font-size:64px;line-height:1}}
h1{{margin:8px 0 10px;font-family:'Oswald',sans-serif;font-weight:600;font-size:72px;line-height:1;text-transform:uppercase}}
.meta{{display:flex;flex-wrap:wrap;gap:10px;margin:0 0 20px}}
.meta span{{padding:8px 14px;border-radius:999px;background:rgba(255,255,255,.65);font-size:13px;font-weight:700}}
.meta b{{color:#5B44BD}}
.intro{{font-size:17px;margin:0}}
h2{{margin:48px 0 16px;font-family:'Oswald',sans-serif;font-weight:600;font-size:40px;line-height:1.05;text-transform:uppercase}}
h2 em{{font-style:normal;color:#6E56CF}}
.sec{{padding:36px 44px;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:28px 40px}}
.sec h3{{margin:0 0 8px;font-family:'Oswald',sans-serif;font-weight:500;font-size:22px;text-transform:uppercase;letter-spacing:.02em;color:#5B44BD}}
.sec p{{margin:0;font-size:15.5px}}
.sec .wide{{grid-column:1/-1}}
.compat{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px}}
.cc{{padding:24px 26px;border-radius:24px;background:linear-gradient(135deg,rgba(255,255,255,.66),rgba(255,255,255,.4));border:1px solid rgba(255,255,255,.9);box-shadow:0 24px 60px rgba(91,68,189,.14)}}
.cc .k{{font-size:12px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:#5B44BD}}
.cc .v{{font-family:'Oswald',sans-serif;font-size:24px;font-weight:500;text-transform:uppercase;margin:6px 0 8px}}
.cc p{{margin:0;font-size:14px;color:#5E5675}}
.cta{{margin:28px 0 0;padding:28px 32px;border-radius:28px;background:linear-gradient(135deg,#6E56CF,#9A6BF0 60%,#F2768A);color:#fff;display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:16px}}
.cta b{{font-family:'Oswald',sans-serif;font-size:26px;font-weight:500;text-transform:uppercase;line-height:1.1}}
.cta a{{display:inline-flex;align-items:center;min-height:52px;padding:0 28px;border-radius:999px;background:#2A2340;color:#FBF8F3;text-decoration:none;font-weight:700}}
.grid{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:20px}}
.card{{display:flex;flex-direction:column;border-radius:28px;overflow:hidden;text-decoration:none;color:#2A2340}}
.card img{{width:100%;aspect-ratio:1;object-fit:cover;object-position:50% 20%;display:block}}
.card div{{padding:16px 20px 20px}}
.card h3{{margin:0;font-family:'Oswald',sans-serif;font-size:24px;font-weight:500;text-transform:uppercase}}
.card p{{margin:4px 0 0;font-size:13px;color:#6B6380}}
h1.list{{margin:24px 0 8px;font-family:'Oswald',sans-serif;font-weight:600;font-size:64px;line-height:1;text-transform:uppercase}}
.lead{{margin:0 0 36px;max-width:720px;font-size:17px;color:#5E5675}}
footer{{margin-top:72px;padding:28px 0 0;border-top:1px solid rgba(110,86,207,.2);font-size:13px;color:#6B6380;display:flex;flex-wrap:wrap;gap:16px;justify-content:space-between}}
@media (max-width:1100px){{.hero{{grid-template-columns:1fr}}.grid{{grid-template-columns:repeat(2,minmax(0,1fr))}}.compat{{grid-template-columns:1fr}}h1{{font-size:56px}}}}
@media (max-width:640px){{.hero,.sec{{padding:24px 20px;border-radius:24px}}.sec{{grid-template-columns:1fr}}h1{{font-size:42px}}h2{{font-size:30px}}.grid{{grid-template-columns:1fr 1fr;gap:12px}}h1.list{{font-size:40px}}}}
</style>
<!--METRIKA--></head>
<body>
<div class="wrap">
<header>
<a class="logo" href="/"><svg width="34" height="22" viewBox="0 0 34 22" aria-hidden="true"><path d="M3 19 A14 14 0 0 1 31 19" fill="none" stroke="#6E56CF" stroke-width="3" stroke-linecap="round"></path><line x1="17" y1="19" x2="25" y2="9" stroke="#2A2340" stroke-width="2.5" stroke-linecap="round"></line><circle cx="17" cy="19" r="2.5" fill="#2A2340"></circle></svg><span><b>Lunarius</b><span>Спидометр совместимости</span></span></a>
<nav aria-label="Основное меню"><a href="/">Совместимость</a><a href="/natal">Натальная карта</a><a href="/signs">Знаки</a><a href="/blog">Статьи</a></nav>
</header>
'''
FOOT = '''<footer><span>© 2026 Lunarius.ru · <a href="mailto:info@lunarius.ru">info@lunarius.ru</a> · <a href="/privacy">Документы</a></span><span>Сайт носит развлекательный характер и не заменяет консультацию специалиста</span></footer>
</div>
</body>
</html>
'''

def card(s):
    return f'<a class="card glass" href="/signs/{s["slug"]}"><img src="/img/{s["img"]}.webp" alt="{s["name"]}" loading="lazy"><div><h3>{s["name"]}</h3><p>{s["dates"]} · {s["element"]}</p></div></a>'

def person_block(label, p):
    return (f'<div class="sec glass"><div class="wide"><h3 style="font-size:16px">{label}</h3><p>{p["character"]}</p></div>'
            f'<div><h3>В любви и отношениях</h3><p>{p["love"]}</p></div>'
            f'<div><h3>В быту и семье</h3><p>{p["home"]}</p></div>'
            f'<div><h3>Что привлекает и что отталкивает</h3><p>{p["likes"]}</p></div>'
            f'<div><h3>Совет партнеру</h3><p>{p["advice"]}</p></div></div>')

for i, s in enumerate(SIGNS):
    title = f'{s["name"]}: характеристика знака, женщина-{s["name"]} и мужчина-{s["name"]} в любви, совместимость | Lunarius'
    desc = f'{s["name"]} ({s["dates"]}): характер, женщина-{s["name"]} и мужчина-{s["name"]} в любви, быту и семье, что привлекает и отталкивает, совместимость с другими знаками. Проверьте пару по натальным картам.'
    page = HEAD.format(title=html.escape(title), desc=html.escape(desc), path='/signs/' + s['slug']).replace('<!--METRIKA-->', METRIKA)
    page += '<p class="crumbs"><a href="/">Главная</a> · <a href="/signs">Знаки зодиака</a></p>'
    page += (f'<section class="hero glass"><img src="/img/{s["img"]}.webp" alt="{s["name"]}"><div>'
             f'<div class="sym" style="color:{ELEM_COLOR[s["element"]]}">{s["symbol"]}</div><h1>{s["name"]}</h1>'
             f'<div class="meta"><span>{s["dates"]}</span><span>Стихия: <b style="color:{ELEM_COLOR[s["element"]]}">{s["element"]}</b></span><span>Крест: <b>{s["mode"]}</b></span><span>Управитель: <b>{s["ruler"]}</b></span></div>'
             f'<p class="intro">{s["intro"]}</p></div></section>')
    page += f'<h2>Женщина-<em>{s["name"]}</em></h2>' + person_block('Характер', s['woman'])
    page += f'<h2>Мужчина-<em>{s["name"]}</em></h2>' + person_block('Характер', s['man'])
    page += f'<h2>Совместимость <em>{GEN[s["slug"]]}</em> с другими знаками</h2><div class="compat">'
    page += f'<div class="cc"><div class="k">Легко</div><div class="v">{pair_links(s["slug"], s["easy"])}</div><p>Та же или дружественная стихия: понимание без усилий, общий темп.</p></div>'
    page += f'<div class="cc"><div class="k">Сложно</div><div class="v">{pair_links(s["slug"], s["hard"])}</div><p>Квадрат: один крест, разные стихии. Сильное трение и борьба за главное.</p></div>'
    page += f'<div class="cc"><div class="k">Противоположность</div><div class="v">{pair_links(s["slug"], s["opposite"])}</div><p>Оппозиция: сильное притяжение и такая же сильная тяга переделать друг друга.</p></div></div>'
    page += f'<p style="margin:16px 0 0;font-size:14px;color:#6B6380">Нажмите на знак, чтобы открыть разбор пары. <a href="/compat">Таблица всех пар</a>.</p>'
    page += '<div class="cta"><b>Знака Солнца мало: Луна, Венера и Марс решают больше.<br>Проверьте пару по натальным картам</b><a href="/">Запустить спидометр</a></div>'
    others = [x for j, x in enumerate(SIGNS) if j != i]
    page += '<h2>Другие знаки</h2><div class="grid">' + ''.join(card(x) for x in others[:4]) + '</div>'
    page += FOOT
    assert 'ё' not in page and '—' not in page, s['slug']
    open(os.path.join(OUT, s['slug'] + '.html'), 'w', encoding='utf-8').write(page)

idx = HEAD.format(title='Знаки зодиака: характеристика, женщина и мужчина каждого знака в любви | Lunarius', desc='12 знаков зодиака: даты, стихия, управитель, характер, женщина и мужчина каждого знака в любви, быту и семье, совместимость с другими знаками.', path='/signs').replace('<!--METRIKA-->', METRIKA)
idx += '<h1 class="list">Знаки зодиака</h1><p class="lead">Характер, любовь, быт и совместимость: отдельно о женщине и о мужчине каждого знака. Нажмите на карточку.</p>'
idx += '<div class="grid">' + ''.join(card(s) for s in SIGNS) + '</div>' + FOOT
open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(idx)
words = sum(len(re.sub(r'<[^>]+>', ' ', open(os.path.join(OUT, s['slug'] + '.html'), encoding='utf-8').read()).split()) for s in SIGNS)
print('signs:', len(SIGNS), 'pages, words total ~', words)
