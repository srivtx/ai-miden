// Rate Limiting Demo — Token bucket algorithm with SQLite storage for multi-server use.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

// SQLite: stores rate limit state in DB so multiple servers share the counter
const db = new Database(':memory:');
db.exec(`CREATE TABLE buckets (
  key TEXT PRIMARY KEY,
  tokens REAL NOT NULL,
  last_refill INTEGER NOT NULL
)`);

// === Token Bucket Algorithm ===
class TokenBucket {
  constructor(capacity, refillPerSecond) {
    this.capacity = capacity;
    this.refillRate = refillPerSecond; // tokens per second
  }

  // Try to consume 1 token. Returns true if allowed, false if rate-limited.
  tryConsume(key) {
    const now = Date.now();
    let entry = db.prepare('SELECT * FROM buckets WHERE key = ?').get(key);
    if (!entry) {
      // New bucket: full
      db.prepare('INSERT INTO buckets (key, tokens, last_refill) VALUES (?, ?, ?)').run(key, this.capacity, now);
      entry = { key, tokens: this.capacity, last_refill: now };
    }
    // Refill based on elapsed time
    const elapsed = (now - entry.last_refill) / 1000;
    const refilled = Math.min(this.capacity, entry.tokens + elapsed * this.refillRate);
    if (refilled < 1) {
      // Save updated (slightly refilled) state
      db.prepare('UPDATE buckets SET tokens = ?, last_refill = ? WHERE key = ?').run(refilled, now, key);
      return { allowed: false, retryAfter: Math.ceil((1 - refilled) / this.refillRate) };
    }
    // Consume one
    db.prepare('UPDATE buckets SET tokens = ?, last_refill = ? WHERE key = ?').run(refilled - 1, now, key);
    return { allowed: true, remaining: Math.floor(refilled - 1) };
  }
}

// === Different buckets for different endpoints ===
const buckets = {
  default: new TokenBucket(100, 100 / 60),  // 100 per minute
  search: new TokenBucket(20, 20 / 60),     // 20 per minute (expensive)
  auth: new TokenBucket(5, 5 / 60),         // 5 per minute (prevent brute force)
  health: new TokenBucket(1000, 1000 / 60), // 1000 per minute (cheap)
};

function rateLimit(bucket, identity = 'ip') {
  return (req, res, next) => {
    const key = `${identity}:${req[identity] || req.ip}:${req.path}`;
    const result = buckets[bucket].tryConsume(key);
    res.set('X-RateLimit-Limit', buckets[bucket].capacity);
    res.set('X-RateLimit-Remaining', result.remaining || 0);
    if (!result.allowed) {
      res.set('Retry-After', result.retryAfter);
      return res.status(429).json({ error: 'Too many requests', retryAfter: result.retryAfter });
    }
    next();
  };
}

// === Endpoints ===
app.get('/health', rateLimit('health'), (req, res) => res.json({ status: 'ok' }));

app.get('/search', rateLimit('search'), (req, res) => res.json({ results: [`result for ${req.query.q || 'all'}`] }));

app.get('/api/data', rateLimit('default'), (req, res) => res.json({ data: 'some data' }));

app.post('/login', rateLimit('auth'), (req, res) => res.json({ message: 'Login attempt' }));

// Inspect bucket state
app.get('/admin/buckets', (req, res) => {
  const all = db.prepare('SELECT * FROM buckets').all();
  res.json({ total: all.length, sample: all.slice(0, 20) });
});

app.listen(3000, () => console.log('Rate limit demo :3000'));
module.exports = app;
