// 09-api-keys: Programmatic access. Long-lived keys for scripts, integrations, and CI.
const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE users (id TEXT PRIMARY KEY, email TEXT)`);
db.exec(`CREATE TABLE api_keys (id TEXT PRIMARY KEY, user_id TEXT, name TEXT, key_hash TEXT, key_prefix TEXT, scopes TEXT, last_used_at TEXT, expires_at TEXT, created_at TEXT DEFAULT (datetime('now')))`);

// Format: ak_<prefix>_<secret>  (the prefix is shown in listings, the secret is hashed)
// Example: ak_abc12345_xyz...
function generateApiKey() {
  const prefix = crypto.randomBytes(4).toString('hex');
  const secret = crypto.randomBytes(24).toString('base64url');
  return { full: `ak_${prefix}_${secret}`, prefix, secret };
}

function hashKey(secret) {
  return crypto.createHash('sha256').update(secret).digest('hex');
}

// Create a key (returns the FULL key — only chance to see it)
app.post('/api-keys', (req, res) => {
  const { user_id, name, scopes, expires_in_days } = req.body;
  if (!user_id || !name) return res.status(422).json({ error: 'user_id and name required' });

  const { full, prefix, secret } = generateApiKey();
  const id = 'k_' + crypto.randomBytes(4).toString('hex');
  const expires = expires_in_days ? new Date(Date.now() + expires_in_days * 86400000).toISOString() : null;

  db.prepare('INSERT INTO api_keys (id, user_id, name, key_hash, key_prefix, scopes, expires_at) VALUES (?, ?, ?, ?, ?, ?, ?)').run(id, user_id, name, hashKey(secret), prefix, JSON.stringify(scopes || ['*']), expires);

  res.status(201).json({
    id,
    name,
    key: full,  // ONLY shown once
    prefix,
    scopes: scopes || ['*'],
    expires_at: expires,
    note: 'Save this key. You will not be able to see it again.',
  });
});

// List keys (only the prefix, not the secret)
app.get('/api-keys', (req, res) => {
  const userId = req.query.user_id;
  if (!userId) return res.status(422).json({ error: 'user_id required' });
  const keys = db.prepare('SELECT id, name, key_prefix, scopes, last_used_at, expires_at, created_at FROM api_keys WHERE user_id = ?').all(userId);
  res.json({ keys });
});

// Revoke a key
app.delete('/api-keys/:id', (req, res) => {
  const userId = req.query.user_id;
  if (!userId) return res.status(422).json({ error: 'user_id required' });
  const r = db.prepare('DELETE FROM api_keys WHERE id = ? AND user_id = ?').run(req.params.id, userId);
  r.changes ? res.status(204).end() : res.status(404).json({ error: 'not found' });
});

// Middleware: verify the key
function apiKeyAuth(req, res, next) {
  const auth = req.headers.authorization;
  if (!auth || !auth.startsWith('Bearer ak_')) {
    return res.status(401).json({ error: 'invalid_api_key_format' });
  }
  const key = auth.slice(7);
  const parts = key.split('_');
  if (parts.length !== 3) return res.status(401).json({ error: 'invalid_api_key_format' });
  const prefix = parts[1];
  const secret = parts[2];
  const keyHash = hashKey(secret);
  const row = db.prepare('SELECT * FROM api_keys WHERE key_hash = ? AND key_prefix = ?').get(keyHash, prefix);
  if (!row) return res.status(401).json({ error: 'invalid_api_key' });
  if (row.expires_at && new Date(row.expires_at) < new Date()) return res.status(401).json({ error: 'expired' });
  // Update last_used_at
  db.prepare("UPDATE api_keys SET last_used_at = datetime('now') WHERE id = ?").run(row.id);
  req.apiKey = row;
  next();
}

// Protected endpoint using API key
app.get('/api/data', apiKeyAuth, (req, res) => {
  res.json({ data: 'some data', key_id: req.apiKey.id, key_name: req.apiKey.name });
});

app.listen(3000, () => console.log('09-api-keys on :3000 (use Bearer ak_<prefix>_<secret>)'));
