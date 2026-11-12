'use strict';
// Отчет по натальной карте одного человека: планеты в знаках и домах, дома, аспекты, баланс стихий.
const { natalChart, norm } = require('./chart');
const T = require('./natal-texts');
const { wheelSvg } = require('./wheel');

const ORDER = ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune', 'pluto'];
const ASPECTS = [
  ['conjunction', 0, 8], ['opposition', 180, 7], ['trine', 120, 7], ['square', 90, 6], ['sextile', 60, 5],
];
const LUMINARY_BONUS = 1.5; // орбис шире для Солнца и Луны
const WEIGHT = { sun: 3, moon: 3, mercury: 2, venus: 2.5, mars: 2.5, jupiter: 1.5, saturn: 1.5, uranus: 1, neptune: 1, pluto: 1, asc: 2.5, mc: 2 };

function fmtDeg(lon) {
  const d = norm(lon) % 30;
  const deg = Math.floor(d), min = Math.floor((d - deg) * 60);
  return `${deg}°${String(min).padStart(2, '0')}'`;
}

function findNatalAspects(chart) {
  const points = ORDER.map((k) => [k, chart.planets[k].lon]);
  if (chart.asc) { points.push(['asc', chart.asc.lon]); points.push(['mc', chart.mc.lon]); }
  const out = [];
  for (let i = 0; i < points.length; i++) {
    for (let j = i + 1; j < points.length; j++) {
      const [a, la] = points[i], [b, lb] = points[j];
      if ((a === 'asc' && b === 'mc') || (a === 'mc' && b === 'asc')) continue;
      let d = Math.abs(norm(la - lb)); if (d > 180) d = 360 - d;
      for (const [type, angle, orb] of ASPECTS) {
        const bonus = (a === 'sun' || a === 'moon' || b === 'sun' || b === 'moon') ? LUMINARY_BONUS : 0;
        const diff = Math.abs(d - angle);
        if (diff <= orb + bonus) {
          out.push({ a, b, type, orb: Math.round(diff * 100) / 100, weight: WEIGHT[a] * WEIGHT[b] / (1 + diff) });
          break;
        }
      }
    }
  }
  out.sort((x, y) => y.weight - x.weight);
  return out;
}

function elementBalance(chart) {
  const count = { fire: 0, earth: 0, air: 0, water: 0 };
  for (const k of ORDER) count[chart.planets[k].element] += 1;
  if (chart.asc) count[chart.asc.element] += 1;
  const notes = [];
  for (const e of Object.keys(count)) {
    if (count[e] >= 4) notes.push(T.ELEMENT_BALANCE[e].many);
    if (count[e] === 0) notes.push(T.ELEMENT_BALANCE[e].none);
  }
  return { count, notes };
}

function natalReport(person) {
  const chart = natalChart(person);
  const planets = ORDER.map((k) => {
    const p = chart.planets[k];
    const slow = k === 'uranus' || k === 'neptune' || k === 'pluto';
    return {
      key: k, name: T.PLANET_RU[k], sign: p.sign, signName: T.SIGN_RU[p.sign], element: p.element, degree: fmtDeg(p.lon), lon: p.lon,
      retro: p.retro, house: p.house || null,
      signText: slow ? T.SLOW_SIGN(k, p.sign) : T.IN_SIGN[k][p.sign],
      houseText: p.house ? T.planetInHouse(k, p.house) : null,
    };
  });
  const node = chart.planets.node;
  const aspects = findNatalAspects(chart).map((x) => ({
    a: T.PLANET_RU[x.a], b: T.PLANET_RU[x.b], type: T.ASPECT_RU[x.type], nature: T.NATURE[x.type], orb: x.orb,
    text: T.aspectText(x.a, x.b, x.type),
  }));
  const houses = chart.houses ? chart.houses.map((c, i) => {
    const s = Math.floor(norm(c) / 30);
    const sign = ['aries', 'taurus', 'gemini', 'cancer', 'leo', 'virgo', 'libra', 'scorpio', 'sagittarius', 'capricorn', 'aquarius', 'pisces'][s];
    return { n: i + 1, title: T.HOUSE_SHORT[i], theme: T.HOUSE_THEME[i], cuspSign: T.SIGN_RU[sign], cusp: fmtDeg(c), lon: c, planets: planets.filter((p) => p.house === i + 1).map((p) => p.name) };
  }) : null;
  const sunSign = chart.planets.sun.sign;
  const big3 = {
    sun: { sign: T.SIGN_RU[sunSign], text: T.IN_SIGN.sun[sunSign] },
    moon: { sign: T.SIGN_RU[chart.planets.moon.sign], text: T.IN_SIGN.moon[chart.planets.moon.sign] },
    asc: chart.asc ? { sign: T.SIGN_RU[chart.asc.sign], degree: fmtDeg(chart.asc.lon), text: T.ASC_SIGN[chart.asc.sign] } : null,
    mc: chart.mc ? { sign: T.SIGN_RU[chart.mc.sign], degree: fmtDeg(chart.mc.lon), text: T.MC_SIGN[chart.mc.sign] } : null,
  };
  const balance = elementBalance(chart);
  const lonOf = {}; planets.forEach((p) => { lonOf[p.name] = p.lon; });
  if (chart.asc) { lonOf[T.PLANET_RU.asc] = chart.asc.lon; lonOf[T.PLANET_RU.mc] = chart.mc.lon; }
  const names = {}; planets.forEach((p) => { names[p.key] = p.name; }); names.node = 'Сев. узел';
  const svg = wheelSvg({
    planets: planets.map((p) => ({ key: p.key, lon: p.lon, retro: p.retro })).concat([{ key: 'node', lon: node.lon, retro: false }]),
    cusps: chart.houses, asc: chart.asc ? chart.asc.lon : null, mc: chart.mc ? chart.mc.lon : null, names,
    aspects: aspects.filter((a) => a.orb <= 5).map((a) => ({ la: lonOf[a.a], lb: lonOf[a.b], nature: a.nature, orb: a.orb })),
  }, 900);
  return {
    svg,
    name: person.name || '', timeKnown: chart.timeKnown, utc: chart.utc,
    big3, planets, node: { signName: T.SIGN_RU[node.sign], degree: fmtDeg(node.lon), house: node.house || null, lon: node.lon },
    houses, aspects, balance,
    wheel: { planets: planets.map((p) => ({ key: p.key, lon: p.lon, retro: p.retro })), cusps: chart.houses, asc: chart.asc ? chart.asc.lon : null, mc: chart.mc ? chart.mc.lon : null },
    note: chart.timeKnown ? 'Дома рассчитаны по системе Плацидуса. Положения планет по астрономическим эфемеридам на момент рождения.' : 'Время рождения не указано: планеты рассчитаны на полдень, Луна может отличаться на несколько градусов, Асцендент и дома не определены.',
  };
}

module.exports = { natalReport };
