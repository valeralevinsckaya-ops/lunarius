# Добавляет на все страницы public/: canonical (если нет), Open Graph, Twitter, JSON-LD (хлебные крошки, статья, сайт).
# Запускается в конце каждого build_*.py. Повторный запуск безопасен: блок между маркерами пересоздается.
import os, re, json, html, glob, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUB = os.path.join(ROOT, 'public')
SITE = 'https://lunarius.ru'
IMG = SITE + '/og-image.jpg'
START, END = '<!--meta:start-->', '<!--meta:end-->'
TODAY = datetime.date.today().isoformat()
SECTIONS = {'blog': ('Блог', '/blog'), 'signs': ('Знаки зодиака', '/signs'), 'compat': ('Совместимость знаков', '/compat')}


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
    if rel.startswith('tpl') or rel.startswith('yandex_') or rel.startswith('google'):
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
    is_article = rel.startswith('blog/') and not rel.endswith('index.html')
    tags = []
    if 'rel="canonical"' not in s:
        tags.append(f'<link rel="canonical" href="{full}">')
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
    else:
        crumbs = [('Главная', '/')]
        if parts[0] in SECTIONS and len(parts) > 1:
            crumbs.append(SECTIONS[parts[0]])
        h1 = re.search(r'<h1[^>]*>(.*?)</h1>', s, re.S)
        name = html.unescape(re.sub(r'<[^>]+>', '', h1.group(1))).strip() if h1 else t_short
        crumbs.append((re.sub(r'\s+', ' ', name), u))
        ld.append({'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': SITE + h} for i, (n, h) in enumerate(crumbs)]})
    if is_article:
        ld.append({'@context': 'https://schema.org', '@type': 'Article', 'headline': t_short[:110], 'description': desc,
                   'image': IMG, 'inLanguage': 'ru', 'dateModified': TODAY, 'mainEntityOfPage': full,
                   'author': {'@type': 'Organization', 'name': 'Lunarius', 'url': SITE + '/'},
                   'publisher': {'@type': 'Organization', 'name': 'Lunarius', 'logo': {'@type': 'ImageObject', 'url': SITE + '/icon-512.png'}}})
    for obj in ld:
        tags.append('<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + '</script>')
    block = START + '\n' + '\n'.join(tags) + '\n' + END + '\n'
    s = s.replace('</head>', block + '</head>', 1)
    open(path, 'w', encoding='utf-8').write(s)
    return True


n = sum(process(p) for p in glob.glob(os.path.join(PUB, '**', '*.html'), recursive=True))
print('meta:', n, 'pages')
