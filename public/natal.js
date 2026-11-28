(function () {
  'use strict';
  var $ = function (id) { return document.getElementById(id); };
  var cityId = null;

  // ---------- автоподсказка городов
  (function setupCity() {
    var input = $('c1');
    var box = document.createElement('div');
    box.className = 'city-list'; box.setAttribute('role', 'listbox'); box.hidden = true;
    input.parentNode.appendChild(box);
    var timer;
    input.addEventListener('input', function () {
      cityId = null; clearTimeout(timer);
      var q = input.value.trim();
      if (q.length < 2) { box.hidden = true; return; }
      timer = setTimeout(function () {
        fetch('/api/cities?q=' + encodeURIComponent(q)).then(function (r) { return r.json(); }).then(function (list) {
          box.innerHTML = '';
          list.forEach(function (c) {
            var b = document.createElement('button');
            b.type = 'button'; b.className = 'city-item'; b.textContent = c.label;
            b.addEventListener('click', function () { input.value = c.name; cityId = c.id; box.hidden = true; });
            box.appendChild(b);
          });
          box.hidden = list.length === 0;
        }).catch(function () { box.hidden = true; });
      }, 200);
    });
    document.addEventListener('click', function (e) { if (!box.contains(e.target) && e.target !== input) box.hidden = true; });
  })();

  function esc(t) { var d = document.createElement('div'); d.textContent = t == null ? '' : String(t); return d.innerHTML; }
  var SIGN_IDX = { aries: 0, taurus: 1, gemini: 2, cancer: 3, leo: 4, virgo: 5, libra: 6, scorpio: 7, sagittarius: 8, capricorn: 9, aquarius: 10, pisces: 11 };
  function sgl(k) { return k in SIGN_IDX ? '<span class="gl">' + SIGN_GLYPH[SIGN_IDX[k]] + '\uFE0E</span>' : ''; }
  function planetsTable(r) {
    var h = '';
    var rows = r.planets.map(function (p) {
      return '<tr><td><span class="gl" style="color:' + PCOLOR[p.key] + '">' + GLYPH[p.key] + '</span> ' + (p.more ? '<a href="' + p.more.url + '">' + esc(p.name) + '</a>' : esc(p.name)) + (p.retro ? ' <span class="retro">R</span>' : '') + '</td><td>' + sgl(p.sign) + ' ' + esc(p.signName) + '</td><td class="num">' + esc(p.degree) + '</td><td class="num">' + (p.house || '') + '</td></tr>';
    }).join('');
    rows += '<tr><td><span class="gl">☊</span> Сев. узел</td><td>' + sgl(r.node.sign) + ' ' + esc(r.node.signName) + '</td><td class="num">' + esc(r.node.degree) + '</td><td class="num">' + (r.node.house || '') + '</td></tr>';
    if (r.big3.asc) {
      rows += '<tr><td><span class="gl">AC</span> <a href="' + r.big3.asc.url + '">Асцендент</a></td><td>' + sgl(r.big3.asc.signKey) + ' ' + esc(r.big3.asc.sign) + '</td><td class="num">' + esc(r.big3.asc.degree) + '</td><td class="num">1</td></tr>';
      rows += '<tr><td><span class="gl">MC</span> Середина неба</td><td>' + sgl(r.big3.mc.signKey) + ' ' + esc(r.big3.mc.sign) + '</td><td class="num">' + esc(r.big3.mc.degree) + '</td><td class="num">10</td></tr>';
    }
    return '<div class="ctbl"><table><caption>Планеты</caption><tr><th>Планета</th><th>Знак</th><th>Градус</th><th>Дом</th></tr>' + rows + '</table></div>';
  }
  function housesTable(r) {
    var h = '';
    if (r.houses) {
      var ANG = { 1: ' (AC)', 4: ' (IC)', 7: ' (DC)', 10: ' (MC)' };
      h += '<div class="ctbl"><table><caption>Дома (Плацидус)</caption><tr><th>Дом</th><th>Куспид</th><th>Управитель</th><th>Дом упр.</th></tr>' + r.houses.map(function (x) {
        return '<tr><td><a href="' + x.url + '">' + x.n + ' дом</a>' + (ANG[x.n] || '') + '</td><td>' + sgl(x.signKey) + ' ' + esc(x.cuspSign) + ' <span class="num">' + esc(x.cusp) + '</span></td><td>' + esc(x.rulerName || '') + '</td><td class="num">' + (x.rulerHouse || '') + '</td></tr>';
      }).join('') + '</table></div>';
    } else {
      h += '<div class="ctbl"><table><caption>Дома</caption><tr><td style="white-space:normal">Без времени рождения дома и Асцендент не рассчитываются.</td></tr></table></div>';
    }
    return h;
  }
  function aspectsTable(r) {
    var h = '';
    if (r.aspects.length) {
      h += '<div class="ctbl"><table><caption>Аспекты</caption><tr><th>Планета</th><th>Аспект</th><th>Планета</th><th>Орбис</th></tr>' + r.aspects.map(function (a) {
        var c = a.nature === 'harmony' ? 'is-h' : a.nature === 'tension' ? 'is-t' : 'is-c';
        return '<tr><td>' + esc(a.a) + '</td><td class="' + c + '">' + esc(a.type) + '</td><td>' + esc(a.b) + '</td><td class="num">' + a.orb.toFixed(1).replace('.', ',') + '°</td></tr>';
      }).join('') + '</table></div>';
    }
    return h;
  }
  function link(url, text) { return url && text ? '<a class="plink" href="' + url + '">' + esc(text) + '</a>' : ''; }
  function moreHtml(m) {
    if (!m) return '';
    var h = '<div class="pmore">';
    if (m.goal) h += '<p class="ptext">' + esc(m.goal) + '</p>';
    if (m.plus) h += '<p class="ptext">' + esc(m.plus) + '</p>';
    if (m.advice) h += '<p class="ptext">Совет: ' + esc(m.advice) + '</p>';
    if (m.woman || m.man) h += '<details><summary>У женщины и у мужчины</summary>' + (m.woman ? '<p>' + esc(m.woman) + '</p>' : '') + (m.man ? '<p>' + esc(m.man) + '</p>' : '') + '</details>';
    h += '<a class="plink" href="' + m.url + '">' + esc(m.label) + '</a></div>';
    return h;
  }

  // ---------- колесо карты
  var GLYPH = { sun: '☉', moon: '☽', mercury: '☿', venus: '♀', mars: '♂', jupiter: '♃', saturn: '♄', uranus: '♅', neptune: '♆', pluto: '♇' };
  var SIGN_GLYPH = ['♈', '♉', '♊', '♋', '♌', '♍', '♎', '♏', '♐', '♑', '♒', '♓'];
  var ELEM_COLOR = ['#F2768A', '#D9A93E', '#5E8BF2', '#6E56CF'];
  var PCOLOR = { sun: '#D9A93E', moon: '#5E8BF2', mercury: '#6E56CF', venus: '#F2768A', mars: '#E8762E', jupiter: '#8C5FD6', saturn: '#2A2340', uranus: '#5E8BF2', neptune: '#6E56CF', pluto: '#2A2340' };

  function wheel(w) {
    var cx = 260, cy = 260, asc = w.asc == null ? 0 : w.asc;
    function pt(lon, r) { var a = (180 + (lon - asc)) * Math.PI / 180; return [cx + r * Math.cos(a), cy - r * Math.sin(a)]; }
    function arc(r1, r2, l1, l2, fill) {
      var p1 = pt(l1, r2), p2 = pt(l2, r2), p3 = pt(l2, r1), p4 = pt(l1, r1);
      return '<path d="M' + p1[0] + ' ' + p1[1] + ' A' + r2 + ' ' + r2 + ' 0 0 0 ' + p2[0] + ' ' + p2[1] + ' L' + p3[0] + ' ' + p3[1] + ' A' + r1 + ' ' + r1 + ' 0 0 1 ' + p4[0] + ' ' + p4[1] + ' Z" fill="' + fill + '" stroke="#fff" stroke-width="1"/>';
    }
    var s = '<svg class="wheel" viewBox="0 0 520 520" role="img" aria-label="Колесо натальной карты">';
    s += '<circle cx="260" cy="260" r="252" fill="rgba(255,255,255,0.55)" stroke="#fff" stroke-width="2"/>';
    for (var i = 0; i < 12; i++) {
      s += arc(216, 250, i * 30, i * 30 + 30, ELEM_COLOR[i % 4] + '33');
      var g = pt(i * 30 + 15, 233);
      s += '<text x="' + g[0] + '" y="' + g[1] + '" text-anchor="middle" dominant-baseline="central" font-size="18" fill="' + ELEM_COLOR[i % 4] + '">' + SIGN_GLYPH[i] + '</text>';
    }
    s += '<circle cx="260" cy="260" r="216" fill="none" stroke="#D8CDEE"/>';
    s += '<circle cx="260" cy="260" r="120" fill="rgba(255,255,255,0.5)" stroke="#D8CDEE"/>';
    if (w.cusps) {
      for (var h = 0; h < 12; h++) {
        var a1 = pt(w.cusps[h], 120), a2 = pt(w.cusps[h], 216);
        var strong = h === 0 || h === 3 || h === 6 || h === 9;
        s += '<line x1="' + a1[0] + '" y1="' + a1[1] + '" x2="' + a2[0] + '" y2="' + a2[1] + '" stroke="' + (strong ? '#2A2340' : '#B9ABDD') + '" stroke-width="' + (strong ? 2 : 1) + '"/>';
        var mid = pt((w.cusps[h] + ((w.cusps[(h + 1) % 12] - w.cusps[h] + 360) % 360) / 2) % 360, 132);
        s += '<text x="' + mid[0] + '" y="' + mid[1] + '" text-anchor="middle" dominant-baseline="central" font-size="11" fill="#6B6380">' + (h + 1) + '</text>';
      }
      var ap = pt(w.asc, 262); s += '<text x="' + ap[0] + '" y="' + ap[1] + '" text-anchor="end" dominant-baseline="central" font-size="11" font-weight="700" fill="#2A2340">ASC</text>';
      var mp = pt(w.mc, 262); s += '<text x="' + mp[0] + '" y="' + (mp[1] - 2) + '" text-anchor="middle" font-size="11" font-weight="700" fill="#2A2340">MC</text>';
    } else {
      var a0 = pt(0, 120), b0 = pt(0, 216);
      s += '<line x1="' + a0[0] + '" y1="' + a0[1] + '" x2="' + b0[0] + '" y2="' + b0[1] + '" stroke="#B9ABDD"/>';
    }
    // аспекты
    (w.aspects || []).forEach(function (x) {
      var p1 = pt(x.la, 118), p2 = pt(x.lb, 118);
      var col = x.nature === 'harmony' ? '#5B44BD' : x.nature === 'tension' ? '#E8762E' : '#D9A93E';
      s += '<line x1="' + p1[0] + '" y1="' + p1[1] + '" x2="' + p2[0] + '" y2="' + p2[1] + '" stroke="' + col + '" stroke-width="1.2" opacity="0.7"/>';
    });
    // планеты с разведением
    var ps = w.planets.slice().sort(function (a, b) { return a.lon - b.lon; });
    var lastLon = -99, level = 0;
    ps.forEach(function (p) {
      var d = p.lon - lastLon; if (d < 0) d += 360;
      level = d < 7 ? (level + 1) % 3 : 0; lastLon = p.lon;
      var r = 178 - level * 22;
      var q = pt(p.lon, r), tick = pt(p.lon, 216), tick2 = pt(p.lon, 208);
      s += '<line x1="' + tick[0] + '" y1="' + tick[1] + '" x2="' + tick2[0] + '" y2="' + tick2[1] + '" stroke="' + PCOLOR[p.key] + '" stroke-width="2"/>';
      s += '<circle cx="' + q[0] + '" cy="' + q[1] + '" r="13" fill="#fff" stroke="' + PCOLOR[p.key] + '" stroke-width="1.5"/>';
      s += '<text x="' + q[0] + '" y="' + q[1] + '" text-anchor="middle" dominant-baseline="central" font-size="15" fill="' + PCOLOR[p.key] + '">' + GLYPH[p.key] + (p.retro ? '<tspan font-size="8" dy="-6">R</tspan>' : '') + '</text>';
    });
    s += '</svg>';
    return s;
  }

  function render(r) {
    var html = '<h2 class="r-h">' + 'Ваша натальная карта' + '</h2>';
    // большая тройка
    html += '<div class="g4">';
    html += '<div class="card"><span class="who">Солнце</span><div class="big">' + esc(r.big3.sun.sign) + '</div><p>' + esc(r.big3.sun.text) + '</p>' + link(r.big3.sun.url, r.big3.sun.link) + '</div>';
    html += '<div class="card"><span class="who">Луна</span><div class="big">' + esc(r.big3.moon.sign) + '</div><p>' + esc(r.big3.moon.text) + (r.timeKnown ? '' : ' Без времени рождения знак Луны может быть соседним.') + '</p>' + link(r.big3.moon.url, r.big3.moon.link) + '</div>';
    if (r.big3.asc) {
      html += '<div class="card"><span class="who">Асцендент</span><div class="big">' + esc(r.big3.asc.sign) + '<small>' + esc(r.big3.asc.degree) + '</small></div><p>' + esc(r.big3.asc.text) + '</p>' + link(r.big3.asc.url, r.big3.asc.link) + '</div>';
      html += '<div class="card"><span class="who">Середина неба</span><div class="big">' + esc(r.big3.mc.sign) + '<small>' + esc(r.big3.mc.degree) + '</small></div><p>' + esc(r.big3.mc.text) + '</p></div>';
    } else {
      html += '<div class="card" style="grid-column: span 2"><span class="who">Асцендент и дома</span><div class="big">Нужно время</div><p>Асцендент меняется каждые два часа. Укажите время рождения, и появятся Асцендент, Середина неба, дома и аспекты к ним.</p></div>';
    }
    html += '</div>';
    if (r.portrait && r.portrait.length) html += '<h3 class="r-sub">Портрет по карте</h3><div class="card portrait">' + r.portrait.map(function (t) { return '<p>' + esc(t) + '</p>'; }).join('') + '</div>';
    // колесо и планеты
    var lonOf = {}; r.planets.forEach(function (p) { lonOf[p.name] = p.lon; });
    if (r.big3.asc) { lonOf['Асцендент'] = r.wheel.asc; lonOf['Середина неба'] = r.wheel.mc; }
    var aspLines = r.aspects.filter(function (a) { return a.orb <= 4; }).map(function (a) { return { la: lonOf[a.a], lb: lonOf[a.b], nature: a.nature }; });
    html += '<div class="wheel-wrap"><div class="card wheel-card" style="padding:16px 16px 12px">' + (r.svg || wheel({ planets: r.wheel.planets, cusps: r.wheel.cusps, asc: r.wheel.asc, mc: r.wheel.mc, aspects: aspLines })) + '<p class="wheel-cap" id="wheel-cap">Наведите на знак, чтобы увидеть планеты в нем</p></div>';
    html += '<div class="card pscroll" id="pscroll"><span class="who">Расшифровка планет</span><div class="plist">' + r.planets.map(function (p) {
      return '<div class="prow"><b style="color:' + PCOLOR[p.key] + '">' + esc(p.name) + '</b><span class="pos">' + esc(p.signName) + ' ' + esc(p.degree) + (p.retro ? '<span class="retro">R</span>' : '') + '</span><span class="house">' + (p.house ? p.house + ' дом' : '') + '</span><p class="pabout">' + esc(p.about || '') + '</p><p class="ptext">' + esc(p.signText) + (p.elemText ? ' ' + esc(p.elemText) : '') + (p.dignity ? ' ' + esc(p.dignity) : '') + '</p>' + (p.houseText ? '<p class="ptext">' + esc(p.houseText) + '</p>' : '') + (p.retroText ? '<p class="ptext">' + esc(p.retroText) + '</p>' : '') + moreHtml(p.more) + '</div>';
    }).join('') + '<div class="prow"><b>Сев. узел</b><span class="pos">' + esc(r.node.signName) + ' ' + esc(r.node.degree) + '</span><span class="house">' + (r.node.house ? r.node.house + ' дом' : '') + '</span><p class="pabout">Северный узел показывает направление развития: качества, которые нужно осваивать в течение жизни.</p><p class="ptext">' + esc(r.node.text || '') + '</p></div></div></div></div>';
    html += '<div class="g2 tables2">' + planetsTable(r) + housesTable(r) + '</div>' + (r.aspects.length ? '<div class="tables2">' + aspectsTable(r) + '</div>' : '');
    // стихии
    var names = { fire: 'Огонь', earth: 'Земля', air: 'Воздух', water: 'Вода' }, cols = { fire: '#F2768A', earth: '#D9A93E', air: '#5E8BF2', water: '#6E56CF' };
    html += '<div class="card"><span class="who">Баланс стихий</span><div class="bal" style="margin-top:10px">' + Object.keys(r.balance.count).map(function (k) { return '<span><i style="background:' + cols[k] + '"></i>' + names[k] + ': ' + r.balance.count[k] + '</span>'; }).join('') + '</div>' + (r.balance.notes.length ? '<p style="margin-top:12px">' + r.balance.notes.map(esc).join(' ') + '</p>' : '<p style="margin-top:12px">Стихии распределены ровно: ни одна не перевешивает.</p>') + (r.balance.modes ? '<div class="bal" style="margin-top:14px"><span>Кардинальные: ' + r.balance.modes.cardinal + '</span><span>Фиксированные: ' + r.balance.modes.fixed + '</span><span>Мутабельные: ' + r.balance.modes.mutable + '</span></div><p style="margin-top:12px">' + (r.balance.modeNotes.length ? r.balance.modeNotes.map(esc).join(' ') : 'Кресты распределены ровно: вы умеете и начинать, и удерживать, и меняться.') + '</p>' : '') + ((r.balance.hemi || []).length ? '<p style="margin-top:12px">' + r.balance.hemi.map(esc).join(' ') + '</p>' : '') + '</div>';
    // дома
    if (r.houses) {
      html += '<h3 class="r-sub">Дома</h3><div class="g4">' + r.houses.map(function (h) {
        return '<div class="card hcard"><div class="n">' + h.n + ' дом · ' + esc(h.title) + '</div><div class="cs">' + esc(h.cuspSign) + ' ' + esc(h.cusp) + '</div><p>' + esc(h.theme.charAt(0).toUpperCase() + h.theme.slice(1)) + '.</p>' + (h.planets.length ? '<div class="pl">' + h.planets.map(esc).join(', ') + '</div>' : '<div class="pl" style="color:#6B6380">Планет нет</div>') + (h.ruler ? '<p class="hr">' + esc(h.ruler) + (h.empty ? ' ' + esc(h.empty) : '') + '</p>' : '') + (h.url ? '<a class="plink" href="' + h.url + '">Подробнее о ' + h.n + ' доме</a>' : '') + '</div>';
      }).join('') + '</div>';
    }
    // аспекты
    html += '<h3 class="r-sub">Аспекты</h3><div class="g2">' + r.aspects.map(function (a) {
      return '<div class="card asp ' + (a.nature === 'harmony' ? 'is-h' : a.nature === 'tension' ? 'is-t' : 'is-c') + '"><strong>' + esc(a.a) + ' ' + esc(a.type) + ' ' + esc(a.b) + '<span class="orb">орбис ' + a.orb.toFixed(1) + '°</span></strong><p>' + esc(a.text) + '</p>' + (a.more ? '<p class="amore">' + esc(a.more) + '</p>' : '') + '</div>';
    }).join('') + '</div>';
    html += '<p class="note">' + esc(r.note) + ' Орбисы: соединение 8°, трин и оппозиция 7°, квадрат 6°, секстиль 5°, для Солнца и Луны на 1,5° шире. Чем меньше орбис, тем сильнее аспект.</p>';
    var box = $('result'); box.innerHTML = html; box.hidden = false;
    box.scrollIntoView({ behavior: 'smooth', block: 'start' });
    // блок расшифровки рядом с колесом: высота как у колеса, прокручивается отдельно
    var ps = $('pscroll'), wc = box.querySelector('.wheel-card');
    function fitPs() { if (!ps || !wc) return; ps.style.maxHeight = window.innerWidth > 1100 ? wc.offsetHeight + 'px' : ''; }
    fitPs(); window.addEventListener('resize', fitPs);
    // наведение на знак: увеличение сектора и подпись
    var cap = $('wheel-cap'), groups = box.querySelectorAll('.sg');
    function on(g) { groups.forEach(function (x) { x.classList.remove('on'); }); g.parentNode.appendChild(g); g.classList.add('on'); if (cap) cap.textContent = g.getAttribute('data-title'); }
    function off(g) { g.classList.remove('on'); }
    groups.forEach(function (g) {
      g.addEventListener('mouseenter', function () { on(g); });
      g.addEventListener('mouseleave', function () { off(g); });
      g.addEventListener('click', function (e) { e.stopPropagation(); if (g.classList.contains('on')) off(g); else on(g); });
    });
  }

  var btn = $('run'), err = $('form-error');
  function showError(t) { err.textContent = t; err.hidden = !t; }
  btn.addEventListener('click', function () {
    showError(''); try { ym(114224190, 'reachGoal', 'natal_click'); } catch (e) {}
    var p = { name: '', date: $('d1').value, time: ($('tu1') && $('tu1').checked) ? null : ($('t1').value || null), cityId: cityId };
    if (!p.date) return showError('Укажите дату рождения');
    if (p.cityId == null) return showError('Выберите город рождения из списка подсказок');
    if (!$('agree').checked) return showError('Отметьте согласие на обработку персональных данных');
    btn.disabled = true; var old = btn.textContent; btn.textContent = 'Считаем...';
    fetch('/api/natal', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ person: p, consent: true }) })
      .then(function (r) { return r.json().then(function (j) { if (!r.ok) throw new Error(j.error || 'Ошибка'); return j; }); })
      .then(function (j) { try { ym(114224190, 'reachGoal', 'natal_done'); } catch (e) {} return j; })
      .then(render)
      .catch(function (e) { showError(e.message); })
      .finally(function () { btn.disabled = false; btn.textContent = old; });
  });
  (function () { var cb = $('tu1'), t = $('t1'); if (cb && t) cb.addEventListener('change', function () { t.disabled = cb.checked; if (cb.checked) t.value = ''; }); })();
})();
