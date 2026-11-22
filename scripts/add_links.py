# Перелинковка новых разделов: дописывает блок ссылок на страницы пар, знаков и хаб /compat.
# Запускать после build_pairs.py / build_signs.py. Повторный запуск безопасен (маркеры <!--lnk-->).
import os, re, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'public')
LOC = {'oven': 'Овне', 'telec': 'Тельце', 'bliznecy': 'Близнецах', 'rak': 'Раке', 'lev': 'Льве', 'deva': 'Деве', 'vesy': 'Весах',
       'skorpion': 'Скорпионе', 'strelec': 'Стрельце', 'kozerog': 'Козероге', 'vodoley': 'Водолее', 'ryby': 'Рыбах'}
ST = 'margin:12px 0 0;font-size:15px;line-height:1.9'
ASP = ('<a href="/blog/solnce-luna-sinastriya">Солнце и Луна</a>, <a href="/blog/venera-mars-sinastriya">Венера и Марс</a>, '
       '<a href="/blog/solnce-venera-sinastriya">Солнце и Венера</a>, <a href="/blog/venera-pluton-sinastriya">Венера и Плутон</a>, '
       '<a href="/blog/lilit-v-sinastrii">Лилит в синастрии</a>, <a href="/blog/pluton-v-sinastrii">Плутон в синастрии</a>')

def put(path, html_, anchor_re):
    s = open(path, encoding='utf-8').read()
    s = re.sub(r'<!--lnk-->.*?<!--/lnk-->', '', s, flags=re.S)
    m = None
    for m in re.finditer(anchor_re, s, re.S): pass
    if not m: return False
    s = s[:m.end()] + '<!--lnk-->' + html_ + '<!--/lnk-->' + s[m.end():]
    open(path, 'w', encoding='utf-8').write(s); return True

n = 0
ANCH = r'Читайте также:.*?</p>'
for f in glob.glob(os.path.join(P, 'compat', '*-*.html')):
    a, b = os.path.basename(f)[:-5].split('-')
    signs = [a] if a == b else [a, b]
    pl = ', '.join(f'<a href="/luna/{x}">Луна в {LOC[x]}</a>, <a href="/venera/{x}">Венера в {LOC[x]}</a>' for x in signs)
    h = f'<p style="{ST}">Аспекты, которые решают совместимость пары: {ASP}. Луна и Венера в знаках пары: {pl}.</p>'
    n += put(f, h, ANCH)
for f in glob.glob(os.path.join(P, 'signs', '*.html')):
    k = os.path.basename(f)[:-5]
    if k == 'index':
        h = f'<p style="{ST}">Кроме знака Солнца в карте есть знаки Луны и Венеры: разделы <a href="/luna">Луна в знаках</a> и <a href="/venera">Венера в знаках</a>, а сферы жизни описывают <a href="/doma">дома</a>.</p>'
    else:
        h = f'<p style="{ST}">Знак Солнца не единственный в карте. Читайте также: <a href="/luna/{k}">Луна в {LOC[k]}</a>, <a href="/venera/{k}">Венера в {LOC[k]}</a>, <a href="/doma">дома в натальной карте</a>.</p>'
    n += put(f, h, ANCH)
h = f'<p style="{ST}">Знаки Солнца это первый шаг. Совместимость пары решают аспекты планет: {ASP}. Знаки Луны и Венеры: <a href="/luna">Луна в знаках</a>, <a href="/venera">Венера в знаках</a>.</p>'
n += put(os.path.join(P, 'compat', 'index.html'), h, ANCH)
print('links:', n)
