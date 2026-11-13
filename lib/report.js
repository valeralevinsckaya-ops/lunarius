'use strict';
// Собирает итоговый отчет совместимости для API
const { natalChart, houseOf } = require('./chart');
const { synastry, polarity, pairWeight, SPHERES } = require('./synastry');
const T = require('./texts');
const TS = require('./texts-synastry');
const calibration = require('../data/calibration.json');

const round2 = (x) => Math.round(x * 100) / 100;
const OVERLAY_PLANETS = ['sun', 'moon', 'venus', 'mars', 'saturn', 'jupiter'];

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

function natureOf(x) {
  if (x.aspect === 'conjunction') return 'conj';
  return polarity(x.aspect, x.a, x.b) >= 0 ? 'harmony' : 'tension';
}

function pairText(x) {
  const key = [x.a, x.b].sort().join('|');
  const n = natureOf(x);
  const t = TS.PAIRS[key];
  if (t && t[n]) return t[n];
  // старые тексты как запасной вариант
  if (n !== 'conj') return T.aspectText(x, polarity(x.aspect, x.a, x.b));
  return TS.NATURE_FALLBACK.conj;
}

function compatibility(a, b) {
  const A = person(a), B = person(b);
  const s = synastry(A.chart, B.chart, calibration);
  const zA = T.zoneOf(s.forA), zB = T.zoneOf(s.forB), zT = T.zoneOf(s.trend);
  const nameA = 'Вы', nameB = 'Партнер';

  const describe = (x) => ({
    a: x.a, b: x.b, aspect: x.aspect, orb: x.orb, strength: x.strength,
    title: `${T.PLANET[x.a]} (${nameA}) ${T.ASPECT[x.aspect]} ${T.PLANET[x.b]} (${nameB})`,
    nature: natureOf(x) === 'conj' ? (polarity(x.aspect, x.a, x.b) >= 0 ? 'harmony' : 'tension') : natureOf(x),
    kind: natureOf(x),
    weight: round2(Math.abs(polarity(x.aspect, x.a, x.b)) * x.strength * pairWeight(x.a, x.b)),
    text: pairText(x),
    details: TS.aspectDetails({ ...x, nature: natureOf(x) }, nameA, nameB, T.PLANET),
  });
  const aspects = s.topAspects.map(describe);
  const all = s.allAspects.map(describe).filter((x) => x.weight > 0).sort((p, q) => q.weight - p.weight);
  const topKeys = new Set(aspects.map((x) => x.title));
  const moreAspects = all.filter((x) => !topKeys.has(x.title));

  // сферы с перечнем влияющих связей
  const spheres = Object.entries(s.spheres).map(([k, v]) => {
    const planets = SPHERES[k];
    const related = all.filter((x) => planets.includes(x.a) || planets.includes(x.b)).slice(0, 4)
      .map((x) => ({ title: x.title, nature: x.nature }));
    return { key: k, title: T.SPHERE[k], value: round2(v), text: T.sphereText(k, v), related };
  });

  // сравнение знаков личных точек
  const compare = ['sun', 'moon', 'venus', 'mars'].map((k) => {
    const pa = A.chart.planets[k], pb = B.chart.planets[k];
    const rel = TS.elementRelation(pa.element, pb.element);
    return { key: k, title: TS.COMPARE[k].title, a: `${T.SIGN[pa.sign]} (${TS.ELEMENT_RU[pa.element]})`, b: `${T.SIGN[pb.sign]} (${TS.ELEMENT_RU[pb.element]})`, relation: rel, text: TS.COMPARE[k][rel] };
  });

  // планеты партнера в домах
  const overlays = [];
  const overlay = (host, guest, title) => {
    if (!host.chart.houses) return null;
    return {
      title,
      items: OVERLAY_PLANETS.map((k) => {
        const h = houseOf(guest.chart.planets[k].lon, host.chart.houses);
        return { planet: T.PLANET[k], house: h, text: TS.overlayText(k, h) };
      }),
    };
  };
  const oAB = overlay(A, B, 'Планеты партнера в ваших домах: как партнер влияет на вашу жизнь'),
    oBA = overlay(B, A, 'Ваши планеты в домах партнера: так ваше влияние ощущает партнер (здесь «партнер» в текстах - это вы)');
  if (oAB) overlays.push(oAB);
  if (oBA) overlays.push(oBA);

  // краткий итог
  const bestH = all.find((x) => x.nature === 'harmony'), bestT = all.find((x) => x.nature === 'tension');
  const summary = [
    `Всего между картами ${all.length} значимых связей: ${all.filter((x) => x.nature === 'harmony').length} гармоничных и ${all.filter((x) => x.nature === 'tension').length} напряженных.`,
    bestH ? `Главная опора пары: ${bestH.title}.` : '',
    bestT ? `Главная зона роста: ${bestT.title}.` : 'Напряженных связей почти нет: отношениям может не хватать искры, но и поводов для ссор мало.',
  ].filter(Boolean).join(' ');

  return {
    partners: [
      { name: 'Вы', signs: describeChart(A.chart), score: s.forA, zone: zA.title, text: zA.text },
      { name: 'Партнер', signs: describeChart(B.chart), score: s.forB, zone: zB.title, text: zB.text },
    ],
    trend: { score: s.trend, zone: zT.title, text: zT.text },
    strength: s.strength,
    summary,
    compare,
    spheres,
    aspects,
    moreAspects,
    overlays,
    note: !A.chart.timeKnown || !B.chart.timeKnown ? 'Время рождения указано не у обоих: Асцендент и дома не учитывались, положение Луны приблизительное.' : null,
  };
}

module.exports = { compatibility };
