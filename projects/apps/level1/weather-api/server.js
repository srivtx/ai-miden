// Weather API — Step 5. Adds: external API calls, caching, time-series, fallback.
const express = require('express');
const app = express();
app.use(express.json());

// In-memory cache (cache-aside)
const cache = new Map(); // city -> { data, expiresAt }
const CACHE_TTL_MS = 10 * 60 * 1000; // 10 minutes
const history = []; // query history

// === Mock external API ===
function fetchWeatherFromProvider(city) {
  return new Promise((resolve) => {
    setTimeout(() => {
      const hash = [...city].reduce((a, c) => a + c.charCodeAt(0), 0);
      resolve({
        city, tempC: 15 + (hash % 20), humidity: 40 + (hash % 50), windKph: 5 + (hash % 30),
        conditions: ['sunny', 'cloudy', 'rainy', 'snowy'][hash % 4], observedAt: new Date().toISOString(),
      });
    }, 100 + Math.random() * 200);
  });
}

async function getWeather(city) {
  const cached = cache.get(city.toLowerCase());
  if (cached && cached.expiresAt > Date.now()) { cached.data.cached = true; return cached.data; }
  const data = await fetchWeatherFromProvider(city);
  cache.set(city.toLowerCase(), { data, expiresAt: Date.now() + CACHE_TTL_MS });
  history.unshift({ city, ts: Date.now(), cached: false });
  if (history.length > 100) history.pop();
  return { ...data, cached: false };
}

app.get('/weather/:city', async (req, res) => {
  try { res.json(await getWeather(req.params.city)); }
  catch (e) { res.status(502).json({ error: 'provider_error', detail: e.message }); }
});

app.get('/weather/:city/forecast', async (req, res) => {
  // 5-day forecast (mocked from same provider)
  const days = parseInt(req.query.days) || 5;
  const current = await getWeather(req.params.city);
  const forecast = Array.from({ length: days }, (_, i) => ({
    date: new Date(Date.now() + i * 86400000).toISOString().slice(0, 10),
    tempC: current.tempC + (Math.random() * 10 - 5),
    conditions: current.conditions,
  }));
  res.json({ city: req.params.city, current, forecast });
});

app.get('/weather/:city/history', (req, res) => {
  const cityHistory = history.filter(h => h.city === req.params.city);
  res.json({ city: req.params.city, count: cityHistory.length, history: cityHistory });
});

app.get('/admin/cache', (req, res) => {
  const items = Array.from(cache.entries()).map(([k, v]) => ({ city: k, expiresIn: Math.max(0, v.expiresAt - Date.now()) + 'ms' }));
  res.json({ count: items.length, items });
});

app.delete('/admin/cache/:city', (req, res) => {
  cache.delete(req.params.city.toLowerCase());
  res.status(204).end();
});

app.listen(3000, () => console.log('Weather API :3000 — GET /weather/:city, /weather/:city/forecast'));
module.exports = app;
