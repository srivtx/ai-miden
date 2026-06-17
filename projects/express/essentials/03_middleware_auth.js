// 03_middleware_auth.js — Middleware chain: logger → auth → role check → handler → error.

const express = require('express');
const app = express();

// 1. Global: runs on every request
app.use((req, res, next) => {
  const start = Date.now();
  res.on('finish', () => console.log(`${req.method} ${req.url} ${res.statusCode} ${Date.now() - start}ms`));
  next();
});

// 2. Parse JSON only for /api routes
app.use('/api', express.json());

// 3. Auth middleware factory
function auth(requiredRole) {
  return (req, res, next) => {
    const token = req.headers.authorization;
    if (!token) return res.status(401).json({ error: 'No token' });
    const users = { 'admin-token': { role: 'admin' }, 'user-token': { role: 'user' } };
    const user = users[token.replace('Bearer ', '')];
    if (!user) return res.status(401).json({ error: 'Invalid token' });
    if (requiredRole && user.role !== requiredRole) return res.status(403).json({ error: 'Forbidden' });
    req.user = user;
    next();
  };
}

app.get('/public', (req, res) => res.json({ msg: 'Anyone' }));
app.get('/api/user', auth(), (req, res) => res.json({ msg: `Hello ${req.user.role}` }));
app.get('/api/admin', auth('admin'), (req, res) => res.json({ msg: 'Welcome admin' }));

// 4. Error handler (last middleware, 4 args)
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Internal error' });
});

app.listen(3000, () => console.log('Middleware demo :3000'));
