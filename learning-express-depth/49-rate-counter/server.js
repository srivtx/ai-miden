// 49 — Rate Counter
// NEW CONCEPT: count requests per time window.
// Different from rate limiting (which blocks). This just observes.
const express = require('express');
const app = express();

// Sliding window counters
// Each route gets: { count, windowStart }
const counters = new Map();
const WINDOW_MS = 60 * 1000;  // 1 minute

// Middleware: count every request
app.use((req, res, next) => {
  const key = req.method + ' ' + req.path;
  const now = Date.now();

  if (!counters.has(key)) {
    counters.set(key, { count: 0, windowStart: now });
  }

  const c = counters.get(key);
  // Reset if window expired
  if (now - c.windowStart > WINDOW_MS) {
    c.count = 0;
    c.windowStart = now;
  }
  c.count += 1;
  next();
});

// Some sample endpoints
app.get('/api/users', (req, res) => res.json({ users: [] }));
app.get('/api/orders', (req, res) => res.json({ orders: [] }));
app.get('/api/products', (req, res) => res.json({ products: [] }));

// Stats endpoint
app.get('/admin/stats', (req, res) => {
  const out = {};
  for (const [key, c] of counters) {
    const elapsed = (Date.now() - c.windowStart) / 1000;
    out[key] = { count: c.count, windowAge: `${elapsed.toFixed(1)}s` };
  }
  res.json(out);
});

// Reset all counters
app.post('/admin/reset', (req, res) => {
  counters.clear();
  res.json({ message: 'reset' });
});

app.listen(3000, () => console.log('Rate counter on http://localhost:3000'));
