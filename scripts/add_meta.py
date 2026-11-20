# Добавляет на все страницы public/: canonical (если нет), Open Graph, Twitter, JSON-LD (хлебные крошки, статья, сайт).
# Запускается в конце каждого build_*.py. Повторный запуск безопасен: блок между маркерами пересоздается.
import os, re, json, html, glob, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUB = os.path.join(ROOT, 'public')
SITE = 'https://lunarius.ru'
IMG = SITE + '/og-image.jpg'
START, END = '<!--meta:start-->', '<!--meta:end-->'
TODAY = datetime.date.today().isoformat()
SECTIONS = {'blog': ('Блог', '/blog'), 'signs': ('Знаки зодиака', '/signs'), 'compat': ('Совместимость знаков', '/compat'),
            'ascendant': ('Асцендент', '/ascendant'), 'elements': ('Стихии', '/elements')}
ARTICLE_SECTIONS = ('blog', 'signs', 'compat', 'ascendant', 'elements')
# дата изменения статьи берется из sitemap (lastmod), дата публикации - из истории git (первый коммит файла)
import subprocess
try:
    _sm = open(os.path.join(PUB, 'sitemap.xml'), encoding='utf-8').read()
    LASTMOD = dict(re.findall(r'<loc>https://lunarius\.ru([^<]*)</loc><lastmod>([0-9-]+)</lastmod>', _sm))
except OSError:
    LASTMOD = {}
def published(path):
    try:
        out = subprocess.run(['git', 'log', '--format=%cs', '--diff-filter=A', '--', path], cwd=ROOT, capture_output=True, text=True).stdout.split()
        return out[-1] if out else None
    except Exception:
        return None
# калькуляторы: разметка WebApplication
APPS = {
    '/': ('Спидометр совместимости Lunarius', 'Расчет совместимости пары по датам рождения: синастрия двух натальных карт, шкала от -10 до +10.'),
    '/natal': ('Натальная карта онлайн', 'Расчет натальной карты по дате, времени и месту рождения: планеты в знаках и домах, Асцендент, аспекты с расшифровкой.'),
    '/ascendant': ('Калькулятор Асцендента', 'Расчет Асцендента (восходящего знака) по дате, времени и городу рождения с расшифровкой.'),
}


# Запасные шрифты с подогнанными метриками: пока Manrope и Oswald грузятся, текст занимает то же место,
# и макет не прыгает (CLS). Коэффициенты измерены в Chrome по тексту главной относительно Arial.
FB_START, FB_END = '<!--fontfb:start-->', '<!--fontfb:end-->'
_LOCAL = "local('Arial'),local('Liberation Sans'),local('Roboto'),local('Helvetica Neue')"
_LOCAL_B = "local('Arial Bold'),local('Liberation Sans Bold'),local('Roboto Bold'),local('Helvetica Neue Bold')"
FB_CSS = ('<style>'
          "@font-face{font-family:'Manrope Fallback';src:" + _LOCAL + ";font-weight:200 500;size-adjust:100.5%;ascent-override:106.1%;descent-override:29.9%;line-gap-override:0%}"
          "@font-face{font-family:'Manrope Fallback';src:" + _LOCAL_B + ";font-weight:600 800;size-adjust:98.5%;ascent-override:108.2%;descent-override:30.5%;line-gap-override:0%}"
          "@font-face{font-family:'Oswald Fallback';src:" + _LOCAL + ";font-weight:200 700;size-adjust:82%;ascent-override:145.5%;descent-override:35.2%;line-gap-override:0%}"
          '</style>')
_FAM = re.compile(r"(font-family:\s*)(['\"]?)(Oswald|Manrope)\2(?!\s*;\s*src)(?!\s*,\s*'(?:Oswald|Manrope) Fallback')")


def font_fallback(path):
    s = open(path, encoding='utf-8').read()
    if '</head>' not in s or '/fonts/' not in s:
        return
    new = re.sub(re.escape(FB_START) + r'.*?' + re.escape(FB_END) + r'\n?', '', s, flags=re.S)
    new = _FAM.sub(lambda m: f"{m.group(1)}'{m.group(3)}','{m.group(3)} Fallback'", new)
    new = new.replace('</head>', FB_START + FB_CSS + FB_END + '\n</head>', 1)
    if new != s:
        open(path, 'w', encoding='utf-8').write(new)


def url_of(rel):
    rel = rel.replace(os.sep, '/')
    if rel == 'index.html':
        return '/'
    if rel.endswith('/index.html'):
        return '/' + rel[:-len('/index.html')]
    return '/' + rel[:-len('.html')]


def esc(t):
    return html.escape(t, quote=True)


def process(path):
    rel = os.path.relpath(path, PUB)
    if rel.startswith('tpl') or rel.startswith('yandex_') or rel.startswith('google') or rel == '404.html':
        return False
    s = open(path, encoding='utf-8').read()
    if '<title>' not in s or '</head>' not in s:
        return False
    s = re.sub(re.escape(START) + r'.*?' + re.escape(END) + r'\n?', '', s, flags=re.S)
    u = url_of(rel)
    full = SITE + (u if u != '/' else '/')
    title = html.unescape(re.search(r'<title>(.*?)</title>', s, re.S).group(1).strip())
    t_short = re.sub(r'\s*\|\s*Lunarius\s*$', '', title)
    m = re.search(r'<meta name="description" content="([^"]*)"', s)
    desc = html.unescape(m.group(1)) if m else ''
    _p = rel.replace(os.sep, '/').split('/')
    is_article = len(_p) == 2 and _p[0] in ARTICLE_SECTIONS and _p[1] != 'index.html'
    tags = []
    if 'rel="canonical"' not in s:
        tags.append(f'<link rel="canonical" href="{full}">')
    if rel == 'index.html':
        tags.append('<meta name="msvalidate.01" content="3692369FBDC7EFDF2ED863E77175A327">')  # Bing Webmaster
    tags += [
        f'<meta property="og:type" content="{"article" if is_article else "website"}">',
        '<meta property="og:site_name" content="Lunarius">',
        '<meta property="og:locale" content="ru_RU">',
        f'<meta property="og:title" content="{esc(t_short)}">',
        f'<meta property="og:description" content="{esc(desc)}">',
        f'<meta property="og:url" content="{full}">',
        f'<meta property="og:image" content="{IMG}">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        '<meta name="twitter:card" content="summary_large_image">',
    ]
    ld = []
    parts = u.strip('/').split('/')
    if u == '/':
        ld.append({'@context': 'https://schema.org', '@type': 'WebSite', 'name': 'Lunarius', 'alternateName': 'Спидометр совместимости', 'url': SITE + '/', 'inLanguage': 'ru'})
        ld.append({'@context': 'https://schema.org', '@type': 'Organization', 'name': 'Lunarius', 'url': SITE + '/', 'logo': SITE + '/icon-512.png', 'email': 'info@lunarius.ru'})
    elif 'BreadcrumbList' not in s:
        crumbs = [('Главная', '/')]
        if parts[0] in SECTIONS and len(parts) > 1:
            crumbs.append(SECTIONS[parts[0]])
        h1 = re.search(r'<h1[^>]*>(.*?)</h1>', s, re.S)
        name = html.unescape(re.sub(r'<[^>]+>', '', h1.group(1))).strip() if h1 else t_short
        crumbs.append((re.sub(r'\s+', ' ', name), u))
        ld.append({'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': SITE + h} for i, (n, h) in enumerate(crumbs)]})
    faq = re.search(r'<section id="faq".*?</section>', s, re.S)
    if faq:
        clean = lambda x: re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', x))).strip()
        qa = re.findall(r'<h3[^>]*>(.*?)</h3>\s*<p[^>]*>(.*?)</p>', faq.group(0), re.S)
        if qa:
            ld.append({'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
                {'@type': 'Question', 'name': clean(a), 'acceptedAnswer': {'@type': 'Answer', 'text': clean(b)}} for a, b in qa]})
    if is_article:
        art = {'@context': 'https://schema.org', '@type': 'Article', 'headline': t_short[:110], 'description': desc,
                   'image': IMG, 'inLanguage': 'ru', 'dateModified': LASTMOD.get(u, TODAY) + 'T12:00:00+03:00', 'mainEntityOfPage': full,
                   'author': {'@type': 'Organization', 'name': 'Lunarius', 'url': SITE + '/'},
                   'publisher': {'@type': 'Organization', 'name': 'Lunarius', 'logo': {'@type': 'ImageObject', 'url': SITE + '/icon-512.png'}}}
        pub = published(path)
        if pub:
            art['datePublished'] = pub + 'T12:00:00+03:00'
        ld.append(art)
    if u in APPS:
        ld.append({'@context': 'https://schema.org', '@type': 'WebApplication', 'name': APPS[u][0], 'description': APPS[u][1], 'url': full,
                   'applicationCategory': 'LifestyleApplication', 'operatingSystem': 'Any', 'browserRequirements': 'Требуется JavaScript', 'inLanguage': 'ru',
                   'isAccessibleForFree': True, 'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'RUB'},
                   'publisher': {'@type': 'Organization', 'name': 'Lunarius', 'url': SITE + '/'}})
    for obj in ld:
        tags.append('<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + '</script>')
    block = START + '\n' + '\n'.join(tags) + '\n' + END + '\n'
    s = s.replace('</head>', block + '</head>', 1)
    open(path, 'w', encoding='utf-8').write(s)
    return True


_pages = glob.glob(os.path.join(PUB, '**', '*.html'), recursive=True)
n = sum(process(p) for p in _pages)
for _p in _pages:
    font_fallback(_p)
print('meta:', n, 'pages')
