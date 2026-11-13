# Собирает страницы блога из docs/blog-articles-edited.html (выгрузка Google Doc) в public/blog/
import re, os, html

def make_lead(t, n=170):
    t = t.strip()
    if len(t) <= n: return t
    cut = t[:n]
    # конец предложения внутри лимита
    m = max(cut.rfind('. '), cut.rfind('! '), cut.rfind('? '))
    if m > 80: return cut[:m + 1]
    cut = cut.rsplit(' ', 1)[0].rstrip(',;:-')
    return cut + '...'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
METRIKA = open(os.path.join(ROOT, 'design/metrika.html'), encoding='utf-8').read()
src = open(os.path.join(ROOT, 'docs/blog-articles-edited.html'), encoding='utf-8').read()
out_dir = os.path.join(ROOT, 'public/blog'); os.makedirs(out_dir, exist_ok=True)

IMAGES = ['aries', 'taurus', 'gemini', 'cancer', 'leo', 'virgo', 'libra', 'scorpio', 'sagittarius', 'capricorn', 'aquarius', 'pisces']
TAGS = {'natalnaya-karta': 'Натальная карта', 'sovmestimost-po-date-rozhdeniya': 'Совместимость', 'ascendent': 'Натальная карта', 'sovmestimost-znakov-zodiaka': 'Знаки',
        'sinastriya': 'Основы', 'doma-v-natalnoy-karte': 'Натальная карта', 'venera-v-sinastrii': 'Притяжение', 'luna-v-sinastrii': 'Эмоции', 'aspekty-v-natalnoy-karte': 'Аспекты'}

# разбиваем на статьи по карточкам "Статья N."
parts = re.split(r'(?=<p><b>Статья \d+\.</b>)', src)[1:]
articles = []
for part in parts:
    m_url = re.search(r'<p>URL: lunarius\.ru/blog/([a-z0-9-]+)</p>', part)
    m_title = re.search(r'<p>Title: (.*?)</p>', part)
    m_desc = re.search(r'<p>Description: (.*?)</p>', part)
    m_h1 = re.search(r'<h1>(.*?)</h1>', part)
    body = part[m_h1.end():]
    body = re.sub(r'<p><b>Статья.*', '', body, flags=re.S)
    # списки: подряд идущие <li> оборачиваем в <ul>
    body = re.sub(r'((?:<li>.*?</li>\n?)+)', lambda m: '<ul>' + m.group(1) + '</ul>', body)
    # внутренние ссылки на статьи
    body = body.replace('lunarius.ru/privacy', '<a href="/privacy">lunarius.ru/privacy</a>')
    # таблица
    body = body.replace('<table>', '<div class="tbl"><table>').replace('</table>', '</table></div>')
    body = re.sub(r'<table><tr>(.*?)</tr>', lambda m: '<table><tr>' + m.group(1).replace('<td>', '<th>').replace('</td>', '</th>') + '</tr>', body, count=1, flags=re.S)
    first_p = re.search(r'<p>(.*?)</p>', body, re.S)
    articles.append({'slug': m_url.group(1), 'title': html.unescape(m_title.group(1)), 'desc': html.unescape(m_desc.group(1)), 'h1': m_h1.group(1), 'body': body.strip(),
                     'lead': make_lead(re.sub(r'<[^>]+>', '', first_p.group(1))) if first_p else ''})

HEAD = '''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="https://lunarius.ru{path}">
<link rel="icon" href="/favicon-64.png" sizes="64x64" type="image/png">
<link rel="icon" href="/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="#FBF8F3">

<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Oswald:wght@400;500;600;700&family=Manrope:wght@400;500;600;700&display=swap" rel="stylesheet">
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
article{{max-width:820px;margin:0 auto;padding:48px 56px}}
article h1{{margin:0 0 20px;font-family:'Oswald',sans-serif;font-weight:600;font-size:48px;line-height:1.05;text-transform:uppercase}}
article h2{{margin:40px 0 12px;font-family:'Oswald',sans-serif;font-weight:600;font-size:30px;line-height:1.1;text-transform:uppercase}}
article h3{{margin:28px 0 8px;font-family:'Oswald',sans-serif;font-weight:500;font-size:21px;text-transform:uppercase;letter-spacing:.02em}}
article p,article li{{font-size:16px}}article p{{margin:0 0 14px}}article ul{{margin:0 0 14px;padding-left:22px}}article li{{margin:0 0 6px}}
.tag{{display:inline-block;padding:4px 12px;border-radius:999px;background:#E2D5FA;font-size:11px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:#3E2C8F;margin-bottom:16px}}
.tbl{{overflow:auto;margin:0 0 14px}}table{{border-collapse:collapse;width:100%;font-size:14px}}th,td{{padding:10px 12px;border:1px solid #D8CDEE;text-align:left;vertical-align:top}}th{{background:rgba(226,213,250,.6);font-family:'Oswald',sans-serif;text-transform:uppercase;font-weight:500}}
.cta{{margin:40px 0 0;padding:24px 28px;border-radius:24px;background:linear-gradient(135deg,#6E56CF,#9A6BF0 60%,#F2768A);color:#fff;display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:16px}}
.cta b{{font-family:'Oswald',sans-serif;font-size:22px;font-weight:500;text-transform:uppercase}}
.cta a{{display:inline-flex;align-items:center;min-height:48px;padding:0 24px;border-radius:999px;background:#2A2340;color:#FBF8F3;text-decoration:none;font-weight:700}}
.rel{{max-width:820px;margin:32px auto 0}}.rel h2{{font-family:'Oswald',sans-serif;font-weight:600;font-size:28px;text-transform:uppercase;margin:0 0 16px}}
.grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:24px}}
.cardl{{display:flex;flex-direction:column;border-radius:30px;overflow:hidden;text-decoration:none;color:#2A2340}}
.cardl img{{width:100%;height:200px;object-fit:cover;object-position:50% 25%;display:block}}
.cardl div{{display:flex;flex-direction:column;gap:10px;padding:22px 24px 26px}}
.cardl h3{{margin:0;font-family:'Oswald',sans-serif;font-size:22px;font-weight:500;line-height:1.2;text-transform:uppercase}}
.cardl p{{margin:0;font-size:14px;color:#5E5675}}.cardl .more{{font-size:14px;font-weight:700;color:#5B44BD}}
h1.list{{margin:24px 0 8px;font-family:'Oswald',sans-serif;font-weight:600;font-size:64px;line-height:1;text-transform:uppercase}}
.lead{{margin:0 0 36px;max-width:720px;font-size:17px;color:#5E5675}}
footer{{margin-top:72px;padding:28px 0 0;border-top:1px solid rgba(110,86,207,.2);font-size:13px;color:#6B6380;display:flex;flex-wrap:wrap;gap:16px;justify-content:space-between}}
@media (max-width:1100px){{.grid{{grid-template-columns:repeat(2,minmax(0,1fr))}}}}
@media (max-width:640px){{article{{padding:28px 20px;border-radius:24px}}article h1{{font-size:32px}}article h2{{font-size:24px}}h1.list{{font-size:40px}}.grid{{grid-template-columns:1fr}}}}
</style>
{metrika}
</head>
<body>
<div class="wrap">
<header>
<a class="logo" href="/"><svg width="34" height="22" viewBox="0 0 34 22" aria-hidden="true"><path d="M3 19 A14 14 0 0 1 31 19" fill="none" stroke="#6E56CF" stroke-width="3" stroke-linecap="round"></path><line x1="17" y1="19" x2="25" y2="9" stroke="#2A2340" stroke-width="2.5" stroke-linecap="round"></line><circle cx="17" cy="19" r="2.5" fill="#2A2340"></circle></svg><span><b>Lunarius</b><span>Спидометр совместимости</span></span></a>
<nav aria-label="Основное меню"><a href="/">Совместимость</a><a href="/natal">Натальная карта</a><a href="/blog">Статьи</a><a href="/#faq">Вопросы</a></nav>
</header>
'''
FOOT = '''<footer><span>© 2026 Lunarius.ru · <a href="mailto:info@lunarius.ru">info@lunarius.ru</a> · <a href="/privacy">Документы</a></span><span>Сайт носит развлекательный характер и не заменяет консультацию специалиста</span></footer>
</div>
</body>
</html>
'''

def card(a, i):
    return f'<a class="cardl glass" href="/blog/{a["slug"]}"><img src="/img/{IMAGES[i % 12]}.webp" alt="" loading="lazy"><div><span class="tag" style="margin:0;align-self:flex-start">{TAGS.get(a["slug"], "Статья")}</span><h3>{a["h1"]}</h3><p>{html.escape(a["lead"])}</p><span class="more">Читать статью →</span></div></a>'

for i, a in enumerate(articles):
    cta_natal = a['slug'] in ('natalnaya-karta', 'ascendent', 'doma-v-natalnoy-karte', 'aspekty-v-natalnoy-karte')
    cta = ('<div class="cta"><b>Рассчитать натальную карту</b><a href="/natal">Открыть</a></div>' if cta_natal else '<div class="cta"><b>Проверить совместимость пары</b><a href="/">Запустить спидометр</a></div>')
    others = [x for x in articles if x['slug'] != a['slug']]
    rel = others[i % len(others):][:3] if len(others) >= 3 else others
    if len(rel) < 3: rel = (rel + others)[:3]
    page = HEAD.format(metrika=METRIKA, title=html.escape(a['title']), desc=html.escape(a['desc']), path='/blog/' + a['slug'])
    page += f'<p class="crumbs"><a href="/">Главная</a> · <a href="/blog">Статьи</a></p>'
    page += f'<article class="glass"><span class="tag">{TAGS.get(a["slug"], "Статья")}</span><h1>{a["h1"]}</h1>\n{a["body"]}\n{cta}</article>'
    page += '<section class="rel"><h2>Читайте также</h2><div class="grid">' + ''.join(card(x, articles.index(x)) for x in rel) + '</div></section>'
    page += FOOT
    assert 'ё' not in page and '—' not in page, a['slug']
    open(os.path.join(out_dir, a['slug'] + '.html'), 'w', encoding='utf-8').write(page)

idx = HEAD.format(metrika=METRIKA, title='Статьи об астрологии отношений: натальная карта, синастрия, совместимость | Lunarius', desc='Статьи Lunarius простым языком: как читать натальную карту, что такое асцендент и дома, совместимость знаков зодиака, синастрия, Луна и Венера в отношениях.', path='/blog')
idx += '<h1 class="list">Статьи</h1><p class="lead">Астрология отношений простым языком: от основ синастрии до отдельных планет. Все статьи заканчиваются тем, что можно проверить на себе.</p>'
idx += '<div class="grid">' + ''.join(card(a, i) for i, a in enumerate(articles)) + '</div>' + FOOT
open(os.path.join(out_dir, 'index.html'), 'w', encoding='utf-8').write(idx)
print('blog:', len(articles), 'статей ->', [a['slug'] for a in articles])
