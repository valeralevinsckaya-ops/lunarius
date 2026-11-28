#!/usr/bin/env python3
"""Собирает lib/natal-more.js: короткие выдержки со страниц «Планета в знаке»
для результата натальной карты (ссылка «Подробнее», сильные стороны, совет,
у женщины и у мужчины). Источник: docs/*_signs.py и docs/planets_extra.py.
Запуск: python3 scripts/build_natal_more.py (после правки текстов планет)."""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'docs'))
sys.dont_write_bytecode = True

import moon_signs, venus_signs, mars_signs, saturn_signs, mercury_signs, planets_extra  # noqa: E402

SLUG = {'aries': 'oven', 'taurus': 'telec', 'gemini': 'bliznecy', 'cancer': 'rak', 'leo': 'lev', 'virgo': 'deva',
        'libra': 'vesy', 'scorpio': 'skorpion', 'sagittarius': 'strelec', 'capricorn': 'kozerog', 'aquarius': 'vodoley', 'pisces': 'ryby'}
SRC = {'moon': ('luna', moon_signs.P), 'venus': ('venera', venus_signs.P), 'mars': ('mars', mars_signs.P),
       'saturn': ('saturn', saturn_signs.P), 'mercury': ('merkuriy', mercury_signs.P)}


def sentences(t, n):
    parts = re.split(r'(?<=[.!?])\s+', t.strip())
    return ' '.join(parts[:n])


def fix(t):
    return re.sub(r'(?<![а-яА-Я])([вВ]) Льве', r'\1о Льве', t)


out = {'slug': SLUG, 'planets': {}, 'sun': {}}
for key, (section, data) in SRC.items():
    out['planets'][key] = {'section': section, 'signs': {}}
    for eng, slug in SLUG.items():
        d = data[slug]
        plus = d.get('plus') or []
        out['planets'][key]['signs'][eng] = {
            'plus': fix('Сильные стороны: ' + ', '.join(plus) + '.') if plus else '',
            'advice': fix(sentences(d.get('advice', ''), 2)),
            'woman': fix(sentences(d.get('woman', ''), 3)),
            'man': fix(sentences(d.get('man', ''), 3)),
        }
for eng, slug in SLUG.items():
    goal = planets_extra.SUN[slug][0]
    out['sun'][eng] = goal

js = ("'use strict';\n// Собрано scripts/build_natal_more.py из docs/*_signs.py. Не править вручную.\n"
      "module.exports = " + json.dumps(out, ensure_ascii=False, indent=1) + ";\n")
with open(os.path.join(ROOT, 'lib', 'natal-more.js'), 'w', encoding='utf-8') as f:
    f.write(js)
print('natal-more:', sum(len(v['signs']) for v in out['planets'].values()), 'planet texts,', len(out['sun']), 'sun')
