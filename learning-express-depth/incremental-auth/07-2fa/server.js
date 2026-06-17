// 07-2fa: Two-factor auth with TOTP. Set up, get a secret, verify codes on login.
const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE users (id TEXT PRIMARY KEY, email TEXT, password_hash TEXT, salt TEXT, totp_secret TEXT, totp_enabled INTEGER DEFAULT 0)`);

// TOTP (RFC 6238) — 30-second window, 6 digits, HMAC-SHA1
function generateTOTP(secret, time = Date.now()) {
  const counter = Math.floor(time / 1000 / 30);
  const counterBytes = Buffer.alloc(8);
  counterBytes.writeBigInt64BE(BigInt(counter));
  const hmac = crypto.createHmac('sha1', Buffer.from(secret, 'base32')).update(counterBytes).digest();
  const offset = hmac[hmac.length - 1] & 0xf;
  const code = ((hmac[offset] & 0x7f) << 24 | (hmac[offset + 1] & 0xff) << 16 | (hmac[offset + 2] & 0xff) << 8 | (hmac[offset + 3] & 0xff)) % (10 ** 6);
  return code.toString().padStart(6, '0');
}

function verifyTOTP(secret, code) {
  // Accept current window ± 1 for clock skew
  for (const offset of [-1, 0, 1]) {
    const expected = generateTOTP(secret, Date.now() + offset * 30000);
    if (expected === code) return true;
  }
  return false;
}

const B32 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567';
function base32Encode(buf) {
  let bits = '', out = '';
  for (const b of buf) bits += b.toString(2).padStart(8, '0');
  for (let i = 0; i < bits.length; i += 5) out += B32[parseInt(bits.slice(i, i + 5).padEnd(5, '0'), 2)];
  return out;
}

// Setup 2FA: generate a secret, return provisioning info
app.post('/2fa/setup', (req, res) => {
  const { user_id } = req.body;
  if (!user_id) return res.status(422).json({ error: 'user_id required' });
  const user = db.prepare('SELECT * FROM users WHERE id = ?').get(user_id);
  if (!user) return res.status(404).json({ error: 'not found' });
  const secret = base32Encode(crypto.randomBytes(20));
  // Store temporarily (will be confirmed by /2fa/enable)
  db.prepare('UPDATE users SET totp_secret = ?, totp_enabled = 0 WHERE id = ?').run(secret, user_id);
  res.json({
    secret,
    otpauth_url: `otpauth://totp/MyApp:${user.email}?secret=${secret}&issuer=MyApp`,
    note: 'Add to Google Authenticator or any TOTP app, then verify with /2fa/enable',
  });
});

// Enable 2FA: verify user can produce a valid code
app.post('/2fa/enable', (req, res) => {
  const { user_id, code } = req.body;
  const user = db.prepare('SELECT * FROM users WHERE id = ?').get(user_id);
  if (!user || !user.totp_secret) return res.status(400).json({ error: 'setup first' });
  if (!verifyTOTP(user.totp_secret, code)) return res.status(400).json({ error: 'invalid_code' });
  db.prepare('UPDATE users SET totp_enabled = 1 WHERE id = ?').run(user_id);
  res.json({ enabled: true });
});

// Get current code (for testing — never expose in production)
app.get('/2fa/current-code', (req, res) => {
  const { secret } = req.query;
  if (!secret) return res.status(422).json({ error: 'secret required' });
  const code = generateTOTP(secret);
  res.json({ code, ms_until_next: 30000 - (Date.now() % 30000) });
});

// Disable 2FA
app.post('/2fa/disable', (req, res) => {
  const { user_id, code } = req.body;
  const user = db.prepare('SELECT * FROM users WHERE id = ?').get(user_id);
  if (!user || !user.totp_enabled) return res.status(400).json({ error: 'not enabled' });
  if (!verifyTOTP(user.totp_secret, code)) return res.status(400).json({ error: 'invalid_code' });
  db.prepare('UPDATE users SET totp_secret = NULL, totp_enabled = 0 WHERE id = ?').run(user_id);
  res.json({ disabled: true });
});

app.listen(3000, () => console.log('07-2fa on :3000'));
