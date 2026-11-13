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
    return { name: $('n' + k).value.trim(), date: $('d' + k).value, time: $('t' + k).value || null, cityId: cityIds[k] };
  }

  function esc(t) { var d = document.createElement('div'); d.textContent = t == null ? '' : String(t); return d.innerHTML; }

  function bar(v) {
    var w = Math.abs(v) / 10 * 50, left = v < 0 ? 50 - w : 50;
    return '<div class="sb"><span class="sb-mid"></span><span class="sb-fill" style="left:' + left + '%;width:' + w + '%;background:' + color(v) + '"></span></div>';
  }

  function render(r) {
    setGauge(r.trend.score, r.trend.zone);
    var p = r.partners;
    var who = function (x, i) { return esc(x.name || ('Партнер ' + (i + 1))); };
    var signs = function (s) {
      return 'Солнце: ' + esc(s.sun) + ' · Луна: ' + esc(s.moon) + ' · Венера: ' + esc(s.venus) + (s.asc ? ' · Асцендент: ' + esc(s.asc) : '');
    };
    var html = '<h2 class="r-h">Ваш результат</h2>' +
      '<div class="r-grid">' + p.map(function (x, i) {
        return '<div class="r-card"><span class="r-who">' + who(x, i) + '</span>' +
          '<span class="r-score" style="color:' + color(x.score) + '">' + fmt(x.score) + '</span>' +
          '<strong class="r-zone">' + esc(x.zone) + '</strong>' +
          '<p class="r-text">Как карта партнера влияет на этого человека. ' + esc(x.text) + '</p>' +
          '<p class="r-signs">' + signs(x.signs) + '</p></div>';
      }).join('') +
      '<div class="r-card r-trend"><span class="r-who">Общая тенденция</span><span class="r-score" style="color:' + color(r.trend.score) + '">' + fmt(r.trend.score) + '</span><strong class="r-zone">' + esc(r.trend.zone) + '</strong><p class="r-text">' + esc(r.trend.text) + '</p>' + (r.summary ? '<p class="r-text r-summary">' + esc(r.summary) + '</p>' : '') + '</div></div>' +
      (r.compare ? '<h3 class="r-sub">Знаки рядом</h3><div class="r-spheres">' + r.compare.map(function (c) {
        var col = c.relation === 'hard' ? '#E8762E' : '#5B44BD';
        return '<div class="r-sphere"><div class="r-sphere-top" style="font-size:18px"><span>' + esc(c.title) + '</span></div><p class="r-cmp"><b style="color:' + col + '">' + esc(c.a) + '</b> и <b style="color:' + col + '">' + esc(c.b) + '</b></p><p>' + esc(c.text) + '</p></div>';
      }).join('') + '</div>' : '') +
      '<h3 class="r-sub">По сферам</h3><div class="r-spheres">' + r.spheres.map(function (s) {
        var rel = (s.related || []).map(function (x) { return '<span class="r-chip ' + (x.nature === 'harmony' ? 'is-h' : 'is-t') + '">' + esc(x.title) + '</span>'; }).join('');
        return '<div class="r-sphere"><div class="r-sphere-top"><span>' + esc(s.title) + '</span><b style="color:' + color(s.value) + '">' + fmt(s.value) + '</b></div>' + bar(s.value) + '<p>' + esc(s.text) + '</p>' + (rel ? '<div class="r-chips">' + rel + '</div>' : '') + '</div>';
      }).join('') + '</div>' +
      '<h3 class="r-sub">Главные связи между картами</h3><div class="r-aspects">' + r.aspects.map(function (a) {
        return '<div class="r-aspect ' + (a.nature === 'harmony' ? 'is-h' : 'is-t') + '"><strong>' + esc(a.title) + (a.kind === 'conj' ? '<span class="r-orb">соединение</span>' : '') + '<span class="r-orb">орбис ' + a.orb.toFixed(1) + '°</span></strong><p>' + esc(a.text) + '</p></div>';
      }).join('') + '</div>' +
      (r.moreAspects && r.moreAspects.length ? '<details class="r-more"><summary>Остальные связи: еще ' + r.moreAspects.length + '</summary><div class="r-aspects">' + r.moreAspects.map(function (a) {
        return '<div class="r-aspect ' + (a.nature === 'harmony' ? 'is-h' : 'is-t') + '"><strong>' + esc(a.title) + '<span class="r-orb">орбис ' + a.orb.toFixed(1) + '°</span></strong><p>' + esc(a.text) + '</p></div>';
      }).join('') + '</div></details>' : '') +
      (r.overlays && r.overlays.length ? '<h3 class="r-sub">Планеты партнера в ваших домах</h3><div class="r-aspects">' + r.overlays.map(function (o) {
        return '<div class="r-card"><span class="r-who">' + esc(o.title) + '</span>' + o.items.map(function (i) { return '<p class="r-text"><b>' + esc(i.planet) + ' в ' + i.house + ' доме.</b> ' + esc(i.text) + '</p>'; }).join('') + '</div>';
      }).join('') + '</div>' : '') +
      (r.note ? '<p class="r-note">' + esc(r.note) + '</p>' : '');
    var box = $('result');
    box.innerHTML = html; box.hidden = false;
    box.scrollIntoView({ behavior: 'smooth', block: 'start' });
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
})();
