'use strict';
// Точное колесо натальной карты в SVG: градусная шкала, знаки, дома с куспидами, планеты с градусами, аспекты.
const GLYPH = { sun: '☉', moon: '☽', mercury: '☿', venus: '♀', mars: '♂', jupiter: '♃', saturn: '♄', uranus: '♅', neptune: '♆', pluto: '♇', node: '☊' };
const SIGN_GLYPH = ['♈', '♉', '♊', '♋', '♌', '♍', '♎', '♏', '♐', '♑', '♒', '♓'];
const ELEM = ['#F2768A', '#D9A93E', '#5E8BF2', '#6E56CF'];
const PCOLOR = { sun: '#D9A93E', moon: '#5E8BF2', mercury: '#6E56CF', venus: '#F2768A', mars: '#E8762E', jupiter: '#8C5FD6', saturn: '#2A2340', uranus: '#5E8BF2', neptune: '#6E56CF', pluto: '#2A2340', node: '#6B6380' };
const norm = (x) => ((x % 360) + 360) % 360;

function fmt(lon) {
  const d = norm(lon) % 30, deg = Math.floor(d), min = Math.floor((d - deg) * 60);
  return `${deg}°${String(min).padStart(2, '0')}'`;
}

// data: { planets:[{key,lon,retro}], cusps:[12]|null, asc, mc, aspects:[{la,lb,nature}] }
function wheelSvg(data, size = 900) {
  const S = size, cx = S / 2, cy = S / 2, R = S / 2 - 44;
  const asc = data.asc == null ? 0 : data.asc;
  const pt = (lon, r) => { const a = (180 + (lon - asc)) * Math.PI / 180; return [cx + r * Math.cos(a), cy - r * Math.sin(a)]; };
  const r = { signOut: R, signIn: R - 54, tickOut: R - 54, tick: R - 54, houseOut: R - 86, planet: R - 150, houseNum: R - 200, inner: R - 230 };
  const f = (n) => n.toFixed(1);
  let s = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${S} ${S}" width="${S}" height="${S}" font-family="'Manrope','Segoe UI Symbol','Noto Sans Symbols2',sans-serif">`;
  s += `<rect width="${S}" height="${S}" fill="none"/>`;
  s += `<circle cx="${cx}" cy="${cy}" r="${r.signOut}" fill="rgba(255,255,255,0.72)" stroke="#fff" stroke-width="2"/>`;
  s += `<circle cx="${cx}" cy="${cy}" r="${r.signIn}" fill="none" stroke="#B9ABDD" stroke-width="1"/>`;
  s += `<circle cx="${cx}" cy="${cy}" r="${r.houseOut}" fill="none" stroke="#D8CDEE" stroke-width="1"/>`;
  s += `<circle cx="${cx}" cy="${cy}" r="${r.inner}" fill="rgba(255,255,255,0.55)" stroke="#D8CDEE" stroke-width="1"/>`;
  // --- дома
  if (data.cusps) {
    for (let h = 0; h < 12; h++) {
      const c = data.cusps[h], strong = h % 3 === 0;
      const p1 = pt(c, r.inner), p2 = pt(c, r.signIn);
      s += `<line x1="${f(p1[0])}" y1="${f(p1[1])}" x2="${f(p2[0])}" y2="${f(p2[1])}" stroke="${strong ? '#2A2340' : '#9A8CC4'}" stroke-width="${strong ? 2.2 : 1}"/>`;
      // подпись куспида: градус и знак
      const si = Math.floor(norm(c) / 30);
      const lab = pt(c + 2.2, r.houseOut + 14);
      s += `<rect x="${f(lab[0] - 25)}" y="${f(lab[1] - 7)}" width="50" height="14" rx="7" fill="#fff" fill-opacity="0.85"/>`;
      s += `<text x="${f(lab[0])}" y="${f(lab[1])}" text-anchor="middle" dominant-baseline="central" font-size="9.5" font-weight="700" fill="${strong ? '#2A2340' : '#5B44BD'}">${fmt(c)} <tspan font-family="'Noto Sans Symbols','Segoe UI Symbol',sans-serif" fill="${ELEM[si % 4]}">${SIGN_GLYPH[si]}</tspan></text>`;
      // номер дома в середине сектора у центра
      const next = data.cusps[(h + 1) % 12], span = norm(next - c);
      const m = pt(c + span / 2, r.inner + 16);
      s += `<text x="${f(m[0])}" y="${f(m[1])}" text-anchor="middle" dominant-baseline="central" font-size="13" font-weight="700" fill="#6B6380">${h + 1}</text>`;
    }
    const axes = [['ASC', data.asc, 'end', 0], ['DSC', norm(data.asc + 180), 'start', 0], ['MC', data.mc, 'middle', -6], ['IC', norm(data.mc + 180), 'middle', 10]];
    for (const [name, lon, anchor, dy] of axes) {
      const p = pt(lon, r.signOut + 4);
      const dir = pt(lon, r.signOut + 26);
      s += `<text x="${f(dir[0])}" y="${f(dir[1])}" text-anchor="middle" dominant-baseline="central" font-size="13" font-weight="800" fill="#2A2340">${name}</text>`;
      s += `<path d="M${f(p[0])} ${f(p[1])} l-5 -8 l10 0 Z" fill="#2A2340" transform="rotate(${f(-(norm(180 + (lon - asc))) + 90)} ${f(p[0])} ${f(p[1])})"/>`;
    }
  }
  // --- аспекты
  for (const a of data.aspects || []) {
    const p1 = pt(a.la, r.inner - 2), p2 = pt(a.lb, r.inner - 2);
    const col = a.nature === 'harmony' ? '#5B44BD' : a.nature === 'tension' ? '#E8762E' : '#D9A93E';
    s += `<line x1="${f(p1[0])}" y1="${f(p1[1])}" x2="${f(p2[0])}" y2="${f(p2[1])}" stroke="${col}" stroke-width="${a.orb != null && a.orb < 2 ? 1.8 : 1}" opacity="${a.orb != null && a.orb < 2 ? 0.85 : 0.45}"${a.nature === 'conj' ? '' : ''}/>`;
  }
  // --- разведение планет
  const ps = data.planets.slice().sort((a, b) => a.lon - b.lon);
  const placed = [];
  const drawLon = new Map();
  for (const p of ps) {
    let lonDraw = p.lon;
    for (const q of placed) { if (Math.abs(((lonDraw - q + 540) % 360) - 180) < 5.5) lonDraw = q + 5.5; }
    placed.push(lonDraw); drawLon.set(p, lonDraw);
  }
  // --- группы знаков: сектор + шкала + планеты знака (для подсветки и увеличения при наведении)
  const SIGN_RU = ['Овен', 'Телец', 'Близнецы', 'Рак', 'Лев', 'Дева', 'Весы', 'Скорпион', 'Стрелец', 'Козерог', 'Водолей', 'Рыбы'];
  for (let i = 0; i < 12; i++) {
    const inSign = ps.filter((p) => Math.floor(norm(p.lon) / 30) === i);
    const title = SIGN_RU[i] + (inSign.length ? ': ' + inSign.map((p) => (data.names ? data.names[p.key] : p.key) + ' ' + fmt(p.lon) + (p.retro ? ' R' : '')).join(', ') : ': планет нет');
    s += `<g class="sg" data-sign="${i}" data-title="${title}" style="transform-origin:${cx}px ${cy}px">`;
    const a1 = pt(i * 30, r.signOut), a2 = pt(i * 30 + 30, r.signOut), b2 = pt(i * 30 + 30, r.signIn), b1 = pt(i * 30, r.signIn);
    s += `<path class="sector" d="M${f(a1[0])} ${f(a1[1])} A${r.signOut} ${r.signOut} 0 0 0 ${f(a2[0])} ${f(a2[1])} L${f(b2[0])} ${f(b2[1])} A${r.signIn} ${r.signIn} 0 0 1 ${f(b1[0])} ${f(b1[1])} Z" fill="${ELEM[i % 4]}" fill-opacity="0.16" stroke="#fff" stroke-width="1.5"/>`;
    const g = pt(i * 30 + 15, r.signOut - 24);
    s += `<text x="${f(g[0])}" y="${f(g[1])}" text-anchor="middle" dominant-baseline="central" font-size="24" font-family="'Noto Sans Symbols','Segoe UI Symbol',sans-serif" fill="${ELEM[i % 4]}">${SIGN_GLYPH[i]}</text>`;
    for (let d = i * 30; d < i * 30 + 30; d++) {
      const len = d % 10 === 0 ? 14 : d % 5 === 0 ? 9 : 5;
      const p1 = pt(d, r.tick), p2 = pt(d, r.tick - len);
      s += `<line x1="${f(p1[0])}" y1="${f(p1[1])}" x2="${f(p2[0])}" y2="${f(p2[1])}" stroke="#2A2340" stroke-width="${d % 10 === 0 ? 1.4 : 0.8}" opacity="${d % 5 === 0 ? 0.8 : 0.4}"/>`;
      if (d % 10 === 0 && d % 30 !== 0) {
        const t = pt(d, r.tick - 24);
        s += `<text x="${f(t[0])}" y="${f(t[1])}" text-anchor="middle" dominant-baseline="central" font-size="9" fill="#6B6380">${d % 30}</text>`;
      }
    }
    for (const p of inSign) {
      const lonDraw = drawLon.get(p);
      const t1 = pt(p.lon, r.signIn), t2 = pt(p.lon, r.signIn - 6);
      s += `<line x1="${f(t1[0])}" y1="${f(t1[1])}" x2="${f(t2[0])}" y2="${f(t2[1])}" stroke="${PCOLOR[p.key]}" stroke-width="2.5"/>`;
      const gp = pt(lonDraw, r.planet), dp = pt(lonDraw, r.planet - 30);
      const c1 = pt(p.lon, r.houseOut), c2 = pt(lonDraw, r.planet + 18);
      s += `<line x1="${f(c1[0])}" y1="${f(c1[1])}" x2="${f(c2[0])}" y2="${f(c2[1])}" stroke="${PCOLOR[p.key]}" stroke-width="1" opacity="0.5"/>`;
      s += `<g class="pl"><title>${data.names ? data.names[p.key] : p.key} ${fmt(p.lon)}${p.retro ? ' R' : ''}</title><circle cx="${f(gp[0])}" cy="${f(gp[1])}" r="15" fill="#fff" stroke="${PCOLOR[p.key]}" stroke-width="1.5"/>`;
      s += `<text x="${f(gp[0])}" y="${f(gp[1])}" text-anchor="middle" dominant-baseline="central" font-size="18" font-family="'Noto Sans Symbols','Segoe UI Symbol',sans-serif" fill="${PCOLOR[p.key]}">${GLYPH[p.key]}</text>`;
      s += `<text x="${f(dp[0])}" y="${f(dp[1])}" text-anchor="middle" dominant-baseline="central" font-size="10" font-weight="700" fill="#2A2340">${fmt(p.lon)}${p.retro ? ' R' : ''}</text></g>`;
    }
    s += '</g>';
  }
  s += '</svg>';
  return s;
}

module.exports = { wheelSvg };
