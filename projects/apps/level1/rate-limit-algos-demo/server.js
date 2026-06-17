// Rate Limiting Algorithms Demo — Compare fixed window, sliding window, token bucket.
const express = require('express');
const app = express();
app.use(express.json());

// === Three algorithms ===

// 1. Fixed window: count requests in current minute, reset at minute boundary
class FixedWindow {
  constructor(limit, windowMs) { this.limit = limit; this.windowMs = windowMs; this.counters = new Map(); }
  check(key) {
    const now = Date.now();
    const windowStart = Math.floor(now / this.windowMs) * this.windowMs;
    const k = `${key}:${windowStart}`;
    const count = (this.counters.get(k) || 0) + 1;
    this.counters.set(k, count);
    if (count > this.limit) return { allowed: false, count, limit: this.limit, retryAfter: Math.ceil((windowStart + this.windowMs - now) / 1000) };
    return { allowed: true, count, limit: this.limit, remaining: this.limit - count };
  }
}

// 2. Sliding window: track timestamps of recent requests, drop old ones
class SlidingWindow {
  constructor(limit, windowMs) { this.limit = limit; this.windowMs = windowMs; this.requests = new Map(); }
  check(key) {
    const now = Date.now();
    const cutoff = now - this.windowMs;
    const list = (this.requests.get(key) || []).filter(t => t > cutoff);
    if (list.length >= this.limit) {
      this.requests.set(key, list);
      return { allowed: false, count: list.length, limit: this.limit, retryAfter: Math.ceil((list[0] + this.windowMs - now) / 1000) };
    }
    list.push(now);
    this.requests.set(key, list);
    return { allowed: true, count: list.length, limit: this.limit, remaining: this.limit - list.length };
  }
}

// 3. Token bucket: refill tokens at a rate, consume one per request
class TokenBucket {
  constructor(capacity, refillPerSec) { this.capacity = capacity; this.refillPerSec = refillPerSec; this.buckets = new Map(); }
  check(key) {
    const now = Date.now();
    let b = this.buckets.get(key);
    if (!b) { b = { tokens: this.capacity, lastRefill: now }; this.buckets.set(key, b); }
    const elapsed = (now - b.lastRefill) / 1000;
    b.tokens = Math.min(this.capacity, b.tokens + elapsed * this.refillPerSec);
    b.lastRefill = now;
    if (b.tokens < 1) return { allowed: false, tokens: b.tokens, capacity: this.capacity, retryAfter: Math.ceil((1 - b.tokens) / this.refillPerSec) };
    b.tokens -= 1;
    return { allowed: true, tokens: Math.floor(b.tokens), capacity: this.capacity };
  }
}

const limiters = { fixed: new FixedWindow(10, 60000), sliding: new SlidingWindow(10, 60000), token: new TokenBucket(10, 10 / 60) };

// === Endpoints ===
app.get('/test/:algo', (req, res) => {
  const algo = limiters[req.params.algo];
  if (!algo) return res.status(404).json({ error: 'unknown_algo', available: Object.keys(limiters) });
  const key = req.ip || 'anon';
  const result = algo.check(key);
  res.set('X-RateLimit-Limit', result.limit || result.capacity);
  res.set('X-RateLimit-Remaining', result.remaining !== undefined ? result.remaining : Math.floor(result.tokens));
  if (result.retryAfter) res.set('Retry-After', result.retryAfter);
  res.status(result.allowed ? 200 : 429).json(result);
});

// === Compare: hit all three 15 times rapidly ===
app.get('/burst', (req, res) => {
  const results = {};
  for (const [name, algo] of Object.entries(limiters)) {
    const key = req.ip + ':burst';
    const history = [];
    for (let i = 0; i < 15; i++) history.push({ attempt: i + 1, ...algo.check(key) });
    results[name] = history.map(r => ({ attempt: r.attempt, allowed: r.allowed }));
  }
  res.json(results);
});

// === Admin: inspect all three ===
app.get('/admin/limits', (req, res) => res.json({ limiters: Object.fromEntries(Object.entries(limiters).map(([k, v]) => [k, { config: v }])) }));

app.listen(3000, () => console.log('Rate limit algorithms demo :3000 — /test/fixed, /test/sliding, /test/token, /burst'));
module.exports = app;
