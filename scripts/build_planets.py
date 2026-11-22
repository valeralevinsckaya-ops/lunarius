# Собирает разделы «Луна в знаках» (/luna) и «Венера в знаках» (/venera).
# Тексты: docs/moon_signs.py, docs/venus_signs.py. Оформление со страницы стихий, как у раздела «Дома».
import os, sys, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'docs'))
import moon_signs, venus_signs, planets_extra as PX
from signs_content import SIGNS
P = os.path.join(ROOT, 'public')
LOC = {'oven': 'Овне', 'telec': 'Тельце', 'bliznecy': 'Близнецах', 'rak': 'Раке', 'lev': 'Льве', 'deva': 'Деве', 'vesy': 'Весах',
       'skorpion': 'Скорпионе', 'strelec': 'Стрельце', 'kozerog': 'Козероге', 'vodoley': 'Водолее', 'ryby': 'Рыбах'}
GEN = {'oven': 'Овна', 'telec': 'Тельца', 'bliznecy': 'Близнецов', 'rak': 'Рака', 'lev': 'Льва', 'deva': 'Девы', 'vesy': 'Весов',
       'skorpion': 'Скорпиона', 'strelec': 'Стрельца', 'kozerog': 'Козерога', 'vodoley': 'Водолея', 'ryby': 'Рыб'}

tpl = open(os.path.join(P, 'elements', 'index.html'), encoding='utf-8').read()
tpl = re.sub(r'<!--meta:start-->.*?<!--meta:end-->\n?', '', tpl, flags=re.S)
tpl = re.sub(r'<script type="application/ld\+json">.*?</script>\n?', '', tpl, flags=re.S)
HEAD, rest = tpl.split('</header>', 1)
FOOT = rest[rest.index('<footer'):]
CSS = ('<style>.hn{display:flex;flex-wrap:wrap;gap:10px;margin:24px 0 0}'
       '.hn a{display:inline-flex;align-items:center;min-height:42px;padding:0 16px;border-radius:999px;background:rgba(255,255,255,.7);border:1.5px solid rgba(255,255,255,.9);text-decoration:none;color:#2A2340;font-weight:600;font-size:14px}'
       '.hn a.on{background:#6E56CF;color:#fff}.pl-top{display:flex;gap:24px;align-items:center;flex-wrap:wrap}.pl-top img{width:120px;height:120px;object-fit:cover;border-radius:24px}'
       '.sec ul{margin:0;padding-left:20px}.sec li{margin:0 0 6px;font-size:15.5px}</style>')

def head(title, desc, path):
    h = re.sub(r'<title>.*?</title>', f'<title>{title}</title>', HEAD, flags=re.S)
    h = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{desc}">', h)
    h = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="https://lunarius.ru{path}">', h)
    return h.replace('</head>', CSS + '\n</head>', 1) + '</header>'

def faq(items):
    return '<section id="faq" class="sec glass">' + ''.join(f'<div class="wide"><h3>{q}</h3><p>{a}</p></div>' for q, a in items) + '</section>'

ELN = {'Огонь': 'огненных', 'Земля': 'земных', 'Воздух': 'воздушных', 'Вода': 'водных'}
EL_SIGNS = {}
for _s in SIGNS: EL_SIGNS.setdefault(_s['element'], []).append(_s['name'])
ORDER = [x['slug'] for x in SIGNS]
def extra(slug_p, k, s, name, loc):
    if slug_p == 'luna':
        st, home = PX.MOON[k]
        rows = ''.join(f'<div><h3>Солнце в {ELN[el]} знаках</h3><p style="font-size:14px;color:#5B44BD;margin:0 0 6px">{", ".join(EL_SIGNS[el])}</p><p>{PX.SUN_MOON[(el, s["element"])]}</p></div>' for el in ['Огонь', 'Земля', 'Воздух', 'Вода'])
        return (f'<h2 id="stress">{name} в {loc} <em>в стрессе</em></h2><div class="sec glass"><div class="wide"><p>{st}</p></div></div>'
                f'<h2 id="dom">Дом, семья <em>и дети</em></h2><div class="sec glass"><div class="wide"><p>{home}</p></div></div>'
                f'<h2 id="solnce">{name} в {loc} <em>и знак Солнца</em></h2><p class="lead" style="margin:0 0 12px;font-size:15px">Знак Солнца показывает волю и цели, Луна потребности. Вот как Луна в {loc} сочетается с Солнцем в разных стихиях.</p><div class="sec glass">' + rows + '</div>')
    style, money = PX.VENUS[k]
    i = ORDER.index(k)
    suns = [SIGNS[(i + d) % 12] for d in (-2, -1, 0, 1, 2)]
    lst = ', '.join(f'<a href="/signs/{x["slug"]}">{x["name"]}</a>' for x in suns)
    return (f'<h2 id="stil">Вкус <em>и стиль</em></h2><div class="sec glass"><div class="wide"><p>{style}</p></div></div>'
            f'<h2 id="dengi">{name} в {loc} <em>и деньги</em></h2><div class="sec glass"><div class="wide"><p>{money}</p></div></div>'
            f'<h2 id="u-kogo">У каких знаков <em>бывает {name} в {loc}</em></h2><div class="sec glass"><div class="wide"><p>Венера не отходит от Солнца дальше 47 градусов, поэтому {name} в {loc} встречается только у пяти знаков Солнца: {lst}. Если ваш знак Солнца {suns[2]["name"]}, Венера может стоять в том же знаке: тогда любовь и характер говорят на одном языке. У остальных четырех знаков Венера добавляет к их стилю любви черты {GEN[k]}.</p></div></div>')

PLANETS = [
    ('luna', 'Луна', 'Луны', moon_signs, 'Луна в знаках', '/blog/luna-v-sinastrii', 'Луна в синастрии'),
    ('venera', 'Венера', 'Венеры', venus_signs, 'Венера в знаках', '/blog/venera-v-sinastrii', 'Венера в синастрии'),
]
CTA = '<div class="cta" style="margin-top:36px"><b>Узнать свою {gen} и совместимость</b><a href="/natal">Рассчитать натальную карту</a></div>'

count = 0
for slug_p, name, gen_p, mod, section, art, art_t in PLANETS:
    out = os.path.join(P, slug_p); os.makedirs(out, exist_ok=True)
    other = [x for x in PLANETS if x[0] != slug_p][0]
    for s in SIGNS:
        k = s['slug']; t = mod.P[k]; loc = LOC[k]
        title = f'{name} в {loc} у женщины и мужчины | Lunarius'
        desc = f'{name} в {loc} в натальной карте: характер, {name} в {loc} у женщины и у мужчины, в любви и совместимости, сильные стороны и советы.'
        assert len(desc) <= 160 and len(title) <= 71, (k, len(desc), len(title))
        nav = '<div class="hn">' + ''.join(f'<a href="/{slug_p}/{x["slug"]}"{" class=\"on\"" if x["slug"] == k else ""}>{name} в {LOC[x["slug"]]}</a>' for x in SIGNS) + '</div>'
        body = (f'<main>\n<p class="crumbs"><a href="/">Главная</a> · <a href="/{slug_p}">{section}</a> · {name} в {loc}</p>'
                f'<div class="pl-top"><img src="/img/{s["img"]}.webp" alt="{s["name"]}" width="120" height="120"><div><h1 class="list">{name} <em style="font-style:normal;color:#6E56CF">в {loc}</em></h1>'
                f'<p class="lead" style="margin:0">{s["name"]}: {s["element"].lower()}, {s["mode"]} знак, управитель {s["ruler"]}.</p></div></div>'
                f'<h2 id="znachenie">Что значит {name} <em>в {loc}</em></h2><div class="sec glass">' + ''.join(f'<div class="wide"><p>{p}</p></div>' for p in t['about']) + '</div>'
                f'<h2 id="zhenshchina">{name} в {loc} <em>у женщины</em></h2><div class="sec glass"><div class="wide"><p>{t["woman"]}</p></div></div>'
                f'<h2 id="muzhchina">{name} в {loc} <em>у мужчины</em></h2><div class="sec glass"><div class="wide"><p>{t["man"]}</p></div></div>'
                f'<h2 id="lyubov">{name} в {loc} <em>в любви</em></h2><div class="sec glass"><div class="wide"><p>{t["love"]}</p></div></div>'
                + extra(slug_p, k, s, name, loc) +
                f'<h2 id="plyusy">Сильные стороны <em>и сложности</em></h2><div class="sec glass">'
                f'<div><h3>Сильные стороны</h3><ul>' + ''.join(f'<li>{x[0].upper() + x[1:]}</li>' for x in t['plus']) + '</ul></div>'
                f'<div><h3>Сложности</h3><ul>' + ''.join(f'<li>{x[0].upper() + x[1:]}</li>' for x in t['minus']) + '</ul></div></div>'
                f'<h2 id="sovmestimost">Совместимость: <em>{name} в {loc}</em></h2><div class="sec glass"><div class="wide"><p>{t["match"]}</p>'
                f'<p style="margin-top:10px">Полную картину пары дает синастрия всех планет, ее считает <a href="/">спидометр совместимости</a>. Подробнее в статье <a href="{art}">{art_t}</a>.</p></div></div>'
                f'<h2 id="sovety">Советы <em>для {gen_p} в {loc}</em></h2><div class="sec glass"><div class="wide"><p>{t["advice"]}</p></div></div>'
                f'<h2 id="voprosy">Частые <em>вопросы</em></h2>' + faq(t['faq'])
                + CTA.format(gen=name[:-1] + 'у')
                + f'<h2 style="margin-top:48px">{section}</h2>' + nav +
                f'<p style="margin:24px 0 0;font-size:15px;color:#5E5675">Читайте также: <a href="/signs/{k}">знак {GEN[k]}</a>, <a href="/{other[0]}/{k}">{other[1]} в {loc}</a>, <a href="/doma">дома в натальной карте</a>, <a href="/natal">натальная карта онлайн</a>.</p>'
                '</main>')
        page = head(title, desc, f'/{slug_p}/{k}') + body + FOOT
        assert 'ё' not in page and '—' not in page, k
        open(os.path.join(out, k + '.html'), 'w', encoding='utf-8').write(page); count += 1
    h = mod.HUB
    cards = ''.join(f'<a class="ecard glass" href="/{slug_p}/{s["slug"]}" style="text-decoration:none;color:inherit;padding:22px 24px;display:block"><h2 style="font-size:22px;margin:0 0 6px">{name} в {LOC[s["slug"]]}</h2><p style="margin:0;font-size:15px">{mod.P[s["slug"]]["about"][0].split(". ")[0]}.</p></a>' for s in SIGNS)
    hub = (head(h['title'], h['desc'], f'/{slug_p}') + f'<main>\n<p class="crumbs"><a href="/">Главная</a> · {section}</p>'
           f'<h1 class="list">{h["h1"]}</h1><p class="lead">{h["lead"]}</p><div class="grid">{cards}</div>'
           f'<h2 id="chto">{name} <em>в натальной карте</em></h2><div class="sec glass">' + ''.join(f'<div><h3>{a}</h3><p>{b}</p></div>' for a, b in h['intro']) + '</div>'
           '<h2 id="voprosy">Частые <em>вопросы</em></h2>' + faq(h['faq'])
           + CTA.format(gen=name[:-1] + 'у')
           + f'<p style="margin:24px 0 0;font-size:15px;color:#5E5675">Другие разделы: <a href="/{other[0]}">{other[4]}</a>, <a href="/doma">дома в натальной карте</a>, <a href="/signs">знаки зодиака</a>, <a href="/ascendant">Асцендент</a>.</p></main>' + FOOT)
    assert 'ё' not in hub and '—' not in hub
    open(os.path.join(out, 'index.html'), 'w', encoding='utf-8').write(hub); count += 1
print('planets:', count)
