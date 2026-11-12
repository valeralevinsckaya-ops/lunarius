'use strict';
// Сервер "Спидометра совместимости": отдает сайт и считает совместимость.
// Данные пользователей не сохраняются: расчет идет в памяти и сразу возвращается.
const path = require('path');
const express = require('express');
const { compatibility } = require('./lib/report');
const cities = require('./data/cities.json');

const app = express();
app.disable('x-powered-by');
app.use(express.json({ limit: '10kb' }));

// --- поиск городов
const normq = (s) => String(s || '').toLowerCase().replace(/ё/g, 'е').trim();
const index = cities.map((c, i) => ({ i, n: normq(c.n), e: normq(c.e) }));
app.get('/api/cities', (req, res) => {
  const q = normq(req.query.q);
  if (q.length < 2) return res.json([]);
  const out = [];
  for (const x of index) {
    if (x.n.startsWith(q) || x.e.startsWith(q)) out.push(x.i);
    if (out.length >= 10) break;
  }
  res.json(out.map((i) => {
    const c = cities[i];
    return { id: i, name: c.n, label: [c.n, c.r, c.c].filter(Boolean).join(', ') };
  }));
});

// --- простое ограничение частоты запросов
const hits = new Map();
function limited(ip) {
  const now = Date.now();
  const arr = (hits.get(ip) || []).filter((t) => now - t < 60_000);
  arr.push(now); hits.set(ip, arr);
  return arr.length > 30;
}
setInterval(() => hits.clear(), 10 * 60_000).unref();

function readPerson(p) {
  if (!p || typeof p !== 'object') throw new Error('Нет данных партнера');
  if (!/^\d{4}-\d{2}-\d{2}$/.test(p.date || '')) throw new Error('Укажите дату рождения');
  const year = Number(p.date.slice(0, 4));
  if (year < 1900 || year > 2100) throw new Error('Проверьте год рождения');
  if (p.time && !/^\d{1,2}:\d{2}$/.test(p.time)) throw new Error('Проверьте время рождения');
  const city = cities[Number(p.cityId)];
  if (!city) throw new Error('Выберите город рождения из списка');
  return { name: String(p.name || '').slice(0, 40), date: p.date, time: p.time || null, lat: city.la, lon: city.lo, tz: city.tz };
}

app.post('/api/compatibility', (req, res) => {
  if (limited(req.ip)) return res.status(429).json({ error: 'Слишком много расчетов, попробуйте через минуту' });
  if (req.body?.consent !== true) return res.status(400).json({ error: 'Нужно согласие на обработку персональных данных' });
  try {
    const a = readPerson(req.body.a), b = readPerson(req.body.b);
    res.json(compatibility(a, b));
  } catch (e) {
    res.status(400).json({ error: e.message || 'Ошибка расчета' });
  }
});

app.get('/privacy', (req, res) => res.sendFile(path.join(__dirname, 'public', 'privacy.html')));
app.use(express.static(path.join(__dirname, 'public'), { maxAge: '1h' }));

const PORT = Number(process.env.PORT || 3000);
app.listen(PORT, '0.0.0.0', () => console.log(`Спидометр совместимости запущен на порту ${PORT}`));
