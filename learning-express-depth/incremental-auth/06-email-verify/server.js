// 06-email-verify: After signup, the email is unverified. Send a verification link.
const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE users (id TEXT PRIMARY KEY, email TEXT UNIQUE, password_hash TEXT, salt TEXT, email_verified INTEGER DEFAULT 0, verify_token TEXT, verify_expires_at TEXT)`);

function hashPassword(password, salt) {
  salt = salt || crypto.randomBytes(16).toString('hex');
  return { hash: crypto.pbkdf2Sync(password, salt, 100000, 64, 'sha512').toString('hex'), salt };
}

app.post('/auth/signup', (req, res) => {
  const { email, password } = req.body;
  if (!email || !password || password.length < 8) return res.status(422).json({ error: 'invalid_input' });
  const id = 'u_' + crypto.randomBytes(8).toString('hex');
  const { hash, salt } = hashPassword(password);
  const token = crypto.randomBytes(32).toString('hex');
  const expires = new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString();
  try {
    db.prepare('INSERT INTO users (id, email, password_hash, salt, verify_token, verify_expires_at) VALUES (?, ?, ?, ?, ?, ?)').run(id, email, hash, salt, token, expires);
    console.log(`[email] Verify link: /auth/verify-email?token=${token}`);
    res.status(201).json({ id, email, verified: false, dev_verify_url: `/auth/verify-email?token=${token}` });
  } catch { res.status(409).json({ error: 'email_taken' }); }
});

// Click the verification link
app.get('/auth/verify-email', (req, res) => {
  const { token } = req.query;
  if (!token) return res.status(422).json({ error: 'token required' });
  const user = db.prepare('SELECT * FROM users WHERE verify_token = ?').get(token);
  if (!user) return res.status(400).json({ error: 'invalid_token' });
  if (new Date(user.verify_expires_at) < new Date()) return res.status(400).json({ error: 'token_expired' });
  db.prepare('UPDATE users SET email_verified = 1, verify_token = NULL, verify_expires_at = NULL WHERE id = ?').run(user.id);
  res.json({ verified: true });
});

// Resend verification
app.post('/auth/resend-verification', (req, res) => {
  const { email } = req.body;
  const user = db.prepare('SELECT * FROM users WHERE email = ?').get(email);
  if (!user) return res.json({ message: 'If the email exists, a new link has been sent.' });
  if (user.email_verified) return res.json({ message: 'Already verified' });
  const token = crypto.randomBytes(32).toString('hex');
  const expires = new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString();
  db.prepare('UPDATE users SET verify_token = ?, verify_expires_at = ? WHERE id = ?').run(token, expires, user.id);
  console.log(`[email] New verify link for ${email}: /auth/verify-email?token=${token}`);
  res.json({ message: 'Verification email sent' });
});

// Check verification status
app.get('/auth/verification-status', (req, res) => {
  const { email } = req.query;
  const user = db.prepare('SELECT email_verified FROM users WHERE email = ?').get(email);
  if (!user) return res.status(404).json({ error: 'not found' });
  res.json({ email, verified: !!user.email_verified });
});

app.listen(3000, () => console.log('06-email-verify on :3000'));
