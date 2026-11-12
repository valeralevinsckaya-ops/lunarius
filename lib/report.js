'use strict';
// Собирает итоговый отчет совместимости для API
const { natalChart } = require('./chart');
const { synastry, polarity } = require('./synastry');
const T = require('./texts');
const calibration = require('../data/calibration.json');

const round2 = (x) => Math.round(x * 100) / 100;

function person(p) {
  return {
    name: (p.name || '').trim().slice(0, 40),
    chart: natalChart({ date: p.date, time: p.time || null, lat: p.lat, lon: p.lon, tz: p.tz }),
  };
}

function describeChart(c) {
  const out = { sun: T.SIGN[c.planets.sun.sign], moon: T.SIGN[c.planets.moon.sign], venus: T.SIGN[c.planets.venus.sign], mars: T.SIGN[c.planets.mars.sign] };
  if (c.asc) out.asc = T.SIGN[c.asc.sign];
  out.timeKnown = c.timeKnown;
  return out;
}

function compatibility(a, b) {
  const A = person(a), B = person(b);
  const s = synastry(A.chart, B.chart, calibration);
  const zA = T.zoneOf(s.forA), zB = T.zoneOf(s.forB), zT = T.zoneOf(s.trend);
  const aspects = s.topAspects.map((x) => ({
    a: x.a, b: x.b, aspect: x.aspect, orb: x.orb,
    title: `${T.PLANET[x.a]} (${A.name || 'партнер 1'}) ${T.ASPECT[x.aspect]} ${T.PLANET[x.b]} (${B.name || 'партнер 2'})`,
    nature: polarity(x.aspect, x.a, x.b) >= 0 ? 'harmony' : 'tension',
    text: T.aspectText(x, polarity(x.aspect, x.a, x.b)),
  }));
  const spheres = Object.entries(s.spheres).map(([k, v]) => ({ key: k, title: T.SPHERE[k], value: round2(v), text: T.sphereText(k, v) }));
  return {
    partners: [
      { name: A.name, signs: describeChart(A.chart), score: s.forA, zone: zA.title, text: zA.text },
      { name: B.name, signs: describeChart(B.chart), score: s.forB, zone: zB.title, text: zB.text },
    ],
    trend: { score: s.trend, zone: zT.title, text: zT.text },
    strength: s.strength,
    spheres,
    aspects,
    note: !A.chart.timeKnown || !B.chart.timeKnown ? 'Время рождения указано не у обоих: Асцендент и дома не учитывались, положение Луны приблизительное.' : null,
  };
}

module.exports = { compatibility };
