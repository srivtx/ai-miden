// Password Reset Demo — Request, email link, verify token, set new password.
const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE users (id TEXT PRIMARY KEY, email TEXT UNIQUE, password_hash TEXT, salt TEXT)`);
db.exec(`CREATE TABLE reset_tokens (token TEXT PRIMARY KEY, user_id TEXT, expires_at INTEGER, used INTEGER DEFAULT 0)`);

const TOKEN_TTL_MS = 60 * 60 * 1000; // 1 hour
const BASE_URL = process.env.BASE_URL || 'http://localhost:3000';

function hashPassword(password, salt) {
  salt = salt || crypto.randomBytes(16).toString('hex');
  const hash = crypto.pbkdf2Sync(password, salt, 100000, 64, 'sha512').toString('hex');
  return { hash, salt };
}

function verifyPassword(password, hash, salt) {
  const test = crypto.pbkdf2Sync(password, salt, 100000, 64, 'sha512').toString('hex');
  return test.length === hash.length && crypto.timingSafeEqual(Buffer.from(test, 'hex'), Buffer.from(hash, 'hex'));
}

// Seed
const { hash, salt } = hashPassword('original-password-123');
db.prepare('INSERT INTO users (id, email, password_hash, salt) VALUES (?, ?, ?, ?)').run('u_alice', 'alice@example.com', hash, salt);

// === Request reset (returns the link in dev) ===
app.post('/auth/forgot-password', (req, res) => {
  const { email } = req.body;
  if (!email) return res.status(422).json({ error: 'missing_email' });
  const user = db.prepare('SELECT * FROM users WHERE email = ?').get(email);
  // Always return success to prevent email enumeration
  if (!user) return res.json({ message: 'If the email exists, a reset link has been sent.' });
  const token = crypto.randomBytes(32).toString('hex');
  db.prepare('INSERT INTO reset_tokens (token, user_id, expires_at) VALUES (?, ?, ?)').run(token, user.id, Date.now() + TOKEN_TTL_MS);
  const resetLink = `${BASE_URL}/auth/reset-password?token=${token}`;
  console.log(`[email] To ${email}: ${resetLink}`);
  res.json({ message: 'If the email exists, a reset link has been sent.', dev_only: { resetLink, token } });
});

// === Verify token (the user clicks the link) ===
app.get('/auth/reset-password', (req, res) => {
  const { token } = req.query;
  if (!token) return res.status(422).json({ error: 'missing_token' });
  const row = db.prepare('SELECT * FROM reset_tokens WHERE token = ?').get(token);
  if (!row) return res.status(400).json({ error: 'invalid_token' });
  if (row.used) return res.status(400).json({ error: 'token_used' });
  if (row.expires_at < Date.now()) return res.status(400).json({ error: 'token_expired' });
  res.json({ valid: true, userId: row.user_id });
});

// === Set new password ===
app.post('/auth/reset-password', (req, res) => {
  const { token, newPassword } = req.body;
  if (!token || !newPassword) return res.status(422).json({ error: 'missing_fields' });
  if (newPassword.length < 8) return res.status(422).json({ error: 'weak_password' });
  const row = db.prepare('SELECT * FROM reset_tokens WHERE token = ?').get(token);
  if (!row || row.used || row.expires_at < Date.now()) return res.status(400).json({ error: 'invalid_token' });
  const { hash, salt } = hashPassword(newPassword);
  db.prepare('UPDATE users SET password_hash = ?, salt = ? WHERE id = ?').run(hash, salt, row.user_id);
  db.prepare('UPDATE reset_tokens SET used = 1 WHERE token = ?').run(token);
  // Invalidate all other tokens for this user
  db.prepare('UPDATE reset_tokens SET used = 1 WHERE user_id = ? AND token != ?').run(row.user_id, token);
  res.json({ message: 'Password reset successful' });
});

// === Login (to verify reset worked) ===
app.post('/auth/login', (req, res) => {
  const { email, password } = req.body;
  const user = db.prepare('SELECT * FROM users WHERE email = ?').get(email);
  if (!user || !verifyPassword(password, user.password_hash, user.salt)) return res.status(401).json({ error: 'invalid_credentials' });
  res.json({ message: 'logged in', user: { id: user.id, email: user.email } });
});

app.listen(3000, () => console.log('Password reset demo :3000'));
module.exports = app;
