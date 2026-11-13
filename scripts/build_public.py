# Собирает public/index.html из макета design/Main.dc.html
import re, math, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAVICON = '''<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="#FBF8F3">
'''
METRIKA = open(os.path.join(ROOT, 'design/metrika.html'), encoding='utf-8').read()
s = open(os.path.join(ROOT, 'design/Main.dc.html'), encoding='utf-8').read()
helmet = re.search(r'<helmet>(.*?)</helmet>', s, re.S).group(1)
body = re.search(r'</helmet>(.*?)</x-dc>', s, re.S).group(1)
body = re.sub(r'<sc-if[^>]*>', '', body).replace('</sc-if>', '')

v = 0.0
f = (1 + math.copysign(math.sqrt(abs(v) / 10), v)) / 2
for k, val in {'{{vtxt}}': '0.00', '{{vcolor}}': '#5B44BD', '{{needle}}': f'rotate({f*180:.1f} 160 160)', '{{verdict}}': 'Введите данные, чтобы запустить стрелку'}.items():
    body = body.replace(k, val)
assert '{{' not in body, re.findall(r'\{\{[^}]*\}\}', body)

ids = {'88a35e110baae4cce69a4be534440a02': 'aries', '21e35c77482bff69ddbb969f4b879689': 'taurus', '4623eeae74e2fa0f1c37e129c7a3a0ee': 'gemini', '5afd3d4467e47ec02186ffdcd102c707': 'cancer', 'f3b8a208b4d9784ef3110daa0fc64b23': 'leo', 'ee951f567a9ef8bf5425599b5aa55fbc': 'virgo', '6c5ee69188a9cdec9fd31e2c4df08b99': 'libra', '7d4248d41e8f6edaa85b3968306b644e': 'scorpio', '0a51d34354b8f19e6fd0d23e5b21dd35': 'sagittarius', 'db0aa8de0d58f1d4fdeedd4bb6a8d2d7': 'capricorn', '2f13985994fe488536a61120c777e116': 'aquarius', 'f5c4447b2fea67b5ca1555d94beaedc0': 'pisces'}
body = re.sub(r'src="/_blob/([0-9a-f]{32})"', lambda m: f'src="/img/{ids[m.group(1)]}.webp" loading="lazy"', body)

# точки привязки для скрипта
body = body.replace('stroke="#2A2340" stroke-width="5" stroke-linecap="round" transform="rotate(', 'id="needle" stroke="#2A2340" stroke-width="5" stroke-linecap="round" transform="rotate(', 1)
body = re.sub(r'(<p )(style="margin: 0; font-family: \'Oswald\', sans-serif; font-size: 72px;[^"]*">0\.00</p>)', r'\1id="score" \2', body, count=1)
body = body.replace('<p style="margin: 0; font-size: 15px; font-weight: 600; color: #5B44BD">Введите данные', '<p id="verdict" style="margin: 0; font-size: 15px; font-weight: 600; color: #5B44BD">Введите данные', 1)
body = body.replace('<button type="button" style="align-self: center; margin-top: 8px; min-height: 58px;', '<p id="form-error" role="alert" hidden style="align-self: center; margin: 0; padding: 10px 16px; border-radius: 12px; background: #FDE9DC; color: #A8461A; font-size: 14px; font-weight: 600"></p><button id="run" type="button" style="align-self: center; margin-top: 8px; min-height: 58px;', 1)
for need in ['id="needle"', 'id="score"', 'id="verdict"', 'id="run"', 'id="c1"', 'id="agree"']:
    assert need in body, need
body = body.replace('<span>Сайт носит развлекательный характер и не заменяет консультацию специалиста</span>', '<span>Сайт носит развлекательный характер и не заменяет консультацию специалиста · Данные о городах: <a href="https://www.geonames.org/" style="color: #EDE5FF">GeoNames</a> (CC BY 4.0)</span>', 1)
# блок результата сразу после первого экрана
hero_end = body.index('</form></section>') + len('</form></section>')
body = body[:hero_end] + '\n<section id="result" class="result" hidden aria-live="polite"></section>\n' + body[hero_end:]

css = '''<style>
html{scroll-behavior:smooth}
.city-list{position:absolute;left:0;right:0;top:100%;z-index:30;margin-top:4px;max-height:260px;overflow:auto;background:#fff;border:1px solid #D8CDEE;border-radius:14px;box-shadow:0 18px 40px rgba(75,58,158,.18)}
.city-item{display:block;width:100%;min-height:44px;padding:10px 14px;border:0;background:none;text-align:left;font:inherit;font-size:14px;color:#2A2340;cursor:pointer}
.city-item:hover,.city-item:focus{background:#F3ECFF;outline:none}
.result{padding:0 0 96px;display:flex;flex-direction:column;gap:24px;scroll-margin-top:24px}
.r-h{margin:0;font-family:'Oswald',sans-serif;font-weight:600;font-size:52px;text-transform:uppercase}
.r-sub{margin:16px 0 0;font-family:'Oswald',sans-serif;font-weight:500;font-size:28px;text-transform:uppercase}
.r-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px}
.r-card,.r-sphere,.r-aspect{padding:24px;border-radius:24px;background:linear-gradient(135deg,rgba(255,255,255,.62) 0%,rgba(255,255,255,.34) 50%,rgba(255,255,255,.5) 100%);backdrop-filter:blur(26px) saturate(160%);-webkit-backdrop-filter:blur(26px) saturate(160%);border:1px solid rgba(255,255,255,.85);box-shadow:inset 0 1px 0 rgba(255,255,255,.95),inset 0 20px 40px rgba(255,255,255,.22),0 24px 60px rgba(91,68,189,.18)}
.r-card{display:flex;flex-direction:column;gap:8px}
.r-who{font-size:12px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:#5B44BD}
.r-score{font-family:'Oswald',sans-serif;font-size:56px;font-weight:600;line-height:1}
.r-zone{font-family:'Oswald',sans-serif;font-size:22px;font-weight:500;text-transform:uppercase}
.r-text,.r-sphere p,.r-aspect p{margin:0;font-size:15px;line-height:1.6;color:#5E5675}
.r-signs{margin:4px 0 0;font-size:13px;color:#6B6380}
.r-spheres{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px}
.r-sphere{display:flex;flex-direction:column;gap:10px}
.r-sphere-top{display:flex;justify-content:space-between;align-items:baseline;font-family:'Oswald',sans-serif;font-size:22px;text-transform:uppercase}
.sb{position:relative;height:10px;border-radius:999px;background:#E6DCF8;overflow:hidden}
.sb-mid{position:absolute;left:50%;top:0;bottom:0;width:2px;background:#fff}
.sb-fill{position:absolute;top:0;bottom:0;border-radius:999px}
.r-aspects{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}
.r-aspect{display:flex;flex-direction:column;gap:6px;border-left-width:1px}
.r-aspect strong{font-size:15px;color:#2A2340}
.r-aspect.is-h strong::before{content:'+ ';color:#5B44BD}
.r-aspect.is-t strong::before{content:'- ';color:#E8762E}
.r-note{margin:0;font-size:14px;color:#6B6380}
.r-summary{margin-top:10px!important;padding-top:10px;border-top:1px solid rgba(110,86,207,.18);color:#2A2340!important}
.r-cmp{font-size:15px!important;color:#2A2340!important}
.r-chips{display:flex;flex-wrap:wrap;gap:6px;margin-top:4px}
.r-chip{font-size:12px;font-weight:600;padding:4px 10px;border-radius:999px;background:rgba(255,255,255,.7);color:#2A2340}
.r-chip.is-h{box-shadow:inset 0 0 0 1px #5B44BD55}.r-chip.is-t{box-shadow:inset 0 0 0 1px #E8762E66}
.r-orb{font-size:12px;color:#6B6380;font-weight:400;margin-left:8px}
.r-more{padding:0}.r-more summary{cursor:pointer;font-family:'Oswald',sans-serif;font-size:22px;text-transform:uppercase;color:#5B44BD;margin-bottom:16px;list-style:none}.r-more summary::before{content:'+ ';}.r-more[open] summary::before{content:'- ';}
@media (max-width:1100px){.r-grid,.r-spheres{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media (max-width:640px){.r-grid,.r-spheres,.r-aspects{grid-template-columns:1fr}.r-h{font-size:34px}
#cookie-bar{left:12px!important;right:12px!important;bottom:12px!important;transform:none!important;max-width:none!important;padding:14px 16px!important;font-size:13px!important;gap:12px!important}}
</style>'''

cookie = ('<div role="region" aria-label="Уведомление о cookie" id="cookie-bar" style="position: fixed; left: 50%; bottom: 24px; transform: translateX(-50%); z-index: 50; display: flex; align-items: center; gap: 20px; max-width: 760px; padding: 16px 20px 16px 24px; border-radius: 22px; background: rgba(255,255,255,0.92); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); box-shadow: 0 20px 50px rgba(75,58,158,0.25); font-family: Manrope, sans-serif; font-size: 14px; line-height: 1.5; color: #2A2340">'
          '<span>Мы используем cookie и сервисы аналитики, чтобы сайт работал лучше. Подробнее в <a href="/privacy#cookies" style="color: #5B44BD">правилах использования cookie</a>.</span>'
          '<button type="button" id="cookie-ok" style="flex: 0 0 auto; min-height: 44px; padding: 0 22px; border: 0; border-radius: 999px; background: #2A2340; color: #FBF8F3; font-family: inherit; font-size: 14px; font-weight: 700; cursor: pointer">Понятно</button></div>'
          '<script>(function(){var b=document.getElementById("cookie-bar");try{if(localStorage.getItem("cookie-ok")){b.remove();return;}}catch(e){}document.getElementById("cookie-ok").onclick=function(){try{localStorage.setItem("cookie-ok","1")}catch(e){}b.remove();};})();</script>')

html = ('<!doctype html>\n<html lang="ru">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<title>Lunarius: спидометр совместимости по натальным картам</title>\n' + FAVICON +
        '<meta name="description" content="Узнайте совместимость пары по натальным картам: введите даты, время и место рождения, и спидометр покажет, где между вами гармония, а где напряжение.">\n'
        + helmet + css + METRIKA + '\n</head>\n<body>\n' + body + cookie + '\n<script src="/app.js" defer></script>\n</body>\n</html>\n')
open(os.path.join(ROOT, 'public/index.html'), 'w', encoding='utf-8').write(html)
print('public/index.html', len(html) // 1024, 'KB')
