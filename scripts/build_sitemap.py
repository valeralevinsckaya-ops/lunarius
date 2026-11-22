# Собирает public/sitemap.xml и public/robots.txt из существующих страниц
import os, glob, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'public')
today = datetime.date.today().isoformat()
urls = [('/', '1.0', 'weekly'), ('/natal', '0.9', 'monthly'), ('/ascendant', '0.9', 'monthly'), ('/signs', '0.8', 'monthly'), ('/elements', '0.8', 'monthly'), ('/compat', '0.8', 'monthly'), ('/blog', '0.7', 'weekly'), ('/doma', '0.8', 'monthly'), ('/luna', '0.8', 'monthly'), ('/venera', '0.8', 'monthly'), ('/mars', '0.8', 'monthly'), ('/saturn', '0.8', 'monthly'), ('/merkuriy', '0.8', 'monthly'), ('/vidzhet', '0.6', 'monthly')]
for d, pr in (('signs', '0.8'), ('elements', '0.8'), ('ascendant', '0.8'), ('doma', '0.8'), ('luna', '0.8'), ('venera', '0.8'), ('mars', '0.8'), ('saturn', '0.8'), ('merkuriy', '0.8'), ('compat', '0.7'), ('blog', '0.7')):
    for f in sorted(glob.glob(os.path.join(P, d, '*.html'))):
        n = os.path.basename(f)[:-5]
        if n != 'index': urls.append((f'/{d}/{n}', pr, 'monthly'))
xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(
    f'  <url><loc>https://lunarius.ru{u}</loc><lastmod>{today}</lastmod><changefreq>{cf}</changefreq><priority>{pr}</priority></url>\n' for u, pr, cf in urls) + '</urlset>\n'
open(os.path.join(P, 'sitemap.xml'), 'w', encoding='utf-8').write(xml)
open(os.path.join(P, 'robots.txt'), 'w', encoding='utf-8').write('User-agent: *\nAllow: /\nDisallow: /api/\nDisallow: /tpl/\nSitemap: https://lunarius.ru/sitemap.xml\n')
print('sitemap urls:', len(urls))
