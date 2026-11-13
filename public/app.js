(function () {
  'use strict';
  var $ = function (id) { return document.getElementById(id); };
  var cityIds = { 1: null, 2: null };

  // ---------- автоподсказка городов
  function setupCity(k) {
    var input = $('c' + k);
    if (!input) return;
    input.setAttribute('autocomplete', 'off');
    var box = document.createElement('div');
    box.className = 'city-list'; box.setAttribute('role', 'listbox'); box.hidden = true;
    input.parentNode.style.position = 'relative';
    input.parentNode.appendChild(box);
    var timer;
    input.addEventListener('input', function () {
      cityIds[k] = null;
      clearTimeout(timer);
      var q = input.value.trim();
      if (q.length < 2) { box.hidden = true; return; }
      timer = setTimeout(function () {
        fetch('/api/cities?q=' + encodeURIComponent(q)).then(function (r) { return r.json(); }).then(function (list) {
          box.innerHTML = '';
          list.forEach(function (c) {
            var b = document.createElement('button');
            b.type = 'button'; b.className = 'city-item'; b.textContent = c.label;
            b.addEventListener('click', function () { input.value = c.name; cityIds[k] = c.id; box.hidden = true; });
            box.appendChild(b);
          });
          box.hidden = list.length === 0;
        }).catch(function () { box.hidden = true; });
      }, 200);
    });
    document.addEventListener('click', function (e) { if (!box.contains(e.target) && e.target !== input) box.hidden = true; });
  }
  setupCity(1); setupCity(2);

  // ---------- спидометр
  function needleAngle(v) { var f = (1 + Math.sign(v) * Math.sqrt(Math.abs(v) / 10)) / 2; return f * 180; }
  function fmt(v) { return (v > 0 ? '+' : '') + v.toFixed(2); }
  function color(v) { return v < 0 ? '#E8762E' : '#5B44BD'; }
  function setGauge(v, zone) {
    var n = $('needle'), s = $('score'), z = $('verdict');
    if (n) n.setAttribute('transform', 'rotate(' + needleAngle(v).toFixed(1) + ' 160 160)');
    if (s) { s.textContent = fmt(v); s.style.color = color(v); }
    if (z) z.textContent = zone;
  }

  function person(k) {
    return { name: '', date: $('d' + k).value, time: $('t' + k).value || null, cityId: cityIds[k] };
  }

  function esc(t) { var d = document.createElement('div'); d.textContent = t == null ? '' : String(t); return d.innerHTML; }

  function bar(v) {
    var w = Math.abs(v) / 10 * 50, left = v < 0 ? 50 - w : 50;
    return '<div class="sb"><span class="sb-mid"></span><span class="sb-fill" style="left:' + left + '%;width:' + w + '%;background:' + color(v) + '"></span></div>';
  }

  function render(r) {
    setGauge(r.trend.score, r.trend.zone);
    var p = r.partners;
    var who = function (x, i) { return i === 0 ? 'Вы' : 'Партнер'; };
    var signs = function (s) {
      return 'Солнце: ' + esc(s.sun) + ' · Луна: ' + esc(s.moon) + ' · Венера: ' + esc(s.venus) + (s.asc ? ' · Асцендент: ' + esc(s.asc) : '');
    };
    var html = '<h2 class="r-h">Ваш результат</h2>' +
      '<div class="r-grid">' + p.map(function (x, i) {
        return '<div class="r-card"><span class="r-who">' + who(x, i) + '</span>' +
          '<span class="r-score" style="color:' + color(x.score) + '">' + fmt(x.score) + '</span>' +
          '<strong class="r-zone">' + esc(x.zone) + '</strong>' +
          '<p class="r-text">' + (i === 0 ? 'Как карта партнера влияет на вас. ' : 'Как ваша карта влияет на партнера. ') + esc(x.text) + '</p>' +
          '<p class="r-signs">' + signs(x.signs) + '</p></div>';
      }).join('') +
      '<div class="r-card r-trend"><span class="r-who">Общая тенденция</span><span class="r-score" style="color:' + color(r.trend.score) + '">' + fmt(r.trend.score) + '</span><strong class="r-zone">' + esc(r.trend.zone) + '</strong><p class="r-text">' + esc(r.trend.text) + '</p>' + (r.summary ? '<p class="r-text r-summary">' + esc(r.summary) + '</p>' : '') + '</div></div>' +
      shareBar() +
      (r.compare ? '<h3 class="r-sub">Знаки рядом</h3><div class="r-spheres">' + r.compare.map(function (c) {
        var col = c.relation === 'hard' ? '#E8762E' : '#5B44BD';
        return '<div class="r-sphere"><div class="r-sphere-top" style="font-size:18px"><span>' + esc(c.title) + '</span></div><p class="r-cmp">У вас <b style="color:' + col + '">' + esc(c.a) + '</b>, у партнера <b style="color:' + col + '">' + esc(c.b) + '</b></p><p>' + esc(c.text) + '</p></div>';
      }).join('') + '</div>' : '') +
      '<h3 class="r-sub">По сферам</h3><div class="r-spheres">' + r.spheres.map(function (s) {
        var rel = (s.related || []).map(function (x) { return '<button type="button" class="r-chip ' + (x.nature === 'harmony' ? 'is-h' : 'is-t') + '" data-asp="' + esc(x.title) + '" title="Читать описание связи">' + esc(x.title) + '</button>'; }).join('');
        return '<div class="r-sphere"><div class="r-sphere-top"><span>' + esc(s.title) + '</span><b style="color:' + color(s.value) + '">' + fmt(s.value) + '</b></div>' + bar(s.value) + '<p>' + esc(s.text) + '</p>' + (rel ? '<div class="r-chips">' + rel + '</div>' : '') + '</div>';
      }).join('') + '</div>' +
      '<h3 class="r-sub">Главные связи между картами</h3><div class="r-aspects">' + r.aspects.map(function (a) {
        return '<div class="r-aspect ' + (a.nature === 'harmony' ? 'is-h' : 'is-t') + '" data-asp="' + esc(a.title) + '"><strong>' + esc(a.title) + '<span class="r-orb">орбис ' + a.orb.toFixed(1) + '°</span></strong><p class="r-lead">' + esc(a.text) + '</p>' + (a.details || []).map(function (d) { return '<p>' + esc(d) + '</p>'; }).join('') + '</div>';
      }).join('') + '</div>' +
      (r.moreAspects && r.moreAspects.length ? '<details class="r-more"><summary>Остальные связи: еще ' + r.moreAspects.length + '</summary><div class="r-aspects">' + r.moreAspects.map(function (a) {
        return '<div class="r-aspect ' + (a.nature === 'harmony' ? 'is-h' : 'is-t') + '" data-asp="' + esc(a.title) + '"><strong>' + esc(a.title) + '<span class="r-orb">орбис ' + a.orb.toFixed(1) + '°</span></strong><p class="r-lead">' + esc(a.text) + '</p><details class="r-det"><summary>Подробнее</summary>' + (a.details || []).map(function (d) { return '<p>' + esc(d) + '</p>'; }).join('') + '</details></div>';
      }).join('') + '</div></details>' : '') +
      (r.overlays && r.overlays.length ? '<h3 class="r-sub">Планеты в домах друг друга</h3><div class="r-aspects">' + r.overlays.map(function (o) {
        return '<div class="r-card"><span class="r-who">' + esc(o.title) + '</span>' + o.items.map(function (i) { return '<p class="r-text"><b>' + esc(i.planet) + ' в ' + i.house + ' доме.</b> ' + esc(i.text) + '</p>'; }).join('') + '</div>';
      }).join('') + '</div>' : '') +
      (r.note ? '<p class="r-note">' + esc(r.note) + '</p>' : '');
    var box = $('result');
    box.innerHTML = html; box.hidden = false;
    box.scrollIntoView({ behavior: 'smooth', block: 'start' });
    setupShare(r);
    box.querySelectorAll('.r-chip[data-asp]').forEach(function (ch) {
      ch.addEventListener('click', function () {
        var key = ch.getAttribute('data-asp'), card = null;
        box.querySelectorAll('.r-aspect[data-asp]').forEach(function (c) { if (!card && c.getAttribute('data-asp') === key) card = c; });
        if (!card) return;
        var d = card.parentNode; while (d && d !== box) { if (d.tagName === 'DETAILS') d.open = true; d = d.parentNode; }
        var det = card.querySelector('.r-det'); if (det) det.open = true;
        card.scrollIntoView({ behavior: 'smooth', block: 'center' });
        card.classList.remove('is-flash'); void card.offsetWidth; card.classList.add('is-flash');
        try { ym(114224190, 'reachGoal', 'aspect_chip'); } catch (e) {}
      });
    });
  }

  // ---------- поделиться результатом
  var SITE = 'https://lunarius.ru/';
  function goal(ch) { try { ym(114224190, 'reachGoal', 'share_click', { channel: ch }); } catch (e) {} }
  function shareBar() {
    return '<div class="r-share" id="r-share"><div class="r-share-txt"><h3 class="r-sub" style="margin:0">Поделитесь результатом</h3>' +
      '<p class="r-text">Отправьте картинку партнеру или подругам: пусть тоже проверят свои пары.</p>' +
      '<div class="r-share-btns">' +
      '<button type="button" class="sh-main" data-sh="native">Поделиться картинкой</button>' +
      '<button type="button" data-sh="download">Скачать картинку</button>' +
      '<a data-sh="tg" target="_blank" rel="noopener">Telegram</a>' +
      '<a data-sh="vk" target="_blank" rel="noopener">ВКонтакте</a>' +
      '<a data-sh="wa" target="_blank" rel="noopener">WhatsApp</a>' +
      '<button type="button" data-sh="copy">Скопировать ссылку</button>' +
      '</div><p class="r-share-msg" id="r-share-msg" hidden></p></div>' +
      '<div class="r-share-pic"><img id="r-share-img" alt="Картинка с результатом совместимости"></div></div>';
  }
  function shareText(r) {
    return 'Наша совместимость по натальным картам: ' + fmt(r.trend.score) + ', «' + r.trend.zone + '». Проверь свою пару на спидометре совместимости:';
  }
  function roundRect(c, x, y, w, h, rad) { c.beginPath(); c.moveTo(x + rad, y); c.arcTo(x + w, y, x + w, y + h, rad); c.arcTo(x + w, y + h, x, y + h, rad); c.arcTo(x, y + h, x, y, rad); c.arcTo(x, y, x + w, y, rad); c.closePath(); }
  function blob(c, x, y, rad, col) { var g = c.createRadialGradient(x, y, 0, x, y, rad); g.addColorStop(0, col); g.addColorStop(1, 'rgba(251,248,243,0)'); c.fillStyle = g; c.fillRect(0, 0, 1080, 1350); }
  function drawCard(r) {
    var W = 1080, H = 1350, cv = document.createElement('canvas'); cv.width = W; cv.height = H; var c = cv.getContext('2d');
    c.fillStyle = '#FBF8F3'; c.fillRect(0, 0, W, H);
    blob(c, 1080, 0, 800, 'rgba(242,180,120,0.75)'); blob(c, 0, 380, 850, 'rgba(197,178,247,0.85)'); blob(c, 760, 1350, 700, 'rgba(242,118,138,0.45)'); blob(c, 60, 1350, 600, 'rgba(94,139,242,0.3)');
    c.textAlign = 'center'; c.textBaseline = 'alphabetic';
    c.fillStyle = '#2A2340'; c.font = '600 46px Oswald, sans-serif'; c.fillText('L U N A R I U S', W / 2, 110);
    c.fillStyle = '#5B44BD'; c.font = '700 22px Manrope, sans-serif'; c.fillText('С П И Д О М Е Т Р   С О В М Е С Т И М О С Т И', W / 2, 150);
    var title = 'ВЫ + ПАРТНЕР';
    var fs = 92; c.font = '600 ' + fs + 'px Oswald, sans-serif'; while (c.measureText(title).width > 940 && fs > 40) { fs -= 4; c.font = '600 ' + fs + 'px Oswald, sans-serif'; }
    c.fillStyle = '#2A2340'; c.fillText(title, W / 2, 290);
    // стеклянная карточка
    roundRect(c, 70, 350, 940, 830, 56); c.fillStyle = 'rgba(255,255,255,0.62)'; c.fill(); c.lineWidth = 3; c.strokeStyle = 'rgba(255,255,255,0.95)'; c.stroke();
    // дуга спидометра
    var cx = W / 2, cy = 800, R = 330;
    var g = c.createLinearGradient(cx - R, 0, cx + R, 0);
    g.addColorStop(0, '#5E8BF2'); g.addColorStop(0.32, '#9A6BF0'); g.addColorStop(0.5, '#C3A6F5'); g.addColorStop(0.72, '#F2768A'); g.addColorStop(1, '#F7B731');
    c.beginPath(); c.arc(cx, cy, R, Math.PI, 2 * Math.PI); c.lineWidth = 48; c.lineCap = 'round'; c.strokeStyle = g; c.stroke();
    c.lineCap = 'butt'; c.strokeStyle = 'rgba(42,35,64,0.35)'; c.lineWidth = 3;
    for (var i = 0; i <= 10; i++) { var a = Math.PI + i * Math.PI / 10; c.beginPath(); c.moveTo(cx + Math.cos(a) * (R - 44), cy + Math.sin(a) * (R - 44)); c.lineTo(cx + Math.cos(a) * (R - 62), cy + Math.sin(a) * (R - 62)); c.stroke(); }
    // стрелка
    var ang = Math.PI + needleAngle(r.trend.score) * Math.PI / 180, L = R - 70;
    var tx = cx + Math.cos(ang) * L, ty = cy + Math.sin(ang) * L, px = Math.cos(ang + Math.PI / 2) * 14, py = Math.sin(ang + Math.PI / 2) * 14;
    c.save(); c.translate(cx, cy); c.rotate(ang); c.beginPath(); c.moveTo(L, 0); c.lineTo(L - 70, -34); c.lineTo(L - 62, -14); c.lineTo(0, -14); c.lineTo(0, 14); c.lineTo(L - 62, 14); c.lineTo(L - 70, 34); c.closePath(); c.fillStyle = '#2A2340'; c.lineJoin = 'round'; c.lineWidth = 6; c.strokeStyle = '#2A2340'; c.fill(); c.stroke(); c.restore();
    c.fillStyle = '#2A2340'; c.beginPath(); c.arc(cx, cy, 30, 0, 2 * Math.PI); c.fill(); c.fillStyle = '#FBF8F3'; c.beginPath(); c.arc(cx, cy, 10, 0, 2 * Math.PI); c.fill();
    c.fillStyle = '#6B6380'; c.font = '700 26px Manrope, sans-serif'; c.fillText('-10', cx - R, cy + 50); c.fillText('+10', cx + R, cy + 50); c.fillText('0', cx, cy - R - 40);
    // число и зона
    c.fillStyle = color(r.trend.score); c.font = '600 180px Oswald, sans-serif'; c.fillText(fmt(r.trend.score), cx, 1010);
    c.fillStyle = '#2A2340'; c.font = '500 56px Oswald, sans-serif'; c.fillText(String(r.trend.zone).toUpperCase(), cx, 1085);
    var pp = 'для вас: ' + fmt(r.partners[0].score) + '   ·   для партнера: ' + fmt(r.partners[1].score);
    c.fillStyle = '#5E5675'; c.font = '600 30px Manrope, sans-serif'; c.fillText(pp, cx, 1140);
    // призыв
    roundRect(c, 190, 1215, 700, 92, 46); c.fillStyle = '#2A2340'; c.fill();
    c.fillStyle = '#FBF8F3'; c.font = '600 38px Oswald, sans-serif'; c.fillText('ПРОВЕРЬ СВОЮ ПАРУ: LUNARIUS.RU', cx, 1275);
    return cv;
  }
  function setupShare(r) {
    var wrap = $('r-share'); if (!wrap) return;
    var img = $('r-share-img'), msg = $('r-share-msg'), text = shareText(r), cardBlob = null;
    function say(t) { msg.textContent = t; msg.hidden = false; setTimeout(function () { msg.hidden = true; }, 4000); }
    var ready = (document.fonts && document.fonts.load ? Promise.all([document.fonts.load('600 80px Oswald'), document.fonts.load('500 56px Oswald'), document.fonts.load('700 26px Manrope')]) : Promise.resolve())
      .catch(function () {}).then(function () {
        var cv = drawCard(r); img.src = cv.toDataURL('image/png');
        return new Promise(function (res) { cv.toBlob(function (b) { cardBlob = b; res(b); }, 'image/png'); });
      });
    var link = function (ch) { return SITE + '?utm_source=share&utm_medium=' + ch; };
    var enc = encodeURIComponent;
    wrap.querySelector('[data-sh="tg"]').href = 'https://t.me/share/url?url=' + enc(link('telegram')) + '&text=' + enc(text);
    wrap.querySelector('[data-sh="vk"]').href = 'https://vk.com/share.php?url=' + enc(link('vk')) + '&title=' + enc(text);
    wrap.querySelector('[data-sh="wa"]').href = 'https://wa.me/?text=' + enc(text + ' ' + link('whatsapp'));
    function download() {
      ready.then(function (b) { var a = document.createElement('a'); a.href = URL.createObjectURL(b); a.download = 'lunarius-sovmestimost.png'; document.body.appendChild(a); a.click(); a.remove(); setTimeout(function () { URL.revokeObjectURL(a.href); }, 2000); });
    }
    wrap.addEventListener('click', function (e) {
      var t = e.target.closest('[data-sh]'); if (!t) return;
      var ch = t.getAttribute('data-sh'); goal(ch);
      if (ch === 'download') { download(); say('Картинка сохранена'); }
      else if (ch === 'copy') {
        var u = link('copy');
        (navigator.clipboard ? navigator.clipboard.writeText(text + ' ' + u) : Promise.reject()).then(function () { say('Ссылка скопирована'); }, function () { window.prompt('Скопируйте ссылку', u); });
      } else if (ch === 'native') {
        ready.then(function (b) {
          var file = typeof File === 'function' ? new File([b], 'lunarius-sovmestimost.png', { type: 'image/png' }) : null;
          if (file && navigator.canShare && navigator.canShare({ files: [file] })) {
            navigator.share({ files: [file], text: text + ' ' + link('native') }).catch(function () {});
          } else if (navigator.share) {
            navigator.share({ text: text, url: link('native') }).catch(function () {});
          } else { download(); say('На компьютере картинка сохраняется: отправьте ее из папки загрузок'); }
        });
      }
    });
  }

  var btn = $('run');
  var err = $('form-error');
  function showError(t) { if (err) { err.textContent = t; err.hidden = !t; } }
  if (btn) btn.addEventListener('click', function () {
    showError(''); try { ym(114224190, 'reachGoal', 'compat_click'); } catch (e) {}
    var a = person(1), b = person(2);
    if (!a.date || !b.date) return showError('Укажите даты рождения обоих партнеров');
    if (a.cityId == null || b.cityId == null) return showError('Выберите города рождения из списка подсказок');
    if (!$('agree').checked) return showError('Отметьте согласие на обработку персональных данных');
    btn.disabled = true; var old = btn.textContent; btn.textContent = 'Считаем...';
    fetch('/api/compatibility', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ a: a, b: b, consent: true }) })
      .then(function (r) { return r.json().then(function (j) { if (!r.ok) throw new Error(j.error || 'Ошибка'); return j; }); })
      .then(function (j) { try { ym(114224190, 'reachGoal', 'compat_done'); } catch (e) {} return j; })
      .then(render)
      .catch(function (e) { showError(e.message); try { ym(114224190, 'reachGoal', 'compat_error'); } catch (x) {} })
      .finally(function () { btn.disabled = false; btn.textContent = old; });
  });

  // ---------- карусель знаков: крутится сама, тянется мышкой и пальцем
  (function () {
    var ring = document.querySelector('.zring'); if (!ring) return;
    var stage = ring.closest('.zring-stage') || ring.parentNode;
    var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
    ring.style.animation = 'none';
    stage.style.cursor = 'grab'; stage.style.touchAction = 'pan-y'; stage.style.userSelect = 'none';
    stage.querySelectorAll('a, img').forEach(function (el) { el.setAttribute('draggable', 'false'); });
    var angle = 0, vel = 0, hover = false, drag = null, moved = false, last = performance.now();
    var AUTO = -360 / 48; // градусов в секунду, как было в CSS
    function apply() { ring.style.transform = 'rotateX(-8deg) rotateY(' + angle.toFixed(2) + 'deg)'; }
    function tick(t) {
      var dt = Math.min(0.05, (t - last) / 1000); last = t;
      if (!drag) {
        if (Math.abs(vel) > 0.5) { angle += vel * dt; vel *= Math.pow(0.04, dt); }
        else if (!hover && !reduce) { vel = 0; angle += AUTO * dt; }
        apply();
      }
      requestAnimationFrame(tick);
    }
    stage.addEventListener('pointerenter', function () { hover = true; });
    stage.addEventListener('pointerleave', function () { hover = false; });
    stage.addEventListener('pointerdown', function (e) {
      if (e.button !== 0) return;
      drag = { x: e.clientX, y: e.clientY, a: angle, lx: e.clientX, lt: performance.now(), id: e.pointerId, locked: e.pointerType !== 'touch' };
      moved = false; vel = 0;
    });
    window.addEventListener('pointermove', function (e) {
      if (!drag || e.pointerId !== drag.id) return;
      var dx = e.clientX - drag.x, dy = e.clientY - drag.y;
      if (!drag.locked) { if (Math.abs(dy) > Math.abs(dx) && Math.abs(dy) > 8) { drag = null; return; } if (Math.abs(dx) > 8) drag.locked = true; else return; }
      if (Math.abs(dx) > 5 && !moved) { moved = true; stage.style.cursor = 'grabbing'; try { stage.setPointerCapture(e.pointerId); } catch (x) {} }
      angle = drag.a + dx * 0.25;
      var now = performance.now(), dtm = Math.max(1, now - drag.lt);
      vel = (e.clientX - drag.lx) * 0.25 / dtm * 1000; drag.lx = e.clientX; drag.lt = now;
      apply();
    });
    function end() { if (!drag) return; if (performance.now() - drag.lt > 120) vel = 0; drag = null; stage.style.cursor = 'grab'; }
    window.addEventListener('pointerup', end); window.addEventListener('pointercancel', end);
    stage.addEventListener('click', function (e) { if (moved) { e.preventDefault(); e.stopPropagation(); moved = false; } }, true);
    stage.addEventListener('wheel', function (e) {
      var d = Math.abs(e.deltaX) > Math.abs(e.deltaY) ? e.deltaX : (e.shiftKey ? e.deltaY : 0);
      if (!d) return;
      e.preventDefault(); vel = 0; angle -= d * 0.15; apply();
    }, { passive: false });
    apply(); requestAnimationFrame(tick);
  })();
})();
