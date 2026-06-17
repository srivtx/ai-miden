// 44 — Rate Limiter
// NEW CONCEPT: limit how many requests each client can make.
// Token bucket: each client has a bucket of tokens. Each request takes one.
const express = require('express');
const app = express();

// Token bucket for each client (keyed by IP)
const buckets = new Map();
const CAPACITY = 10;       // max tokens
const REFILL_RATE = 1;     // tokens per second

function getBucket(ip) {
  if (!buckets.has(ip)) {
    buckets.set(ip, { tokens: CAPACITY, lastRefill: Date.now() });
  }
  return buckets.get(ip);
}

function refill(bucket) {
  const now = Date.now();
  const elapsed = (now - bucket.lastRefill) / 1000;
  bucket.tokens = Math.min(CAPACITY, bucket.tokens + elapsed * REFILL_RATE);
  bucket.lastRefill = now;
}

// Middleware: rate limit by IP
function rateLimit(req, res, next) {
  const ip = req.ip;
  const bucket = getBucket(ip);
  refill(bucket);

  if (bucket.tokens < 1) {
    res.set('Retry-After', '1');
    return res.status(429).json({ error: 'Too many requests' });
  }

  bucket.tokens -= 1;
  res.set('X-RateLimit-Limit', CAPACITY);
  res.set('X-RateLimit-Remaining', Math.floor(bucket.tokens));
  next();
}

app.use(rateLimit);

app.get('/api/data', (req, res) => res.json({ data: 'some data' }));
app.get('/health', (req, res) => res.json({ status: 'ok' }));

// Admin: see all buckets
app.get('/admin/buckets', (req, res) => {
  const out = {};
  for (const [ip, b] of buckets) {
    out[ip] = { tokens: Math.floor(b.tokens), lastRefill: b.lastRefill };
  }
  res.json(out);
});

app.listen(3000, () => console.log('Rate limiter on http://localhost:3000'));
