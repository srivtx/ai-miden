// 01_hello_routes.js — First Express server. Learn: routes, params, query, JSON body.

const express = require('express');
const app = express();
app.use(express.json()); // Parse JSON request bodies

// ---- GET: read data ----
app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

// ---- GET with query params: /search?q=hello&limit=10 ----
app.get('/search', (req, res) => {
  const { q, limit } = req.query;
  res.json({ query: q, limit: parseInt(limit) || 10 });
});

// ---- GET with path params: /users/42 ----
app.get('/users/:id', (req, res) => {
  res.json({ userId: req.params.id });
});

// ---- POST: create data ----
app.post('/users', (req, res) => {
  const { name, email } = req.body;
  if (!name || !email) {
    return res.status(400).json({ error: 'name and email required' });
  }
  res.status(201).json({ id: Date.now(), name, email });
});

// ---- PUT: replace data ----
app.put('/users/:id', (req, res) => {
  res.json({ id: req.params.id, ...req.body, updated: true });
});

// ---- DELETE: remove data ----
app.delete('/users/:id', (req, res) => {
  res.json({ id: req.params.id, deleted: true });
});

// ---- 404 for unmatched routes ----
app.use((req, res) => {
  res.status(404).json({ error: `Route ${req.method} ${req.url} not found` });
});

app.listen(3000, () => console.log('http://localhost:3000'));
/* Test:
   curl localhost:3000/health
   curl "localhost:3000/search?q=hi&limit=5"
   curl localhost:3000/users/42
   curl -X POST localhost:3000/users -H "Content-Type: application/json" -d '{"name":"Zen","email":"zen@test.com"}'
   curl -X PUT localhost:3000/users/42 -H "Content-Type: application/json" -d '{"name":"New"}'
   curl -X DELETE localhost:3000/users/42
   curl localhost:3000/nonexistent
*/
