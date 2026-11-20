# Дополняет статичные страницы public/elements/<slug>.html разделами из docs/elements_deep.py.
# Повторный запуск безопасен: блоки между маркерами <!--el:...--> пересоздаются.
import os, sys, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'docs'))
from elements_deep import E, PLANETS
import json, collections
from signs_content import SIGNS
_S = json.load(open(os.path.join(ROOT, 'docs', 'pairs_stats.json'), encoding='utf-8'))
_EL = {x['slug']: x['element'] for x in SIGNS}
_AVG = collections.defaultdict(list)
for _k, _v in _S.items():
    _a, _b = _k.split('-')
    if _a != _b: _AVG[frozenset([_EL[_a], _EL[_b]])].append(_v['mean'])
_AVG = {k: sum(v) / len(v) for k, v in _AVG.items()}
_fmt = lambda v: ('+' if v > 0 else '') + f'{v:.2f}'.replace('.', ',')
ELS = ['Огонь', 'Земля', 'Воздух', 'Вода']

def block(name, html):
    return f'<!--el:{name}-->{html}<!--/el:{name}-->'

def sec(cards):
    return '<div class="sec glass">' + ''.join(f'<div><h3>{h}</h3><p>{t}</p></div>' for h, t in cards) + '</div>'

for slug, x in E.items():
    f = os.path.join(ROOT, 'public/elements', slug + '.html')
    s = open(f, encoding='utf-8').read()
    s = re.sub(r'<!--el:(\w+)-->.*?<!--/el:\1-->', '', s, flags=re.S)
    g = x['gen']
    people = block('people', f'<h2 id="lyudi">Люди стихии <em>{g}</em></h2>' + sec(x['people']))
    rows = ''.join(f'<tr><td style="padding:7px 10px;border-bottom:1px solid rgba(110,86,207,.12)">{x["name"]} и {o if o != x["name"] else o + " (своя стихия)"}</td><td style="padding:7px 10px;border-bottom:1px solid rgba(110,86,207,.12)">{_fmt(_AVG[frozenset([x["name"], o])])}</td></tr>' for o in sorted(ELS, key=lambda o: -_AVG[frozenset([x["name"], o])]))
    table = ('<p class="lead" style="margin:18px 0 12px;max-width:820px">Средний балл спидометра Lunarius по парам знаков разных стихий: по 20 000 смоделированных пар на каждое сочетание знаков, без пар одного знака, шкала от -10 до +10. Разница невелика, но порядок совпадает с классикой.</p>'
             '<div class="glass" style="padding:20px 24px;overflow-x:auto"><table style="border-collapse:collapse;width:100%;font-size:15px"><tr style="text-align:left"><th style="padding:7px 10px">Сочетание стихий</th><th style="padding:7px 10px">Средний балл</th></tr>' + rows + '</table></div>')
    combos = block('combos', f'<h2 id="sovmestimost">{x["name"]} и другие стихии: <em>совместимость</em></h2>' + sec(x['combos']) + table
                   + '<p style="margin:16px 0 0;font-size:14px;color:#6B6380">Разбор конкретной пары знаков - в <a href="/compat">таблице всех 78 пар</a>.</p>')
    extra = block('extra', f'<h2 id="planety">{x["name"]} в натальной карте: <em>Луна, Венера, Марс</em></h2>' + sec(PLANETS[slug]) + f'<h2 id="balans">Много и мало <em>{g}</em> в натальной карте</h2>' + sec(x['balance'])
                  + f'<h2 id="simvoly">Символ, камни и цвета <em>{g}</em></h2><div class="sec glass"><div class="wide"><p>{x["symbols"]}</p></div></div>'
                  + f'<h2 id="voprosy">Частые <em>вопросы</em></h2><section id="faq" class="sec glass">' + ''.join(f'<div class="wide"><h3>{q}</h3><p>{a}</p></div>' for q, a in x['faq']) + '</section>')
    # старый блок совместимости (до cta) заменяется новым
    m = re.search(r'<h2>Совместимость <em>[^<]*</em> с другими стихиями</h2>.*?(?=<div class="cta">)', s, re.S)
    if m:
        s = s[:m.start()] + people + combos + s[m.end():]
    else:
        i = s.index('<div class="cta">'); s = s[:i] + people + combos + s[i:]
    i = s.index('<h2>Знаки <em>')
    s = s[:i] + extra + s[i:]
    open(f, 'w', encoding='utf-8').write(s)
print('elements:', len(E))
