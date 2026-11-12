'use strict';
// Натальная карта: положения планет, Асцендент, MC и дома Плацидуса.
// Астрономия: astronomy-engine (MIT), часовые пояса: IANA через luxon.
const A = require('astronomy-engine');
const { DateTime } = require('luxon');

const D2R = Math.PI / 180;
const R2D = 180 / Math.PI;
const norm = (x) => ((x % 360) + 360) % 360;

const BODIES = [
  ['sun', A.Body.Sun], ['moon', A.Body.Moon], ['mercury', A.Body.Mercury],
  ['venus', A.Body.Venus], ['mars', A.Body.Mars], ['jupiter', A.Body.Jupiter],
  ['saturn', A.Body.Saturn], ['uranus', A.Body.Uranus], ['neptune', A.Body.Neptune],
  ['pluto', A.Body.Pluto],
];

const SIGNS = ['aries', 'taurus', 'gemini', 'cancer', 'leo', 'virgo', 'libra', 'scorpio', 'sagittarius', 'capricorn', 'aquarius', 'pisces'];
const ELEMENT = ['fire', 'earth', 'air', 'water'];

function signOf(lon) {
  const i = Math.floor(norm(lon) / 30);
  return { sign: SIGNS[i], element: ELEMENT[i % 4], degree: norm(lon) - i * 30 };
}

// Местное время рождения -> UTC с учетом исторических смен часовых поясов
function toUtc({ date, time, tz }) {
  const t = time && /^\d{1,2}:\d{2}$/.test(time) ? time.padStart(5, '0') : '12:00';
  const dt = DateTime.fromISO(`${date}T${t}`, { zone: tz });
  if (!dt.isValid) throw new Error('Некорректная дата или часовой пояс');
  return { utc: dt.toUTC().toJSDate(), offsetMinutes: dt.offset, timeKnown: Boolean(time) };
}

// Эклиптическая долгота на эклиптике даты (тропический зодиак)
function eclipticOfDate(body, time) {
  if (body === A.Body.Sun) return A.SunPosition(time).elon;
  if (body === A.Body.Moon) return A.EclipticGeoMoon(time).lon;
  const vec = A.GeoVector(body, time, true);
  const rot = A.Rotation_EQJ_ECT(time);
  const ect = A.RotateVector(rot, vec);
  return norm(A.SphereFromVector(ect).lon);
}

function speed(body, time) {
  const t2 = time.AddDays(1);
  let d = eclipticOfDate(body, t2) - eclipticOfDate(body, time);
  if (d > 180) d -= 360; if (d < -180) d += 360;
  return d;
}

// Средний лунный узел
function meanNode(time) {
  const T = time.tt / 36525;
  return norm(125.04452 - 1934.136261 * T + 0.0020708 * T * T + (T * T * T) / 450000);
}

function obliquity(time) { return A.e_tilt(time).tobl; }

function lonFromRA(ra, eps) {
  return norm(Math.atan2(Math.sin(ra * D2R), Math.cos(ra * D2R) * Math.cos(eps * D2R)) * R2D);
}

function angles(time, lat, lon) {
  const eps = obliquity(time);
  const ramc = norm(A.SiderealTime(time) * 15 + lon);
  const mc = lonFromRA(ramc, eps);
  const r = ramc * D2R, e = eps * D2R, f = lat * D2R;
  let asc = Math.atan2(Math.cos(r), -(Math.sin(r) * Math.cos(e) + Math.tan(f) * Math.sin(e))) * R2D;
  asc = norm(asc);
  return { asc, mc, ramc, eps };
}

// Дома Плацидуса (итерационный метод), выше 66° широты - Порфирий
function placidus({ asc, mc, ramc, eps }, lat) {
  const cusps = new Array(12);
  cusps[0] = asc; cusps[9] = mc; cusps[3] = norm(mc + 180); cusps[6] = norm(asc + 180);
  const porphyry = () => {
    const q1 = norm(asc - mc), q2 = norm(cusps[3] - asc);
    cusps[10] = norm(mc + q1 / 3); cusps[11] = norm(mc + (2 * q1) / 3);
    cusps[1] = norm(asc + q2 / 3); cusps[2] = norm(asc + (2 * q2) / 3);
  };
  if (Math.abs(lat) > 66) { porphyry(); }
  else {
    const e = eps * D2R, f = lat * D2R;
    const cusp = (frac, below) => {
      let lam = norm(ramc + (below ? 180 : 0) + 30);
      for (let k = 0; k < 30; k++) {
        const dec = Math.asin(Math.sin(e) * Math.sin(lam * D2R));
        const x = -Math.tan(f) * Math.tan(dec);
        if (x < -1 || x > 1) return null;
        const sa = Math.acos(x) * R2D;
        const nsa = 180 - sa;
        const ra = below ? ramc + 180 - frac * nsa : ramc + frac * sa;
        const next = lonFromRA(norm(ra), eps);
        if (Math.abs(next - lam) < 1e-7) { lam = next; break; }
        lam = next;
      }
      return lam;
    };
    const c11 = cusp(1 / 3, false), c12 = cusp(2 / 3, false), c2 = cusp(2 / 3, true), c3 = cusp(1 / 3, true);
    if ([c11, c12, c2, c3].some((v) => v === null)) porphyry();
    else { cusps[10] = c11; cusps[11] = c12; cusps[1] = c2; cusps[2] = c3; }
  }
  // противоположные куспиды: 5=11+180, 6=12+180, 8=2+180, 9=3+180
  cusps[4] = norm(cusps[10] + 180); cusps[5] = norm(cusps[11] + 180);
  cusps[7] = norm(cusps[1] + 180); cusps[8] = norm(cusps[2] + 180);
  return cusps;
}

function houseOf(lon, cusps) {
  for (let i = 0; i < 12; i++) {
    const a = cusps[i], b = cusps[(i + 1) % 12];
    const span = norm(b - a), d = norm(lon - a);
    if (d < span) return i + 1;
  }
  return 12;
}

// Главная функция: input {date:'YYYY-MM-DD', time:'HH:MM'|null, lat, lon, tz}
function natalChart(input) {
  const { utc, offsetMinutes, timeKnown } = toUtc(input);
  const time = A.MakeTime(utc);
  const planets = {};
  for (const [key, body] of BODIES) {
    const lon = eclipticOfDate(body, time);
    planets[key] = { lon, ...signOf(lon), retro: key !== 'sun' && key !== 'moon' ? speed(body, time) < 0 : false };
  }
  planets.node = { lon: meanNode(time), ...signOf(meanNode(time)), retro: true };
  const chart = { utc: utc.toISOString(), offsetMinutes, timeKnown, planets, houses: null, asc: null, mc: null };
  if (timeKnown && typeof input.lat === 'number' && typeof input.lon === 'number') {
    const ang = angles(time, input.lat, input.lon);
    const cusps = placidus(ang, input.lat);
    chart.asc = { lon: ang.asc, ...signOf(ang.asc) };
    chart.mc = { lon: ang.mc, ...signOf(ang.mc) };
    chart.houses = cusps;
    for (const k of Object.keys(planets)) planets[k].house = houseOf(planets[k].lon, cusps);
  }
  return chart;
}

module.exports = { natalChart, signOf, norm, SIGNS };
