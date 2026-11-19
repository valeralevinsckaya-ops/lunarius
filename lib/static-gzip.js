'use strict';
// Отдает текстовые файлы из public/ сжатыми (gzip), если браузер или робот это поддерживает.
// Без внешних пакетов: сжатый вариант считается один раз на файл и хранится в памяти.
// Все, что не подошло (картинки, нет поддержки gzip, файла нет), уходит дальше по цепочке.
const fs = require('fs');
const path = require('path');
const zlib = require('zlib');
const crypto = require('crypto');

const TYPES = {
  '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8',
  '.xml': 'application/xml; charset=utf-8', '.txt': 'text/plain; charset=utf-8', '.svg': 'image/svg+xml',
  '.json': 'application/json; charset=utf-8', '.webmanifest': 'application/manifest+json',
};

module.exports = function staticGzip(root, { maxAge = 3600 } = {}) {
  root = path.resolve(root);
  const cache = new Map();

  function resolve(urlPath) {
    if (urlPath.includes('\0') || urlPath.split('/').some((seg) => seg === '..' || seg.startsWith('.'))) return null;
    const rel = urlPath === '/' ? '/index.html' : urlPath;
    const candidates = path.extname(rel) ? [rel] : [rel + '.html', rel + '/index.html'];
    for (const c of candidates) {
      const file = path.join(root, c);
      if (!file.startsWith(root + path.sep)) continue;
      try { const st = fs.statSync(file); if (st.isFile()) return { file, st }; } catch (e) { /* нет такого файла */ }
    }
    return null;
  }

  return function (req, res, next) {
    if (req.method !== 'GET' && req.method !== 'HEAD') return next();
    if (!/\bgzip\b/.test(String(req.headers['accept-encoding'] || ''))) return next();
    let urlPath;
    try { urlPath = decodeURIComponent(String(req.path || req.url).split('?')[0]); } catch (e) { return next(); }
    const hit = resolve(urlPath);
    if (!hit) return next();
    const type = TYPES[path.extname(hit.file).toLowerCase()];
    if (!type) return next();

    let entry = cache.get(hit.file);
    if (!entry || entry.mtime !== hit.st.mtimeMs) {
      const raw = fs.readFileSync(hit.file);
      entry = { mtime: hit.st.mtimeMs, gz: zlib.gzipSync(raw, { level: 9 }),
        etag: 'W/"' + crypto.createHash('sha1').update(raw).digest('hex').slice(0, 16) + '-gz"' };
      cache.set(hit.file, entry);
    }
    res.setHeader('Vary', 'Accept-Encoding');
    res.setHeader('Cache-Control', 'public, max-age=' + maxAge);
    res.setHeader('ETag', entry.etag);
    if (req.headers['if-none-match'] === entry.etag) { res.statusCode = 304; return res.end(); }
    res.setHeader('Content-Type', type);
    res.setHeader('Content-Encoding', 'gzip');
    res.setHeader('Content-Length', entry.gz.length);
    res.statusCode = 200;
    res.end(req.method === 'HEAD' ? undefined : entry.gz);
  };
};
