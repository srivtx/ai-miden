// 09_cache_redis.js — Response caching + session store with Redis.
const express = require('express');
const Redis = require('ioredis');
const app = express();
const redis = new Redis();

// Middleware: cache GET responses for N seconds
function cache(ttl = 60) {
  return async (req, res, next) => {
    if (req.method !== 'GET') return next();
    const key = `cache:${req.originalUrl}`;
    const hit = await redis.get(key);
    if (hit) return res.json({ ...JSON.parse(hit), cached: true });
    const orig = res.json.bind(res);
    res.json = (body) => { redis.setex(key, ttl, JSON.stringify(body)); orig(body); };
    next();
  };
}

// Simulated slow DB
app.get('/api/users', cache(30), async (req, res) => {
  await new Promise(r => setTimeout(r, 800));
  res.json({ users: [{ id: 1, name: 'Zen' }], ts: new Date().toISOString() });
});

// Cache invalidation on write
app.post('/api/users', async (req, res) => {
  await redis.del('cache:/api/users');
  res.json({ msg: 'Created, cache cleared' });
});

// Session store (simplified — real apps use express-session + connect-redis)
app.get('/session', async (req, res) => {
  const sid = req.headers['x-session-id'] || 'default';
  const key = `session:${sid}`;
  const data = JSON.parse((await redis.get(key)) || '{"visits":0}');
  data.visits++; data.lastVisit = new Date().toISOString();
  await redis.setex(key, 3600, JSON.stringify(data));
  res.json({ sessionId: sid, ...data });
});

app.listen(3000, () => console.log('Redis :3000'));
