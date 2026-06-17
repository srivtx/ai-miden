// 57 — CORS
// NEW CONCEPT: cross-origin resource sharing.
// By default, browsers block JS from one site (e.g. localhost:3001) from calling another (localhost:3000).
// CORS headers tell the browser "this is OK."
const express = require('express');
const app = express();

// Allowed origins
const ALLOWED_ORIGINS = ['http://localhost:3001', 'https://myapp.com'];

// CORS middleware
function cors(req, res, next) {
  const origin = req.headers.origin;
  if (ALLOWED_ORIGINS.includes(origin)) {
    res.set('Access-Control-Allow-Origin', origin);
    res.set('Vary', 'Origin');
  }
  res.set('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS');
  res.set('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-CSRF-Token');
  res.set('Access-Control-Allow-Credentials', 'true');
  res.set('Access-Control-Max-Age', '86400');  // Cache preflight for 24h

  // Handle preflight (OPTIONS request)
  if (req.method === 'OPTIONS') {
    return res.status(204).end();
  }
  next();
}

app.use(cors);

app.get('/api/data', (req, res) => res.json({ data: 'some data' }));
app.post('/api/data', (req, res) => res.json({ created: true }));

app.listen(3000, () => console.log('CORS demo on http://localhost:3000'));
