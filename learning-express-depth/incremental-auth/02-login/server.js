// 02-login: Verify password, return user info. Same error for invalid email and password.
const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE users (id TEXT PRIMARY KEY, email TEXT UNIQUE, password_hash TEXT, salt TEXT, failed_attempts INTEGER DEFAULT 0, locked_until TEXT)`);

function hashPassword(password, salt) {
  salt = salt || crypto.randomBytes(16).toString('hex');
  return { hash: crypto.pbkdf2Sync(password, salt, 100000, 64, 'sha512').toString('hex'), salt };
}

function verifyPassword(password, hash, salt) {
  const test = crypto.pbkdf2Sync(password, salt, 100000, 64, 'sha512').toString('hex');
  return test.length === hash.length && crypto.timingSafeEqual(Buffer.from(test, 'hex'), Buffer.from(hash, 'hex'));
}

// Track failed login attempts
const MAX_ATTEMPTS = 5;
const LOCK_DURATION_MS = 15 * 60 * 1000;  // 15 minutes

// Signup (same as before)
app.post('/auth/signup', (req, res) => {
  const { email, password } = req.body;
  if (!email || !password || password.length < 8) return res.status(422).json({ error: 'invalid input' });
  const id = 'u_' + crypto.randomBytes(8).toString('hex');
  const { hash, salt } = hashPassword(password);
  try {
    db.prepare('INSERT INTO users (id, email, password_hash, salt) VALUES (?, ?, ?, ?)').run(id, email, hash, salt);
    res.status(201).json({ id, email });
  } catch { res.status(409).json({ error: 'email_taken' }); }
});

// Login: always return the same error to prevent email enumeration
app.post('/auth/login', (req, res) => {
  const { email, password } = req.body;
  if (!email || !password) return res.status(400).json({ error: 'invalid_request' });

  const user = db.prepare('SELECT * FROM users WHERE email = ?').get(email);

  // Check if locked
  if (user && user.locked_until && new Date(user.locked_until) > new Date()) {
    return res.status(423).json({ error: 'account_locked', locked_until: user.locked_until });
  }

  // Always run verify (even for missing user) to prevent timing attacks
  let valid = false;
  if (user) {
    valid = verifyPassword(password, user.password_hash, user.salt);
  } else {
    // Dummy verify to take similar time
    crypto.pbkdf2Sync(password, '0'.repeat(32), 100000, 64, 'sha512');
  }

  if (!user || !valid) {
    // Track failed attempts
    if (user) {
      const attempts = user.failed_attempts + 1;
      const lockedUntil = attempts >= MAX_ATTEMPTS ? new Date(Date.now() + LOCK_DURATION_MS).toISOString() : null;
      db.prepare('UPDATE users SET failed_attempts = ?, locked_until = ? WHERE id = ?').run(attempts, lockedUntil, user.id);
    }
    return res.status(401).json({ error: 'invalid_credentials' });
  }

  // Success: reset failed attempts
  db.prepare('UPDATE users SET failed_attempts = 0, locked_until = NULL WHERE id = ?').run(user.id);
  res.json({ id: user.id, email: user.email });
});

app.listen(3000, () => console.log('02-login on :3000'));
