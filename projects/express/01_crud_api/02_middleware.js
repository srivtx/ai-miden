// 02_middleware.js — The middleware pipeline: functions that run before your route handler.

const express = require('express');
const app = express();

// ---- Middleware 1: runs on EVERY request ----
app.use((req, res, next) => {
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.url}`);
  next(); // pass control to next middleware or route
});

// ---- Middleware 2: runs only for /api/* routes ----
app.use('/api', (req, res, next) => {
  console.log('  API middleware triggered');
  req.apiHit = true; // attach data to request for downstream handlers
  next();
});

// ---- Middleware 3: authentication check (simulated) ----
function requireAuth(req, res, next) {
  const token = req.headers.authorization;
  if (!token) return res.status(401).json({ error: 'No token' });
  req.user = { id: 1, role: 'admin' }; // decoded from token in real app
  next();
}

// ---- Route: public (no auth) ----
app.get('/public', (req, res) => {
  // req.apiHit is undefined here because /public doesn't match /api prefix
  res.json({ message: 'Anyone can see this' });
});

// ---- Route: API with prefix middleware ----
app.get('/api/data', (req, res) => {
  res.json({ data: 'some data', apiHit: req.apiHit }); // apiHit will be true
});

// ---- Route: protected (requires auth) ----
app.get('/admin/dashboard', requireAuth, (req, res) => {
  res.json({ message: `Welcome user ${req.user.id}`, role: req.user.role });
});

// ---- Error-handling middleware (4 args = Express knows it's error handler) ----
app.use((err, req, res, next) => {
  console.error('ERROR:', err.message);
  res.status(500).json({ error: 'Internal server error' });
});

app.listen(3000, () => console.log('http://localhost:3000'));
/*
Test:
  curl localhost:3000/public
  curl localhost:3000/api/data
  curl localhost:3000/admin/dashboard                          // 401
  curl -H "Authorization: Bearer mytoken" localhost:3000/admin/dashboard  // 200
*/
