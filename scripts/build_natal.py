# Дополняет public/natal.html разделами из docs/natal_extra.py. Повторный запуск безопасен (маркеры <!--nx:...-->).
import os, sys, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'docs'))
import natal_extra as X
f = os.path.join(ROOT, 'public', 'natal.html')
s = open(f, encoding='utf-8').read()
s = re.sub(r'<!--nx:(\w+)-->.*?<!--/nx:\1-->', '', s, flags=re.S)
blk = lambda n, h: f'<!--nx:{n}-->{h}<!--/nx:{n}-->'
anchor = '<h2 class="r-sub" style="margin-top:64px">Как читать натальную карту</h2>'
i = s.index(anchor)
s = s[:i] + blk('planets', X.PLANETS) + blk('houses', X.HOUSES_HTML) + blk('aspects', X.ASPECTS) + s[i:]
faq = '<h2 class="r-sub" style="margin-top:64px">Частые вопросы о натальной карте</h2>'
i = s.index(faq)
s = s[:i] + blk('example', X.EXAMPLE) + blk('steps', X.STEPS) + s[i:]
i = s.index('</div></section>', s.index('<section id="faq">'))
s = s[:i] + blk('faq', ''.join(f'<div class="card"><h3>{q}</h3><p>{a}</p></div>' for q, a in X.FAQ_EXTRA)) + s[i:]
assert 'ё' not in s and '—' not in s
open(f, 'w', encoding='utf-8').write(s)
print('natal ok')
