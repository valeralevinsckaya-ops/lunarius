# Собирает HTML-шаблоны для импорта в Canva: public/tpl/telegram.html (1080x1080) и public/tpl/stories.html (1080x1920)
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'public/tpl'); os.makedirs(OUT, exist_ok=True)
IMG = 'https://lunarius.ru/img/'

CSS = '''
<link href="https://fonts.googleapis.com/css2?family=Oswald:wght@500;600;700&family=Manrope:wght@500;600;700&display=swap" rel="stylesheet">
<style>
body{margin:0;background:#ddd}
.page{position:relative;overflow:hidden;font-family:'Manrope',sans-serif;color:#2A2340;margin:0 0 24px}
.bg{position:absolute;inset:0;background:#FBF8F3;background-image:radial-gradient(70% 55% at 100% 0%,rgba(242,180,120,.75),transparent 70%),radial-gradient(75% 60% at 0% 25%,rgba(197,178,247,.85),transparent 70%),radial-gradient(60% 50% at 70% 100%,rgba(242,118,138,.45),transparent 70%),radial-gradient(55% 45% at 5% 100%,rgba(94,139,242,.35),transparent 70%)}
.ring{position:absolute;border-radius:50%;border:2px solid rgba(110,86,207,.22)}
.star{position:absolute;color:#D9A93E;font-size:40px;line-height:1}
.logo{position:absolute;left:72px;top:64px;font-family:'Oswald',sans-serif;font-weight:600;font-size:34px;letter-spacing:.08em;text-transform:uppercase;color:#2A2340}
.logo small{display:block;font-family:'Manrope',sans-serif;font-size:14px;letter-spacing:.14em;font-weight:700;color:#5B44BD}
.url{position:absolute;right:72px;top:72px;font-size:22px;font-weight:700;color:#5B44BD}
.tag{position:absolute;padding:10px 22px;border-radius:999px;background:#E2D5FA;font-size:18px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:#3E2C8F}
.glass{position:absolute;border-radius:48px;background:rgba(255,255,255,.62);border:2px solid rgba(255,255,255,.95);box-shadow:0 40px 90px rgba(62,44,143,.22)}
.h{position:absolute;margin:0;font-family:'Oswald',sans-serif;font-weight:600;text-transform:uppercase;line-height:1.02;color:#2A2340}
.h em{font-style:normal;color:#6E56CF}
.p{position:absolute;margin:0;font-size:30px;line-height:1.4;font-weight:500;color:#4A4260}
.num{position:absolute;margin:0;font-family:'Oswald',sans-serif;font-weight:600;line-height:1;color:#5B44BD}
.btn{position:absolute;padding:0 44px;height:84px;line-height:84px;border-radius:999px;background:#2A2340;color:#FBF8F3;font-family:'Oswald',sans-serif;font-size:30px;font-weight:500;letter-spacing:.06em;text-transform:uppercase}
.img{position:absolute;object-fit:cover;border-radius:40px}
.arc{position:absolute}
.foot{position:absolute;left:72px;bottom:56px;font-size:20px;font-weight:700;color:#5B44BD}
</style>'''

def gauge(x, y, w, v=0.72, color='#5B44BD'):
    return f'<img src="https://lunarius.ru/tpl/gauge-{w}.png" style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{w // 2 + 20}px">'

def gauge_svg(x, y, w, v=0.72, color='#5B44BD'):
    # полукруг спидометра, v от 0 до 1 задает угол стрелки
    import math
    r = w / 2; cx = x + r; cy = y + r
    a = math.pi * (1 - v); nx = cx + (r - 30) * math.cos(a); ny = cy - (r - 30) * math.sin(a)
    return f'''<svg class="arc" style="left:{x}px;top:{y}px" width="{w}" height="{r + 20}" viewBox="0 0 {w} {r + 20}">
<defs><linearGradient id="g{x}{y}" x1="0" x2="1"><stop offset="0" stop-color="#6E56CF"/><stop offset=".5" stop-color="#F2768A"/><stop offset="1" stop-color="#F2B478"/></linearGradient></defs>
<path d="M 16 {cy - y} A {r - 16} {r - 16} 0 0 1 {w - 16} {cy - y}" fill="none" stroke="url(#g{x}{y})" stroke-width="26" stroke-linecap="round"/>
<line x1="{r}" y1="{cy - y}" x2="{nx - x}" y2="{ny - y}" stroke="#2A2340" stroke-width="8" stroke-linecap="round"/>
<circle cx="{r}" cy="{cy - y}" r="14" fill="#2A2340"/></svg>'''

def deco(w, h):
    return f'<img src="https://lunarius.ru/tpl/bg-{"post" if h == w else "story"}.png" style="position:absolute;left:0;top:0;width:{w}px;height:{h}px">'

def deco_css(w, h):
    return (f'<div class="bg"></div><div class="ring" style="width:{int(w*.9)}px;height:{int(w*.9)}px;right:-{int(w*.35)}px;top:-{int(w*.25)}px"></div>'
            f'<div class="ring" style="width:{int(w*.6)}px;height:{int(w*.6)}px;left:-{int(w*.25)}px;bottom:-{int(w*.15)}px;border-color:rgba(242,118,138,.25)"></div>'
            f'<span class="star" style="left:{int(w*.82)}px;top:{int(h*.18)}px">✦</span><span class="star" style="left:{int(w*.12)}px;top:{int(h*.72)}px;font-size:28px">✦</span><span class="star" style="left:{int(w*.9)}px;top:{int(h*.6)}px;font-size:24px;color:#6E56CF">✦</span>')

def head(w):
    return '<div class="logo">Lunarius<small>Спидометр совместимости</small></div><div class="url">lunarius.ru</div>'

# ---------- посты 1080x1080
W = H = 1080
posts = []
# 1. Анонс статьи
posts.append(('Анонс статьи', deco(W, H) + head(W) +
    '<span class="tag" style="left:72px;top:200px">Статья</span>'
    '<h1 class="h" style="left:72px;top:270px;width:900px;font-size:96px">Луна <em>в синастрии</em></h1>'
    '<p class="p" style="left:72px;top:600px;width:560px;font-size:34px">Почему с одними уютно, а с другими нет. Разбираем соединение, квадрат и оппозицию Лун.</p>'
    '<span class="btn" style="left:72px;top:800px">Читать на lunarius.ru</span>'
    f'<img class="img" src="{IMG}cancer.webp" style="right:40px;bottom:60px;width:360px;height:440px;border-radius:40px">'))
# 2. Факт / карточка знания
posts.append(('Факт', deco(W, H) + head(W) +
    '<div class="glass" style="left:72px;top:190px;width:936px;height:780px"></div>'
    '<span class="tag" style="left:128px;top:250px">Знаете ли вы</span>'
    '<h1 class="h" style="left:128px;top:330px;width:830px;font-size:72px">Луна проходит знак <em>за 2,5 дня</em></h1>'
    '<p class="p" style="left:128px;top:600px;width:820px">Поэтому без времени рождения знак Луны может быть соседним. Для расчета быта в паре время нужно обоим.</p>'
    '<span class="foot" style="left:128px;bottom:150px">#натальнаякарта #синастрия</span>'))
# 3. Пара знаков
posts.append(('Пара знаков', deco(W, H) + head(W) +
    f'<img class="img" src="{IMG}leo.webp" style="left:72px;top:190px;width:440px;height:520px">'
    f'<img class="img" src="{IMG}aquarius.webp" style="left:568px;top:190px;width:440px;height:520px">'
    '<div class="num" style="left:484px;top:394px;width:112px;height:112px;line-height:112px;border-radius:50%;background:#2A2340;text-align:center;font-size:72px;color:#FBF8F3;box-shadow:0 10px 30px rgba(42,35,64,.35)">+</div>'
    '<h1 class="h" style="left:72px;top:760px;width:936px;font-size:76px">Лев <em>и Водолей</em></h1>'
    '<p class="p" style="left:72px;top:860px;width:936px;font-size:30px">Противоположности: спор «я» и «мы», из которого вырастают яркие пары. Проверьте свою пару по натальным картам.</p>'))
# 4. Результат спидометра
posts.append(('Результат спидометра', deco(W, H) + head(W) +
    '<div class="glass" style="left:72px;top:190px;width:936px;height:800px"></div>'
    '<span class="tag" style="left:128px;top:250px">Спидометр совместимости</span>'
    + gauge(240, 300, 600, 0.78) +
    '<div class="num" style="left:0;top:600px;width:1080px;text-align:center;font-size:130px">+2.07</div>'
    '<h1 class="h" style="left:0;top:760px;width:1080px;text-align:center;font-size:52px">Сильная связь</h1>'
    '<p class="p" style="left:0;top:850px;width:1080px;text-align:center;font-size:28px">Расчет по двум натальным картам: бесплатно, за минуту</p>'))
# 5. Вопрос
posts.append(('Вопрос', deco(W, H) + head(W) +
    '<span class="tag" style="left:72px;top:200px">Вопрос</span>'
    '<h1 class="h" style="left:72px;top:280px;width:936px;font-size:88px">Какой у вас <em>Асцендент?</em></h1>'
    '<p class="p" style="left:72px;top:620px;width:860px;font-size:32px">Напишите в комментариях знак. Если не знаете, считается за минуту по дате, времени и городу рождения.</p>'
    '<span class="btn" style="left:72px;top:840px">lunarius.ru/natal</span>'))

# ---------- сторис 1080x1920
SW, SH = 1080, 1920
stories = []
stories.append(('Анонс статьи', deco(SW, SH) + head(SW) +
    f'<img class="img" src="{IMG}pisces.webp" style="left:72px;top:260px;width:936px;height:760px;border-radius:56px">'
    '<span class="tag" style="left:72px;top:1080px">Новая статья</span>'
    '<h1 class="h" style="left:72px;top:1160px;width:936px;font-size:96px">Луна <em>в синастрии</em></h1>'
    '<p class="p" style="left:72px;top:1480px;width:900px;font-size:34px">Почему с одними уютно, а с другими нет</p>'
    '<span class="btn" style="left:72px;top:1640px">Читать: ссылка в профиле</span>'))
stories.append(('Результат', deco(SW, SH) + head(SW) +
    '<div class="glass" style="left:72px;top:330px;width:936px;height:1160px"></div>'
    '<span class="tag" style="left:128px;top:400px">Спидометр совместимости</span>'
    + gauge(240, 500, 600, 0.78) +
    '<div class="num" style="left:0;top:860px;width:1080px;text-align:center;font-size:170px">+2.07</div>'
    '<h1 class="h" style="left:0;top:1060px;width:1080px;text-align:center;font-size:64px">Сильная связь</h1>'
    '<p class="p" style="left:128px;top:1180px;width:824px;text-align:center;font-size:32px">Лера + Иван. Притяжение +4,1, эмоции +1,8, общение +0,6</p>'
    '<span class="btn" style="left:270px;top:1600px">Проверить свою пару</span>'))
stories.append(('Факт дня', deco(SW, SH) + head(SW) +
    '<span class="tag" style="left:72px;top:420px">Факт дня</span>'
    '<h1 class="h" style="left:72px;top:520px;width:936px;font-size:110px">Асцендент меняется <em>каждые 2 часа</em></h1>'
    '<p class="p" style="left:72px;top:1180px;width:900px;font-size:36px">Люди, родившиеся в один день утром и вечером, выглядят и входят в новое по-разному.</p>'
    '<span class="foot" style="bottom:120px;font-size:26px">lunarius.ru/natal</span>'))
stories.append(('Опрос', deco(SW, SH) + head(SW) +
    f'<img class="img" src="{IMG}scorpio.webp" style="left:290px;top:260px;width:500px;height:600px;border-radius:250px 250px 56px 56px">'
    '<h1 class="h" style="left:72px;top:940px;width:936px;text-align:center;font-size:88px">Скорпион: <em>да или нет?</em></h1>'
    '<p class="p" style="left:120px;top:1260px;width:840px;text-align:center;font-size:34px">Место для стикера-опроса. Ответ в следующей сторис: с кем Скорпиону легко, а с кем война.</p>'
    '<div class="glass" style="left:240px;top:1480px;width:600px;height:120px;border-radius:999px"></div>'
    '<p class="p" style="left:240px;top:1510px;width:600px;text-align:center;font-size:34px;font-weight:700;color:#5B44BD">Опрос здесь</p>'))
stories.append(('Призыв', deco(SW, SH) + head(SW) +
    '<h1 class="h" style="left:72px;top:420px;width:936px;font-size:120px">Проверь <em>совместимость</em> по натальным картам</h1>'
    '<p class="p" style="left:72px;top:1120px;width:900px;font-size:36px">Две даты рождения, время и город. Стрелка покажет результат для каждого из вас отдельно.</p>'
    + gauge(340, 1300, 400, 0.62) +
    '<span class="btn" style="left:300px;top:1680px">lunarius.ru</span>'))

def build(name, pages, w, h):
    html = '<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>%s</title>%s</head><body>' % (name, CSS)
    for label, body in pages:
        html += f'<div class="page" data-document-role="page" data-label="{label}" style="width:{w}px;height:{h}px">{body}</div>\n'
    html += '</body></html>'
    assert 'ё' not in html and '—' not in html
    open(os.path.join(OUT, name + '.html'), 'w', encoding='utf-8').write(html)

build('telegram', posts, W, H)
build('stories', stories, SW, SH)
print('ok', len(posts), len(stories))
