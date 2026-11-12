'use strict';
// Синастрия: аспекты между двумя картами, показатель для каждого партнера
// по шкале -10..+10 и шесть сфер отношений.
const { norm } = require('./chart');

const ASPECTS = [
  { key: 'conjunction', angle: 0, orb: 8 },
  { key: 'sextile', angle: 60, orb: 5 },
  { key: 'square', angle: 90, orb: 6 },
  { key: 'trine', angle: 120, orb: 7 },
  { key: 'opposition', angle: 180, orb: 7 },
];
const OUTER = new Set(['uranus', 'neptune', 'pluto', 'node']);
const MALEFIC = new Set(['mars', 'saturn', 'uranus', 'pluto']);
const BENEFIC = new Set(['venus', 'jupiter']);

// Насколько важна планета человека, на которую "действует" партнер
const RECEIVE = { sun: 1.3, moon: 1.4, venus: 1.3, mars: 1.0, mercury: 0.9, jupiter: 0.7, saturn: 0.7, asc: 1.2, uranus: 0.3, neptune: 0.3, pluto: 0.3, node: 0.4 };

// Вес пары планет (неупорядоченная пара)
const PAIR = {
  'sun|moon': 3, 'moon|moon': 2.5, 'venus|mars': 3, 'sun|venus': 2.2, 'moon|venus': 2.5,
  'sun|sun': 1.5, 'venus|venus': 1.6, 'mars|mars': 1, 'sun|mars': 1.6, 'moon|mars': 1.6,
  'mercury|mercury': 1.6, 'mercury|moon': 1.5, 'mercury|venus': 1.4, 'mercury|sun': 1.3, 'mars|mercury': 1.1,
  'jupiter|sun': 1.5, 'jupiter|moon': 1.5, 'jupiter|venus': 1.5, 'jupiter|mars': 1, 'jupiter|mercury': 1,
  'saturn|sun': 2, 'moon|saturn': 2, 'saturn|venus': 2, 'mars|saturn': 1.3, 'mercury|saturn': 1.2,
  'asc|sun': 1.6, 'asc|moon': 1.6, 'asc|venus': 1.6, 'asc|mars': 1.2, 'asc|asc': 1.2,
  'moon|node': 1.2, 'node|sun': 1.2, 'node|venus': 1.2,
};
const pairKey = (a, b) => [a, b].sort().join('|');
function pairWeight(a, b) {
  const k = pairKey(a, b);
  if (PAIR[k] != null) return PAIR[k];
  if (OUTER.has(a) && OUTER.has(b)) return 0; // поколенческие аспекты не считаем
  if (OUTER.has(a) || OUTER.has(b)) return 0.8;
  if (a === 'jupiter' || b === 'jupiter' || a === 'saturn' || b === 'saturn') return 0.7;
  return 0.8;
}

// Знак влияния аспекта: + гармония, - напряжение
function polarity(aspect, a, b) {
  switch (aspect) {
    case 'trine': return 1;
    case 'sextile': return 0.8;
    case 'square': return -1;
    case 'opposition': {
      // оппозиция Венера-Марс или Солнце-Луна дает притяжение, остальные напрягают
      const k = pairKey(a, b);
      return k === 'venus|mars' || k === 'sun|moon' ? 0.3 : -0.7;
    }
    case 'conjunction': {
      if (BENEFIC.has(a) || BENEFIC.has(b)) return 1;
      const k = pairKey(a, b);
      if (k === 'sun|moon' || k === 'moon|moon' || k === 'venus|mars' || k === 'node|sun' || k === 'moon|node' || k === 'node|venus') return 1;
      if (MALEFIC.has(a) || MALEFIC.has(b)) return -0.5;
      return 0.6;
    }
    default: return 0;
  }
}

// Сферы отношений: какие планеты к ним относятся
const SPHERES = {
  attraction: ['venus', 'mars', 'sun', 'moon', 'asc'],
  emotions: ['moon'],
  communication: ['mercury'],
  values: ['venus', 'jupiter'],
  stability: ['saturn'],
  growth: ['sun', 'jupiter'],
};

function points(chart) {
  const p = Object.entries(chart.planets).map(([k, v]) => ({ key: k, lon: v.lon }));
  if (chart.asc) p.push({ key: 'asc', lon: chart.asc.lon });
  return p;
}

function findAspects(a, b) {
  const list = [];
  for (const x of points(a)) for (const y of points(b)) {
    if (OUTER.has(x.key) && OUTER.has(y.key)) continue;
    let d = Math.abs(norm(x.lon - y.lon)); if (d > 180) d = 360 - d;
    for (const asp of ASPECTS) {
      let orb = asp.orb;
      if (OUTER.has(x.key) || OUTER.has(y.key)) orb -= 2;
      if (x.key === 'asc' || y.key === 'asc') orb -= 1;
      const dev = Math.abs(d - asp.angle);
      if (dev <= orb) {
        const strength = Math.cos((dev / orb) * (Math.PI / 2)); // 1 при точном аспекте
        list.push({ a: x.key, b: y.key, aspect: asp.key, orb: +dev.toFixed(2), strength: +strength.toFixed(3) });
      }
    }
  }
  return list;
}

const ELEMENT_SCORE = (e1, e2) => {
  if (e1 === e2) return 1;
  const ok = new Set(['fire|air', 'air|fire', 'earth|water', 'water|earth']);
  return ok.has(`${e1}|${e2}`) ? 0.6 : -0.4;
};

// Сырые баллы: для партнера A (как карта B влияет на A) и наоборот
function raw(chartA, chartB) {
  const aspects = findAspects(chartA, chartB);
  const res = { forA: 0, forB: 0, strength: 0, spheres: {}, aspects };
  for (const s of Object.keys(SPHERES)) res.spheres[s] = 0;
  for (const asp of aspects) {
    const base = polarity(asp.aspect, asp.a, asp.b) * asp.strength * pairWeight(asp.a, asp.b);
    res.forA += base * (RECEIVE[asp.a] ?? 0.5);
    res.forB += base * (RECEIVE[asp.b] ?? 0.5);
    res.strength += Math.abs(base);
    for (const [s, keys] of Object.entries(SPHERES)) {
      if (keys.includes(asp.a) || keys.includes(asp.b)) {
        if (s === 'attraction' && !(['venus', 'mars'].includes(asp.a) || ['venus', 'mars'].includes(asp.b) || pairKey(asp.a, asp.b) === 'sun|moon')) continue;
        res.spheres[s] += base;
      }
    }
  }
  // стихии личных точек
  const keys = ['sun', 'moon', 'venus', 'mars'];
  let el = 0;
  for (const k of keys) el += ELEMENT_SCORE(chartA.planets[k].element, chartB.planets[k].element);
  el += ELEMENT_SCORE(chartA.planets.sun.element, chartB.planets.moon.element) + ELEMENT_SCORE(chartA.planets.moon.element, chartB.planets.sun.element);
  res.forA += el * 0.5; res.forB += el * 0.5;
  return res;
}

// Перевод в шкалу -10..+10 по калибровке на случайных парах
function scale(value, cal) {
  if (!cal) return 0;
  const z = (value - cal.median) / cal.spread;
  const s = 10 * Math.tanh(z / 3.0);
  return Math.max(-10, Math.min(10, Math.round(s * 100) / 100));
}

function synastry(chartA, chartB, calibration) {
  const r = raw(chartA, chartB);
  const forA = scale(r.forA, calibration?.forA);
  const forB = scale(r.forB, calibration?.forA);
  const spheres = {};
  for (const s of Object.keys(SPHERES)) spheres[s] = scale(r.spheres[s], calibration?.spheres?.[s]);
  const top = [...r.aspects]
    .map((x) => ({ ...x, weight: Math.abs(polarity(x.aspect, x.a, x.b) * x.strength * pairWeight(x.a, x.b)) }))
    .filter((x) => x.weight > 0)
    .sort((p, q) => q.weight - p.weight)
    .slice(0, 8);
  return {
    forA, forB,
    trend: Math.round(((forA + forB) / 2) * 100) / 100,
    strength: scale(r.strength, calibration?.strength),
    spheres,
    topAspects: top,
    raw: { forA: r.forA, forB: r.forB, strength: r.strength },
  };
}

module.exports = { synastry, raw, findAspects, polarity, SPHERES };
