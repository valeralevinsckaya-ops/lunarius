# Аватар и обложки актуальных для Instagram: public/tpl/ig/*.png
import asyncio, os
from playwright.async_api import async_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'public/tpl/ig'); os.makedirs(OUT, exist_ok=True)

CSS = '''<link href="https://fonts.googleapis.com/css2?family=Oswald:wght@500;600;700&family=Manrope:wght@600;700&display=swap" rel="stylesheet">
<style>
body{margin:0;background:transparent}
.av{position:relative;width:1080px;height:1080px;border-radius:50%;overflow:hidden;background:#FBF8F3;background-image:radial-gradient(70% 55% at 100% 0%,rgba(242,180,120,.85),transparent 70%),radial-gradient(75% 60% at 0% 30%,rgba(197,178,247,.95),transparent 70%),radial-gradient(60% 50% at 70% 100%,rgba(242,118,138,.55),transparent 70%);font-family:'Oswald',sans-serif;color:#2A2340}
.ring{position:absolute;border-radius:50%;border:3px solid rgba(110,86,207,.25)}
.star{position:absolute;color:#D9A93E;font-size:46px;line-height:1}
.gauge{position:absolute;left:190px;top:200px}
.word{position:absolute;left:0;right:0;top:640px;text-align:center;font-size:150px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;line-height:1}
.sub{position:absolute;left:0;right:0;top:810px;text-align:center;font-family:'Manrope',sans-serif;font-size:34px;font-weight:700;letter-spacing:.22em;text-transform:uppercase;color:#5B44BD}
.hl{position:relative;width:1080px;height:1080px;border-radius:50%;overflow:hidden;background:#FBF8F3;background-image:radial-gradient(70% 55% at 100% 0%,rgba(242,180,120,.7),transparent 70%),radial-gradient(75% 60% at 0% 30%,rgba(197,178,247,.85),transparent 70%),radial-gradient(60% 50% at 70% 100%,rgba(242,118,138,.45),transparent 70%);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:28px;font-family:'Oswald',sans-serif;color:#2A2340}
.hl .ic{width:360px;height:360px;display:flex;align-items:center;justify-content:center}
.hl .t{font-size:92px;font-weight:600;letter-spacing:.08em;text-transform:uppercase}
</style>'''

def gauge(w=700, v=0.72):
    import math
    r = w / 2; a = math.pi * (1 - v); nx = r + (r - 40) * math.cos(a); ny = r - (r - 40) * math.sin(a)
    return f'''<svg class="gauge" width="{w}" height="{r + 40}" viewBox="0 0 {w} {r + 40}"><defs><linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="#6E56CF"/><stop offset=".5" stop-color="#F2768A"/><stop offset="1" stop-color="#F2B478"/></linearGradient></defs>
<path d="M 24 {r} A {r - 24} {r - 24} 0 0 1 {w - 24} {r}" fill="none" stroke="url(#g)" stroke-width="40" stroke-linecap="round"/>
<line x1="{r}" y1="{r}" x2="{nx}" y2="{ny}" stroke="#2A2340" stroke-width="14" stroke-linecap="round"/><circle cx="{r}" cy="{r}" r="24" fill="#2A2340"/></svg>'''

AVATAR = f'''<div class="av"><div class="ring" style="width:1300px;height:1300px;right:-520px;top:-420px"></div><div class="ring" style="width:800px;height:800px;left:-380px;bottom:-260px;border-color:rgba(242,118,138,.3)"></div>
<span class="star" style="left:860px;top:230px">✦</span><span class="star" style="left:180px;top:720px;font-size:30px">✦</span><span class="star" style="left:900px;top:760px;font-size:28px;color:#6E56CF">✦</span>
{gauge(700, 0.72)}<div class="word">Lunarius</div><div class="sub">Спидометр совместимости</div></div>'''

ICONS = {
 'speed': ('Спидометр', '<svg width="340" height="200" viewBox="0 0 340 200"><defs><linearGradient id="h" x1="0" x2="1"><stop offset="0" stop-color="#6E56CF"/><stop offset=".5" stop-color="#F2768A"/><stop offset="1" stop-color="#F2B478"/></linearGradient></defs><path d="M20 180 A150 150 0 0 1 320 180" fill="none" stroke="url(#h)" stroke-width="28" stroke-linecap="round"/><line x1="170" y1="180" x2="250" y2="70" stroke="#2A2340" stroke-width="12" stroke-linecap="round"/><circle cx="170" cy="180" r="18" fill="#2A2340"/></svg>'),
 'natal': ('Карта', '<svg width="300" height="300" viewBox="0 0 300 300"><circle cx="150" cy="150" r="140" fill="none" stroke="#6E56CF" stroke-width="10"/><circle cx="150" cy="150" r="100" fill="none" stroke="#6E56CF" stroke-width="6" opacity=".6"/><circle cx="150" cy="150" r="52" fill="none" stroke="#6E56CF" stroke-width="6" opacity=".4"/><line x1="10" y1="150" x2="290" y2="150" stroke="#2A2340" stroke-width="6"/><line x1="150" y1="10" x2="150" y2="290" stroke="#2A2340" stroke-width="6"/><circle cx="222" cy="78" r="14" fill="#D9A93E"/><circle cx="92" cy="214" r="14" fill="#F2768A"/><circle cx="238" cy="190" r="12" fill="#5E8BF2"/></svg>'),
 'signs': ('Знаки', '<div style="font-family:\'Noto Sans Symbols\',\'Segoe UI Symbol\',sans-serif;font-size:150px;line-height:1;color:#6E56CF;display:grid;grid-template-columns:1fr 1fr;gap:10px 40px;text-align:center"><span style="color:#F2768A">♈︎</span><span style="color:#D9A93E">♉︎</span><span style="color:#5E8BF2">♊︎</span><span>♋︎</span></div>'),
 'articles': ('Статьи', '<svg width="260" height="300" viewBox="0 0 260 300"><rect x="20" y="20" width="220" height="260" rx="28" fill="#fff" fill-opacity=".8" stroke="#6E56CF" stroke-width="10"/><line x1="60" y1="90" x2="200" y2="90" stroke="#2A2340" stroke-width="12" stroke-linecap="round"/><line x1="60" y1="140" x2="200" y2="140" stroke="#6E56CF" stroke-width="10" stroke-linecap="round" opacity=".6"/><line x1="60" y1="185" x2="170" y2="185" stroke="#6E56CF" stroke-width="10" stroke-linecap="round" opacity=".6"/><line x1="60" y1="230" x2="190" y2="230" stroke="#6E56CF" stroke-width="10" stroke-linecap="round" opacity=".6"/></svg>'),
 'faq': ('Вопросы', '<div style="font-family:\'Oswald\',sans-serif;font-size:300px;font-weight:600;line-height:1;background:linear-gradient(135deg,#6E56CF,#F2768A);-webkit-background-clip:text;color:transparent">?</div>'),
 'moon': ('Луна', '<svg width="300" height="300" viewBox="0 0 300 300"><path d="M190 20 A130 130 0 1 0 190 280 A100 130 0 0 1 190 20 Z" fill="#6E56CF"/><circle cx="235" cy="70" r="10" fill="#D9A93E"/><circle cx="262" cy="130" r="7" fill="#D9A93E"/><circle cx="240" cy="200" r="8" fill="#F2768A"/></svg>'),
}

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width': 1080, 'height': 1080}, device_scale_factor=1)
        await pg.set_content('<html><head><meta charset="utf-8">' + CSS + '</head><body>' + AVATAR + '</body></html>')
        await pg.wait_for_timeout(1200)
        await pg.screenshot(path=os.path.join(OUT, 'avatar.png'), omit_background=True)
        for key, (title, icon) in ICONS.items():
            await pg.set_content('<html><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Symbols&display=swap" rel="stylesheet">' + CSS + f'</head><body><div class="hl"><div class="ic">{icon}</div><div class="t">{title}</div></div></body></html>')
            await pg.wait_for_timeout(1200)
            await pg.screenshot(path=os.path.join(OUT, f'hl-{key}.png'), omit_background=True)
        await b.close()
asyncio.run(main())
print('ok')
