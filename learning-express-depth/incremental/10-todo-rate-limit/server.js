// 10-todo-rate-limit: Per-user rate limit. Different limits for read vs write.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE todos (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, done INTEGER DEFAULT 0, user_id TEXT)`);

const buckets = new Map();

class TokenBucket {
  constructor(capacity, refillPerSec) {
    this.capacity = capacity;
    this.refillRate = refillPerSec;
  }
  tryConsume(key) {
    const now = Date.now();
    if (!buckets.has(key)) buckets.set(key, { tokens: this.capacity, lastRefill: now });
    const b = buckets.get(key);
    b.tokens = Math.min(this.capacity, b.tokens + ((now - b.lastRefill) / 1000) * this.refillRate);
    b.lastRefill = now;
    if (b.tokens < 1) return { allowed: false, retryAfter: Math.ceil((1 - b.tokens) / this.refillRate) };
    b.tokens -= 1;
    return { allowed: true, remaining: Math.floor(b.tokens) };
  }
}

const limits = {
  read: new TokenBucket(60, 60 / 60),  // 60 per minute
  write: new TokenBucket(10, 10 / 60), // 10 per minute
};

function rateLimit(type) {
  const limiter = limits[type];
  return (req, res, next) => {
    const key = req.headers['x-user-id'] || req.ip;
    const r = limiter.tryConsume(`${type}:${key}`);
    res.set('X-RateLimit-Limit', limiter.capacity);
    res.set('X-RateLimit-Remaining', r.remaining || 0);
    if (!r.allowed) {
      res.set('Retry-After', r.retryAfter);
      return res.status(429).json({ error: 'too many requests', retryAfter: r.retryAfter });
    }
    next();
  };
}

app.get('/todos', rateLimit('read'), (req, res) => {
  const todos = db.prepare('SELECT * FROM todos WHERE user_id = ? OR ? IS NULL').all(req.headers['x-user-id'], req.headers['x-user-id']);
  res.json({ count: todos.length, todos });
});

app.post('/todos', rateLimit('write'), (req, res) => {
  if (!req.body.title) return res.status(422).json({ error: 'title required' });
  const r = db.prepare('INSERT INTO todos (title, user_id) VALUES (?, ?)').run(req.body.title, req.headers['x-user-id']);
  res.status(201).json(db.prepare('SELECT * FROM todos WHERE id = ?').get(r.lastInsertRowid));
});

app.get('/admin/buckets', (req, res) => res.json({ size: buckets.size }));

app.listen(3000, () => console.log('10-todo-rate-limit on :3000'));
