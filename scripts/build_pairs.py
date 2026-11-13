# Собирает страницы совместимости пар знаков: public/compat/<a>-<b>.html (78 пар) и public/compat/index.html
import os, sys, html, re, itertools
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'docs'))
from pairs_content import SIGNS, TRAITS, RELATION, ESSENCE, essence_key
from signs_content import SIGNS as SIGN_PAGES
OUT = os.path.join(ROOT, 'public/compat'); os.makedirs(OUT, exist_ok=True)
METRIKA = open(os.path.join(ROOT, 'design/metrika.html'), encoding='utf-8').read()
EASY = {s['slug']: s['easy'] for s in SIGN_PAGES}
ELEM_COLOR = {'Огонь': '#F2768A', 'Земля': '#D9A93E', 'Воздух': '#5E8BF2', 'Вода': '#6E56CF'}
IDX = {s[0]: i for i, s in enumerate(SIGNS)}

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
@media (max-width:640px){{.pair{{grid-template-columns:1fr 1fr;padding:20px}}.plus{{display:none}}.pname{{font-size:22px}}.verdict,.essence{{padding:24px 20px}}}}
</style>'''
HEAD = HEAD.replace('</style>', EXTRA_CSS, 1)
FOOT = '''<footer><span>© 2026 Lunarius.ru · <a href="mailto:info@lunarius.ru">info@lunarius.ru</a> · <a href="/privacy">Документы</a></span><span>Сайт носит развлекательный характер и не заменяет консультацию специалиста</span></footer>
</div>
</body>
</html>
'''
CTA = '<div class="cta"><b>Знака Солнца мало: у каждого из вас еще девять планет.<br>Прокатитесь на спидометре совместимости по натальным картам</b><a href="/">Запустить спидометр</a></div>'

def rel_index(a, b):
    d = abs(IDX[a] - IDX[b]); return min(d, 12 - d)

def cap(s): return s[0].upper() + s[1:]

def page_for(a, b):
    A = SIGNS[IDX[a]]; B = SIGNS[IDX[b]]
    ta, tb = TRAITS[a], TRAITS[b]
    r = RELATION[rel_index(a, b)]
    same = a == b
    nameA, nameB = A[1], B[1]
    title = f'Совместимость {A[2]} и {B[2]}: любовь, быт, конфликты и совет паре | Lunarius'
    desc = f'{nameA} и {nameB}: подходят ли друг другу в любви и браке, что притягивает, где трение, как ссорятся и живут вместе. Проверьте пару по натальным картам на спидометре совместимости.'
    page = HEAD.format(title=html.escape(title), desc=html.escape(desc), path=f'/compat/{a}-{b}').replace('<!--METRIKA-->', METRIKA)
    page += f'<p class="crumbs"><a href="/">Главная</a> · <a href="/compat">Совместимость знаков</a></p>'
    page += (f'<section class="pair glass"><div><img src="/img/{A[5]}.webp" alt="{nameA}"><div class="pname">{nameA}</div><div class="pel" style="color:{ELEM_COLOR[A[4]]}">{A[4]}</div></div>'
             f'<div class="plus">+</div><div><img src="/img/{B[5]}.webp" alt="{nameB}"><div class="pname">{nameB}</div><div class="pel" style="color:{ELEM_COLOR[B[4]]}">{B[4]}</div></div></section>')
    page += f'<section class="verdict glass"><div class="stars">{"★" * r["stars"]}{"☆" * (5 - r["stars"])}</div><div style="flex:1;min-width:260px"><h2>{r["title"]}</h2><p>{r["text"]}</p></div></section>'
    ess = ESSENCE.get(essence_key(a, b))
    if ess: page += f'<h2>{nameA} и <em>{nameB}</em>: суть пары</h2><section class="essence glass"><p>{ess}</p></section>'
    # притяжение и трение
    page += f'<h2>Что <em>притягивает</em></h2><section class="sec glass">'
    page += f'<div><h3>Что дает {nameA}</h3><p>{cap(ta["gives"])}. {cap(ta["teaches"])} - этому {nameA} учит {B[2]}.</p></div>'
    page += f'<div><h3>Что дает {nameB}</h3><p>{cap(tb["gives"])}. {cap(tb["teaches"])} - этому {nameB} учит {A[2]}.</p></div>'
    page += f'<div class="wide"><h3>Что каждому нужно</h3><p>{nameA} ждет от партнера {ta["needs"]}. {nameB} ждет {tb["needs"]}. ' + (
        'Запросы похожи, поэтому понимать друг друга легко.' if same else 'Насколько эти ожидания совпадают, и есть суть вашей совместимости: там, где один дает именно то, чего ждет другой, пара держится сама.') + '</p></div></section>'
    page += f'<h2>В <em>любви</em></h2><section class="sec glass"><div><h3>{nameA}</h3><p>{cap(ta["love"])}.</p></div><div><h3>{nameB}</h3><p>{cap(tb["love"])}.</p></div></section>'
    page += f'<h2>Где <em>трение</em></h2><section class="sec glass">'
    page += f'<div><h3>Как ссорится {nameA}</h3><p>{cap(ta["fight"])}.</p></div><div><h3>Как ссорится {nameB}</h3><p>{cap(tb["fight"])}.</p></div>'
    page += f'<div class="wide"><h3>Что раздражает</h3><p>{nameA}: партнера могут раздражать {ta["irritates"]}. {nameB}: партнера могут раздражать {tb["irritates"]}. Это не недостатки, а обратная сторона того, за что вы друг друга выбрали.</p></div></section>'
    page += f'<h2>В <em>быту</em></h2><section class="sec glass"><div><h3>{nameA}</h3><p>{cap(ta["home"])}.</p></div><div><h3>{nameB}</h3><p>{cap(tb["home"])}.</p></div></section>'
    # совет
    adv = {0: 'Заводите разные интересы и друзей за пределами пары: вам нужен взгляд со стороны. И смейтесь над общими слабостями раньше, чем они начнут мешать.',
           1: 'Не ждите, что партнер будет понимать вас по умолчанию: объясняйте. Ваша совместимость строится руками, зато она ваша.',
           2: 'Берегите легкость: планируйте общее, благодарите вслух и не считайте, что все само. Вам достался хороший старт, не упустите его.',
           3: 'Договоритесь о правилах ссоры: без унижений, без «ты всегда», с перерывом, когда горячо. Спорить вы будете, вопрос в том, как.',
           4: 'Вносите новое: поездки, людей, задачи. Самая легкая пара зодиака чаще всего рискует не поссориться, а заскучать.',
           5: 'Не пытайтесь переделать: принимайте, что партнер устроен иначе, и спрашивайте вместо того, чтобы догадываться. Вы разные, и это ваш ресурс.',
           6: 'Помните, что раздражает именно то, чего вам не хватает. Когда захочется переделать партнера, спросите себя, не этому ли вы у него учитесь.'}[rel_index(a, b)]
    page += f'<h2>Совет <em>паре</em></h2><section class="essence glass"><p>{adv}</p></section>'
    page += CTA
    # другие пары с этими знаками
    others = [s for s in SIGNS if s[0] not in (a, b)][:4]
    page += f'<h2>{nameA} с другими знаками</h2><div class="grid">' + ''.join(
        f'<a class="card glass" href="/compat/{min(a, s[0], key=lambda k: IDX[k])}-{max(a, s[0], key=lambda k: IDX[k])}"><img src="/img/{s[5]}.webp" alt="" loading="lazy"><div><h3>{nameA} + {s[1]}</h3><p>{RELATION[rel_index(a, s[0])]["title"]}</p></div></a>' for s in others) + '</div>'
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
