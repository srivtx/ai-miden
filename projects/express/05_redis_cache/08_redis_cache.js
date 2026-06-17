// 08_redis_cache.js — Redis caching + rate limiting. Learn: Redis as cache, sliding window limiter.

const express = require('express');
const Redis = require('ioredis');
const app = express();
app.use(express.json());

const redis = new Redis(); // connects to localhost:6379 by default

// ---- 1. Response cache: cache API results for N seconds ----
function cacheMiddleware(ttl = 60) {
  return async (req, res, next) => {
    // Only cache GET requests
    if (req.method !== 'GET') return next();

    const key = `cache:${req.originalUrl}`;
    const cached = await redis.get(key);
    if (cached) {
      return res.json({ ...JSON.parse(cached), fromCache: true });
    }

    // Monkey-patch res.json to cache the response
    const originalJson = res.json.bind(res);
    res.json = (body) => {
      redis.setex(key, ttl, JSON.stringify(body)); // set with expiry
      originalJson(body);
    };
    next();
  };
}

// ---- 2. Sliding window rate limiter ----
async function rateLimiter(req, res, next) {
  const ip = req.ip;
  const key = `ratelimit:${ip}`;
  const now = Date.now();
  const windowMs = 60 * 1000; // 1 minute
  const maxRequests = 30;

  // Remove entries outside the window
  await redis.zremrangebyscore(key, 0, now - windowMs);
  // Count current requests in window
  const count = await redis.zcard(key);

  if (count >= maxRequests) {
    const oldest = await redis.zrange(key, 0, 0, 'WITHSCORES');
    const retryAfter = Math.ceil((parseInt(oldest[1]) + windowMs - now) / 1000);
    return res.status(429).json({
      error: 'Too many requests',
      retryAfter: `${retryAfter}s`
    });
  }

  // Record this request
  await redis.zadd(key, now, `${now}-${Math.random()}`);
  await redis.expire(key, Math.ceil(windowMs / 1000) + 1);
  next();
}

// ---- Slow endpoint (simulated) — result gets cached ----
app.get('/api/slow-data', cacheMiddleware(30), async (req, res) => {
  await new Promise(r => setTimeout(r, 1000)); // simulate slow DB query
  res.json({ data: [1, 2, 3, 4, 5], timestamp: new Date().toISOString() });
});

// ---- Rate-limited endpoint ----
app.get('/api/fast', rateLimiter, (req, res) => {
  res.json({ message: 'Fast response' });
});

// ---- Cache invalidation on write ----
app.post('/api/update', async (req, res) => {
  // Delete all GET cache keys for this resource
  const keys = await redis.keys('cache:/api/*');
  if (keys.length) await redis.del(keys);
  res.json({ message: 'Updated, cache cleared', clearedKeys: keys.length });
});

app.listen(3000, () => console.log('Redis cache on :3000'));
/*
Test:
  curl localhost:3000/api/slow-data         # ~1s first time, cached after
  curl localhost:3000/api/slow-data         # instant (from cache)
  curl localhost:3000/api/update            # invalidates cache
  # Rate limit: run this 31 times quickly
  for i in {1..35}; do curl -s localhost:3000/api/fast | grep -c "Fast"; done
*/
