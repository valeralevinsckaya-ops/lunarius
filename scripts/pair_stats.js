'use strict';
// Средний балл спидометра для 78 сочетаний знаков Солнца: случайные люди 1960-2008, по 20 000 пар на сочетание.
// Запуск: node scripts/pair_stats.js 1500 20000 docs/pairs_stats.json (нужны установленные пакеты проекта).
// После пересчета калибровки (npm run calibrate) пересчитать и этот файл, затем python3 scripts/build_pairs.py.
const path = require('path');
const ROOT = path.join(__dirname, '..');
const { natalChart } = require(ROOT + '/lib/chart');
const { synastry, SPHERES } = require(ROOT + '/lib/synastry');
const calibration = require(ROOT + '/data/calibration.json');
const cities = require(ROOT + '/data/cities.json').filter((c) => c.cc === 'RU').slice(0, 300);
const PER = Number(process.argv[2] || 150), PAIRS = Number(process.argv[3] || 3000);
let seed = 20261120;
const rnd = () => ((seed = (seed * 1664525 + 1013904223) % 4294967296) / 4294967296);
const ORDER = ['aries','taurus','gemini','cancer','leo','virgo','libra','scorpio','sagittarius','capricorn','aquarius','pisces'];
const SLUG = ['oven','telec','bliznecy','rak','lev','deva','vesy','skorpion','strelec','kozerog','vodoley','ryby'];
const bySign = {};
let made = 0, firstSign = null;
while (true) {
  const start = Date.UTC(1960, 0, 1), end = Date.UTC(2008, 11, 31);
  const d = new Date(start + rnd() * (end - start));
  const c = cities[Math.floor(rnd() * cities.length)];
  const hh = String(Math.floor(rnd() * 24)).padStart(2, '0'), mm = String(Math.floor(rnd() * 60)).padStart(2, '0');
  const ch = natalChart({ date: d.toISOString().slice(0, 10), time: `${hh}:${mm}`, lat: c.la, lon: c.lo, tz: c.tz });
  const s = ch.planets.sun.sign; if (!firstSign) firstSign = s;
  (bySign[s] = bySign[s] || []);
  if (bySign[s].length < PER) { bySign[s].push(ch); made++; }
  if (Object.keys(bySign).length === 12 && Object.values(bySign).every((a) => a.length >= PER)) break;
}
const keys = Object.keys(bySign);
const idx = (s) => { let i = ORDER.indexOf(String(s).toLowerCase()); return i; };
if (keys.some((k) => idx(k) < 0)) { console.error('sign keys', keys); process.exit(1); }
const out = {};
const sphereKeys = Object.keys(SPHERES);
for (let i = 0; i < 12; i++) for (let j = i; j < 12; j++) {
  const ka = keys.find((k) => idx(k) === i), kb = keys.find((k) => idx(k) === j);
  const A = bySign[ka], B = bySign[kb];
  const tr = []; const sp = {}; for (const s of sphereKeys) sp[s] = 0;
  let n = 0;
  for (let k = 0; k < PAIRS; k++) {
    const a = A[Math.floor(rnd() * A.length)], b = B[Math.floor(rnd() * B.length)];
    if (a === b) continue;
    const r = synastry(a, b, calibration);
    tr.push(r.trend); for (const s of sphereKeys) sp[s] += r.spheres[s]; n++;
  }
  tr.sort((x, y) => x - y);
  const mean = tr.reduce((x, y) => x + y, 0) / n;
  const sd = Math.sqrt(tr.reduce((x, y) => x + (y - mean) ** 2, 0) / n);
  const q = (p) => tr[Math.floor(p * (n - 1))];
  const o = { n, mean: +mean.toFixed(2), se: +(sd / Math.sqrt(n)).toFixed(3), median: +q(0.5).toFixed(2), p10: +q(0.1).toFixed(1), p90: +q(0.9).toFixed(1),
    good: Math.round(100 * tr.filter((v) => v > 0.5).length / n), strong: Math.round(100 * tr.filter((v) => v > 2).length / n), tense: Math.round(100 * tr.filter((v) => v <= -0.5).length / n), spheres: {} };
  for (const s of sphereKeys) o.spheres[s] = +(sp[s] / n).toFixed(2);
  out[`${SLUG[i]}-${SLUG[j]}`] = o;
}
require('fs').writeFileSync(process.argv[4] || '/tmp/sim/out.json', JSON.stringify(out, null, 1));
const all = Object.values(out).map((o) => o.mean);
console.log('people', made, 'pairs', Object.keys(out).length, 'mean range', Math.min(...all), Math.max(...all), 'sphereKeys', sphereKeys.join(','), 'signkeys', keys.join(','));
