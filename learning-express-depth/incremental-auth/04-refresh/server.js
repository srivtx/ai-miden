// 04-refresh: Short-lived access tokens (1h) + long-lived refresh tokens (7d). Refresh rotates both.
const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const jwt = require('jsonwebtoken');
const app = express();
app.use(express.json());

const SECRET = 'dev-secret';
const db = new Database(':memory:');
db.exec(`CREATE TABLE users (id TEXT PRIMARY KEY, email TEXT UNIQUE, password_hash TEXT, salt TEXT)`);
db.exec(`CREATE TABLE refresh_tokens (token TEXT PRIMARY KEY, user_id TEXT, expires_at TEXT, revoked INTEGER DEFAULT 0)`);

function hashPassword(password, salt) {
  salt = salt || crypto.randomBytes(16).toString('hex');
  return { hash: crypto.pbkdf2Sync(password, salt, 100000, 64, 'sha512').toString('hex'), salt };
}
function verifyPassword(password, hash, salt) {
  const test = crypto.pbkdf2Sync(password, salt, 100000, 64, 'sha512').toString('hex');
  return test.length === hash.length && crypto.timingSafeEqual(Buffer.from(test, 'hex'), Buffer.from(hash, 'hex'));
}
function signAccess(user) {
  return jwt.sign({ sub: user.id, email: user.email, type: 'access' }, SECRET, { expiresIn: '1h' });
}
function signRefresh(user) {
  const token = crypto.randomBytes(32).toString('hex');
  const expires = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString();
  db.prepare('INSERT INTO refresh_tokens (token, user_id, expires_at) VALUES (?, ?, ?)').run(token, user.id, expires);
  return { token, expires_in: 7 * 24 * 60 * 60 };
}

app.post('/auth/signup', (req, res) => {
  const { email, password } = req.body;
  if (!email || !password || password.length < 8) return res.status(422).json({ error: 'invalid_input' });
  const id = 'u_' + crypto.randomBytes(8).toString('hex');
  const { hash, salt } = hashPassword(password);
  try {
    db.prepare('INSERT INTO users (id, email, password_hash, salt) VALUES (?, ?, ?, ?)').run(id, email, hash, salt);
    res.status(201).json({ id, email });
  } catch { res.status(409).json({ error: 'email_taken' }); }
});

app.post('/auth/login', (req, res) => {
  const { email, password } = req.body;
  const user = db.prepare('SELECT * FROM users WHERE email = ?').get(email);
  if (!user || !verifyPassword(password, user.password_hash, user.salt)) {
    return res.status(401).json({ error: 'invalid_credentials' });
  }
  res.json({
    access_token: signAccess(user),
    refresh_token: signRefresh(user).token,
    expires_in: 3600,
  });
});

// Refresh: rotate the refresh token
app.post('/auth/refresh', (req, res) => {
  const { refresh_token } = req.body;
  if (!refresh_token) return res.status(422).json({ error: 'refresh_token required' });
  const row = db.prepare('SELECT * FROM refresh_tokens WHERE token = ?').get(refresh_token);
  if (!row) return res.status(401).json({ error: 'invalid_refresh' });
  if (row.revoked) return res.status(401).json({ error: 'revoked' });
  if (new Date(row.expires_at) < new Date()) return res.status(401).json({ error: 'expired' });
  // Rotate: revoke old, issue new
  db.prepare('UPDATE refresh_tokens SET revoked = 1 WHERE token = ?').run(refresh_token);
  const user = db.prepare('SELECT * FROM users WHERE id = ?').get(row.user_id);
  res.json({
    access_token: signAccess(user),
    refresh_token: signRefresh(user).token,
  });
});

// Logout: revoke the refresh token
app.post('/auth/logout', (req, res) => {
  const { refresh_token } = req.body;
  if (refresh_token) db.prepare('UPDATE refresh_tokens SET revoked = 1 WHERE token = ?').run(refresh_token);
  res.json({ logged_out: true });
});

function auth(req, res, next) {
  const auth = req.headers.authorization;
  if (!auth || !auth.startsWith('Bearer ')) return res.status(401).json({ error: 'missing_token' });
  try {
    req.user = jwt.verify(auth.slice(7), SECRET);
    if (req.user.type !== 'access') return res.status(401).json({ error: 'wrong_token_type' });
    next();
  } catch { res.status(401).json({ error: 'invalid_token' }); }
}

app.get('/me', auth, (req, res) => res.json({ user: req.user }));

app.listen(3000, () => console.log('04-refresh on :3000'));
