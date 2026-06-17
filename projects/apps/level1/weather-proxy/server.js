// Weather Proxy — Call external API, cache results, rate limit, error handling.
const express = require('express');
const https = require('https');
const app = express();

const cache = new Map(); // city -> { data, expires }
const CACHE_TTL = 30 * 60 * 1000; // 30 minutes
const rateLimit = new Map(); // ip -> { count, reset }

// Rate limiter: 20 req/min per IP
app.use((req, res, next) => {
  const ip = req.ip; const now = Date.now();
  const entry = rateLimit.get(ip);
  if (!entry || now > entry.reset) { rateLimit.set(ip, { count: 1, reset: now + 60000 }); return next(); }
  entry.count++;
  if (entry.count > 20) return res.status(429).json({ error: 'Rate limit exceeded', retryAfter: Math.ceil((entry.reset - now) / 1000) });
  next();
});

// Get weather for a city
async function fetchWeather(city) {
  return new Promise((resolve, reject) => {
    const url = `https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&current_weather=true`; // Free API — no key needed
    // Real app: geocode city -> lat/lon first. This demo uses fixed Berlin coordinates.
    https.get(url, (res) => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        try { resolve(JSON.parse(data)); }
        catch (e) { reject(new Error('API parse error')); }
      });
    }).on('error', reject);
  });
}

app.get('/weather/:city', async (req, res) => {
  const city = req.params.city.toLowerCase();
  const now = Date.now();

  // Check cache
  const cached = cache.get(city);
  if (cached && now < cached.expires) return res.json({ ...cached.data, cached: true });

  try {
    const data = await fetchWeather(city);
    const result = {
      city: req.params.city,
      temperature: data.current_weather?.temperature,
      windspeed: data.current_weather?.windspeed,
      condition: data.current_weather?.weathercode,
      time: data.current_weather?.time,
    };
    cache.set(city, { data: result, expires: now + CACHE_TTL });
    res.json({ ...result, cached: false });
  } catch (err) {
    // Return stale cache if API fails
    if (cached) return res.json({ ...cached.data, cached: true, stale: true });
    res.status(502).json({ error: 'Weather API unavailable' });
  }
});

// Cache management
app.get('/admin/cache', (req, res) => {
  const entries = [...cache.entries()].map(([city, v]) => ({ city, expires: new Date(v.expires).toISOString(), ttl: Math.max(0, Math.ceil((v.expires - Date.now()) / 1000)) }));
  res.json({ count: entries.length, entries });
});

app.delete('/admin/cache', (req, res) => {
  const size = cache.size; cache.clear();
  res.json({ cleared: size });
});

app.listen(3000, () => console.log('Weather API :3000'));
module.exports = app;
