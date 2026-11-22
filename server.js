'use strict';
// Сервер "Спидометра совместимости": отдает сайт и считает совместимость.
// Данные пользователей не сохраняются: расчет идет в памяти и сразу возвращается.
const path = require('path');
const express = require('express');
const { compatibility } = require('./lib/report');
const { natalReport } = require('./lib/natal');
const cities = require('./data/cities.json');

const app = express();
app.disable('x-powered-by');
app.use(express.json({ limit: '10kb' }));

// Адрес с www: один основной адрес сайта без www, все остальное 301 на него.
app.use((req, res, next) => {
  const host = String(req.headers['x-forwarded-host'] || req.headers.host || '').split(',')[0].trim().toLowerCase().replace(/:\d+$/, '');
  if (host === 'www.lunarius.ru') return res.redirect(301, 'https://lunarius.ru' + req.originalUrl);
  next();
});

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

app.post('/api/natal', (req, res) => {
  if (limited(req.ip)) return res.status(429).json({ error: 'Слишком много расчетов, попробуйте через минуту' });
  if (req.body?.consent !== true) return res.status(400).json({ error: 'Нужно согласие на обработку персональных данных' });
  try {
    res.json(natalReport(readPerson(req.body.person)));
  } catch (e) {
    res.status(400).json({ error: e.message || 'Ошибка расчета' });
  }
});

app.get('/api/indexnow-status', (req, res) => res.json(lastIndexNow || { status: 'еще не отправлялось' }));
app.use(stripSlash); // до маршрутов /natal и /privacy, чтобы /natal/ тоже уходил на /natal
app.use(require('./lib/static-gzip')(path.join(__dirname, 'public'), { maxAge: 3600 })); // сжатые HTML, JS, XML
app.get('/natal', (req, res) => res.sendFile(path.join(__dirname, 'public', 'natal.html')));
app.get('/privacy', (req, res) => res.sendFile(path.join(__dirname, 'public', 'privacy.html')));

// --- один адрес на страницу: без слэша на конце.
// Адрес со слэшем (/blog/, /natal/) отдает 301 на адрес без слэша,
// а разделы (/blog, /compat, /signs ...) открываются сразу, без редиректа.
const PUBLIC = path.join(__dirname, 'public');
function stripSlash(req, res, next) {
  if ((req.method !== 'GET' && req.method !== 'HEAD') || req.path === '/' || !req.path.endsWith('/')) return next();
  const q = req.originalUrl.indexOf('?');
  res.redirect(301, '/' + req.path.replace(/^\/+|\/+$/g, '') + (q === -1 ? '' : req.originalUrl.slice(q)));
}
function sectionIndex(req, res, next) {
  if ((req.method !== 'GET' && req.method !== 'HEAD') || !/^\/[a-z0-9-]+$/.test(req.path)) return next();
  res.sendFile(path.join(PUBLIC, req.path.slice(1), 'index.html'), { maxAge: '1h' }, (err) => { if (err) next(); });
}
// --- статья о домах заменена разделом /doma
const MOVED = { '/blog/doma-v-natalnoy-karte': '/doma' };
app.use((req, res, next) => (MOVED[req.path] ? res.redirect(301, MOVED[req.path]) : next()));
app.use(sectionIndex);
app.use('/fonts', express.static(path.join(PUBLIC, 'fonts'), { maxAge: '365d', immutable: true })); // свои шрифты Oswald и Manrope
app.use('/img', express.static(path.join(PUBLIC, 'img'), { maxAge: '30d' })); // картинки знаков меняются редко
app.use(express.static(PUBLIC, { maxAge: '1h', extensions: ['html'], redirect: false }));

// --- пара в обратном порядке: /compat/lev-oven -> /compat/oven-lev
app.get(/^\/compat\/([a-z]+)-([a-z]+)$/, (req, res, next) => {
  const [, a, b] = req.path.match(/^\/compat\/([a-z]+)-([a-z]+)$/);
  require('fs').access(path.join(PUBLIC, 'compat', `${b}-${a}.html`), (err) => (err ? next() : res.redirect(301, `/compat/${b}-${a}`)));
});

// --- все остальное: страница 404 с меню и ссылками на разделы
app.use((req, res) => {
  if (req.path.startsWith('/api/')) return res.status(404).json({ error: 'Не найдено' });
  res.status(404).sendFile(path.join(PUBLIC, '404.html'), (err) => { if (err && !res.headersSent) res.type('text').send('Страница не найдена'); });
});

// --- IndexNow: при запуске на хостинге сообщаем Яндексу и Bing адреса из sitemap.
// Запуск происходит после каждого деплоя, то есть когда страницы могли измениться.
// Ключ лежит в public/<ключ>.txt. Отключить (например, при запуске на своем компьютере): INDEXNOW=off npm start
const INDEXNOW_KEY = '9952f21193d82752bb1c4449964a4d67';
async function pingIndexNow() {
  if (process.env.INDEXNOW === 'off' || process.env.NODE_ENV === 'development') { lastIndexNow = { status: 'отключено' }; return; }
  try {
    const xml = require('fs').readFileSync(path.join(PUBLIC, 'sitemap.xml'), 'utf8');
    const urlList = [...xml.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => m[1]);
    if (!urlList.length) return;
    // Яндекс и Bing (через Bing адреса получают и другие участники IndexNow)
    const body = JSON.stringify({ host: 'lunarius.ru', key: INDEXNOW_KEY, keyLocation: `https://lunarius.ru/${INDEXNOW_KEY}.txt`, urlList });
    const engines = { yandex: 'https://yandex.com/indexnow', bing: 'https://www.bing.com/indexnow' };
    const status = {};
    for (const [name, url] of Object.entries(engines)) {
      try {
        const r = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json; charset=utf-8' }, body });
        status[name] = r.status;
      } catch (e) {
        status[name] = 'ошибка: ' + String(e.message || e);
      }
    }
    lastIndexNow = { at: new Date().toISOString(), status, urls: urlList.length };
    console.log(`IndexNow: отправлено ${urlList.length} адресов, ответы ${JSON.stringify(status)}`);
  } catch (e) {
    lastIndexNow = { at: new Date().toISOString(), error: String(e.message || e) };
    console.log('IndexNow: не удалось отправить', e.message || e);
  }
}
let lastIndexNow = null;

const PORT = Number(process.env.PORT || 3000);
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Спидометр совместимости запущен на порту ${PORT}`);
  setTimeout(pingIndexNow, 30_000).unref(); // даем хостингу переключить трафик на новую версию
});
