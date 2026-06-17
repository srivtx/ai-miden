// 01-signup: Create a user. Email, password (hashed), basic validation.
const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE users (id TEXT PRIMARY KEY, email TEXT UNIQUE, password_hash TEXT, salt TEXT, created_at TEXT DEFAULT (datetime('now')))`);

function hashPassword(password, salt) {
  salt = salt || crypto.randomBytes(16).toString('hex');
  const hash = crypto.pbkdf2Sync(password, salt, 100000, 64, 'sha512').toString('hex');
  return { hash, salt };
}

function validateEmail(email) {
  return typeof email === 'string' && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function validatePassword(password) {
  const errors = [];
  if (typeof password !== 'string') errors.push('password must be a string');
  if (password && password.length < 8) errors.push('password must be at least 8 characters');
  if (password && password.length > 128) errors.push('password must be at most 128 characters');
  if (password && !/[A-Z]/.test(password)) errors.push('password must contain an uppercase letter');
  if (password && !/[a-z]/.test(password)) errors.push('password must contain a lowercase letter');
  if (password && !/[0-9]/.test(password)) errors.push('password must contain a digit');
  return errors;
}

app.post('/auth/signup', (req, res) => {
  const { email, password } = req.body;

  // Validate email
  if (!validateEmail(email)) {
    return res.status(422).json({ error: 'invalid_email', message: 'must be a valid email' });
  }

  // Validate password
  const pwErrors = validatePassword(password);
  if (pwErrors.length) {
    return res.status(422).json({ error: 'weak_password', errors: pwErrors });
  }

  // Check for existing
  if (db.prepare('SELECT id FROM users WHERE email = ?').get(email)) {
    return res.status(409).json({ error: 'email_taken' });
  }

  // Create user
  const id = 'u_' + crypto.randomBytes(8).toString('hex');
  const { hash, salt } = hashPassword(password);
  db.prepare('INSERT INTO users (id, email, password_hash, salt) VALUES (?, ?, ?, ?)').run(id, email, hash, salt);

  res.status(201).json({ id, email, created_at: new Date().toISOString() });
});

app.listen(3000, () => console.log('01-signup on :3000'));
