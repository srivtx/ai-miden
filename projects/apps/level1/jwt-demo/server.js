// JWT Demo — Issue, sign, verify, decode, refresh. No external deps (uses crypto for HMAC).
const express = require('express');
const crypto = require('crypto');
const app = express();
app.use(express.json());

const SECRET = process.env.JWT_SECRET || 'demo-secret-do-not-use-in-prod';
const ALG = 'HS256';

// === Base64URL encoding ===
function b64url(input) {
  return Buffer.from(input).toString('base64').replace(/=+$/, '').replace(/\+/g, '-').replace(/\//g, '_');
}

// === Sign ===
function sign(payload, expiresInSec = 3600) {
  const header = b64url(JSON.stringify({ alg: ALG, typ: 'JWT' }));
  const now = Math.floor(Date.now() / 1000);
  const body = b64url(JSON.stringify({ ...payload, iat: now, exp: now + expiresInSec }));
  const data = `${header}.${body}`;
  const sig = b64url(crypto.createHmac('sha256', SECRET).update(data).digest());
  return `${data}.${sig}`;
}

// === Verify ===
function verify(token) {
  if (!token || typeof token !== 'string') return { valid: false, reason: 'no_token' };
  const parts = token.split('.');
  if (parts.length !== 3) return { valid: false, reason: 'malformed' };
  const [header, body, sig] = parts;
  const expected = b64url(crypto.createHmac('sha256', SECRET).update(`${header}.${body}`).digest());
  if (sig !== expected) return { valid: false, reason: 'bad_signature' };
  const payload = JSON.parse(Buffer.from(body.replace(/-/g, '+').replace(/_/g, '/'), 'base64').toString());
  if (payload.exp && payload.exp < Math.floor(Date.now() / 1000)) return { valid: false, reason: 'expired', payload };
  return { valid: true, payload };
}

// === Decode (without verification — for inspection only) ===
function decode(token) {
  if (!token) return null;
  const [, body] = token.split('.');
  return JSON.parse(Buffer.from(body.replace(/-/g, '+').replace(/_/g, '/'), 'base64').toString());
}

// === Middleware ===
function requireAuth(req, res, next) {
  const auth = req.headers.authorization || '';
  const token = auth.replace(/^Bearer\s+/i, '');
  const result = verify(token);
  if (!result.valid) return res.status(401).json({ error: 'unauthorized', reason: result.reason });
  req.user = result.payload;
  next();
}

function requireRole(...roles) {
  return (req, res, next) => {
    if (!req.user || !roles.includes(req.user.role)) return res.status(403).json({ error: 'forbidden', requiredRoles: roles });
    next();
  };
}

// === Routes ===
app.post('/login', (req, res) => {
  const { email, password } = req.body;
  if (!email || !password) return res.status(422).json({ error: 'missing_fields' });
  // Fake user lookup
  const user = { id: 42, email, role: email.includes('admin') ? 'admin' : 'user' };
  const accessToken = sign({ sub: user.id, email: user.email, role: user.role }, 3600);
  const refreshToken = sign({ sub: user.id, type: 'refresh' }, 86400 * 7);
  res.json({ accessToken, refreshToken, user });
});

app.post('/refresh', (req, res) => {
  const { refreshToken } = req.body;
  const result = verify(refreshToken);
  if (!result.valid || result.payload.type !== 'refresh') return res.status(401).json({ error: 'invalid_refresh' });
  const accessToken = sign({ sub: result.payload.sub }, 3600);
  res.json({ accessToken });
});

app.get('/me', requireAuth, (req, res) => res.json({ user: req.user }));
app.get('/admin', requireAuth, requireRole('admin'), (req, res) => res.json({ message: 'admin only', user: req.user }));

// === Inspect (decode without verify) ===
app.get('/inspect', (req, res) => res.json({ token: req.query.t, decoded: decode(req.query.t) }));

app.listen(3000, () => console.log('JWT demo :3000'));
module.exports = app;
