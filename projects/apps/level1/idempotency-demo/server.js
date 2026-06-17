// Idempotency Demo — Safe retries with idempotency keys, stored in SQLite.
const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE idempotency (key TEXT PRIMARY KEY, endpoint TEXT, request_hash TEXT, response TEXT, status INTEGER, created_at INTEGER)`);
db.exec(`CREATE TABLE charges (id TEXT PRIMARY KEY, amount INTEGER, currency TEXT, created_at INTEGER)`);

// === Idempotency middleware ===
function idempotency(ttlMs = 24 * 60 * 60 * 1000) {
  return (req, res, next) => {
    const key = req.headers['idempotency-key'];
    if (!key) return next();
    const bodyHash = crypto.createHash('sha256').update(JSON.stringify(req.body)).digest('hex');
    const existing = db.prepare('SELECT * FROM idempotency WHERE key = ? AND created_at > ?').get(key, Date.now() - ttlMs);
    if (existing) {
      if (existing.request_hash !== bodyHash) {
        return res.status(409).json({ error: 'Idempotency key reused with different request body' });
      }
      res.set('Idempotent-Replay', 'true');
      return res.status(existing.status).json(JSON.parse(existing.response));
    }
    // Store request hash so we can detect conflicts
    const originalJson = res.json.bind(res);
    res.json = (body) => {
      db.prepare('INSERT OR REPLACE INTO idempotency (key, endpoint, request_hash, response, status, created_at) VALUES (?, ?, ?, ?, ?, ?)').run(key, req.path, bodyHash, JSON.stringify(body), res.statusCode, Date.now());
      return originalJson(body);
    };
    next();
  };
}

// === Demo: charge a card ===
app.post('/charge', idempotency(), (req, res) => {
  const { amount, currency, card } = req.body;
  if (!amount || !currency || !card) return res.status(400).json({ error: 'missing fields' });
  const id = 'ch_' + crypto.randomBytes(8).toString('hex');
  db.prepare('INSERT INTO charges (id, amount, currency, created_at) VALUES (?, ?, ?, ?)').run(id, amount, currency, Date.now());
  res.status(201).json({ id, status: 'succeeded', amount, currency });
});

// === Demo: create user ===
app.post('/users', idempotency(), (req, res) => {
  const { name, email } = req.body;
  if (!name || !email) return res.status(400).json({ error: 'missing fields' });
  res.status(201).json({ id: 'u_' + crypto.randomBytes(4).toString('hex'), name, email });
});

// === Inspect ===
app.get('/admin/idempotency', (req, res) => {
  res.json({ keys: db.prepare('SELECT * FROM idempotency').all() });
});
app.get('/admin/charges', (req, res) => {
  res.json({ charges: db.prepare('SELECT * FROM charges').all() });
});

app.listen(3000, () => console.log('Idempotency demo :3000'));
module.exports = app;
