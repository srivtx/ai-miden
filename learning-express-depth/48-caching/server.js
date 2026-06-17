// 48 — Caching
// NEW CONCEPT: cache-aside pattern.
// Some data is expensive to fetch. Cache the result. Next time, serve from cache.
const express = require('express');
const app = express();

// Simulated slow database
function slowQuery(key) {
  console.log(`[db] Querying for: ${key}`);
  return new Promise(resolve => {
    setTimeout(() => resolve({ key, value: `value for ${key}`, ts: Date.now() }), 500));
  });
}

// Cache: key -> { data, expiresAt }
const cache = new Map();

async function getWithCache(key) {
  const cached = cache.get(key);
  if (cached && cached.expiresAt > Date.now()) {
    return { ...cached.data, cached: true };
  }
  // Cache miss: query the "database"
  const data = await slowQuery(key);
  cache.set(key, { data, expiresAt: Date.now() + 60 * 1000 });  // 60s TTL
  return { ...data, cached: false };
}

// API
app.get('/items/:key', async (req, res) => {
  const result = await getWithCache(req.params.key);
  res.json(result);
});

// Manual cache management
app.delete('/cache/:key', (req, res) => {
  cache.delete(req.params.key);
  res.status(204).end();
});

app.get('/admin/cache', (req, res) => {
  const out = {};
  for (const [key, entry] of cache) {
    out[key] = { expiresIn: entry.expiresAt - Date.now() };
  }
  res.json(out);
});

app.listen(3000, () => console.log('Cache on http://localhost:3000'));
