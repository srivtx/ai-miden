// 05-reset-password: Forgot password. Request a reset, get a token by email, set a new password.
const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE users (id TEXT PRIMARY KEY, email TEXT UNIQUE, password_hash TEXT, salt TEXT)`);
db.exec(`CREATE TABLE password_resets (token TEXT PRIMARY KEY, user_id TEXT, expires_at TEXT, used INTEGER DEFAULT 0)`);

const RESET_TTL_MS = 60 * 60 * 1000;  // 1 hour

function hashPassword(password, salt) {
  salt = salt || crypto.randomBytes(16).toString('hex');
  return { hash: crypto.pbkdf2Sync(password, salt, 100000, 64, 'sha512').toString('hex'), salt };
}
function verifyPassword(password, hash, salt) {
  const test = crypto.pbkdf2Sync(password, salt, 100000, 64, 'sha512').toString('hex');
  return test.length === hash.length && crypto.timingSafeEqual(Buffer.from(test, 'hex'), Buffer.from(hash, 'hex'));
}

// Request a reset (always returns the same response, even for unknown emails)
app.post('/auth/forgot-password', (req, res) => {
  const { email } = req.body;
  if (!email) return res.status(422).json({ error: 'email required' });
  const user = db.prepare('SELECT * FROM users WHERE email = ?').get(email);

  // Always return success to prevent email enumeration
  if (!user) return res.json({ message: 'If the email exists, a reset link has been sent.' });

  // Generate a token
  const token = crypto.randomBytes(32).toString('hex');
  const expiresAt = new Date(Date.now() + RESET_TTL_MS).toISOString();
  db.prepare('INSERT INTO password_resets (token, user_id, expires_at) VALUES (?, ?, ?)').run(token, user.id, expiresAt);

  // In real apps: send an email with the link
  console.log(`[email] To ${email}: /auth/reset-password?token=${token}`);
  res.json({
    message: 'If the email exists, a reset link has been sent.',
    // In production, don't return the token. For demo, we do.
    dev_token: token,
    dev_link: `/auth/reset-password?token=${token}`,
  });
});

// Verify the token (user clicks the link)
app.get('/auth/reset-password', (req, res) => {
  const { token } = req.query;
  if (!token) return res.status(422).json({ error: 'token required' });
  const row = db.prepare('SELECT * FROM password_resets WHERE token = ?').get(token);
  if (!row) return res.status(400).json({ error: 'invalid_token' });
  if (row.used) return res.status(400).json({ error: 'token_used' });
  if (new Date(row.expires_at) < new Date()) return res.status(400).json({ error: 'token_expired' });
  res.json({ valid: true, user_id: row.user_id });
});

// Set new password
app.post('/auth/reset-password', (req, res) => {
  const { token, new_password } = req.body;
  if (!token || !new_password) return res.status(422).json({ error: 'token and new_password required' });
  if (new_password.length < 8) return res.status(422).json({ error: 'weak_password' });

  const row = db.prepare('SELECT * FROM password_resets WHERE token = ?').get(token);
  if (!row || row.used || new Date(row.expires_at) < new Date()) {
    return res.status(400).json({ error: 'invalid_token' });
  }

  // Update password
  const { hash, salt } = hashPassword(new_password);
  db.prepare('UPDATE users SET password_hash = ?, salt = ? WHERE id = ?').run(hash, salt, row.user_id);
  // Mark token as used
  db.prepare('UPDATE password_resets SET used = 1 WHERE token = ?').run(token);
  // Invalidate all OTHER reset tokens for this user
  db.prepare("UPDATE password_resets SET used = 1 WHERE user_id = ? AND token != ?").run(row.user_id, token);

  res.json({ message: 'Password reset successful' });
});

app.listen(3000, () => console.log('05-reset-password on :3000'));
