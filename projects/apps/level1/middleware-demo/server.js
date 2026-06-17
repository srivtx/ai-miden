// Middleware Demo — Custom middleware: timing, request counter, blocklist, transforms.
const express = require('express');
const app = express();
app.use(express.json());

// === Middleware 1: Request timing ===
function timingMiddleware(req, res, next) {
  const start = process.hrtime.bigint();
  res.on('finish', () => {
    const ms = Number(process.hrtime.bigint() - start) / 1e6;
    res.set('X-Response-Time', ms.toFixed(2) + 'ms');
    console.log(`${req.method} ${req.path} ${res.statusCode} ${ms.toFixed(2)}ms`);
  });
  next();
}

// === Middleware 2: Request counter (in-memory) ===
let requestCount = 0;
const countsByPath = {};
function counterMiddleware(req, res, next) {
  requestCount++;
  countsByPath[req.path] = (countsByPath[req.path] || 0) + 1;
  next();
}

// === Middleware 3: IP blocklist ===
const blockedIPs = new Set(['1.2.3.4', '5.6.7.8']);
function blocklistMiddleware(req, res, next) {
  const ip = req.ip || req.connection.remoteAddress;
  if (blockedIPs.has(ip)) return res.status(403).json({ error: 'blocked' });
  next();
}

// === Middleware 4: Body validation ===
function requireFields(...fields) {
  return (req, res, next) => {
    const missing = fields.filter(f => req.body[f] === undefined || req.body[f] === null || req.body[f] === '');
    if (missing.length) return res.status(422).json({ error: 'missing_fields', fields: missing });
    next();
  };
}

// === Middleware 5: Lowercase email transform ===
function normalizeEmail(req, res, next) {
  if (req.body && req.body.email) req.body.email = req.body.email.toLowerCase().trim();
  if (req.body && req.body.username) req.body.username = req.body.username.toLowerCase().trim();
  next();
}

// Apply order: timing (outermost) → blocklist → counter → route-specific validation
app.use(timingMiddleware);
app.use(blocklistMiddleware);
app.use(counterMiddleware);
app.use(normalizeEmail);

app.get('/health', (req, res) => res.json({ status: 'ok' }));

app.post('/users', requireFields('email', 'username'), (req, res) => {
  res.status(201).json({ id: 'u_' + Math.random().toString(36).slice(2, 8), email: req.body.email, username: req.body.username });
});

app.get('/admin/stats', (req, res) => res.json({ requestCount, countsByPath }));

app.listen(3000, () => console.log('Middleware demo :3000 — GET /admin/stats for counters'));
module.exports = app;
