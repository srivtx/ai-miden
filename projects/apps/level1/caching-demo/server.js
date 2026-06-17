// Caching Demo — Cache-aside with SQLite backend + in-memory Map cache.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

// ---- SQLite database (the "slow" source) ----
const db = new Database(':memory:');
db.exec(`CREATE TABLE products (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL, price REAL NOT NULL,
  category TEXT, stock INTEGER DEFAULT 0
)`);
const insert = db.prepare('INSERT INTO products (name, price, category, stock) VALUES (?, ?, ?, ?)');
for (let i = 1; i <= 50; i++) insert.run(`Product ${i}`, i * 10, i % 3 === 0 ? 'electronics' : 'general', i * 5);

// ---- In-memory cache ----
const cache = new Map();
const stats = { hits: 0, misses: 0, sets: 0, evictions: 0 };
const CACHE_TTL = 60; // seconds
const MAX_CACHE_SIZE = 1000;

// STEP 1: Cache helpers
function cacheGet(key) {
  const entry = cache.get(key);
  if (!entry) return null;
  if (Date.now() > entry.expiresAt) { cache.delete(key); return null; }
  return entry.value;
}

function cacheSet(key, value) {
  if (cache.size >= MAX_CACHE_SIZE && !cache.has(key)) { stats.evictions++; cache.delete(cache.keys().next().value); }
  cache.set(key, { value, expiresAt: Date.now() + CACHE_TTL * 1000 });
  stats.sets++;
}

function cacheInvalidate(pattern) {
  let count = 0;
  for (const key of cache.keys()) {
    if (key === pattern || key.startsWith(pattern + ':')) { cache.delete(key); count++; }
  }
  return count;
}

// STEP 2: Cache-aside pattern
app.get('/products', (req, res) => {
  const key = 'products:all';
  const cached = cacheGet(key);
  if (cached) { stats.hits++; return res.json({ ...cached, cached: true }); }
  stats.misses++;
  const products = db.prepare('SELECT * FROM products').all();
  cacheSet(key, { count: products.length, data: products });
  res.json({ count: products.length, data: products, cached: false });
});

app.get('/products/:id', (req, res) => {
  const key = `product:${req.params.id}`;
  const cached = cacheGet(key);
  if (cached) { stats.hits++; return res.json({ ...cached, cached: true }); }
  stats.misses++;
  const product = db.prepare('SELECT * FROM products WHERE id = ?').get(req.params.id);
  if (!product) return res.status(404).json({ error: 'Not found' });
  cacheSet(key, product);
  res.json({ ...product, cached: false });
});

app.post('/products', (req, res) => {
  const { name, price, category, stock } = req.body;
  if (!name || !price) return res.status(400).json({ error: 'name and price required' });
  const result = db.prepare('INSERT INTO products (name, price, category, stock) VALUES (?, ?, ?, ?)').run(name, price, category || 'general', stock || 0);
  cacheInvalidate('products'); // Invalidate list
  const product = db.prepare('SELECT * FROM products WHERE id = ?').get(result.lastInsertRowid);
  res.status(201).json(product);
});

app.patch('/products/:id', (req, res) => {
  const result = db.prepare('UPDATE products SET name = COALESCE(?, name), price = COALESCE(?, price), category = COALESCE(?, category), stock = COALESCE(?, stock) WHERE id = ?').run(req.body.name, req.body.price, req.body.category, req.body.stock, req.params.id);
  if (!result.changes) return res.status(404).json({ error: 'Not found' });
  cacheInvalidate('products');
  res.json(db.prepare('SELECT * FROM products WHERE id = ?').get(req.params.id));
});

app.delete('/products/:id', (req, res) => {
  const result = db.prepare('DELETE FROM products WHERE id = ?').run(req.params.id);
  if (!result.changes) return res.status(404).json({ error: 'Not found' });
  cacheInvalidate('products');
  res.status(204).send();
});

// STEP 3: Cache management
app.get('/admin/cache', (req, res) => res.json({ size: cache.size, ...stats, hitRate: stats.hits / (stats.hits + stats.misses) || 0 }));

app.post('/admin/cache/clear', (req, res) => {
  const size = cache.size;
  cache.clear();
  res.json({ cleared: size });
});

app.get('/admin/cache/keys', (req, res) => res.json([...cache.keys()].slice(0, 50)));

app.listen(3000, () => console.log('Caching demo :3000'));
module.exports = app;
