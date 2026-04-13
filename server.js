#!/usr/bin/env node
/**
 * SNB Consulting — serveur "tout en 1" (production)
 *
 * Sert :
 *   - le site statique depuis ./docs
 *   - GET /api/status   -> contenu de docs/status.json (avec ETag, cache désactivé)
 *   - GET /api/health   -> healthcheck { status, uptime, version }
 *
 * Aucune dépendance npm — uniquement le runtime Node (>=20).
 */
'use strict';

const http = require('node:http');
const fs = require('node:fs');
const fsp = require('node:fs/promises');
const path = require('node:path');
const crypto = require('node:crypto');

const PORT = Number(process.env.PORT || 3001);
const HOST = process.env.HOST || '0.0.0.0';
const ROOT = path.resolve(__dirname, 'docs');
const STATUS_FILE = path.join(ROOT, 'status.json');

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.htm':  'text/html; charset=utf-8',
  '.css':  'text/css; charset=utf-8',
  '.js':   'application/javascript; charset=utf-8',
  '.mjs':  'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg':  'image/svg+xml',
  '.png':  'image/png',
  '.jpg':  'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif':  'image/gif',
  '.webp': 'image/webp',
  '.ico':  'image/x-icon',
  '.woff': 'font/woff',
  '.woff2':'font/woff2',
  '.ttf':  'font/ttf',
  '.txt':  'text/plain; charset=utf-8',
  '.map':  'application/json; charset=utf-8',
};

const SECURITY_HEADERS = {
  'X-Content-Type-Options': 'nosniff',
  'X-Frame-Options': 'DENY',
  'Referrer-Policy': 'strict-origin-when-cross-origin',
};

function send(res, status, body, headers = {}) {
  res.writeHead(status, { ...SECURITY_HEADERS, ...headers });
  res.end(body);
}

function sendJson(res, status, payload, headers = {}) {
  const body = JSON.stringify(payload);
  send(res, status, body, {
    'Content-Type': 'application/json; charset=utf-8',
    'Access-Control-Allow-Origin': '*',
    ...headers,
  });
}

function safeJoin(root, urlPath) {
  const decoded = decodeURIComponent(urlPath.split('?')[0].split('#')[0]);
  const target = path.normalize(path.join(root, decoded));
  if (!target.startsWith(root)) return null; // path traversal guard
  return target;
}

async function serveStatic(req, res) {
  let filePath = safeJoin(ROOT, req.url === '/' ? '/index.html' : req.url);
  if (!filePath) return send(res, 403, 'Forbidden');

  let stat;
  try {
    stat = await fsp.stat(filePath);
  } catch {
    // SPA fallback : servir index.html pour les routes inconnues
    filePath = path.join(ROOT, 'index.html');
    try {
      stat = await fsp.stat(filePath);
    } catch {
      return send(res, 404, 'Not Found');
    }
  }

  if (stat.isDirectory()) {
    filePath = path.join(filePath, 'index.html');
    try { stat = await fsp.stat(filePath); }
    catch { return send(res, 404, 'Not Found'); }
  }

  const ext = path.extname(filePath).toLowerCase();
  const contentType = MIME[ext] || 'application/octet-stream';
  const cacheControl = ext === '.html'
    ? 'no-cache'
    : 'public, max-age=300';

  res.writeHead(200, {
    ...SECURITY_HEADERS,
    'Content-Type': contentType,
    'Content-Length': stat.size,
    'Cache-Control': cacheControl,
    'Last-Modified': stat.mtime.toUTCString(),
  });
  fs.createReadStream(filePath).pipe(res);
}

async function handleStatus(req, res) {
  try {
    const raw = await fsp.readFile(STATUS_FILE, 'utf-8');
    const etag = '"' + crypto.createHash('sha1').update(raw).digest('hex') + '"';
    if (req.headers['if-none-match'] === etag) {
      return send(res, 304, '', { ETag: etag });
    }
    sendJson(res, 200, JSON.parse(raw), {
      'Cache-Control': 'no-cache, no-store, must-revalidate',
      ETag: etag,
    });
  } catch (err) {
    sendJson(res, 500, { error: 'status_unavailable', message: err.message });
  }
}

function handleHealth(_req, res) {
  sendJson(res, 200, {
    status: 'ok',
    uptime: process.uptime(),
    node: process.version,
    pid: process.pid,
    timestamp: new Date().toISOString(),
  });
}

const server = http.createServer(async (req, res) => {
  const start = Date.now();
  res.on('finish', () => {
    const ms = Date.now() - start;
    console.log(`${req.method} ${req.url} -> ${res.statusCode} (${ms}ms)`);
  });

  try {
    if (req.method !== 'GET' && req.method !== 'HEAD') {
      return send(res, 405, 'Method Not Allowed', { Allow: 'GET, HEAD' });
    }

    const url = req.url || '/';
    if (url === '/api/health' || url.startsWith('/api/health?')) return handleHealth(req, res);
    if (url === '/api/status' || url.startsWith('/api/status?')) return handleStatus(req, res);

    return serveStatic(req, res);
  } catch (err) {
    console.error('Unhandled error:', err);
    sendJson(res, 500, { error: 'internal_error' });
  }
});

server.listen(PORT, HOST, () => {
  console.log(`SNB Consulting — serveur tout-en-un démarré`);
  console.log(`  -> http://${HOST}:${PORT}`);
  console.log(`  -> static : ${ROOT}`);
  console.log(`  -> api    : /api/status, /api/health`);
});

const shutdown = (signal) => {
  console.log(`\nReçu ${signal}, arrêt en cours...`);
  server.close(() => process.exit(0));
  setTimeout(() => process.exit(1), 5000).unref();
};
process.on('SIGINT', () => shutdown('SIGINT'));
process.on('SIGTERM', () => shutdown('SIGTERM'));
