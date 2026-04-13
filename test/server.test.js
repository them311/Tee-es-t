'use strict';
/**
 * Smoke tests pour server.js — utilise node:test (intégré à Node 20+).
 * Démarre le serveur sur un port aléatoire et vérifie les endpoints clés.
 */

const test = require('node:test');
const assert = require('node:assert/strict');
const http = require('node:http');
const { spawn } = require('node:child_process');
const path = require('node:path');

const SERVER_PATH = path.resolve(__dirname, '..', 'server.js');

function get(port, urlPath) {
  return new Promise((resolve, reject) => {
    const req = http.get({ host: '127.0.0.1', port, path: urlPath }, (res) => {
      const chunks = [];
      res.on('data', (c) => chunks.push(c));
      res.on('end', () => resolve({
        status: res.statusCode,
        headers: res.headers,
        body: Buffer.concat(chunks).toString('utf-8'),
      }));
    });
    req.on('error', reject);
    req.setTimeout(5000, () => req.destroy(new Error('timeout')));
  });
}

async function startServer(port) {
  const child = spawn(process.execPath, [SERVER_PATH], {
    env: { ...process.env, PORT: String(port), HOST: '127.0.0.1' },
    stdio: ['ignore', 'pipe', 'pipe'],
  });
  // Attendre que le serveur soit prêt
  await new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error('server start timeout')), 5000);
    child.stdout.on('data', (d) => {
      if (d.toString().includes('démarré')) {
        clearTimeout(timer);
        resolve();
      }
    });
    child.on('exit', (code) => reject(new Error(`server exited early: ${code}`)));
  });
  return child;
}

test('server.js — endpoints', async (t) => {
  const port = 3000 + Math.floor(Math.random() * 1000);
  const server = await startServer(port);

  t.after(() => {
    server.kill('SIGTERM');
  });

  await t.test('GET / serves index.html', async () => {
    const res = await get(port, '/');
    assert.equal(res.status, 200);
    assert.match(res.headers['content-type'], /text\/html/);
    assert.match(res.body, /SNB Consulting/);
  });

  await t.test('GET /api/health returns ok', async () => {
    const res = await get(port, '/api/health');
    assert.equal(res.status, 200);
    const json = JSON.parse(res.body);
    assert.equal(json.status, 'ok');
    assert.ok(typeof json.uptime === 'number');
  });

  await t.test('GET /api/status returns status.json content', async () => {
    const res = await get(port, '/api/status');
    assert.equal(res.status, 200);
    const json = JSON.parse(res.body);
    assert.ok('status' in json);
    assert.ok(Array.isArray(json.activity));
    assert.ok(res.headers.etag);
  });

  await t.test('GET /api/status honours If-None-Match', async () => {
    const first = await get(port, '/api/status');
    const etag = first.headers.etag;
    const second = await new Promise((resolve, reject) => {
      const req = http.get({
        host: '127.0.0.1', port, path: '/api/status',
        headers: { 'If-None-Match': etag },
      }, (res) => {
        res.on('data', () => {});
        res.on('end', () => resolve({ status: res.statusCode }));
      });
      req.on('error', reject);
    });
    assert.equal(second.status, 304);
  });

  await t.test('GET /unknown falls back to index.html (SPA)', async () => {
    const res = await get(port, '/route-inexistante');
    assert.equal(res.status, 200);
    assert.match(res.body, /SNB Consulting/);
  });

  await t.test('POST / is rejected', async () => {
    const res = await new Promise((resolve, reject) => {
      const req = http.request({
        host: '127.0.0.1', port, path: '/', method: 'POST',
      }, (r) => {
        r.on('data', () => {});
        r.on('end', () => resolve({ status: r.statusCode }));
      });
      req.on('error', reject);
      req.end();
    });
    assert.equal(res.status, 405);
  });

  await t.test('Path traversal is blocked', async () => {
    const res = await get(port, '/../package.json');
    // Soit 403, soit fallback vers index.html — jamais le package.json
    assert.notEqual(res.status, 200, 'should not return file outside docs/');
    if (res.status === 200) {
      assert.doesNotMatch(res.body, /"name":\s*"tee-es-t"/);
    }
  });
});
