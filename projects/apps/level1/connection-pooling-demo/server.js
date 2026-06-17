// Connection Pooling Demo — Naive vs Pooled, both with SQLite.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

// === Setup ===
// 1. Naive: new connection per request
function withNaiveDb(fn) {
  const db = new Database(':memory:');
  setupSchema(db);
  return fn(db);
}

// 2. Pooled: reuse a single connection (SQLite is in-process, so this is the typical "pool" pattern)
const pooledDb = new Database(':memory:');
setupSchema(pooledDb);
function withPooledDb(fn) { return fn(pooledDb); }

// 3. Real pool pattern (mimics pg.Pool): queue + max size
class DbPool {
  constructor(size, factory) {
    this.size = size;
    this.factory = factory;
    this.idle = [];
    this.active = 0;
    this.waiting = [];
  }
  acquire() {
    return new Promise((resolve) => {
      const conn = this.idle.pop();
      if (conn) { this.active++; return resolve(conn); }
      if (this.active < this.size) { this.active++; return resolve(this.factory()); }
      this.waiting.push(resolve);
    });
  }
  release(conn) {
    this.active--;
    this.idle.push(conn);
    const next = this.waiting.shift();
    if (next) { this.active++; this.idle.pop(); next(conn); }
  }
}
const realPool = new DbPool(5, () => {
  const d = new Database(':memory:');
  setupSchema(d);
  return d;
});

function setupSchema(db) {
  db.exec(`CREATE TABLE IF NOT EXISTS data (id INTEGER PRIMARY KEY AUTOINCREMENT, value TEXT)`);
  for (let i = 0; i < 1000; i++) db.prepare('INSERT INTO data (value) VALUES (?)').run(`row ${i}`);
}

// === Endpoints ===
// Naive: create new connection each request
app.get('/naive', (req, res) => {
  const start = process.hrtime.bigint();
  withNaiveDb((db) => {
    const rows = db.prepare('SELECT * FROM data LIMIT 20').all();
    const ms = Number(process.hrtime.bigint() - start) / 1e6;
    res.json({ mode: 'naive', ms: ms.toFixed(2), count: rows.length });
  });
});

// Pooled: reuse the same connection
app.get('/pooled', (req, res) => {
  const start = process.hrtime.bigint();
  withPooledDb((db) => {
    const rows = db.prepare('SELECT * FROM data LIMIT 20').all();
    const ms = Number(process.hrtime.bigint() - start) / 1e6;
    res.json({ mode: 'pooled', ms: ms.toFixed(2), count: rows.length });
  });
});

// Real pool: async acquire/release
app.get('/realpool', async (req, res) => {
  const start = process.hrtime.bigint();
  const conn = await realPool.acquire();
  try {
    const rows = conn.prepare('SELECT * FROM data LIMIT 20').all();
    const ms = Number(process.hrtime.bigint() - start) / 1e6;
    res.json({ mode: 'realpool', ms: ms.toFixed(2), count: rows.length, pool: { active: realPool.active, idle: realPool.idle.length, waiting: realPool.waiting.length } });
  } finally {
    realPool.release(conn);
  }
});

// Pool exhausted: simulating many concurrent requests
app.get('/pool-stress', async (req, res) => {
  const start = process.hrtime.bigint();
  const conns = [];
  try {
    // Try to acquire 10 (pool size is 5)
    for (let i = 0; i < 10; i++) conns.push(await realPool.acquire());
    const ms = Number(process.hrtime.bigint() - start) / 1e6;
    res.json({ acquired: 10, poolSize: 5, timeMs: ms.toFixed(2), note: '5 ran in parallel, 5 waited in queue' });
  } finally {
    conns.forEach(c => realPool.release(c));
  }
});

// Pool stats
app.get('/pool/stats', (req, res) => res.json({ size: realPool.size, active: realPool.active, idle: realPool.idle.length, waiting: realPool.waiting.length }));

app.listen(3000, () => console.log('Pool demo :3000'));
module.exports = app;
