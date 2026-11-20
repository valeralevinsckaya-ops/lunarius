# Собирает страницы совместимости пар знаков: public/compat/<a>-<b>.html (78 пар) и public/compat/index.html
import os, sys, html, re, itertools
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'docs'))
from pairs_content import SIGNS, TRAITS, RELATION, ESSENCE, essence_key
from signs_content import SIGNS as SIGN_PAGES
from pairs_deep import DEEP
import glob as _glob, importlib as _il, json as _json
CARDS = {}
for _f in sorted(_glob.glob(os.path.join(ROOT, 'docs', 'pairs_cards_*.py'))): CARDS.update(_il.import_module(os.path.basename(_f)[:-3]).C)
# Средние баллы спидометра по 20 000 случайных пар на сочетание: считает scripts/pair_stats.js
STATS = _json.load(open(os.path.join(ROOT, 'docs', 'pairs_stats.json'), encoding='utf-8'))
RANK = {k: i + 1 for i, (k, v) in enumerate(sorted(STATS.items(), key=lambda kv: -kv[1]['mean']))}
SPHERE_RU = {'attraction': 'притяжение', 'emotions': 'эмоции', 'communication': 'общение', 'values': 'ценности', 'stability': 'устойчивость', 'growth': 'рост вместе'}
REL_NAME = {0: 'один знак', 1: 'соседние знаки', 2: 'секстиль', 3: 'квадрат', 4: 'тригон', 5: 'квинконс', 6: 'оппозиция'}
STARS_RU = {2: 'две звезды', 3: 'три звезды', 4: 'четыре звезды', 5: 'пять звезд'}
def num(x, digits=2):
    t = f'{abs(x):.{digits}f}'.replace('.', ',')
    return ('−' if x < 0 else '+') + t if round(x, digits) != 0 else t
def zone_ru(v):
    return 'Есть напряжение' if v <= -0.5 else 'Нейтрально' if v <= 0.5 else 'Хорошая совместимость'
DATE_FAQ = [
 'Откройте главную страницу, укажите дату, время и город рождения каждого. Расчет бесплатный и занимает несколько секунд.',
 'На главной странице есть спидометр: введите две даты рождения, по возможности со временем и городом, и получите балл пары и разбор по сферам.',
 'Нужны даты рождения обоих, а для точности время и город. Введите их в спидометр на главной: он сравнит десять планет каждой карты.',
 'Запустите спидометр на главной странице и введите данные рождения обоих партнеров. Без времени рождения расчет тоже работает, только без Асцендента и домов.',
 'Знака Солнца для этого мало. Введите полные даты рождения в спидометр на главной, и он покажет балл для каждого из вас и общую стрелку.',
 'Спидометр на главной странице считает пару по натальным картам: введите дату, время и место рождения обоих и прочитайте разбор по шести сферам.',
]
OUT = os.path.join(ROOT, 'public/compat'); os.makedirs(OUT, exist_ok=True)
METRIKA = open(os.path.join(ROOT, 'design/metrika.html'), encoding='utf-8').read()
EASY = {s['slug']: s['easy'] for s in SIGN_PAGES}
ELEM_COLOR = {'Огонь': '#F2768A', 'Земля': '#D9A93E', 'Воздух': '#5E8BF2', 'Вода': '#6E56CF'}
IDX = {s[0]: i for i, s in enumerate(SIGNS)}
EL_SLUG = {'Огонь': 'fire', 'Земля': 'earth', 'Воздух': 'air', 'Вода': 'water'}
LINK = 'style="color:inherit;border-bottom:1px solid rgba(91,68,189,.4);text-decoration:none"'
def pair_url(x, y):
    x, y = sorted([x, y], key=lambda k: IDX[k]); return f'/compat/{x}-{y}'

HEAD = open(os.path.join(ROOT, 'scripts/build_signs.py'), encoding='utf-8').read()
HEAD = re.search(r"HEAD = '''(.*?)'''\nFOOT", HEAD, re.S).group(1)
HEAD = HEAD.replace("''' + FAVICON + '''", '''<link rel="icon" href="/favicon-64.png" sizes="64x64" type="image/png">
<link rel="icon" href="/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="#FBF8F3">
''')
EXTRA_CSS = '''
.pair{{display:grid;grid-template-columns:1fr auto 1fr;gap:24px;align-items:center;padding:36px 44px}}
.pair img{{width:100%;aspect-ratio:4/5;object-fit:cover;object-position:50% 20%;border-radius:32px;display:block}}
.plus{{width:88px;height:88px;border-radius:50%;background:#2A2340;color:#FBF8F3;display:flex;align-items:center;justify-content:center;font-family:'Oswald',sans-serif;font-size:56px;font-weight:600}}
.pname{{margin:10px 0 0;font-family:'Oswald',sans-serif;font-size:34px;font-weight:600;text-transform:uppercase;text-align:center}}
.pel{{text-align:center;font-size:13px;font-weight:700}}
.verdict{{margin:28px 0 0;padding:28px 36px;display:flex;flex-wrap:wrap;gap:24px;align-items:center}}
.stars{{font-size:34px;letter-spacing:4px;color:#D9A93E;white-space:nowrap}}
.verdict h2{{margin:0 0 8px;font-size:30px}}
.verdict p{{margin:0;font-size:15.5px}}
.essence{{padding:32px 40px;font-size:17px;line-height:1.7}}
.essence p{{margin:0}}
.toc{{margin:28px 0 0;padding:20px 28px;font-size:14.5px;line-height:2.3}}
.toc b{{margin-right:8px;font-family:'Oswald',sans-serif;font-weight:500;text-transform:uppercase;letter-spacing:.02em}}
.toc a{{display:inline-block;margin:0 6px 0 0;padding:0 12px;border-radius:999px;background:rgba(255,255,255,.7);color:#5B44BD;text-decoration:none;line-height:2;white-space:nowrap}}
h2[id]{{scroll-margin-top:16px}}
@media (max-width:640px){{.pair{{grid-template-columns:1fr 1fr;padding:20px}}.plus{{display:none}}.pname{{font-size:22px}}.verdict,.essence{{padding:24px 20px}}}}
</style>'''
HEAD = HEAD.replace('</style>', EXTRA_CSS, 1)
FOOT = '''<footer><span>© 2026 Lunarius.ru · <a href="mailto:info@lunarius.ru">info@lunarius.ru</a> · <a href="/privacy">Документы</a></span><span>Сайт носит развлекательный характер и не заменяет консультацию специалиста</span></footer>
</div>
</body>
</html>
'''
CTA = '<div class="cta"><b>Знака Солнца мало: у каждого из вас еще девять планет.<br>Прокатитесь на спидометре совместимости по натальным картам</b><a href="/">Запустить спидометр</a></div>'

GEN_PL = {'oven': 'Овнов', 'telec': 'Тельцов', 'bliznecy': 'Близнецов', 'rak': 'Раков', 'lev': 'Львов', 'deva': 'Дев', 'vesy': 'Весов', 'skorpion': 'Скорпионов', 'strelec': 'Стрельцов', 'kozerog': 'Козерогов', 'vodoley': 'Водолеев', 'ryby': 'Рыб'}

def rel_index(a, b):
    d = abs(IDX[a] - IDX[b]); return min(d, 12 - d)

def cap(s): return s[0].upper() + s[1:]

PLURAL = {'bliznecy', 'vesy', 'ryby'}
def vb(slug, sg, pl): return pl if slug in PLURAL else sg

def page_for(a, b):
    toc = []
    def H(anchor, short, inner):
        toc.append((anchor, short)); return f'<h2 id="{anchor}">{inner}</h2>'
    A = SIGNS[IDX[a]]; B = SIGNS[IDX[b]]
    ta, tb = TRAITS[a], TRAITS[b]
    r = RELATION[rel_index(a, b)]
    same = a == b
    nameA, nameB = A[1], B[1]
    G2 = f'двух {GEN_PL[a]}' if same else f'{A[2]} и {B[2]}'
    title = f'Совместимость {G2} в любви и браке | Lunarius'
    desc = f'Узнайте, подходят ли друг другу {nameA} и {nameB}: любовь, брак, быт, ссоры и совет паре. Проверьте свою пару по датам рождения бесплатно.'
    page = HEAD.format(title=html.escape(title), desc=html.escape(desc), path=f'/compat/{a}-{b}').replace('<!--METRIKA-->', METRIKA)
    page += f'<p class="crumbs"><a href="/">Главная</a> · <a href="/compat">Совместимость знаков</a></p>'
    page += f'<h1 class="list" style="margin-bottom:18px">Совместимость <em>{G2}</em></h1>'
    page += (f'<section class="pair glass"><div><img src="/img/{A[5]}.webp" alt="{nameA}"><div class="pname">{nameA}</div><div class="pel" style="color:{ELEM_COLOR[A[4]]}">{A[4]}</div></div>'
             f'<div class="plus">+</div><div><img src="/img/{B[5]}.webp" alt="{nameB}"><div class="pname">{nameB}</div><div class="pel" style="color:{ELEM_COLOR[B[4]]}">{B[4]}</div></div></section>')
    page += f'<section class="verdict glass"><div class="stars">{"★" * r["stars"]}{"☆" * (5 - r["stars"])}</div><div style="flex:1;min-width:260px"><h2>{r["title"]}</h2><p>{r["text"].split(". ")[0]}. На спидометре у пар «{nameA} и {nameB}» средний балл {num(STATS[f"{a}-{b}"]["mean"])} по шкале от −10 до +10: {RANK[f"{a}-{b}"]}-е место среди 78 сочетаний знаков.</p></div></section>'
    ess = ESSENCE.get(essence_key(a, b))
    deep0 = DEEP.get(essence_key(a, b))
    if deep0 and deep0.get('intro'): page += f'<p class="lead" style="max-width:900px;margin:24px 0 0">{deep0["intro"]}</p>'
    page += '<!--TOC-->'
    if ess: page += H('sut', 'Суть пары', f'{nameA} и <em>{nameB}</em>: суть пары') + f'<section class="essence glass"><p>{ess}</p></section>'
    st = STATS[f'{a}-{b}']
    sp = sorted(st['spheres'].items(), key=lambda kv: kv[1])
    if st['mean'] > 0.5: tail = 'Знак Солнца дает такой паре небольшую фору, но разброс внутри сочетания намного шире этой форы: итог решают Луна, Венера, Марс и точное время рождения.'
    elif st['mean'] < -0.3: tail = 'Знак Солнца дает такой паре небольшой минус, и другие планеты легко его перекрывают: у каждой третьей пары с этими знаками спидометр показывает перевес гармонии.'
    else: tail = 'Знак Солнца почти не сдвигает результат: итог решают Луна, Венера, Марс и точное время рождения.'
    P2 = '<p style="margin:14px 0 0">'
    page += H('ball', 'Балл спидометра', f'Средний балл спидометра: <em>{nameA} и {nameB}</em>') + (
        f'<section class="essence glass"><p>Мы посчитали на спидометре 20 000 случайных пар «{nameA} и {nameB}» с датами рождения 1960-2008 годов. '
        f'В среднем получилось {num(st["mean"])}, это зона «{zone_ru(st["mean"])}»; половина пар набирает больше {num(st["median"])}.</p>'
        f'{P2}У {st["good"]}% таких пар перевешивают гармоничные связи (балл выше +0,5), у {st["tense"]}% перевешивает напряжение (ниже −0,5), у остальных {100 - st["good"] - st["tense"]}% счет близок к нулю. '
        f'Сильную связь, от +2 и выше, получают {st["strong"]}% пар. Восемь пар из десяти укладываются в диапазон от {num(st["p10"], 1)} до {num(st["p90"], 1)}.</p>'
        f'{P2}По сферам у этого сочетания выше всего {SPHERE_RU[sp[-1][0]]} ({num(sp[-1][1])}), ниже всего {SPHERE_RU[sp[0][0]]} ({num(sp[0][1])}). {tail}</p></section>')
    deep = DEEP.get(essence_key(a, b))
    cd = CARDS[f'{a}-{b}']
    def duo(key, ha, hb):
        if same: return f'<div class="wide"><h3>{nameA} рядом с {A[3]}</h3><p>{cd[key]}</p></div>'
        return f'<div><h3>{ha}</h3><p>{cd[key][0]}</p></div><div><h3>{hb}</h3><p>{cd[key][1]}</p></div>'
    if deep:
        def cards(first, rest): return f'<div class="wide"><p>{first}</p></div>' + ''.join(f'<div><h3>{h}</h3><p>{t}</p></div>' for h, t in rest)
        page += H('ona-on', f'Женщина-{nameA} и мужчина-{nameB}', f'Женщина-{nameA} и <em>мужчина-{nameB}</em>') + '<section class="sec glass">' + cards(deep['w_a_m_b'], deep.get('wm', [])) + '</section>'
        if not same: page += H('on-ona', f'Мужчина-{nameA} и женщина-{nameB}', f'Мужчина-{nameA} и <em>женщина-{nameB}</em>') + '<section class="sec glass">' + cards(deep['m_a_w_b'], deep.get('mw', [])) + '</section>'
        page += H('nachalo', 'Начало отношений', f'Как начинаются отношения <em>{G2}</em>') + f'<section class="essence glass"><p>{deep["start"]}</p></section>'
    # притяжение и трение
    page += H('prityazhenie', 'Что притягивает', f'Что притягивает <em>{G2}</em>') + f'<section class="sec glass">'
    page += ''.join(f'<div class="wide"><h3>{h}</h3><p>{t}</p></div>' for h, t in deep['attract']) + '</section>'
    page += H('lyubov', 'В любви', f'{nameA} и {nameB} <em>в любви</em>') + '<section class="sec glass">' + duo('love', nameA, nameB) + (''.join(f'<div class="wide"><h3>{h}</h3><p>{t}</p></div>' for h, t in deep['love']) if deep and deep.get('love') else '') + '</section>'
    page += H('ssory', 'Ссоры', f'Из-за чего ссорятся <em>{nameA} и {nameB}</em>') + f'<section class="sec glass">'
    page += duo('fight', f'Как {vb(a, "ссорится", "ссорятся")} {nameA}', f'Как {vb(b, "ссорится", "ссорятся")} {nameB}')
    page += ''.join(f'<div class="wide"><h3>{h}</h3><p>{t}</p></div>' for h, t in deep['friction']) + '</section>'
    page += H('byt', 'В быту', f'{nameA} и {nameB} <em>в быту</em>') + '<section class="sec glass">' + duo('home', nameA, nameB) + (''.join(f'<div class="wide"><h3>{h}</h3><p>{t}</p></div>' for h, t in deep['home']) if deep and deep.get('home') else '') + '</section>'
    if deep:
        page += H('postel', 'В постели', f'{nameA} и {nameB} <em>в постели</em>') + f'<section class="essence glass"><p>{deep["intimacy"]}</p></section>'
        page += H('druzhba', 'Дружба и работа', f'{nameA} и {nameB} <em>в дружбе и работе</em>') + f'<section class="sec glass"><div><h3>В дружбе</h3><p>{deep["friendship"]}</p></div><div><h3>В работе и деньгах</h3><p>{deep["work"]}</p></div></section>'
        page += H('brak', 'В браке', f'{nameA} и {nameB} <em>в браке</em>') + f'<section class="sec glass"><div><h3>Семья, дети и бюджет</h3><p>{deep["marriage"]}</p></div><div><h3>Кризисы и примирение</h3><p>{deep["crisis"]}</p></div></section>'
        page += H('zavoevat', 'Как завоевать', f'Как завоевать <em>{A[2]}' + ('' if same else f' и {B[2]}') + '</em>') + f'<section class="sec glass"><div><h3>Как завоевать {A[2]}</h3><p>{deep["win_a"]}</p></div>' + ('' if same else f'<div><h3>Как завоевать {B[2]}</h3><p>{deep["win_b"]}</p></div>') + '</section>'
        page += H('plusy', 'Плюсы и минусы', f'Плюсы и минусы пары <em>{nameA} и {nameB}</em>') + f'<section class="sec glass"><div><h3>Сильные стороны</h3><ul>' + ''.join(f'<li>{t}</li>' for t in deep['pros']) + '</ul></div><div><h3>Слабые места</h3><ul>' + ''.join(f'<li>{t}</li>' for t in deep['cons']) + '</ul></div></section>'
    # совет
    adv = {0: 'Заводите разные интересы и друзей за пределами пары: вам нужен взгляд со стороны. И смейтесь над общими слабостями раньше, чем они начнут мешать.',
           1: 'Не ждите, что партнер будет понимать вас по умолчанию: объясняйте. Совместимость вы строите сами, зато она ваша.',
           2: 'Берегите легкость: планируйте общее, благодарите вслух и не думайте, что все получится само. Вам достался хороший старт, не упустите его.',
           3: 'Договоритесь о правилах ссоры: без унижений, без «ты всегда», с перерывом, когда горячо. Спорить вы будете, вопрос в том, как.',
           4: 'Вносите новое: поездки, людей, задачи. Паре одной стихии грозит не ссора, а скука.',
           5: 'Не пытайтесь переделать: принимайте, что партнер устроен иначе, и спрашивайте вместо того, чтобы догадываться. Вы разные, и это ваш ресурс.',
           6: 'Помните, что раздражает то, чего вам не хватает. Когда захочется переделать партнера, спросите себя, не этому ли вы у него учитесь.'}[rel_index(a, b)]
    page += H('sovet', 'Совет паре', f'Совет паре <em>{nameA} и {nameB}</em>') + f'<section class="essence glass"><p>{deep["advice"] if deep and deep.get("advice") else adv}</p></section>'
    def faq_for(items):
        out = []
        for q, t in items:
            if 'в процентах' in q:
                t = (f'Спидометр Lunarius посчитал 20 000 случайных пар с такими знаками Солнца: у {st["good"]}% перевешивают гармоничные связи, у {st["tense"]}% напряженные, средний балл {num(st["mean"])} по шкале от −10 до +10. '
                     f'По классической схеме это {REL_NAME[rel_index(a, b)]}, {STARS_RU[r["stars"]]} из пяти на шкале знаков.')
            elif 'по дате рождения' in q: t = DATE_FAQ[(IDX[a] * 5 + IDX[b]) % len(DATE_FAQ)]
            else: t = t.replace(' Точный ответ дает сравнение натальных карт.', '')
            out.append((q, t))
        return out
    if deep:
        page += H('voprosy', 'Вопросы', f'Вопросы о совместимости <em>{G2}</em>') + f'<section id="faq" class="sec glass">' + ''.join(f'<div class="wide"><h3>{q}</h3><p>{t}</p></div>' for q, t in faq_for(deep['faq'])) + '</section>'
    page += CTA
    # другие пары с этими знаками
    others = [s for s in SIGNS if s[0] not in (a, b)][:4]
    page += f'<h2>{nameA} с другими знаками</h2><div class="grid">' + ''.join(
        f'<a class="card glass" href="/compat/{min(a, s[0], key=lambda k: IDX[k])}-{max(a, s[0], key=lambda k: IDX[k])}"><img src="/img/{s[5]}.webp" alt="" loading="lazy"><div><h3>{nameA} + {s[1]}</h3><p>{RELATION[rel_index(a, s[0])]["title"]}</p></div></a>' for s in others) + '</div>'
    def all_pairs(me, name, gen):
        return f'<p style="margin:16px 0 0;font-size:15px;line-height:1.9">Все пары {gen}: ' + ', '.join(
            f'<a href="{pair_url(me, s[0])}" {LINK}>{name} + {s[1]}</a>' for s in SIGNS if not (me == a and s[0] == b) and not (me == b and s[0] == a)) + '.</p>'
    page += all_pairs(a, nameA, A[2])
    if not same: page += all_pairs(b, nameB, B[2])
    def sign_card(S):
        return f'<a class="card glass" href="/signs/{S[0]}"><img src="/img/{S[5]}.webp" alt="" loading="lazy"><div><h3>{S[1]}</h3><p>Характер, женщина и мужчина знака</p></div></a>'
    def asc_card(S):
        return f'<a class="card glass" href="/ascendant/{S[0]}"><img src="/img/{S[5]}.webp" alt="" loading="lazy"><div><h3>Асцендент: {S[1]}</h3><p>Если это ваш восходящий знак</p></div></a>'
    cards = [sign_card(A)] + ([] if same else [sign_card(B)]) + [asc_card(A)] + ([] if same else [asc_card(B)])
    page += '<h2>Подробнее о <em>знаках</em></h2><div class="grid">' + ''.join(cards) + '</div>'
    els = list(dict.fromkeys([A[4], B[4]]))
    page += '<p style="margin:16px 0 0;font-size:15px">Стихии пары: ' + ', '.join(f'<a href="/elements/{EL_SLUG[e]}" {LINK}>{e}</a>' for e in els) + '. Свою карту можно построить на странице <a href="/natal" ' + LINK + '>«Натальная карта»</a>.</p>'
    page += ('<p style="margin:12px 0 0;font-size:15px;line-height:1.9">Читайте также: <a href="/blog/sovmestimost-znakov-zodiaka" ' + LINK + '>как читать совместимость знаков зодиака</a>, '
             '<a href="/blog/sinastriya" ' + LINK + '>что такое синастрия</a>, <a href="/blog/venera-v-sinastrii" ' + LINK + '>Венера в синастрии</a>, '
             '<a href="/blog/luna-v-sinastrii" ' + LINK + '>Луна в синастрии</a>, <a href="/blog/sovmestimost-po-date-rozhdeniya" ' + LINK + '>совместимость по дате рождения</a>.</p>')
    page = page.replace('<!--TOC-->', '<nav class="toc glass" aria-label="Содержание"><b>На странице:</b> ' + ' '.join(f'<a href="#{i}">{t}</a>' for i, t in toc) + '</nav>')
    page += FOOT
    assert 'ё' not in page and '—' not in page, (a, b)
    return page

n = 0
for i, A in enumerate(SIGNS):
    for j in range(i, len(SIGNS)):
        B = SIGNS[j]
        open(os.path.join(OUT, f'{A[0]}-{B[0]}.html'), 'w', encoding='utf-8').write(page_for(A[0], B[0])); n += 1

# индекс: таблица 12x12
idx = HEAD.format(title='Совместимость знаков зодиака: все пары с описанием | Lunarius', desc='Таблица совместимости 12 знаков зодиака: выберите пару и читайте разбор - притяжение, любовь, трение, быт, совет паре. Затем проверьте пару по натальным картам.', path='/compat').replace('<!--METRIKA-->', METRIKA)
idx += '<h1 class="list">Совместимость знаков</h1><p class="lead">Выберите два знака. У каждой пары своя страница: что притягивает, где трение, как вы любите и живете вместе.</p>'
idx += '<div class="glass" style="padding:24px"><div style="overflow-x:auto"><table style="border-collapse:collapse;width:100%;font-size:13px"><tr><th style="position:sticky;left:0;z-index:1;background:#F6F1FB"></th>' + ''.join(f'<th style="padding:8px 4px;font-family:Oswald;font-weight:500;text-transform:uppercase;font-size:12px">{s[1]}</th>' for s in SIGNS) + '</tr>'
STAR_COLOR = {5: '#5B44BD', 4: '#6E56CF', 3: '#9A8CC4', 2: '#E8762E', 1: '#E8762E'}
for A in SIGNS:
    idx += f'<tr><th style="position:sticky;left:0;z-index:1;background:#F6F1FB;text-align:left;padding:8px 6px;font-family:Oswald;font-weight:500;text-transform:uppercase;font-size:12px">{A[1]}</th>'
    for B in SIGNS:
        a, b = sorted([A[0], B[0]], key=lambda k: IDX[k]); st = RELATION[rel_index(a, b)]['stars']
        idx += f'<td style="text-align:center;padding:4px"><a href="/compat/{a}-{b}" title="{A[1]} и {B[1]}" style="display:block;padding:8px 2px;border-radius:10px;background:rgba(255,255,255,.55);text-decoration:none;color:{STAR_COLOR[st]};font-weight:700">{st}★</a></td>'
    idx += '</tr>'
idx += '</table></div><p style="margin:14px 0 0;font-size:13px;color:#6B6380">На телефоне таблицу можно листать вбок. 5★ одна стихия, 4★ дружественные стихии или один знак, 3★ соседи и противоположности, 2★ квадрат и квинконс. Это оценка по знакам Солнца; настоящую совместимость считает спидометр по полным натальным картам.</p></div>'
idx += CTA + FOOT
open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(idx)
print('pairs:', n)

# OG, canonical, JSON-LD
import runpy as _rp, os as _os
_rp.run_path(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'add_meta.py'))
