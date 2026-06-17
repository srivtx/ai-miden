// 53 — Redis Cache
// NEW CONCEPT: external cache (Redis).
// In-memory cache dies when the server restarts. Redis persists. Multiple servers can share it.
const express = require('express');
const Redis = require('ioredis');
const app = express();

// Connect to Redis (in-memory mode for demo, or use a real Redis URL)
const redis = new Redis(process.env.REDIS_URL || 'redis://localhost:6379');

// Helper: get with cache
async function getWithCache(key, fetchFn, ttlSeconds = 60) {
  const cached = await redis.get(key);
  if (cached) return { data: JSON.parse(cached), cached: true };

  const data = await fetchFn();
  await redis.setex(key, ttlSeconds, JSON.stringify(data));  // SET with EXpire
  return { data, cached: false };
}

// Sample data
const products = {
  1: { id: 1, name: 'Laptop', price: 999 },
  2: { id: 2, name: 'Phone', price: 499 },
  3: { id: 3, name: 'Tablet', price: 299 },
};

// Cached product endpoint
app.get('/products/:id', async (req, res) => {
  const result = await getWithCache(
    `product:${req.params.id}`,
    () => {
      console.log(`[db] Loading product ${req.params.id}`);
      return Promise.resolve(products[req.params.id]);
    },
    300  // 5 minutes
  );
  if (!result.data) return res.status(404).json({ error: 'Not found' });
  res.json(result);
});

// Invalidate cache
app.delete('/cache/product/:id', async (req, res) => {
  await redis.del(`product:${req.params.id}`);
  res.status(204).end();
});

// Cache stats
app.get('/admin/cache', async (req, res) => {
  const keys = await redis.keys('product:*');
  const out = {};
  for (const key of keys) {
    const ttl = await redis.ttl(key);
    out[key] = { ttlSeconds: ttl };
  }
  res.json(out);
});

app.listen(3000, () => console.log('Redis cache on http://localhost:3000'));
