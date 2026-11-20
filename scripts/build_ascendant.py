# Собирает страницы /ascendant из docs/ascendant_content.py в public/ascendant/<slug>.html + public/ascendant/index.html
# Общая часть <head>, стили и шапка берутся из public/elements/index.html, чтобы страницы выглядели одинаково.
import os, sys, json, html, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'docs'))
from ascendant_content import SIGNS, HUB
OUT = os.path.join(ROOT, 'public/ascendant'); os.makedirs(OUT, exist_ok=True)
_el = open(os.path.join(ROOT, 'public/elements/index.html'), encoding='utf-8').read()
_el = re.sub(r'<!--meta:start-->.*?<!--meta:end-->\n?', '', _el, flags=re.S)  # свои OG и canonical страница получает ниже
SHARED = _el[_el.index('<meta name="viewport"'):_el.index('</header>') + len('</header>')]  # от viewport до </header>
SHARED = re.sub(r'<title>.*?</title>\n?|<meta name="description"[^>]*>\n?|<link rel="canonical"[^>]*>\n?|<meta property="og:(?:title|description|url)"[^>]*>\n?', '', SHARED)
assert SHARED.startswith('<meta name="viewport"') and SHARED.endswith('</header>')
P1 = '<!DOCTYPE html>\n<html lang="ru">\n<head>\n<meta charset="utf-8">'
TAIL = '</div>\n</body>\n</html>\n'
FOOT = '<footer><span>© 2026 Lunarius.ru · <a href="mailto:info@lunarius.ru">info@lunarius.ru</a> · <a href="/privacy">Документы</a></span><span>Сайт носит развлекательный характер и не заменяет консультацию специалиста</span></footer>'
ELEM_COLOR = {'Огонь': '#F2768A', 'Земля': '#D9A93E', 'Воздух': '#5E8BF2', 'Вода': '#6E56CF'}
BY = {s['slug']: s for s in SIGNS}
e = html.escape

def ld(obj): return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + '</script>'
def crumbs_ld(items):
    return ld({'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': 'https://lunarius.ru' + u} for i, (n, u) in enumerate(items)]})
def head(title, og, desc, path, extra):
    return '\n'.join([P1, f'<title>{e(title)}</title>', f'<meta name="description" content="{e(desc)}">',
        f'<link rel="canonical" href="https://lunarius.ru{path}">', ] + extra + [SHARED])

# ---------- страницы знаков
import ascendant_texts_1, ascendant_texts_2, ascendant_texts_3
TEXTS = {}
for m in (ascendant_texts_1, ascendant_texts_2, ascendant_texts_3): TEXTS.update(m.TEXTS)
EL_LOC = [('fire', 'Солнце в Огне'), ('earth', 'Солнце в Земле'), ('air', 'Солнце в Воздухе'), ('water', 'Солнце в Воде')]
P2 = '<p style="margin-top:12px">'
def ul(items): return '<ul>' + ''.join(f'<li>{x}</li>' for x in items) + '</ul>'

# ---------- подробные страницы (docs/ascendant_deep_<slug>.py)
import glob, importlib, math
DEEP = {}
for _f in sorted(glob.glob(os.path.join(ROOT, 'docs', 'ascendant_deep_*.py'))):
    DEEP.update(importlib.import_module(os.path.basename(_f)[:-3]).D)
def rise_minutes(i, lat=55.75):
    eps, phi = math.radians(23.44), math.radians(lat)
    def oa(lon):
        l = math.radians(lon); ra = math.atan2(math.sin(l) * math.cos(eps), math.cos(l))
        dec = math.asin(math.sin(eps) * math.sin(l)); return math.degrees(ra - math.asin(math.tan(dec) * math.tan(phi))) % 360
    return round(((oa(i * 30 + 30) - oa(i * 30)) % 360) / 15 * 60 / 1.0027)
def dur(m): return f'{m} мин' if m < 60 else (f'{m // 60} ч {m % 60} мин' if m % 60 >= 10 else f'{m // 60} ч')
BORN = {0: 'около восхода Солнца', 1: 'в последние часы перед рассветом', 2: 'глубокой ночью, после полуночи', 3: 'около полуночи',
        4: 'поздним вечером', 5: 'вечером, после заката', 6: 'около заката', 7: 'ближе к вечеру', 8: 'во второй половине дня',
        9: 'около полудня', 10: 'в первой половине дня', 11: 'утром, вскоре после восхода'}
DEEP_CSS = ('<style>.toc{margin:28px 0 0;padding:20px 28px;font-size:14.5px;line-height:2.3}.toc b{margin-right:8px;font-family:\'Oswald\',sans-serif;font-weight:500;text-transform:uppercase;letter-spacing:.02em}'
            '.toc a{display:inline-block;margin:0 6px 0 0;padding:0 12px;border-radius:999px;background:rgba(255,255,255,.7);color:#5B44BD;text-decoration:none;line-height:2;white-space:nowrap}h2[id]{scroll-margin-top:16px}'
            '.sun-when{margin:0 0 6px!important;font-size:13px!important;color:#6B6380}.sec .sm{margin-top:6px;font-size:13.5px}'
            '.tbl{padding:20px 24px;margin:0;overflow-x:auto}.tbl table{border-collapse:collapse;width:100%;font-size:15px}.tbl th,.tbl td{padding:7px 10px;text-align:left;border-bottom:1px solid rgba(110,86,207,.14)}'
            '.faq{padding:12px 44px}.faq details{padding:18px 0;border-bottom:1px solid rgba(110,86,207,.18)}.faq details:last-child{border-bottom:0}.faq summary{cursor:pointer;font-family:\'Oswald\',sans-serif;font-size:20px;font-weight:500;text-transform:uppercase}.faq p{margin:10px 0 0;font-size:15.5px}'
            '@media (max-width:640px){.faq{padding:6px 20px}}</style>')
def sec(cards, cls=''):
    return '<div class="sec glass">' + ''.join(f'<div{cls}><h3>{h}</h3><p>{t}</p></div>' for h, t in cards) + '</div>'
PL = ['Овны', 'Тельцы', 'Близнецы', 'Раки', 'Львы', 'Девы', 'Весы', 'Скорпионы', 'Стрельцы', 'Козероги', 'Водолеи', 'Рыбы']
TIME_SUN = {0: 'около восхода', 9: 'около полудня', 6: 'около заката', 3: 'около полуночи'}
def fill_defaults(i, s, x):
    t = TEXTS[s['slug']]; d = BY[s['desc']]; name = 'Асцендент ' + s['loc']
    x = dict(x)
    if 'intro_lead' in x: x.setdefault('intro', [x['intro_lead']] + list(t['intro']))
    x.setdefault('look', [('Внешность', t['look'][0]), ('Стиль и манера', t['look'][1])])
    for k in ('behave', 'marks', 'plus', 'minus', 'compat', 'age', 'tips'): x.setdefault(k, t[k])
    x.setdefault('love', t['love'][0]); x.setdefault('descendant', t['love'][1])
    x.setdefault('work', [('Профессии', t['work'][0]), ('Деньги и стиль работы', t['work'][1])])
    when = '; '.join(f'{PL[(i + k) % 12]} {v}' for k, v in [(0, TIME_SUN[0]), (-3, TIME_SUN[9]), (-6, TIME_SUN[6]), (3, TIME_SUN[3])])
    faq = list(x.get('faq', []))
    faq += [(f'Какой Десцендент при Асценденте {s["loc"]}?', f'Десцендент всегда в противоположном знаке, при Асценденте {s["loc"]} он {d["loc"]}. Это начало седьмого дома, дома партнерства: он описывает людей, которых вы притягиваете и которые вас дополняют.'),
            (f'Какая планета управляет картой при Асценденте {s["loc"]}?', f'{s["ruler"]}. Знак и дом, где эта планета стоит в вашей натальной карте, показывают, куда уходит ваша главная энергия.'),
            (f'В какое время рождаются люди с Асцендентом {s["loc"]}?', f'Зависит от даты. Асцендент совпадает со знаком Солнца на восходе и дальше переходит в следующие знаки, в среднем каждые 2 часа. Асцендент {s["loc"]} получают: {when}. Точно его покажет только расчет по времени и городу.'),
            (f'Как узнать, есть ли у меня Асцендент {s["loc"]}?', 'Введите дату, точное время и город рождения в калькулятор на странице «Асцендент». Расчет бесплатный и занимает несколько секунд.')] if 'faq_full' not in x else []
    x['faq'] = x.get('faq_full', faq)
    return x
def deep_asc(i, s, x):
    x = fill_defaults(i, s, x)
    d = BY[s['desc']]; name = 'Асцендент ' + s['loc']; col = ELEM_COLOR[s['element']]
    others = ', '.join(f'<a href="/ascendant/{o["slug"]}">{o["loc"]}</a>' for o in SIGNS if o is not s)
    toc = [('vneshnost', 'Внешность'), ('harakter', 'Характер'), ('zhenshchina', 'У женщины'), ('muzhchina', 'У мужчины'), ('lyubov', 'Любовь'),
           ('solnce', 'Со знаками Солнца'), ('rebenok', 'Ребенок'), ('rabota', 'Работа'), ('vozrast', 'С возрастом'), ('voprosy', 'Вопросы')]
    b = f'<p class="crumbs"><a href="/">Главная</a> · <a href="/ascendant">Асцендент</a> · {s["loc"][0].upper() + s["loc"][1:]}</p>'
    b += f'<section class="hero glass"><img src="/img/{s["img"]}.webp" alt="{name}"><div><h1 style="font-size:56px">{name}</h1>'
    b += (f'<div class="meta"><span>Стихия: <b><a href="/elements/{s["el"]}" style="color:{col};text-decoration:none">{s["element"]}</a></b></span>'
          f'<span>Управитель карты: <b>{s["ruler"]}</b></span><span>Десцендент: <b>{d["loc"]}</b></span><span>Восходит в Москве: <b>{dur(rise_minutes(i))}</b></span></div>')
    b += ''.join(f'<p class="intro"{" style=\"margin-top:12px\"" if k else ""}>{p}</p>' for k, p in enumerate(x['intro'])) + '</div></section>'
    b += '<nav class="toc glass" aria-label="Содержание"><b>На странице:</b> ' + ' '.join(f'<a href="#{a}">{t}</a>' for a, t in toc) + '</nav>'
    b += f'<h2 id="vneshnost">Внешность <em>и стиль</em></h2>' + sec(x['look'])[:-6] + f'<div class="wide"><h3>Как узнать человека с Асцендентом {s["loc"]}</h3>{ul(x["marks"])}</div></div>'
    b += f'<h2 id="harakter">Характер <em>и поведение</em></h2><div class="sec glass"><div class="wide"><p>{x["behave"][0]}</p>{P2}{x["behave"][1]}</p></div><div><h3>Сильные стороны</h3>{ul(x["plus"])}</div><div><h3>Слабые стороны</h3>{ul(x["minus"])}</div></div>'
    b += f'<h2 id="zhenshchina">{name} <em>у женщины</em></h2>' + sec(x['woman'])
    b += f'<h2 id="muzhchina">{name} <em>у мужчины</em></h2>' + sec(x['man'])
    b += (f'<h2 id="lyubov">Любовь <em>и Десцендент</em></h2><div class="sec glass"><div><h3>Как любит</h3><p>{x["love"]}</p></div>'
          f'<div><h3>Десцендент {d["loc"]}</h3><p>{x["descendant"]}</p></div><div class="wide"><h3>Совместимость по Асценденту</h3><p>{x["compat"]}</p></div></div>')
    cards = ''
    for j, o in enumerate(SIGNS):
        k = (j - i) % 12
        cards += (f'<div><h3>{o["name"]} с Асцендентом {s["loc"]}</h3><p class="sun-when">Рождение {BORN[k]}, Солнце в {k + 1} доме</p>'
                  f'<p>{x["sun"][o["slug"]]}</p></div>')
    b += (f'<h2 id="solnce">{name} <em>и знак Солнца</em></h2><p class="lead" style="margin:-6px 0 18px;max-width:820px">Асцендент показывает, каким вас видят, а Солнце, то есть знак зодиака по дате рождения, - кто вы внутри. '
          f'Ниже 12 сочетаний: знак Солнца с Асцендентом {s["loc"]}. Время суток указано примерно, дом считается от Асцендента по целым знакам.</p><div class="sec glass">{cards}</div>')
    b += f'<h2 id="rebenok">Ребенок с Асцендентом <em>{s["loc"]}</em></h2><div class="sec glass"><div class="wide"><p>{x["child"]}</p></div></div>'
    b += f'<h2 id="rabota">Работа <em>и деньги</em></h2>' + sec(x['work'])
    b += (f'<h2 id="vozrast">С возрастом <em>и советы</em></h2><div class="sec glass"><div><h3>Как меняется с годами</h3><p>{x["age"]}</p></div><div><h3>Три совета</h3>{ul(x["tips"])}</div>'
          f'<div class="wide"><h3>Управитель карты</h3><p>Управитель восходящего знака считается управителем всей натальной карты. При Асценденте {s["loc"]} это {s["ruler"]}: знак и дом, в которых стоит эта планета, показывают, куда уходит ваша главная энергия. Найти ее положение можно в <a href="/natal">натальной карте</a>.</p></div></div>')
    b += f'<h2 id="voprosy">Частые <em>вопросы</em></h2><section id="faq" class="sec glass">' + ''.join(f'<div class="wide"><h3>{q}</h3><p>{a}</p></div>' for q, a in x['faq']) + '</section>'
    b += f'<div class="cta"><b>Не уверены в своем Асценденте?<br>Рассчитайте по дате, времени и городу</b><a href="/ascendant">Рассчитать Асцендент</a></div>'
    b += f'<p style="margin:16px 0 0;font-size:14px;color:#6B6380">Асцендент и знак зодиака по дате рождения - разные вещи. О Солнце {s["loc"]} читайте на странице <a href="/signs/{s["slug"]}">знака {s["name"]}</a>, а о парах знака - в <a href="/compat">таблице совместимости</a>. Статьи: <a href="/blog/ascendent">что такое Асцендент</a>, <a href="/blog/doma-v-natalnoy-karte">дома в натальной карте</a>, <a href="/blog/aspekty-v-natalnoy-karte">аспекты в натальной карте</a>. Асцендент в других знаках: {others}.</p>'
    b += FOOT
    page = head(x['title'], name, x['desc'], f'/ascendant/{s["slug"]}', [crumbs_ld([('Главная', '/'), ('Асцендент', '/ascendant'), (name, f'/ascendant/{s["slug"]}')]), DEEP_CSS]) + '\n' + b + '\n' + TAIL
    open(os.path.join(OUT, s['slug'] + '.html'), 'w', encoding='utf-8').write(page)
for _i, s in enumerate(SIGNS):
    if s['slug'] in DEEP:
        deep_asc(_i, s, DEEP[s['slug']]); continue
    x = TEXTS[s['slug']]
    col = ELEM_COLOR[s['element']]; d = BY[s['desc']]; name = 'Асцендент ' + s['loc']
    title = f"{name}: внешность, характер и любовь"
    if len(title) <= 49: title += " | Lunarius"
    og = f"{name}: внешность, характер, любовь"
    desc = f"Узнайте, что дает {name}: внешность, характер, любовь, у женщин и мужчин, сочетание с Солнцем. Рассчитайте свой Асцендент онлайн бесплатно."
    others = ', '.join(f'<a href="/ascendant/{o["slug"]}">{o["loc"]}</a>' for o in SIGNS if o is not s)
    b = f'<p class="crumbs"><a href="/">Главная</a> · <a href="/ascendant">Асцендент</a></p>'
    b += f'<section class="hero glass"><img src="/img/{s["img"]}.webp" alt="{name}"><div><h1 style="font-size:56px">{name}</h1>'
    b += f'<div class="meta"><span>Стихия: <b><a href="/elements/{s["el"]}" style="color:{col};text-decoration:none">{s["element"]}</a></b></span><span>Управитель карты: <b>{s["ruler"]}</b></span><span>Десцендент: <b>{d["loc"]}</b></span></div>'
    b += f'<p class="intro">{x["intro"][0]}</p><p class="intro" style="margin-top:12px">{x["intro"][1]}</p></div></section>'
    b += f'<h2>Внешность и <em>первое впечатление</em></h2><div class="sec glass"><div><h3>Внешность</h3><p>{x["look"][0]}</p></div><div><h3>Стиль и манера</h3><p>{x["look"][1]}</p></div><div class="wide"><h3>Как узнать человека с Асцендентом {s["loc"]}</h3>{ul(x["marks"])}</div></div>'
    b += f'<h2>Характер и <em>поведение</em></h2><div class="sec glass"><div class="wide"><p>{x["behave"][0]}</p>{P2}{x["behave"][1]}</p></div><div><h3>Сильные стороны</h3>{ul(x["plus"])}</div><div><h3>Слабые стороны</h3>{ul(x["minus"])}</div></div>'
    b += f'<h2>{name} <em>в любви</em></h2><div class="sec glass"><div><h3>Как любит</h3><p>{x["love"][0]}</p></div><div><h3>Десцендент {d["loc"]}</h3><p>{x["love"][1]}</p></div><div class="wide"><h3>Совместимость</h3><p>{x["compat"]}</p></div></div>'
    b += f'<h2>У женщины и <em>у мужчины</em></h2><div class="sec glass"><div><h3>{name} у женщины</h3><p>{x["woman"]}</p></div><div><h3>{name} у мужчины</h3><p>{x["man"]}</p></div></div>'
    b += f'<h2>Работа и <em>деньги</em></h2><div class="sec glass"><div><h3>Профессии</h3><p>{x["work"][0]}</p></div><div><h3>Деньги и стиль работы</h3><p>{x["work"][1]}</p></div></div>'
    b += f'<h2>Асцендент и <em>знак Солнца</em></h2><p class="lead" style="margin:-6px 0 18px;max-width:820px">Асцендент показывает, каким вас видят, а Солнце - кто вы внутри. Один и тот же знак Солнца с разным Асцендентом дает очень разных людей. Вот как Асцендент {s["loc"]} сочетается с Солнцем в каждой стихии.</p><div class="sec glass">' + ''.join(f'<div><h3>{lbl}</h3><p>{x["sun"][k]}</p></div>' for k, lbl in EL_LOC) + '</div>'
    b += f'<h2>С возрастом и <em>советы</em></h2><div class="sec glass"><div><h3>Как меняется с годами</h3><p>{x["age"]}</p></div><div><h3>Три совета</h3>{ul(x["tips"])}</div>'
    b += f'<div class="wide"><h3>Управитель карты</h3><p>Управитель восходящего знака считается управителем всей натальной карты. При Асценденте {s["loc"]} это {s["ruler"]}: знак и дом, в которых стоит эта планета, показывают, куда уходит ваша главная энергия и в какой сфере жизни вы проявляетесь ярче всего. Найти ее положение можно в <a href="/natal">натальной карте</a>.</p></div></div>'
    b += f'<div class="cta"><b>Не уверены в своем Асценденте?<br>Рассчитайте по дате, времени и городу</b><a href="/ascendant">Рассчитать Асцендент</a></div>'
    b += f'<p style="margin:16px 0 0;font-size:14px;color:#6B6380">Асцендент и знак зодиака по дате рождения - разные вещи. О Солнце {s["loc"]} читайте на странице <a href="/signs/{s["slug"]}">знака {s["name"]}</a>, а о парах знака - в <a href="/compat">таблице совместимости</a>. Статьи: <a href="/blog/ascendent">что такое Асцендент</a>, <a href="/blog/doma-v-natalnoy-karte">дома в натальной карте</a>, <a href="/blog/aspekty-v-natalnoy-karte">аспекты в натальной карте</a>. Асцендент в других знаках: {others}.</p>'
    b += FOOT
    page = head(title, og, desc, f'/ascendant/{s["slug"]}', [crumbs_ld([('Главная', '/'), ('Асцендент', '/ascendant'), (name, f'/ascendant/{s["slug"]}')])]) + '\n' + b + '\n' + TAIL
    open(os.path.join(OUT, s['slug'] + '.html'), 'w', encoding='utf-8').write(page)

# ---------- хаб с калькулятором
CSS = '''<style>
.calc{padding:32px 36px;display:flex;flex-direction:column;gap:18px}
.calc .row{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}
.calc .f{display:flex;flex-direction:column;gap:6px;position:relative}
.calc label{font-size:12px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:#5E5675}
.calc input[type=text],.calc input[type=date],.calc input[type=time]{font-family:inherit;font-size:15px;color:#2A2340;padding:0 14px;height:50px;border:1px solid rgba(255,255,255,.9);border-radius:999px;background:rgba(255,255,255,.55);box-shadow:inset 0 1px 0 #fff,0 6px 16px rgba(91,68,189,.1);width:100%;-webkit-appearance:none;appearance:none;min-width:0;text-align:left}
.calc .agree{display:flex;align-items:flex-start;gap:10px;text-transform:none;letter-spacing:0;font-weight:500;font-size:13px}
.calc .agree input{flex:0 0 auto;width:20px;height:20px;margin:0;accent-color:#6E56CF}
.btn{align-self:center;margin-top:8px;min-height:58px;padding:0 48px;border:0;border-radius:999px;background:#2A2340;color:#FBF8F3;font-family:'Oswald',sans-serif;font-size:20px;font-weight:500;letter-spacing:.06em;text-transform:uppercase;cursor:pointer}
.btn:disabled{opacity:.6}
#form-error{align-self:center;margin:0;padding:10px 16px;border-radius:12px;background:#FDE9DC;color:#A8461A;font-size:14px;font-weight:600}
.city-list{position:absolute;left:0;right:0;top:100%;z-index:30;margin-top:4px;max-height:260px;overflow:auto;background:#fff;border:1px solid #D8CDEE;border-radius:14px;box-shadow:0 18px 40px rgba(75,58,158,.18)}
.city-item{display:block;width:100%;min-height:44px;padding:10px 14px;border:0;background:none;text-align:left;font:inherit;font-size:14px;color:#2A2340;cursor:pointer}
.city-item:hover,.city-item:focus{background:#F3ECFF;outline:none}
.res{margin-top:24px;padding:32px 36px}
.res .who{font-size:12px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:#5B44BD}
.res .big{font-family:'Oswald',sans-serif;font-size:56px;font-weight:600;line-height:1.05;text-transform:uppercase;margin:4px 0 10px}
.res .big small{font-size:20px;font-weight:400;color:#6B6380;margin-left:10px;text-transform:none}
.res p{margin:0 0 12px;font-size:16px}
.res .more{display:flex;flex-wrap:wrap;gap:12px;margin-top:8px}
.res .more a{display:inline-flex;align-items:center;min-height:46px;padding:0 22px;border-radius:999px;background:#2A2340;color:#FBF8F3;text-decoration:none;font-weight:700;font-size:14px}
.res .more a.alt{background:rgba(255,255,255,.7);color:#2A2340}
.faq{padding:12px 44px}
.faq details{padding:18px 0;border-bottom:1px solid rgba(110,86,207,.18)}
.faq details:last-child{border-bottom:0}
.faq summary{cursor:pointer;font-family:'Oswald',sans-serif;font-size:20px;font-weight:500;text-transform:uppercase}
.faq p{margin:10px 0 0;font-size:15.5px}
@media (max-width:640px){.calc,.res{padding:22px 18px}.calc .row{grid-template-columns:1fr}.res .big{font-size:40px}.faq{padding:6px 20px}}
</style>'''
JS = '''<script>
(function(){
var $=function(id){return document.getElementById(id);};
var cityId=null;
var SLUG={%s};
var LOC={%s};
var input=$('c1'),box=document.createElement('div'),timer;
box.className='city-list';box.setAttribute('role','listbox');box.hidden=true;input.parentNode.appendChild(box);
input.addEventListener('input',function(){
cityId=null;clearTimeout(timer);
var q=input.value.trim();
if(q.length<2){box.hidden=true;return;}
timer=setTimeout(function(){
fetch('/api/cities?q='+encodeURIComponent(q)).then(function(r){return r.json();}).then(function(list){
box.innerHTML='';
list.forEach(function(c){
var b=document.createElement('button');
b.type='button';b.className='city-item';b.textContent=c.label;
b.addEventListener('click',function(){input.value=c.name;cityId=c.id;box.hidden=true;});
box.appendChild(b);
});
box.hidden=list.length===0;
}).catch(function(){box.hidden=true;});
},200);
});
document.addEventListener('click',function(e){if(!box.contains(e.target)&&e.target!==input)box.hidden=true;});
function esc(t){var d=document.createElement('div');d.textContent=t==null?'':String(t);return d.innerHTML;}
var btn=$('run'),err=$('form-error'),res=$('result');
function showError(t){err.textContent=t;err.hidden=!t;}
function render(r){
var a=r.big3&&r.big3.asc;
if(!a){showError('Не удалось определить Асцендент: проверьте время рождения');return;}
var h='<span class="who">Ваш Асцендент</span><div class="big">'+esc(a.sign)+'<small>'+esc(a.degree)+'</small></div><p>'+esc(a.text)+'</p>';
h+='<p>Большая тройка вашей карты: Солнце - '+esc(r.big3.sun.sign)+', Луна - '+esc(r.big3.moon.sign)+', Асцендент - '+esc(a.sign)+'.</p><div class="more">';
if(SLUG[a.sign])h+='<a href="/ascendant/'+SLUG[a.sign]+'">Подробнее: Асцендент '+esc(LOC[a.sign])+'</a>';
h+='<a class="alt" href="/natal">Построить всю натальную карту</a></div>';
res.innerHTML=h;res.hidden=false;res.scrollIntoView({behavior:'smooth',block:'start'});
}
btn.addEventListener('click',function(){
showError('');try{ym(114224190,'reachGoal','asc_click');}catch(e){}
var p={name:'',date:$('d1').value,time:$('t1').value||null,cityId:cityId};
if(!p.date)return showError('Укажите дату рождения');
if(!p.time)return showError('Укажите время рождения: без него Асцендент не рассчитать');
if(p.cityId==null)return showError('Выберите город рождения из списка подсказок');
if(!$('agree').checked)return showError('Отметьте согласие на обработку персональных данных');
btn.disabled=true;var old=btn.textContent;btn.textContent='Считаем...';
fetch('/api/natal',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({person:p,consent:true})})
.then(function(r){return r.json().then(function(j){if(!r.ok)throw new Error(j.error||'Ошибка');return j;});})
.then(function(j){try{ym(114224190,'reachGoal','asc_done');}catch(e){}render(j);})
.catch(function(e){showError(e.message);})
.finally(function(){btn.disabled=false;btn.textContent=old;});
});
})();
</script>''' % (','.join(f"'{s['name']}':'{s['slug']}'" for s in SIGNS), ','.join(f"'{s['name']}':'{s['loc']}'" for s in SIGNS))

b = '<p class="crumbs"><a href="/">Главная</a> · Асцендент</p><h1 class="list">Рассчитать <em style="font-style:normal;color:#6E56CF">Асцендент</em> по дате рождения</h1>'
b += f'<p class="lead" style="max-width:820px">{HUB["lead"]}</p>'
b += '<form class="calc glass" id="asc-form" onsubmit="return false"><div class="row"><div class="f"><label for="d1">Дата рождения</label><input id="d1" type="date"></div><div class="f"><label for="t1">Время рождения</label><input id="t1" type="time"></div><div class="f"><label for="c1">Город рождения</label><input id="c1" type="text" placeholder="Начните вводить город" autocomplete="off"></div></div>'
b += '<label class="agree" for="agree"><input id="agree" type="checkbox"><span>Я соглашаюсь с <a href="/privacy#policy" target="_blank">Политикой конфиденциальности</a> и даю <a href="/privacy#consent" target="_blank">согласие на обработку персональных данных</a></span></label>'
b += '<p id="form-error" role="alert" hidden></p><button id="run" type="button" class="btn">Рассчитать Асцендент</button></form><div class="res glass" id="result" hidden></div>'
from ascendant_hub_deep import H as HD
b = b.replace(HUB['lead'], HD['lead'])
b += '<nav class="toc glass" aria-label="Содержание"><b>На странице:</b> ' + ' '.join(f'<a href="#{a}">{t}</a>' for a, t in [('chto-takoe', 'Что такое Асцендент'), ('kak-rasschitat', 'Как рассчитать'), ('bez-vremeni', 'Без времени рождения'), ('po-vremeni', 'Асцендент по времени рождения'), ('bolshaya-troyka', 'Солнце, Луна, Асцендент'), ('descendent', 'Десцендент и управитель'), ('v-znakah', '12 знаков'), ('voprosy', 'Вопросы')]) + '</nav>'
b += '<h2 id="chto-takoe">Что такое Асцендент <em>простыми словами</em></h2>' + sec(HD['simple'])
b += '<h2 id="kak-rasschitat">Как рассчитать Асцендент <em>по дате рождения</em></h2>' + sec(HD['how'])
b += '<h2 id="bez-vremeni">Асцендент <em>без времени рождения</em></h2><div class="sec glass"><div class="wide">' + ''.join(f'<p{" style=\"margin-top:12px\"" if k else ""}>{p}</p>' for k, p in enumerate(HD['notime'])) + '</div></div>'
_rows = ''.join(f'<tr><td><a href="/ascendant/{o["slug"]}">{o["name"]}</a></td><td>{dur(rise_minutes(j))}</td><td>{dur(rise_minutes(j, 59.94))}</td></tr>' for j, o in enumerate(SIGNS))
b += (f'<h2 id="po-vremeni">Асцендент <em>по времени рождения</em></h2><p class="lead" style="margin:-6px 0 18px;max-width:820px">{HD["time_intro"]}</p>'
      f'<div class="tbl glass"><table><tr><th>Восходящий знак</th><th>Восходит в Москве</th><th>Восходит в Санкт-Петербурге</th></tr>{_rows}</table></div>'
      f'<p class="lead" style="margin:18px 0 0;max-width:820px">{HD["time_note"]}</p>')
b += '<h2 id="bolshaya-troyka">Асцендент, <em>Солнце и Луна</em></h2>' + sec(HD['big3'])[:-6] + f'<div class="wide"><p>{HD["big3_note"]}</p></div></div>'
_rows = ''.join(f'<tr><td><a href="/ascendant/{o["slug"]}">Асцендент {o["loc"]}</a></td><td><a href="/ascendant/{o["desc"]}">{BY[o["desc"]]["name"]}</a></td><td>{o["ruler"]}</td></tr>' for o in SIGNS)
b += (f'<h2 id="descendent">Десцендент <em>и управитель карты</em></h2><p class="lead" style="margin:-6px 0 18px;max-width:820px">{HD["desc_text"]}</p>'
      f'<div class="tbl glass"><table><tr><th>Асцендент</th><th>Десцендент</th><th>Управитель карты</th></tr>{_rows}</table></div>')
b += '<h2 id="v-znakah">Асцендент <em>в знаках</em></h2><div class="grid">' + ''.join(
    f'<a class="card glass" href="/ascendant/{s["slug"]}"><img src="/img/{s["img"]}.webp" alt="Асцендент {s["loc"]}" loading="lazy"><div><h3>{s["loc"][0].upper() + s["loc"][1:]}</h3><p>Управитель: {s["ruler"].split(" (")[0]}</p></div></a>' for s in SIGNS) + '</div>'
b += '<div class="cta"><b>Асцендент - только начало.<br>Постройте всю натальную карту</b><a href="/natal">Натальная карта</a></div>'
b += '<h2 id="voprosy">Частые <em>вопросы</em></h2><div class="faq glass">' + ''.join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q, a in HD['faq']) + '</div>'
b += '<p style="margin:16px 0 0;font-size:14px;color:#6B6380">Читайте также: <a href="/blog/ascendent">Асцендент: что это и как рассчитать</a>, <a href="/blog/natalnaya-karta">натальная карта</a>, <a href="/blog/doma-v-natalnoy-karte">дома в натальной карте</a>, <a href="/signs">знаки зодиака</a>.</p>'
HUB['faq'] = HD['faq']
b += FOOT
faq_ld = ld({'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in HUB['faq']]})
page = head(HUB['title'], HUB['og'], HUB['desc'], '/ascendant', [crumbs_ld([('Главная', '/'), ('Асцендент', '/ascendant')]), faq_ld, DEEP_CSS] + CSS.split('\n')) + '\n' + b + '\n' + JS + '\n' + TAIL
open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(page)
print('ascendant pages:', len(SIGNS) + 1)
