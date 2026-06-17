// 2FA Demo — TOTP-style time-based codes (HMAC-SHA1, 30s window, 6 digits).
const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE users (id TEXT PRIMARY KEY, email TEXT UNIQUE, password_hash TEXT, salt TEXT, totp_secret TEXT, totp_enabled INTEGER DEFAULT 0)`);
db.exec(`CREATE TABLE used_codes (code TEXT, user_id TEXT, used_at INTEGER, PRIMARY KEY (user_id, code))`);

// === TOTP (RFC 6238) — 30-second window, 6 digits, HMAC-SHA1 ===
function generateTOTP(secret, time = Date.now(), window = 30, digits = 6) {
  const counter = Math.floor(time / 1000 / window);
  const counterBytes = Buffer.alloc(8);
  counterBytes.writeBigInt64BE(BigInt(counter));
  const hmac = crypto.createHmac('sha1', Buffer.from(secret, 'base32')).update(counterBytes).digest();
  const offset = hmac[hmac.length - 1] & 0xf;
  const code = ((hmac[offset] & 0x7f) << 24 | (hmac[offset + 1] & 0xff) << 16 | (hmac[offset + 2] & 0xff) << 8 | (hmac[offset + 3] & 0xff)) % (10 ** digits);
  return code.toString().padStart(digits, '0');
}

// === Base32 encode/decode for secrets ===
const B32 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567';
function base32Encode(buf) {
  let bits = '', out = '';
  for (const b of buf) bits += b.toString(2).padStart(8, '0');
  for (let i = 0; i < bits.length; i += 5) out += B32[parseInt(bits.slice(i, i + 5).padEnd(5, '0'), 2)];
  return out;
}

// === Seed user ===
const { hash, salt } = (() => { const salt = crypto.randomBytes(16).toString('hex'); return { hash: crypto.pbkdf2Sync('password-123', salt, 100000, 64, 'sha512').toString('hex'), salt }; })();
db.prepare('INSERT INTO users (id, email, password_hash, salt) VALUES (?, ?, ?, ?)').run('u_alice', 'alice@example.com', hash, salt);

// === 1. Setup 2FA — generate secret, return provisioning info ===
app.post('/2fa/setup', (req, res) => {
  const { userId } = req.body;
  const user = db.prepare('SELECT * FROM users WHERE id = ?').get(userId);
  if (!user) return res.status(404).json({ error: 'user_not_found' });
  const secretBytes = crypto.randomBytes(20);
  const secret = base32Encode(secretBytes);
  // For demo: don't enable yet — user must verify first
  res.json({ secret, otpauth_url: `otpauth://totp/MyApp:alice@example.com?secret=${secret}&issuer=MyApp`, note: 'Use Google Authenticator or any TOTP app with this secret' });
});

// === 2. Enable 2FA — verify user can produce a valid code ===
app.post('/2fa/enable', (req, res) => {
  const { userId, secret, code } = req.body;
  if (!verifyCode(secret, code)) return res.status(400).json({ error: 'invalid_code' });
  db.prepare('UPDATE users SET totp_secret = ?, totp_enabled = 1 WHERE id = ?').run(secret, userId);
  res.json({ enabled: true });
});

// === 3. Login with 2FA ===
app.post('/login', (req, res) => {
  const { email, password, code } = req.body;
  const user = db.prepare('SELECT * FROM users WHERE email = ?').get(email);
  if (!user) return res.status(401).json({ error: 'invalid_credentials' });
  const test = crypto.pbkdf2Sync(password, user.salt, 100000, 64, 'sha512').toString('hex');
  if (test.length !== user.password_hash.length || !crypto.timingSafeEqual(Buffer.from(test, 'hex'), Buffer.from(user.password_hash, 'hex'))) return res.status(401).json({ error: 'invalid_credentials' });
  if (user.totp_enabled) {
    if (!code) return res.status(401).json({ error: '2fa_required', hint: 'POST with code from authenticator app' });
    if (!verifyCode(user.totp_secret, code)) return res.status(401).json({ error: 'invalid_2fa_code' });
    // Prevent replay
    try { db.prepare('INSERT INTO used_codes (code, user_id, used_at) VALUES (?, ?, ?)').run(code, user.id, Date.now()); }
    catch { return res.status(401).json({ error: 'code_already_used' }); }
  }
  res.json({ message: 'logged in', user: { id: user.id, email: user.email, totpEnabled: !!user.totp_enabled } });
});

// === Verify code (current window ± 1 for clock skew) ===
function verifyCode(secret, code) {
  for (const offset of [-1, 0, 1]) {
    const expected = generateTOTP(secret, Date.now() + offset * 30000);
    if (expected === code) return true;
  }
  return false;
}

// === Generate current code (for testing) ===
app.get('/2fa/current-code', (req, res) => {
  if (!req.query.secret) return res.status(422).json({ error: 'missing_secret' });
  const now = Math.floor(Date.now() / 30000) * 30000;
  res.json({ code: generateTOTP(req.query.secret, now), windowEnd: now + 30000, msLeft: 30000 - (Date.now() - now) });
});

app.listen(3000, () => console.log('2FA demo :3000 — see README for full flow'));
module.exports = app;
