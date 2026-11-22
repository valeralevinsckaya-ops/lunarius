# Перелинковка новых разделов: дописывает блок ссылок на страницы пар, знаков и хаб /compat.
# Запускать после build_pairs.py / build_signs.py. Повторный запуск безопасен (маркеры <!--lnk-->).
import os, re, glob, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'public')
sys.path.insert(0, os.path.join(ROOT, 'docs'))
import planets_extra as PX
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
    html_ = re.sub(r'(?<![а-яА-Я])([вВ]) Льве', r'\1о Льве', html_)
    s = s[:m.end()] + '<!--lnk-->' + html_ + '<!--/lnk-->' + s[m.end():]
    open(path, 'w', encoding='utf-8').write(s); return True

n = 0
ANCH = r'Читайте также:.*?</p>'
for f in glob.glob(os.path.join(P, 'compat', '*-*.html')):
    a, b = os.path.basename(f)[:-5].split('-')
    signs = [a] if a == b else [a, b]
    pl = ', '.join(f'<a href="/luna/{x}">Луна в {LOC[x]}</a>, <a href="/venera/{x}">Венера в {LOC[x]}</a>, <a href="/mars/{x}">Марс в {LOC[x]}</a>' for x in signs)
    h = f'<p style="{ST}">Аспекты, которые решают совместимость пары: {ASP}. Луна, Венера и Марс в знаках пары: {pl}.</p>'
    n += put(f, h, ANCH)
for f in glob.glob(os.path.join(P, 'signs', '*.html')):
    k = os.path.basename(f)[:-5]
    if k == 'index':
        h = f'<p style="{ST}">Кроме знака Солнца в карте есть знаки Луны и Венеры: разделы <a href="/luna">Луна в знаках</a>, <a href="/venera">Венера в знаках</a>, <a href="/mars">Марс в знаках</a>, <a href="/merkuriy">Меркурий в знаках</a> и <a href="/saturn">Сатурн в знаках</a>, а сферы жизни описывают <a href="/doma">дома</a>.</p>'
    else:
        h = f'<p style="{ST}">Знак Солнца не единственный в карте. Читайте также: <a href="/luna/{k}">Луна в {LOC[k]}</a>, <a href="/venera/{k}">Венера в {LOC[k]}</a>, <a href="/mars/{k}">Марс в {LOC[k]}</a>, <a href="/merkuriy/{k}">Меркурий в {LOC[k]}</a>, <a href="/saturn/{k}">Сатурн в {LOC[k]}</a>, <a href="/doma">дома в натальной карте</a>.</p>'
    n += put(f, h, ANCH)
# раздел «Солнце в знаке» на страницах знаков, перед блоком о женщине
NAMES = {'oven': 'Овен', 'telec': 'Телец', 'bliznecy': 'Близнецы', 'rak': 'Рак', 'lev': 'Лев', 'deva': 'Дева', 'vesy': 'Весы', 'skorpion': 'Скорпион', 'strelec': 'Стрелец', 'kozerog': 'Козерог', 'vodoley': 'Водолей', 'ryby': 'Рыбы'}
for k, (goal, dig) in PX.SUN.items():
    f = os.path.join(P, 'signs', k + '.html'); s2 = open(f, encoding='utf-8').read()
    s2 = re.sub(r'<!--sun-->.*?<!--/sun-->', '', s2, flags=re.S)
    m = re.search(r'<h2[^>]*>\s*Женщина', s2)
    i = m.start()
    blk = (f'<!--sun--><h2 id="solnce">Солнце в {LOC[k]} <em>в натальной карте</em></h2><div class="sec glass"><div class="wide">'
           f'<p>Знак зодиака, который называют по дате рождения, это положение Солнца. Солнце в натальной карте отвечает за волю, цели и то, кем человек хочет стать. У Солнца в {LOC[k]} главная цель: {goal}. {dig}</p>'
           f'<p style="margin-top:10px">Но Солнце не вся карта. Чувства описывает <a href="/luna/{k}">Луна</a>, любовь <a href="/venera/{k}">Венера</a>, энергию <a href="/mars/{k}">Марс</a>, мышление <a href="/merkuriy/{k}">Меркурий</a>, первое впечатление <a href="/ascendant">Асцендент</a>. Поэтому два человека с Солнцем в {LOC[k]} могут быть разными: знаки остальных планет у них свои. Узнать их можно в <a href="/natal">натальной карте</a>.</p></div></div><!--/sun-->')
    blk = re.sub(r'(?<![а-яА-Я])([вВ]) Льве', r'\1о Льве', blk)
    s2 = s2[:i] + blk + s2[i:]
    open(f, 'w', encoding='utf-8').write(s2); n += 1

h = f'<p style="{ST}">Знаки Солнца это первый шаг. Совместимость пары решают аспекты планет: {ASP}. Знаки Луны и Венеры: <a href="/luna">Луна в знаках</a>, <a href="/venera">Венера в знаках</a>.</p>'
n += put(os.path.join(P, 'compat', 'index.html'), h, ANCH)
print('links:', n)
