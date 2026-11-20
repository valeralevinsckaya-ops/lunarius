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
from signs_extra import EXTRA
import glob as _glob, importlib as _il, json as _json
DEEP = {}
for _f in sorted(_glob.glob(os.path.join(ROOT, 'docs', 'signs_deep_*.py'))): DEEP.update(_il.import_module(os.path.basename(_f)[:-3]).D)
STATS = _json.load(open(os.path.join(ROOT, 'docs', 'pairs_stats.json'), encoding='utf-8'))
GEN = {x[0]: x[2] for x in PSIGNS}
ELEM_COLOR = {'Огонь': '#F2768A', 'Земля': '#D9A93E', 'Воздух': '#5E8BF2', 'Вода': '#6E56CF'}
NAME2SLUG = {s['name']: s['slug'] for s in SIGNS}
ORDER = [s['slug'] for s in SIGNS]
EL_SLUG = {'Огонь': 'fire', 'Земля': 'earth', 'Воздух': 'air', 'Вода': 'water'}
LINK = 'style="color:inherit;border-bottom:1px solid rgba(91,68,189,.4);text-decoration:none"'
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
''' + FAVICON + '''<link rel="preload" href="/fonts/manrope.woff" as="font" type="font/woff" crossorigin>
<link rel="preload" href="/fonts/oswald.woff" as="font" type="font/woff" crossorigin>
<style>@font-face{{font-family:'Manrope';src:url(/fonts/manrope.woff) format('woff');font-weight:200 800;font-style:normal;font-display:swap}}@font-face{{font-family:'Oswald';src:url(/fonts/oswald.woff) format('woff');font-weight:200 700;font-style:normal;font-display:swap}}</style>
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
h1{{margin:8px 0 10px;font-family:'Oswald',sans-serif;font-weight:600;font-size:72px;line-height:1;text-transform:uppercase}}
.meta{{display:flex;flex-wrap:wrap;gap:10px;margin:0 0 20px}}
.meta span{{padding:8px 14px;border-radius:999px;background:rgba(255,255,255,.65);font-size:13px;font-weight:700}}
.meta b{{color:#5B44BD}}
.intro{{font-size:17px;margin:0}}
h2{{margin:48px 0 16px;font-family:'Oswald',sans-serif;font-weight:600;font-size:40px;line-height:1.05;text-transform:uppercase}}
h1 em,h2 em{{font-style:normal;color:#6E56CF}}
.sec{{padding:36px 44px;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:28px 40px}}
.sec h3{{margin:0 0 8px;font-family:'Oswald',sans-serif;font-weight:500;font-size:22px;text-transform:uppercase;letter-spacing:.02em;color:#5B44BD}}
.sec p{{margin:0;font-size:15.5px}}
.sec .wide{{grid-column:1/-1}}
.dec{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}}
.dec .glass{{padding:24px 26px}}
.dec .k{{font-family:'Oswald',sans-serif;font-size:20px;font-weight:500;text-transform:uppercase;color:#5B44BD}}
.dec .d{{margin:4px 0 10px;font-size:13px;font-weight:700;color:#6B6380}}
.dec p{{margin:0;font-size:15px}}
.sec ul{{margin:0;padding:0 0 0 20px;font-size:15.5px;line-height:1.7}}
@media (max-width:640px){{.dec{{grid-template-columns:1fr}}}}
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
.toc{{margin:28px 0 0;padding:20px 28px;font-size:14.5px;line-height:2.3}}.toc b{{margin-right:8px;font-family:'Oswald',sans-serif;font-weight:500;text-transform:uppercase;letter-spacing:.02em}}.toc a{{display:inline-block;margin:0 6px 0 0;padding:0 12px;border-radius:999px;background:rgba(255,255,255,.7);color:#5B44BD;text-decoration:none;line-height:2;white-space:nowrap}}h2[id]{{scroll-margin-top:16px}}.famous{{font-size:15.5px}}
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
<nav aria-label="Основное меню"><a href="/">Совместимость</a><a href="/natal">Натальная карта</a><a href="/ascendant">Асцендент</a><a href="/signs">Знаки</a><a href="/blog">Статьи</a></nav>
</header>
'''
FOOT = '''<footer><span>© 2026 Lunarius.ru · <a href="mailto:info@lunarius.ru">info@lunarius.ru</a> · <a href="/privacy">Документы</a></span><span>Сайт носит развлекательный характер и не заменяет консультацию специалиста</span></footer>
</div>
</body>
</html>
'''

def card(s):
    return f'<a class="card glass" href="/signs/{s["slug"]}"><img src="/img/{s["img"]}.webp" alt="{s["name"]}" loading="lazy"><div><h3>{s["name"]}</h3><p>{s["dates"]} · {s["element"]}</p></div></a>'

def person_block(label, p, inlove_title='', inlove=''):
    return (f'<div class="sec glass"><div class="wide"><h3 style="font-size:16px">{label}</h3><p>{p["character"]}</p></div>'
            f'<div><h3>В любви и отношениях</h3><p>{p["love"]}</p></div>'
            f'<div><h3>В быту и семье</h3><p>{p["home"]}</p></div>'
            f'<div><h3>Что привлекает и что отталкивает</h3><p>{p["likes"]}</p></div>'
            f'<div><h3>Совет партнеру</h3><p>{p["advice"]}</p></div>'
            + (f'<div class="wide"><h3>{inlove_title}</h3><p>{inlove}</p></div>' if inlove else '') + '</div>')

def deep_page(i, s, d):
    x = EXTRA[s['slug']]; nm = s['name']; gen = GEN[s['slug']]
    d = dict(d)
    d['woman'] = {**s['woman'], **d.get('woman', {})}; d['man'] = {**s['man'], **d.get('man', {})}
    for k in ('woman_inlove', 'man_inlove', 'work', 'friendship'): d.setdefault(k, x[k])
    d.setdefault('intro', (d['intro_lead'] + ' ' if d.get('intro_lead') else '') + s['intro'])
    toc = []
    def H(anchor, short, inner):
        toc.append((anchor, short)); return f'<h2 id="{anchor}">{inner}</h2>'
    def secs(items): return '<div class="sec glass">' + ''.join(f'<div class="wide"><h3>{h}</h3><p>{t}</p></div>' for h, t in items) + '</div>'
    def person(p, inlove_title, inlove):
        return (f'<div class="sec glass"><div class="wide"><h3>Характер</h3><p>{p["character"]}</p></div>'
                f'<div><h3>В любви и отношениях</h3><p>{p["love"]}</p></div><div><h3>В постели</h3><p>{p["sex"]}</p></div>'
                f'<div><h3>В браке и семье</h3><p>{p["home"]}</p></div><div><h3>Что привлекает и что отталкивает</h3><p>{p["likes"]}</p></div>'
                f'<div class="wide"><h3>{inlove_title}</h3><p>{inlove}</p></div><div class="wide"><h3>Совет партнеру</h3><p>{p["advice"]}</p></div></div>')
    page = HEAD.format(title=html.escape(d['title']), desc=html.escape(d['desc']), path='/signs/' + s['slug']).replace('<!--METRIKA-->', METRIKA)
    page += '<p class="crumbs"><a href="/">Главная</a> · <a href="/signs">Знаки зодиака</a></p>'
    meta = ''.join(f'<span>{k}: <b>{v}</b></span>' for k, v in d.get('meta_extra', []))
    page += (f'<section class="hero glass"><img src="/img/{s["img"]}.webp" alt="Знак зодиака {nm}"><div>'
             f'<h1>{d["h1"]}</h1>'
             f'<div class="meta"><span>{s["dates"]}</span><span>Стихия: <a href="/elements/{EL_SLUG[s["element"]]}" style="color:{ELEM_COLOR[s["element"]]};font-weight:700;text-decoration:none">{s["element"]}</a></span><span>Крест: <b>{s["mode"]}</b></span><span>Управитель: <b>{s["ruler"]}</b></span>{meta}</div>'
             f'<p class="intro">{d["intro"]}</p></div></section>')
    page += '<!--TOC-->'
    page += H('daty', 'Даты', f'Знак зодиака {nm}: <em>с какого по какое число</em>') + secs(d['dates'])
    page += H('stihiya', 'Стихия и символ', f'Стихия, символ и <em>управитель</em>') + f'<div class="sec glass"><div class="wide"><p>{x["symbolism"]}</p></div><div class="wide"><h3>Стихия {s["element"]} и {s["mode"]} крест</h3><p>{d["element"]}</p></div></div>'
    page += H('dekady', 'Декады', f'Три декады <em>{gen}</em>') + '<p class="lead" style="margin:-6px 0 18px">Знак делится на три части по десять градусов. У каждой декады свой дополнительный управитель, и он меняет характер знака. Даты примерные: в разные годы граница сдвигается на день.</p><div class="dec">' + ''.join(
        f'<div class="glass"><div class="k">{n} декада</div><div class="d">{dd} · управитель {r}</div><p>{t}</p></div>' for n, (dd, r, t) in zip(['Первая', 'Вторая', 'Третья'], d.get('decans', x['decans']))) + '</div>'
    page += H('harakter', 'Характер', f'Характеристика знака <em>{nm}</em>') + (f'<div class="sec glass"><div class="wide"><p>{d["character"]}</p></div><div><h3>Сильные стороны</h3><ul>' + ''.join(f'<li>{t}</li>' for t in x['strengths']) + '</ul></div>'
             f'<div><h3>Слабые стороны</h3><ul>' + ''.join(f'<li>{t}</li>' for t in x['weaknesses']) + f'</ul></div><div class="wide"><p>{d["strengths_text"]}</p></div></div>')
    page += H('zhenshchina', f'Женщина-{nm}', f'Женщина-<em>{nm}</em>: характеристика и любовь') + person(d['woman'], f'Как понять, что женщина-{nm} влюблена', d['woman_inlove'])
    page += H('muzhchina', f'Мужчина-{nm}', f'Мужчина-<em>{nm}</em>: характеристика и любовь') + person(d['man'], f'Как понять, что мужчина-{nm} влюблен', d['man_inlove'])
    page += H('rebenok', 'Ребенок', f'Ребенок-<em>{nm}</em>') + secs(d['child'])
    page += H('rabota', 'Работа и деньги', f'Работа, деньги и <em>дружба</em>') + (f'<div class="sec glass"><div class="wide"><h3>В работе</h3><p>{d["work"]}</p></div><div class="wide"><h3>Подходящие профессии</h3><p>{d["professions"]}</p></div>'
             f'<div><h3>Деньги</h3><p>{d["money"]}</p></div><div><h3>В дружбе</h3><p>{d["friendship"]}</p></div></div>')
    page += H('kamni', 'Камни и цвета', f'Камни, цвета и <em>талисманы</em>') + secs(d['symbols'])
    rows = []
    for o in SIGNS:
        a, b = sorted([s['slug'], o['slug']], key=ORDER.index); st = STATS[f'{a}-{b}']; rows.append((st['mean'], o, a, b, st))
    rows.sort(key=lambda r: -r[0])
    q = lambda r: f'«{nm} + {r[1]["name"]}»'
    speedo = (f'На спидометре Lunarius картина другая: мы посчитали по 20 000 случайных пар на каждое сочетание. Выше всех у знака {nm} пары {q(rows[0])}, {q(rows[1])} и {q(rows[2])}, ниже всех {q(rows[-2])} и {q(rows[-1])}. '
              'Разница между сочетаниями меньше двух баллов по шкале от −10 до +10, а разброс внутри каждого сочетания намного шире, поэтому знак Солнца дает только стартовую подсказку.')
    num = lambda v: ('+' if v > 0 else '−' if v < 0 else '') + f'{abs(v):.2f}'.replace('.', ',')
    table = ('<div class="glass" style="padding:20px 24px;margin:18px 0 0;overflow-x:auto"><table style="border-collapse:collapse;width:100%;font-size:15px"><tr style="text-align:left"><th style="padding:6px 8px">Пара</th><th style="padding:6px 8px">Средний балл</th><th style="padding:6px 8px">Перевес гармонии</th><th style="padding:6px 8px">Перевес напряжения</th></tr>'
             + ''.join(f'<tr><td style="padding:6px 8px"><a href="/compat/{a}-{b}" {LINK}>{nm} + {o["name"]}</a></td><td style="padding:6px 8px">{num(m)}</td><td style="padding:6px 8px">{st["good"]}%</td><td style="padding:6px 8px">{st["tense"]}%</td></tr>' for m, o, a, b, st in rows)
             + '</table><p style="margin:12px 0 0;font-size:13px;color:#6B6380">По 20 000 случайных пар на каждое сочетание, даты рождения 1960-2008, шкала спидометра от −10 до +10.</p></div>')
    page += H('sovmestimost', 'Кто подходит', f'Какой знак зодиака <em>подходит {GEN_DAT.get(s["slug"], nm)}</em>') + f'<div class="sec glass"><div class="wide"><p>{d["match"]} {speedo}</p></div><div><h3>Кто подходит женщине-{GEN_DAT[s["slug"]]}</h3><p>{d["match_woman"]}</p></div><div><h3>Кто подходит мужчине-{GEN_DAT[s["slug"]]}</h3><p>{d["match_man"]}</p></div></div>' + table
    page += '<div class="compat" style="margin-top:20px">'
    page += f'<div class="cc"><div class="k">Легко</div><div class="v">{pair_links(s["slug"], s["easy"])}</div><p>Та же или дружественная стихия: понимание без усилий, общий темп.</p></div>'
    page += f'<div class="cc"><div class="k">Сложно</div><div class="v">{pair_links(s["slug"], s["hard"])}</div><p>Квадрат: один крест, разные стихии. Сильное трение и борьба за главное.</p></div>'
    page += f'<div class="cc"><div class="k">Противоположность</div><div class="v">{pair_links(s["slug"], s["opposite"])}</div><p>Оппозиция: сильное притяжение и такая же сильная тяга переделать друг друга.</p></div></div>'
    page += H('izvestnye', 'Известные', f'Известные <em>{GEN_PL_S.get(s["slug"], nm)}</em>') + f'<div class="sec glass"><div class="wide"><p class="famous">{d["famous"]}</p></div></div>'
    page += H('voprosy', 'Вопросы', f'Вопросы о знаке <em>{nm}</em>') + '<section id="faq" class="sec glass">' + ''.join(f'<div class="wide"><h3>{qq}</h3><p>{t.replace("{SPEEDO}", f"На спидометре Lunarius в среднем лучше всего складываются пары {q(rows[0])}, {q(rows[1])} и {q(rows[2])}, но разница между знаками невелика.")}</p></div>' for qq, t in d['faq']) + '</section>'
    page += '<div class="cta"><b>Знака Солнца мало: Луна, Венера и Марс решают больше.<br>Проверьте пару по натальным картам</b><a href="/">Запустить спидометр</a></div>'
    all_pairs = ', '.join('<a href="/compat/{}-{}" {}>{} + {}</a>'.format(*sorted([s['slug'], o['slug']], key=ORDER.index), LINK, nm, o['name']) for o in SIGNS)
    page += f'<p style="margin:16px 0 0;font-size:15px;line-height:1.9">Все пары {gen}: {all_pairs}.</p>'
    page += (f'<p style="margin:12px 0 0;font-size:15px">Если {nm} - ваш восходящий знак, а не знак Солнца, читайте страницу <a href="/ascendant/{s["slug"]}" {LINK}>Асцендент: {nm}</a>. '
             f'О стихии знака: <a href="/elements/{EL_SLUG[s["element"]]}" {LINK}>{s["element"]}</a>. Свою карту можно построить на странице <a href="/natal" {LINK}>«Натальная карта»</a>.</p>')
    page += (f'<p style="margin:12px 0 0;font-size:15px;line-height:1.9">Читайте также: <a href="/blog/natalnaya-karta" {LINK}>как читать натальную карту</a>, '
             f'<a href="/blog/sovmestimost-znakov-zodiaka" {LINK}>как читать совместимость знаков зодиака</a>, <a href="/blog/ascendent" {LINK}>что такое Асцендент</a>.</p>')
    others = [o for j, o in enumerate(SIGNS) if j != i]
    page += '<h2>Другие знаки</h2><div class="grid">' + ''.join(card(o) for o in others[:4]) + '</div>'
    page += '<p style="margin:16px 0 0;font-size:15px;line-height:1.9">Все знаки: ' + ', '.join(f'<a href="/signs/{o["slug"]}" {LINK}>{o["name"]}</a>' for o in others) + '.</p>'
    page = page.replace('<!--TOC-->', '<nav class="toc glass" aria-label="Содержание"><b>На странице:</b> ' + ' '.join(f'<a href="#{a}">{t}</a>' for a, t in toc) + '</nav>')
    return page + FOOT

GEN_DAT = {'oven': 'Овну', 'telec': 'Тельцу', 'bliznecy': 'Близнецам', 'rak': 'Раку', 'lev': 'Льву', 'deva': 'Деве', 'vesy': 'Весам', 'skorpion': 'Скорпиону', 'strelec': 'Стрельцу', 'kozerog': 'Козерогу', 'vodoley': 'Водолею', 'ryby': 'Рыбам'}
GEN_PL_S = {'oven': 'Овны', 'telec': 'Тельцы', 'bliznecy': 'Близнецы', 'rak': 'Раки', 'lev': 'Львы', 'deva': 'Девы', 'vesy': 'Весы', 'skorpion': 'Скорпионы', 'strelec': 'Стрельцы', 'kozerog': 'Козероги', 'vodoley': 'Водолеи', 'ryby': 'Рыбы'}

for i, s in enumerate(SIGNS):
    if s['slug'] in DEEP:
        page = deep_page(i, s, DEEP[s['slug']])
        assert 'ё' not in page and '—' not in page, s['slug']
        open(os.path.join(OUT, s['slug'] + '.html'), 'w', encoding='utf-8').write(page)
        continue
    title = f'{s["name"]}: характеристика знака, женщина и мужчина | Lunarius'
    desc = f'Читайте характеристику знака {s["name"]} ({s["dates"]}): характер, женщина и мужчина в любви, работа, совместимость. Проверьте свою пару по датам.'
    page = HEAD.format(title=html.escape(title), desc=html.escape(desc), path='/signs/' + s['slug']).replace('<!--METRIKA-->', METRIKA)
    page += '<p class="crumbs"><a href="/">Главная</a> · <a href="/signs">Знаки зодиака</a></p>'
    page += (f'<section class="hero glass"><img src="/img/{s["img"]}.webp" alt="{s["name"]}"><div>'
             f'<h1>{s["name"]}</h1>'
             f'<div class="meta"><span>{s["dates"]}</span><span>Стихия: <a href="/elements/{EL_SLUG[s["element"]]}" style="color:{ELEM_COLOR[s["element"]]};font-weight:700;text-decoration:none">{s["element"]}</a></span><span>Крест: <b>{s["mode"]}</b></span><span>Управитель: <b>{s["ruler"]}</b></span></div>'
             f'<p class="intro">{s["intro"]}</p></div></section>')
    x = EXTRA[s['slug']]
    page += f'<h2>Символ и <em>управитель</em></h2><div class="sec glass"><div class="wide"><p>{x["symbolism"]}</p></div></div>'
    page += f'<h2>Три декады <em>{GEN[s["slug"]]}</em></h2><p class="lead" style="margin:-6px 0 18px">Знак делится на три части по десять градусов. У каждой декады свой дополнительный управитель, и он меняет характер знака. Даты примерные: в разные годы граница сдвигается на день.</p><div class="dec">' + ''.join(
        f'<div class="glass"><div class="k">{n} декада</div><div class="d">{d} · управитель {r}</div><p>{t}</p></div>' for n, (d, r, t) in zip(['Первая', 'Вторая', 'Третья'], x['decans'])) + '</div>'
    page += (f'<h2>Сильные и <em>слабые</em> стороны</h2><div class="sec glass"><div><h3>Сильные стороны</h3><ul>' + ''.join(f'<li>{t}</li>' for t in x['strengths']) + '</ul></div>'
             f'<div><h3>Слабые стороны</h3><ul>' + ''.join(f'<li>{t}</li>' for t in x['weaknesses']) + '</ul></div></div>')
    page += f'<h2>Женщина-<em>{s["name"]}</em></h2>' + person_block('Характер', s['woman'], f'Как понять, что женщина-{s["name"]} влюблена', x['woman_inlove'])
    page += f'<h2>Мужчина-<em>{s["name"]}</em></h2>' + person_block('Характер', s['man'], f'Как понять, что мужчина-{s["name"]} влюблен', x['man_inlove'])
    page += f'<h2>Работа, деньги и <em>дружба</em></h2><div class="sec glass"><div class="wide"><h3>Работа и деньги</h3><p>{x["work"]}</p></div><div class="wide"><h3>В дружбе</h3><p>{x["friendship"]}</p></div></div>'
    page += f'<h2>Совместимость <em>{GEN[s["slug"]]}</em> с другими знаками</h2><div class="compat">'
    page += f'<div class="cc"><div class="k">Легко</div><div class="v">{pair_links(s["slug"], s["easy"])}</div><p>Та же или дружественная стихия: понимание без усилий, общий темп.</p></div>'
    page += f'<div class="cc"><div class="k">Сложно</div><div class="v">{pair_links(s["slug"], s["hard"])}</div><p>Квадрат: один крест, разные стихии. Сильное трение и борьба за главное.</p></div>'
    page += f'<div class="cc"><div class="k">Противоположность</div><div class="v">{pair_links(s["slug"], s["opposite"])}</div><p>Оппозиция: сильное притяжение и такая же сильная тяга переделать друг друга.</p></div></div>'
    page += f'<p style="margin:16px 0 0;font-size:14px;color:#6B6380">Нажмите на знак, чтобы открыть разбор пары. <a href="/compat">Таблица всех пар</a>.</p>'
    all_pairs = ', '.join('<a href="/compat/{}-{}" {}>{} + {}</a>'.format(*sorted([s['slug'], o['slug']], key=ORDER.index), LINK, s['name'], o['name']) for o in SIGNS)
    page += f'<p style="margin:12px 0 0;font-size:15px;line-height:1.9">Все пары {GEN[s["slug"]]}: {all_pairs}.</p>'
    page += (f'<p style="margin:12px 0 0;font-size:15px">Если {s["name"]} - ваш восходящий знак, а не знак Солнца, читайте страницу <a href="/ascendant/{s["slug"]}" {LINK}>Асцендент: {s["name"]}</a>. '
             f'О стихии знака: <a href="/elements/{EL_SLUG[s["element"]]}" {LINK}>{s["element"]}</a>.</p>')
    page += '<div class="cta"><b>Знака Солнца мало: Луна, Венера и Марс решают больше.<br>Проверьте пару по натальным картам</b><a href="/">Запустить спидометр</a></div>'
    others = [x for j, x in enumerate(SIGNS) if j != i]
    page += (f'<p style="margin:12px 0 0;font-size:15px;line-height:1.9">Читайте также: <a href="/blog/natalnaya-karta" {LINK}>как читать натальную карту</a>, '
             f'<a href="/blog/sovmestimost-znakov-zodiaka" {LINK}>как читать совместимость знаков зодиака</a>, <a href="/blog/ascendent" {LINK}>что такое Асцендент</a>.</p>')
    page += '<h2>Другие знаки</h2><div class="grid">' + ''.join(card(x) for x in others[:4]) + '</div>'
    page += '<p style="margin:16px 0 0;font-size:15px;line-height:1.9">Все знаки: ' + ', '.join(f'<a href="/signs/{o["slug"]}" {LINK}>{o["name"]}</a>' for o in others) + '.</p>'
    page += FOOT
    assert 'ё' not in page and '—' not in page, s['slug']
    open(os.path.join(OUT, s['slug'] + '.html'), 'w', encoding='utf-8').write(page)

idx = HEAD.format(title='Знаки зодиака: характеристика, женщина и мужчина каждого знака в любви | Lunarius', desc='12 знаков зодиака: даты, стихия, управитель, характер, женщина и мужчина каждого знака в любви, быту и семье, совместимость с другими знаками.', path='/signs').replace('<!--METRIKA-->', METRIKA)
idx += '<h1 class="list">Знаки зодиака</h1><p class="lead">Характер, любовь, быт и совместимость: отдельно о женщине и о мужчине каждого знака. Нажмите на карточку.</p>'
idx += '<div class="grid">' + ''.join(card(s) for s in SIGNS) + '</div>' + FOOT
open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(idx)
# страница 404: то же оформление, без canonical, закрыта от индексации
p404 = HEAD.format(title='Страница не найдена | Lunarius', desc='Такой страницы нет. Перейдите к расчету совместимости, натальной карте или знакам зодиака.', path='/404').replace('<!--METRIKA-->', METRIKA)
p404 = p404.replace('<link rel="canonical" href="https://lunarius.ru/404">\n', '<meta name="robots" content="noindex">\n')
p404 += ('<h1 class="list">Страница не найдена</h1><p class="lead">Такого адреса на сайте нет: возможно, ссылка устарела или в ней опечатка. Вот что есть на Lunarius.</p>'
         '<div class="compat">'
         '<div class="cc"><div class="k">Расчеты</div><div class="v"><a href="/">Совместимость</a>, <a href="/natal">Натальная карта</a>, <a href="/ascendant">Асцендент</a></div><p>Три калькулятора по дате, времени и месту рождения.</p></div>'
         '<div class="cc"><div class="k">Знаки</div><div class="v"><a href="/signs">Знаки зодиака</a>, <a href="/compat">Совместимость знаков</a>, <a href="/elements">Стихии</a></div><p>Характер каждого знака и разбор всех 78 пар.</p></div>'
         '<div class="cc"><div class="k">Статьи</div><div class="v"><a href="/blog">Блог</a></div><p>Синастрия, дома, аспекты и Асцендент простым языком.</p></div>'
         '</div>' + FOOT)
assert 'ё' not in p404 and '—' not in p404
open(os.path.join(os.path.dirname(OUT), '404.html'), 'w', encoding='utf-8').write(p404)
words = sum(len(re.sub(r'<[^>]+>', ' ', open(os.path.join(OUT, s['slug'] + '.html'), encoding='utf-8').read()).split()) for s in SIGNS)
print('signs:', len(SIGNS), 'pages, words total ~', words)

# OG, canonical, JSON-LD
import runpy as _rp, os as _os
_rp.run_path(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'add_meta.py'))
