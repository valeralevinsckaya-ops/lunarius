# Собирает раздел «Дома в натальной карте»: public/doma/index.html и public/doma/<n>-dom.html
# Тексты: docs/houses_hub.py, docs/houses_1.py, docs/houses_2.py. Оформление берется со страницы стихий.
import os, sys, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'docs'))
import houses_1, houses_2, houses_hub as HUB
P = os.path.join(ROOT, 'public')
OUT = os.path.join(P, 'doma'); os.makedirs(OUT, exist_ok=True)
PL, SG = houses_1.PL, houses_1.SG
HOUSES = houses_1.H + houses_2.H
assert [h['n'] for h in HOUSES] == list(range(1, 13))
PL_LOC = ['Солнце', 'Луна', 'Меркурий', 'Венера', 'Марс', 'Юпитер', 'Сатурн', 'Уран', 'Нептун', 'Плутон']
ORD = ['Первый', 'Второй', 'Третий', 'Четвертый', 'Пятый', 'Шестой', 'Седьмой', 'Восьмой', 'Девятый', 'Десятый', 'Одиннадцатый', 'Двенадцатый']

tpl = open(os.path.join(P, 'elements', 'index.html'), encoding='utf-8').read()
tpl = re.sub(r'<!--meta:start-->.*?<!--meta:end-->\n?', '', tpl, flags=re.S)
tpl = re.sub(r'<script type="application/ld\+json">.*?</script>\n?', '', tpl, flags=re.S)
HEAD, rest = tpl.split('</header>', 1)
FOOT = rest[rest.index('<footer'):]
CSS = ('<style>.tb{padding:20px 24px;overflow-x:auto}.tb table{border-collapse:collapse;width:100%;font-size:15.5px}'
       '.tb td,.tb th{padding:8px 12px;border-bottom:1px solid rgba(110,86,207,.12);text-align:left;vertical-align:top}'
       '.tb td:first-child{white-space:nowrap;font-weight:700;color:#5B44BD}.hn{display:flex;flex-wrap:wrap;gap:10px;margin:24px 0 0}'
       '.hn a{display:inline-flex;align-items:center;min-height:42px;padding:0 16px;border-radius:999px;background:rgba(255,255,255,.7);border:1.5px solid rgba(255,255,255,.9);text-decoration:none;color:#2A2340;font-weight:600;font-size:14px}'
       '.hn a.on{background:#6E56CF;color:#fff}.hcard h2{font-size:24px;margin:0 0 6px}.hcard .s{font-size:13px;color:#5B44BD;font-weight:700;margin-bottom:6px}</style>')

def head(title, desc, path):
    h = re.sub(r'<title>.*?</title>', f'<title>{title}</title>', HEAD, flags=re.S)
    h = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{desc}">', h)
    h = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="https://lunarius.ru{path}">', h)
    return h.replace('</head>', CSS + '\n</head>', 1) + '</header>'

def sec(cards):
    return '<div class="sec glass">' + ''.join(f'<div><h3>{h}</h3><p>{t}</p></div>' for h, t in cards) + '</div>'

def nav(cur=None):
    return '<div class="hn">' + ''.join(f'<a href="/doma/{h["n"]}-dom"{" class=\"on\"" if h["n"] == cur else ""}>{h["n"]} дом</a>' for h in HOUSES) + '</div>'

def faq(items):
    return '<section id="faq" class="sec glass">' + ''.join(f'<div class="wide"><h3>{q}</h3><p>{a}</p></div>' for q, a in items) + '</section>'

CTA = '<div class="cta" style="margin-top:36px"><b>Узнать свои дома</b><a href="/natal">Рассчитать натальную карту</a></div>'

pages = {}
for h in HOUSES:
    n = h['n']
    title = f'{n} дом в натальной карте: значение и планеты | Lunarius'
    desc = f'{n} дом в натальной карте, {h["alias"]}: {h["themes"]}. Планеты в {n} доме, знак на куспиде, пустой {n} дом и {n} дом в синастрии.'
    assert len(title) <= 60 + len(' | Lunarius') and len(desc) <= 160, (n, len(title), len(desc))
    body = (f'<main>\n<p class="crumbs"><a href="/">Главная</a> · <a href="/doma">Дома</a> · {n} дом</p>'
            f'<h1 class="list">{n} дом <em style="font-style:normal;color:#6E56CF">в натальной карте</em></h1>'
            f'<p class="lead">{h["lead"]}</p>'
            f'<p class="lead" style="margin-top:-8px;font-size:15px">{ORD[n-1]} дом, {h["alias"]}. Естественный знак: {h["sign"]}, управитель: {h["ruler"]}. Тип дома: {h["kind"]}.</p>'
            f'<h2 id="znachenie">Что означает {n} дом <em>в натальной карте</em></h2>'
            '<div class="sec glass">' + ''.join(f'<div class="wide"><p>{p}</p></div>' for p in h['about']) + '</div>'
            f'<h2 id="planety">Планеты <em>в {n} доме</em></h2>'
            + sec([(f'{PL_LOC[i]} в {n} доме', t) for i, t in enumerate(h['planets'])]) +
            f'<h2 id="kuspid">Знак на куспиде <em>{n} дома</em></h2>'
            f'<p class="lead" style="margin:0 0 12px;font-size:15px">Знак на границе дома показывает стиль, в котором проживается его тема. Управитель этого знака подсказывает, куда тема ведет дальше.</p>'
            '<div class="glass tb"><table><tr><th>Знак</th><th>Что дает в ' + str(n) + ' доме</th></tr>'
            + ''.join(f'<tr><td>{SG[i]}</td><td>{t[0].upper() + t[1:]}</td></tr>' for i, t in enumerate(h['cusp'])) + '</table></div>'
            f'<h2 id="pustoy">Пустой <em>{n} дом</em></h2><div class="sec glass"><div class="wide"><p>{h["empty"]}</p></div></div>'
            f'<h2 id="sinastriya">{n} дом <em>в синастрии</em></h2><div class="sec glass"><div class="wide"><p>{h["syn"]}</p><p style="margin-top:10px">Проверить общую совместимость пары можно в <a href="/">спидометре совместимости</a>.</p></div></div>'
            f'<h2 id="voprosy">Частые <em>вопросы</em></h2>' + faq(h['faq'])
            + CTA + f'<h2 style="margin-top:48px">Все <em>дома</em></h2>' + nav(n) +
            '<p style="margin:24px 0 0;font-size:15px;color:#5E5675">Читайте также: <a href="/natal">натальная карта онлайн</a>, <a href="/ascendant">Асцендент</a>, <a href="/blog/aspekty-v-natalnoy-karte">аспекты в натальной карте</a>, <a href="/signs">знаки зодиака</a>.</p>'
            '</main>')
    pages[f'{n}-dom.html'] = head(title, desc, f'/doma/{n}-dom') + body + FOOT

cards = ''.join(f'<a class="ecard glass hcard" href="/doma/{h["n"]}-dom" style="text-decoration:none;color:inherit;padding:22px 24px;display:block"><h2>{h["n"]} дом</h2><div class="s">{h["alias"]}</div><p style="margin:0;font-size:15px">{h["themes"][0].upper() + h["themes"][1:]}.</p></a>' for h in HOUSES)
hub = (head(HUB.TITLE, HUB.DESC, '/doma') + '<main>\n<p class="crumbs"><a href="/">Главная</a> · Дома</p>'
       f'<h1 class="list">{HUB.H1}</h1><p class="lead">{HUB.LEAD}</p>'
       '<div class="grid">' + cards + '</div>'
       '<h2 id="chto-takoe">Как устроены <em>дома</em></h2>' + sec(HUB.INTRO)
       + '<h2 id="tipy">Угловые, последующие <em>и падающие</em></h2>' + sec(HUB.KINDS)
       + f'<h2 id="pustye">Пустые <em>дома</em></h2><div class="sec glass"><div class="wide"><p>{HUB.EMPTY}</p></div></div>'
       + f'<h2 id="sinastriya">Дома <em>в синастрии</em></h2><div class="sec glass"><div class="wide"><p>{HUB.SYN}</p></div></div>'
       + '<h2 id="voprosy">Частые <em>вопросы</em></h2>' + faq(HUB.FAQ) + CTA + '</main>' + FOOT)
pages['index.html'] = hub

for name, html_ in pages.items():
    assert 'ё' not in html_ and '—' not in html_, name
    open(os.path.join(OUT, name), 'w', encoding='utf-8').write(html_)
print('doma:', len(pages))
