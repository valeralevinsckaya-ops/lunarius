'use strict';
// Отчет по натальной карте одного человека: планеты в знаках и домах, дома, аспекты, баланс стихий.
const { natalChart, norm } = require('./chart');
const T = require('./natal-texts');
const T2 = require('./natal-texts2');
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

const ELEM_GEN = { fire: 'огня', earth: 'земли', air: 'воздуха', water: 'воды' };
const ELEM_DESC = {
  fire: 'энергия, азарт и вера в себя: вы зажигаетесь быстро и тянете других за собой',
  earth: 'практичность, терпение и надежность: вам важен результат, который можно потрогать',
  air: 'ум, общение и интерес к людям: вы живете идеями и разговорами',
  water: 'чувства, интуиция и глубина: вы понимаете людей без слов',
};
const FRIENDLY = { fire: 'air', air: 'fire', earth: 'water', water: 'earth' };
function buildPortrait(chart, planets, balance) {
  const P = chart.planets, out = [];
  const sun = P.sun, moon = P.moon, asc = chart.asc;
  const loc = (x) => T.SIGN_LOC[x.sign];
  // Солнце и Луна
  let s1 = `Солнце ${loc(sun)}, Луна ${loc(moon)}` + (asc ? `, Асцендент ${loc(asc)}.` : '.');
  if (sun.element === moon.element) s1 += ` Солнце и Луна в одной стихии ${ELEM_GEN[sun.element]}: то, к чему вы стремитесь, и то, что вам нужно для спокойствия, совпадает. Характер цельный, вы редко спорите сами с собой.`;
  else if (FRIENDLY[sun.element] === moon.element) s1 += ` Солнце в стихии ${ELEM_GEN[sun.element]}, Луна в стихии ${ELEM_GEN[moon.element]}: стихии дружат, поэтому цели и чувства поддерживают друг друга.`;
  else s1 += ` Солнце в стихии ${ELEM_GEN[sun.element]}, Луна в стихии ${ELEM_GEN[moon.element]}: цели и чувства говорят на разных языках. Отсюда внутренние противоречия, которые с опытом превращаются в гибкость.`;
  if (asc) s1 += asc.element === sun.element ? ' Асцендент в той же стихии, что и Солнце, поэтому люди сразу видят вашу суть.' : ' Асцендент в другой стихии, чем Солнце, поэтому первое впечатление о вас часто не совпадает с тем, что у вас внутри.';
  out.push(s1);
  // доминирующая стихия
  const c = balance.count, top = Object.keys(c).sort((a, b) => c[b] - c[a])[0], total = Object.values(c).reduce((a, b) => a + b, 0);
  out.push(`Сильнее всего в карте стихия ${ELEM_GEN[top]}: ${c[top]} из ${total} точек. Это ${ELEM_DESC[top]}.`);
  // управитель карты
  if (asc) {
    const rk = T2.MODERN_RULER[asc.sign], rp = P[rk];
    if (rp && rp.house) out.push(`Управитель карты - ${T.PLANET_RU[rk]}, планета знака Асцендента. Эта планета стоит ${T.SIGN_LOC[rp.sign]} в ${rp.house} доме, поэтому многое в вашей жизни крутится вокруг сферы ${T.HOUSE_THEME[rp.house - 1]}.`);
  }
  // стеллиумы
  const bySign = {}, byHouse = {};
  for (const p of planets) { (bySign[p.sign] = bySign[p.sign] || []).push(p.name); if (p.house) (byHouse[p.house] = byHouse[p.house] || []).push(p.name); }
  for (const sg of Object.keys(bySign)) if (bySign[sg].length >= 3) out.push(`${bySign[sg].length} ${bySign[sg].length >= 5 ? 'планет' : 'планеты'} ${T.SIGN_LOC[sg]} (${bySign[sg].join(', ')}): это скопление, или стеллиум. ` + (P.sun.sign === sg ? 'Качества знака Солнца в вас выражены вдвойне.' : 'Качества этого знака в вас проявляются ярче, чем можно ждать по знаку Солнца.'));
  for (const h of Object.keys(byHouse)) if (byHouse[h].length >= 3) out.push(`${byHouse[h].length} ${byHouse[h].length >= 5 ? 'планет' : 'планеты'} в ${h} доме (${byHouse[h].join(', ')}): сфера ${T.HOUSE_THEME[h - 1]} занимает в жизни много места и сил.`);
  // ретроградные личные планеты
  const retro = planets.filter((p) => p.retro && ['mercury', 'venus', 'mars'].includes(p.key)).map((p) => p.name);
  if (retro.length) out.push(`Ретроградные личные планеты: ${retro.join(', ')}. Их темы вы проживаете больше внутри, чем снаружи, и приходите к ним своим путем.`);
  return out;
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
      about: T2.PLANET_INTRO[k],
      elemText: T2.ELEM_ADD[k] ? T2.ELEM_ADD[k][p.element] : null,
      dignity: slow ? null : T2.dignity(k, p.sign, T.PLANET_RU[k], T.IN_SIGN[k][p.sign] || ''),
      retroText: p.retro && T2.RETRO[k] ? T2.RETRO[k] : null,
    };
  });
  const node = chart.planets.node;
  const aspects = findNatalAspects(chart).map((x) => ({
    a: T.PLANET_RU[x.a], b: T.PLANET_RU[x.b], type: T.ASPECT_RU[x.type], nature: T.NATURE[x.type], orb: x.orb,
    text: T.aspectText(x.a, x.b, x.type),
    more: T2.ASPECT_TYPE[x.type] + ' ' + T2.ASPECT_ADVICE[T.NATURE[x.type]] + (x.orb <= 1 ? ' Орбис меньше градуса: аспект почти точный и звучит в карте громко.' : ''),
  }));
  const houses = chart.houses ? chart.houses.map((c, i) => {
    const s = Math.floor(norm(c) / 30);
    const sign = ['aries', 'taurus', 'gemini', 'cancer', 'leo', 'virgo', 'libra', 'scorpio', 'sagittarius', 'capricorn', 'aquarius', 'pisces'][s];
    const rk = T2.MODERN_RULER[sign], rp = chart.planets[rk];
    const ruler = rp && rp.house ? `Управитель дома - ${T.PLANET_RU[rk]} (${rp.house} дом): дела этого дома связаны со сферой ${T.HOUSE_THEME[rp.house - 1]}.` : null;
    const inside = planets.filter((p) => p.house === i + 1).map((p) => p.name);
    return { n: i + 1, title: T.HOUSE_SHORT[i], theme: T.HOUSE_THEME[i], cuspSign: T.SIGN_RU[sign], cusp: fmtDeg(c), lon: c, planets: inside, ruler,
      empty: inside.length ? null : 'Пустой дом не значит, что сфера неважна: она проявляется через управителя дома.' };
  }) : null;
  const sunSign = chart.planets.sun.sign;
  const big3 = {
    sun: { sign: T.SIGN_RU[sunSign], text: T.IN_SIGN.sun[sunSign] },
    moon: { sign: T.SIGN_RU[chart.planets.moon.sign], text: T.IN_SIGN.moon[chart.planets.moon.sign] },
    asc: chart.asc ? { sign: T.SIGN_RU[chart.asc.sign], degree: fmtDeg(chart.asc.lon), text: T.ASC_SIGN[chart.asc.sign] } : null,
    mc: chart.mc ? { sign: T.SIGN_RU[chart.mc.sign], degree: fmtDeg(chart.mc.lon), text: T.MC_SIGN[chart.mc.sign] } : null,
  };
  const balance = elementBalance(chart);
  // кресты
  const modes = { cardinal: 0, fixed: 0, mutable: 0 };
  for (const k of ORDER) modes[T.MODE[chart.planets[k].sign]] += 1;
  if (chart.asc) modes[T.MODE[chart.asc.sign]] += 1;
  balance.modes = modes;
  balance.modeNotes = Object.keys(modes).filter((m) => modes[m] >= 5 || modes[m] === 0).map((m) => (modes[m] === 0 ? T2.MODE_BALANCE[m].none : T2.MODE_BALANCE[m].many));
  // полушария
  balance.hemi = [];
  if (chart.asc) {
    let east = 0, south = 0;
    for (const k of ORDER) { const h = chart.planets[k].house; if (h >= 10 || h <= 3) east += 1; if (h >= 7) south += 1; }
    if (east >= 7) balance.hemi.push(T2.HEMI.east); else if (east <= 3) balance.hemi.push(T2.HEMI.west);
    if (south >= 7) balance.hemi.push(T2.HEMI.south); else if (south <= 3) balance.hemi.push(T2.HEMI.north);
  }
  const portrait = buildPortrait(chart, planets, balance);
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
    big3, portrait, planets, node: { signName: T.SIGN_RU[node.sign], degree: fmtDeg(node.lon), house: node.house || null, lon: node.lon, text: T2.NODE_SIGN[node.sign] + (node.house ? ` В ${node.house} доме: развитие идет через сферу ${T.HOUSE_THEME[node.house - 1]}.` : '') },
    houses, aspects, balance,
    wheel: { planets: planets.map((p) => ({ key: p.key, lon: p.lon, retro: p.retro })), cusps: chart.houses, asc: chart.asc ? chart.asc.lon : null, mc: chart.mc ? chart.mc.lon : null },
    note: chart.timeKnown ? 'Дома рассчитаны по системе Плацидуса. Положения планет рассчитаны по астрономическим эфемеридам на момент рождения.' : 'Время рождения не указано: планеты рассчитаны на полдень, Луна может отличаться на несколько градусов, Асцендент и дома не определены.',
  };
}

module.exports = { natalReport };
