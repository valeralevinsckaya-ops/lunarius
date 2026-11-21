# Собирает виджет для чужих сайтов (public/widget.html, noindex) и страницу с кодом вставки (public/vidzhet.html).
# Спидометр берется с главной, чтобы виджет выглядел так же, как сайт.
import os, re, html
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'public')
idx = open(os.path.join(P, 'index.html'), encoding='utf-8').read()
m = re.search(r'<svg viewBox="0 0 320 196".*?</svg>', idx, re.S)
gauge = m.group(0)
gauge = re.sub(r'<svg [^>]*>', '<svg viewBox="0 0 320 196" class="g" role="img" aria-label="Спидометр совместимости по шкале от -10 до +10">', gauge, count=1)
gauge = re.sub(r'\s*id="score"', '', gauge)
gauge = gauge.replace('transform="rotate(90.0 160 160)"', 'transform="rotate(90 160 160)"')
MOSCOW = 20
FONTS = "@font-face{font-family:'Manrope';src:url(/fonts/manrope.woff) format('woff');font-weight:200 800;font-display:swap}@font-face{font-family:'Oswald';src:url(/fonts/oswald.woff) format('woff');font-weight:200 700;font-display:swap}"

widget = f'''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Спидометр совместимости Lunarius: виджет</title>
<meta name="description" content="Виджет спидометра совместимости Lunarius для вставки на сайт.">
<meta name="robots" content="noindex, nofollow">
<link rel="canonical" href="https://lunarius.ru/vidzhet">
<style>{FONTS}
*{{box-sizing:border-box}}
html,body{{margin:0;height:100%}}
body{{font-family:'Manrope',Arial,sans-serif;color:#2A2340;font-size:14px;line-height:1.45;background:#FBF8F3;background-image:radial-gradient(420px 300px at 100% 0%,rgba(242,180,120,.45),transparent 60%),radial-gradient(420px 340px at 0% 30%,rgba(197,178,247,.55),transparent 60%)}}
.w{{max-width:560px;margin:0 auto;padding:16px 16px 12px}}
.hd{{display:flex;align-items:center;gap:10px;text-decoration:none;color:#2A2340;margin-bottom:12px}}
.hd b{{display:block;font-family:'Oswald',Arial,sans-serif;font-weight:600;font-size:20px;letter-spacing:.08em;text-transform:uppercase;line-height:1}}
.hd span span{{display:block;font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:#5B44BD}}
.row{{display:grid;grid-template-columns:1fr 1fr;gap:10px}}
.p{{background:rgba(255,255,255,.72);border:1.5px solid rgba(255,255,255,.95);border-radius:16px;padding:10px 12px;box-shadow:0 6px 18px rgba(91,68,189,.08)}}
.p h2{{margin:0 0 6px;font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:#5B44BD}}
label{{display:block;font-size:12px;color:#5E5675;margin:6px 0 3px}}
input[type=date],input[type=text]{{width:100%;height:38px;border:1.5px solid rgba(110,86,207,.25);border-radius:10px;padding:0 10px;font:inherit;color:#2A2340;background:#fff}}
input:focus{{outline:2px solid #6E56CF;outline-offset:1px}}
.ok{{display:flex;gap:8px;align-items:flex-start;font-size:12px;color:#5E5675;margin:10px 2px}}
.ok input{{margin-top:2px;accent-color:#6E56CF}}
.ok a{{color:#5B44BD}}
button{{width:100%;height:44px;border:0;border-radius:999px;background:#6E56CF;color:#fff;font:700 15px 'Manrope',Arial,sans-serif;cursor:pointer;box-shadow:0 8px 20px rgba(110,86,207,.3)}}
button:hover{{background:#5B44BD}}
button:disabled{{opacity:.6;cursor:wait}}
.res{{text-align:center;margin-top:10px}}
.g{{width:100%;max-width:270px;height:auto;overflow:visible;display:block;margin:0 auto}}
#needle{{transition:transform .9s cubic-bezier(.3,1.4,.5,1)}}
.sc{{font-family:'Oswald',Arial,sans-serif;font-size:34px;font-weight:600;line-height:1;margin-top:2px;color:#5B44BD}}
.zn{{font-weight:700;font-size:15px;margin-top:4px}}
.tx{{color:#5E5675;font-size:13px;margin:6px auto 0;max-width:460px}}
.err{{color:#C2410C;font-size:13px;margin-top:8px;min-height:1em}}
.more{{display:inline-flex;align-items:center;min-height:40px;padding:0 18px;margin-top:10px;border-radius:999px;background:#2A2340;color:#FBF8F3;text-decoration:none;font-weight:700;font-size:13px}}
.ft{{text-align:center;font-size:11px;color:#6B6380;margin-top:10px}}
.ft a{{color:#5B44BD}}
@media (max-width:420px){{.row{{grid-template-columns:1fr}}}}
</style>
</head>
<body>
<div class="w">
<a class="hd" href="https://lunarius.ru/?utm_source=widget&amp;utm_medium=iframe" target="_blank" rel="noopener"><svg width="34" height="22" viewBox="0 0 34 22" aria-hidden="true"><path d="M3 19 A14 14 0 0 1 31 19" fill="none" stroke="#6E56CF" stroke-width="3" stroke-linecap="round"></path><line x1="17" y1="19" x2="25" y2="9" stroke="#2A2340" stroke-width="2.5" stroke-linecap="round"></line><circle cx="17" cy="19" r="2.5" fill="#2A2340"></circle></svg><span><b>Lunarius</b><span>Спидометр совместимости</span></span></a>
<form id="f" novalidate>
<div class="row">
<div class="p"><h2>Вы</h2><label for="da">Дата рождения</label><input type="date" id="da" min="1900-01-01" max="2100-12-31" required><label for="ca">Город рождения</label><input type="text" id="ca" list="cl" value="Москва" autocomplete="off"></div>
<div class="p"><h2>Партнер</h2><label for="db">Дата рождения</label><input type="date" id="db" min="1900-01-01" max="2100-12-31" required><label for="cb">Город рождения</label><input type="text" id="cb" list="cl" value="Москва" autocomplete="off"></div>
</div>
<datalist id="cl"></datalist>
<label class="ok"><input type="checkbox" id="ok"><span>Согласен(на) на обработку данных о рождении для расчета по <a href="https://lunarius.ru/privacy" target="_blank" rel="noopener">политике конфиденциальности</a>. Данные не сохраняются.</span></label>
<button type="submit" id="go">Проверить совместимость</button>
<div class="err" id="err" role="alert"></div>
</form>
<div class="res" aria-live="polite">
{gauge}
<div class="sc" id="sc">0,00</div>
<div class="zn" id="zn">Укажите две даты рождения</div>
<div class="tx" id="tx">Стрелка покажет общий тренд пары по шкале от -10 до +10. Без времени рождения расчет идет на полдень.</div>
<a class="more" id="more" href="https://lunarius.ru/?utm_source=widget&amp;utm_medium=iframe" target="_blank" rel="noopener">Подробный разбор пары на Lunarius.ru</a>
</div>
<div class="ft">Расчет: <a href="https://lunarius.ru/?utm_source=widget&amp;utm_medium=iframe" target="_blank" rel="noopener">спидометр совместимости Lunarius</a></div>
</div>
<script>
(function () {{
  var $ = function (i) {{ return document.getElementById(i); }};
  var ids = {{}}; ids['москва'] = {MOSCOW};
  var host = ''; try {{ host = new URL(document.referrer).hostname; }} catch (e) {{}}
  if (host) document.querySelectorAll('a[href*="utm_source=widget"]').forEach(function (a) {{ a.href += '&utm_campaign=' + encodeURIComponent(host); }});
  var t;
  function suggest(e) {{
    var q = e.target.value.trim(); clearTimeout(t);
    if (q.length < 2) return;
    t = setTimeout(function () {{
      fetch('/api/cities?q=' + encodeURIComponent(q)).then(function (r) {{ return r.json(); }}).then(function (list) {{
        var dl = $('cl'); dl.innerHTML = '';
        list.forEach(function (c) {{ ids[c.label.toLowerCase()] = c.id; ids[c.name.toLowerCase()] = ids[c.name.toLowerCase()] == null ? c.id : ids[c.name.toLowerCase()]; var o = document.createElement('option'); o.value = c.label; dl.appendChild(o); }});
      }}).catch(function () {{}});
    }}, 200);
  }}
  $('ca').addEventListener('input', suggest); $('cb').addEventListener('input', suggest);
  function city(v) {{ v = v.trim().toLowerCase(); return ids[v]; }}
  function angle(v) {{ var f = (1 + Math.sign(v) * Math.sqrt(Math.abs(v) / 10)) / 2; return f * 180; }}
  function fmt(v) {{ return (v > 0 ? '+' : '') + v.toFixed(2).replace('.', ','); }}
  $('f').addEventListener('submit', function (e) {{
    e.preventDefault(); $('err').textContent = '';
    var a = $('da').value, b = $('db').value, ca = city($('ca').value), cb = city($('cb').value);
    if (!a || !b) {{ $('err').textContent = 'Укажите обе даты рождения'; return; }}
    if (ca == null || cb == null) {{ $('err').textContent = 'Выберите город рождения из подсказок'; return; }}
    if (!$('ok').checked) {{ $('err').textContent = 'Отметьте согласие на обработку данных'; return; }}
    $('go').disabled = true;
    fetch('/api/compatibility', {{ method: 'POST', headers: {{ 'Content-Type': 'application/json' }}, body: JSON.stringify({{ consent: true, a: {{ date: a, cityId: ca }}, b: {{ date: b, cityId: cb }} }}) }})
      .then(function (r) {{ return r.json().then(function (j) {{ if (!r.ok) throw new Error(j.error || 'Ошибка расчета'); return j; }}); }})
      .then(function (r) {{
        var v = r.trend.score;
        $('needle').setAttribute('transform', 'rotate(' + angle(v).toFixed(1) + ' 160 160)');
        $('sc').textContent = fmt(v); $('sc').style.color = v < 0 ? '#E8762E' : '#5B44BD';
        $('zn').textContent = r.trend.zone; $('tx').textContent = r.trend.text;
        try {{ parent.postMessage({{ lunarius: 'done', score: v }}, '*'); }} catch (e) {{}}
      }})
      .catch(function (er) {{ $('err').textContent = er.message || 'Ошибка расчета, попробуйте еще раз'; }})
      .then(function () {{ $('go').disabled = false; }});
  }});
}})();
</script>
</body>
</html>
'''
open(os.path.join(P, 'widget.html'), 'w', encoding='utf-8').write(widget)

# Страница с кодом вставки: берем оформление страницы стихий
tpl = open(os.path.join(P, 'elements', 'index.html'), encoding='utf-8').read()
tpl = re.sub(r'<!--meta:start-->.*?<!--meta:end-->\n?', '', tpl, flags=re.S)
tpl = re.sub(r'<script type="application/ld\+json">.*?</script>\n?', '', tpl, flags=re.S)
head, rest = tpl.split('</header>', 1)
foot = rest[rest.index('<footer'):]
TITLE = 'Виджет «Спидометр совместимости» для сайта | Lunarius'
DESC = 'Бесплатный виджет совместимости по дате рождения для вашего сайта или блога: спидометр Lunarius от -10 до +10, код для вставки в одну строку.'
head = re.sub(r'<title>.*?</title>', f'<title>{TITLE}</title>', head, flags=re.S)
head = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{DESC}">', head)
head = re.sub(r'<link rel="canonical" href="[^"]*">', '<link rel="canonical" href="https://lunarius.ru/vidzhet">', head)
CODE = ('<iframe src="https://lunarius.ru/widget" width="100%" height="740" style="max-width:560px;border:0;border-radius:20px" '
        'loading="lazy" title="Спидометр совместимости Lunarius"></iframe>\n'
        '<p style="max-width:560px;font-size:13px;text-align:center"><a href="https://lunarius.ru/">Спидометр совместимости Lunarius</a></p>')
css = ('<style>.wbox{display:grid;grid-template-columns:minmax(0,560px) minmax(0,1fr);gap:28px;align-items:start;margin:8px 0 36px}'
       '.wbox iframe{width:100%;height:740px;border:0;border-radius:20px;box-shadow:0 18px 40px rgba(91,68,189,.15);background:#FBF8F3}'
       '.code{padding:22px 24px}.code pre{white-space:pre-wrap;word-break:break-all;margin:0 0 14px;padding:14px;border-radius:14px;background:#2A2340;color:#FBF8F3;font-size:13px;line-height:1.5}'
       '.code button{display:inline-flex;align-items:center;min-height:44px;padding:0 22px;border:0;border-radius:999px;background:#6E56CF;color:#fff;font:700 14px Manrope,sans-serif;cursor:pointer}'
       '.steps{padding:24px 28px}.steps ol{margin:0;padding-left:20px}.steps li{margin:0 0 8px}'
       '@media (max-width:860px){.wbox{grid-template-columns:1fr}}</style>')
head = head.replace('</head>', css + '\n</head>', 1)
faq = [
    ('Сколько стоит виджет?', 'Виджет бесплатный. Регистрация и ключи не нужны: скопируйте код и вставьте его на страницу.'),
    ('Что увидят посетители вашего сайта?', 'Форму с двумя датами и городами рождения, кнопку расчета и спидометр совместимости от -10 до +10 с названием зоны и коротким пояснением. Из виджета посетитель может перейти к подробному разбору пары на Lunarius.ru.'),
    ('Сохраняются ли данные посетителей?', 'Нет. Даты и города рождения передаются по HTTPS, расчет идет в памяти сервера, после ответа данные не хранятся. Подробно об этом написано в <a href="/privacy">политике конфиденциальности</a>.'),
    ('Можно ли поменять размер?', 'Да. Ширина подстраивается под колонку сайта, высоту можно задать в атрибуте height. На узких экранах поля встают друг под другом, поэтому для мобильной версии лучше оставить высоту 740 пикселей или больше.'),
    ('Какие условия использования?', 'Подпись со ссылкой на Lunarius под виджетом должна остаться на месте. Виджет нельзя встраивать на страницы с запрещенным контентом. В остальном ставьте его на любые страницы: в блог, в статью о знаках зодиака, на сайт астролога или свадебного агентства.'),
    ('Насколько точен расчет?', 'Виджет использует тот же алгоритм, что и главная страница Lunarius: синастрию натальных карт двух людей с учетом аспектов Солнца, Луны, Венеры, Марса и других планет. Время рождения в виджете не спрашивается, поэтому расчет идет на полдень. Сайт носит развлекательный характер.'),
]
body = (
    '<main>\n<p class="crumbs"><a href="/">Главная</a> · Виджет</p>'
    '<h1 class="list">Виджет <em style="font-style:normal;color:#6E56CF">«Спидометр совместимости»</em> для сайта</h1>'
    '<p class="lead">Поставьте калькулятор совместимости Lunarius на свой сайт или в блог. Посетитель вводит две даты рождения и сразу видит, куда показывает стрелка: от -10 (пара на сопротивлении) до +10 (пара на подъеме). Виджет бесплатный, код вставки занимает две строки.</p>'
    '<div class="wbox"><iframe src="/widget" title="Спидометр совместимости Lunarius" loading="lazy"></iframe>'
    '<div><div class="code glass"><h2 style="margin:0 0 14px;font-size:26px">Код для вставки</h2><pre id="code">' + html.escape(CODE) + '</pre>'
    '<button type="button" id="copy">Скопировать код</button></div>'
    '<div class="steps glass" style="margin-top:20px"><h2 style="margin:0 0 14px;font-size:26px">Как установить</h2><ol>'
    '<li>Скопируйте код кнопкой выше.</li>'
    '<li>Откройте редактор страницы на своем сайте и переключитесь в режим HTML (в WordPress это блок «Произвольный HTML», в Tilda блок T123, в Битрикс режим «Исходный код»).</li>'
    '<li>Вставьте код в то место, где нужен спидометр, и сохраните страницу.</li>'
    '<li>Проверьте расчет: введите две даты рождения и нажмите кнопку.</li></ol></div></div></div>'
    '<h2>Кому подойдет <em>виджет</em></h2><div class="sec glass">'
    '<div><h3>Блоги об астрологии</h3><p>Статья о совместимости знаков становится интерактивной: читатель проверяет свою пару прямо на странице и дольше остается на сайте.</p></div>'
    '<div><h3>Сайты астрологов</h3><p>Спидометр дает клиенту быстрый первый ответ, а за подробной консультацией он приходит к вам.</p></div>'
    '<div><h3>Свадебные и праздничные сайты</h3><p>Развлекательный тест для пар перед свадьбой или годовщиной: легко поделиться результатом с партнером.</p></div>'
    '<div><h3>Женские и развлекательные медиа</h3><p>Виджет рядом с гороскопом или тестом добавляет на страницу живой элемент без доработки сайта.</p></div>'
    '</div>'
    '<h2>Частые <em>вопросы</em></h2><section id="faq" class="sec glass">'
    + ''.join(f'<div class="wide"><h3>{q}</h3><p>{a}</p></div>' for q, a in faq) +
    '</section>'
    '<div class="cta"><b>Подробный разбор своей пары</b><a href="/">Открыть спидометр</a></div>'
    '<script>document.getElementById("copy").addEventListener("click",function(){var t=document.getElementById("code").textContent,b=this;(navigator.clipboard?navigator.clipboard.writeText(t):Promise.reject()).then(function(){b.textContent="Код скопирован"},function(){var r=document.createRange();r.selectNodeContents(document.getElementById("code"));var s=getSelection();s.removeAllRanges();s.addRange(r);b.textContent="Выделено, нажмите Ctrl+C"})})</script>'
    '</main>'
)
open(os.path.join(P, 'vidzhet.html'), 'w', encoding='utf-8').write(head + '</header>' + body + foot)
print('widget ok')
