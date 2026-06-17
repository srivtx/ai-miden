// API Versioning — Multiple ways: URL path, header, content type, query param.
const express = require('express');
const app = express();
app.use(express.json());

const users = [
  { id: 1, name: 'Zen', email: 'zen@test.com' },
  { id: 2, name: 'Ava', email: 'ava@test.com' },
];

// === Method 1: URL path versioning ===
app.get('/api/v1/users', (req, res) => res.json({ version: 'v1', users: users.map(u => ({ id: u.id, name: u.name })) }));
app.get('/api/v2/users', (req, res) => res.json({ version: 'v2', users }));

// === Method 2: Header versioning (Accept header) ===
app.get('/api/users', (req, res) => {
  const accept = req.headers.accept || '';
  if (accept.includes('version=2')) {
    res.json({ version: 'v2', users, deprecatedFields: [] });
  } else if (accept.includes('version=1')) {
    res.json({ version: 'v1', users: users.map(u => ({ id: u.id, name: u.name })) });
  } else {
    // Default to v2 (latest)
    res.json({ version: 'v2 (default)', users });
  }
});

// === Method 3: Custom header (X-API-Version) ===
app.get('/api-via-header/users', (req, res) => {
  const version = req.headers['x-api-version'] || '2';
  if (version === '1') res.json({ version: 'v1', users: users.map(u => ({ id: u.id, name: u.name })) });
  else res.json({ version: 'v2', users });
});

// === Method 4: Query param ===
app.get('/api-via-query/users', (req, res) => {
  const version = req.query.version || '2';
  if (version === '1') res.json({ version: 'v1', users: users.map(u => ({ id: u.id, name: u.name })) });
  else res.json({ version: 'v2', users });
});

// === Deprecation: Sunset header ===
app.get('/api/v1/users', (req, res) => {
  res.set('Sunset', 'Sat, 01 Jan 2025 00:00:00 GMT');
  res.set('Deprecation', 'true');
  res.set('Link', '</api/v2/users>; rel="successor-version"');
  res.json({ version: 'v1 (deprecated)', message: 'Migrate to /api/v2/users', users: users.map(u => ({ id: u.id, name: u.name })) });
});

app.listen(3000, () => console.log('API versioning :3000'));
module.exports = app;
