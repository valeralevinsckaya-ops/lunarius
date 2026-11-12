'use strict';
// Калибровка шкалы -10..+10 на случайных парах людей
const fs = require('fs');
const path = require('path');
const { natalChart } = require('../lib/chart');
const { raw, SPHERES } = require('../lib/synastry');
const cities = require('../data/cities.json').filter((c) => c.cc === 'RU').slice(0, 300);

const N = Number(process.argv[2] || 1200); // людей
const PAIRS = Number(process.argv[3] || 20000);
let seed = 42;
const rnd = () => ((seed = (seed * 1664525 + 1013904223) % 4294967296) / 4294967296);

const people = [];
for (let i = 0; i < N; i++) {
  const start = Date.UTC(1960, 0, 1), end = Date.UTC(2008, 11, 31);
  const d = new Date(start + rnd() * (end - start));
  const c = cities[Math.floor(rnd() * cities.length)];
  const hh = String(Math.floor(rnd() * 24)).padStart(2, '0'), mm = String(Math.floor(rnd() * 60)).padStart(2, '0');
  people.push(natalChart({ date: d.toISOString().slice(0, 10), time: `${hh}:${mm}`, lat: c.la, lon: c.lo, tz: c.tz }));
}
const vals = { forA: [], strength: [], spheres: {} };
for (const s of Object.keys(SPHERES)) vals.spheres[s] = [];
for (let k = 0; k < PAIRS; k++) {
  const a = people[Math.floor(rnd() * N)], b = people[Math.floor(rnd() * N)];
  if (a === b) continue;
  const r = raw(a, b);
  vals.forA.push(r.forA, r.forB); vals.strength.push(r.strength);
  for (const s of Object.keys(SPHERES)) vals.spheres[s].push(r.spheres[s]);
}
const stat = (arr) => {
  const s = [...arr].sort((x, y) => x - y);
  const q = (p) => s[Math.floor(p * (s.length - 1))];
  const median = q(0.5);
  const mad = [...s].map((v) => Math.abs(v - median)).sort((x, y) => x - y)[Math.floor(s.length / 2)];
  return { median: +median.toFixed(4), spread: +(1.4826 * mad || 1).toFixed(4), p05: +q(0.05).toFixed(3), p95: +q(0.95).toFixed(3) };
};
const cal = { createdAt: new Date().toISOString(), people: N, pairs: PAIRS, forA: stat(vals.forA), strength: stat(vals.strength), spheres: {} };
for (const s of Object.keys(SPHERES)) cal.spheres[s] = stat(vals.spheres[s]);
fs.writeFileSync(path.join(__dirname, '../data/calibration.json'), JSON.stringify(cal, null, 2));
console.log(JSON.stringify(cal, null, 2));
