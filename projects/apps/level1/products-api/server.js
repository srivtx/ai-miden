// Products API — Step 4. Adds: categories, prices, inventory, search, sort, filter.
const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE categories (id TEXT PRIMARY KEY, name TEXT UNIQUE, slug TEXT UNIQUE)`);
db.exec(`CREATE TABLE products (id TEXT PRIMARY KEY, sku TEXT UNIQUE, name TEXT, description TEXT, price_cents INTEGER, stock INTEGER DEFAULT 0, category_id TEXT, created_at TEXT DEFAULT (datetime('now')))`);
db.exec(`CREATE INDEX idx_products_category ON products(category_id)`);
db.exec(`CREATE INDEX idx_products_price ON products(price_cents)`);

// Seed
const cat = { id: 'c_' + crypto.randomBytes(3).toString('hex'), name: 'Electronics', slug: 'electronics' };
db.prepare('INSERT INTO categories (id, name, slug) VALUES (?, ?, ?)').run(cat.id, cat.name, cat.slug);
const products = [
  { sku: 'LP-001', name: 'Laptop Pro', desc: 'Powerful laptop', price: 129900, stock: 15 },
  { sku: 'PH-002', name: 'Phone X', desc: 'Latest phone', price: 89900, stock: 30 },
  { sku: 'TB-003', name: 'Tablet Mini', desc: 'Compact tablet', price: 49900, stock: 0 },
  { sku: 'HD-004', name: 'Headphones', desc: 'Noise-cancelling', price: 29900, stock: 50 },
];
for (const p of products) {
  db.prepare('INSERT INTO products (id, sku, name, description, price_cents, stock, category_id) VALUES (?, ?, ?, ?, ?, ?, ?)').run('p_' + crypto.randomBytes(3).toString('hex'), p.sku, p.name, p.desc, p.price, p.stock, cat.id);
}

app.get('/products', (req, res) => {
  const { q, category, min_price, max_price, in_stock, sort = 'created_at', order = 'desc', limit = 20, offset = 0 } = req.query;
  let query = `SELECT p.*, c.name as category_name, c.slug as category_slug FROM products p LEFT JOIN categories c ON c.id = p.category_id WHERE 1=1`;
  const params = [];
  if (q) { query += ' AND (p.name LIKE ? OR p.description LIKE ? OR p.sku LIKE ?)'; params.push('%' + q + '%', '%' + q + '%', '%' + q + '%'); }
  if (category) { query += ' AND c.slug = ?'; params.push(category); }
  if (min_price) { query += ' AND p.price_cents >= ?'; params.push(parseInt(min_price)); }
  if (max_price) { query += ' AND p.price_cents <= ?'; params.push(parseInt(max_price)); }
  if (in_stock === 'true') { query += ' AND p.stock > 0'; }
  const validSorts = ['created_at', 'price_cents', 'name', 'stock'];
  const sortCol = validSorts.includes(sort) ? sort : 'created_at';
  const sortOrder = order === 'asc' ? 'ASC' : 'DESC';
  query += ` ORDER BY p.${sortCol} ${sortOrder} LIMIT ? OFFSET ?`;
  params.push(parseInt(limit), parseInt(offset));
  const items = db.prepare(query).all(...params);
  // Convert price_cents to dollars
  for (const p of items) p.price = (p.price_cents / 100).toFixed(2);
  res.json({ count: items.length, items });
});

app.get('/products/:id', (req, res) => {
  const product = db.prepare('SELECT p.*, c.name as category_name, c.slug as category_slug FROM products p LEFT JOIN categories c ON c.id = p.category_id WHERE p.id = ? OR p.sku = ?').get(req.params.id, req.params.id);
  if (!product) return res.status(404).json({ error: 'not_found' });
  product.price = (product.price_cents / 100).toFixed(2);
  res.json(product);
});

app.post('/products', (req, res) => {
  const { sku, name, description, price_cents, stock, category_id } = req.body;
  if (!sku || !name || price_cents === undefined) return res.status(422).json({ error: 'missing_fields' });
  const id = 'p_' + crypto.randomBytes(4).toString('hex');
  try { db.prepare('INSERT INTO products (id, sku, name, description, price_cents, stock, category_id) VALUES (?, ?, ?, ?, ?, ?, ?)').run(id, sku, name, description || '', price_cents, stock || 0, category_id || null); res.status(201).json(db.prepare('SELECT * FROM products WHERE id = ?').get(id)); }
  catch (e) { res.status(409).json({ error: 'sku_taken' }); }
});

app.patch('/products/:id', (req, res) => {
  const product = db.prepare('SELECT * FROM products WHERE id = ?').get(req.params.id);
  if (!product) return res.status(404).json({ error: 'not_found' });
  const updates = [];
  const params = [];
  for (const f of ['name', 'description', 'price_cents', 'stock', 'category_id']) {
    if (req.body[f] !== undefined) { updates.push(`${f} = ?`); params.push(req.body[f]); }
  }
  if (updates.length) {
    params.push(req.params.id);
    db.prepare(`UPDATE products SET ${updates.join(', ')} WHERE id = ?`).run(...params);
  }
  res.json(db.prepare('SELECT * FROM products WHERE id = ?').get(req.params.id));
});

app.patch('/products/:id/stock', (req, res) => {
  const delta = parseInt(req.body.delta || 0);
  const result = db.prepare('UPDATE products SET stock = MAX(0, stock + ?) WHERE id = ?').run(delta, req.params.id);
  result.changes ? res.json(db.prepare('SELECT id, stock FROM products WHERE id = ?').get(req.params.id)) : res.status(404).json({ error: 'not_found' });
});

app.delete('/products/:id', (req, res) => {
  const result = db.prepare('DELETE FROM products WHERE id = ?').run(req.params.id);
  result.changes ? res.status(204).end() : res.status(404).json({ error: 'not_found' });
});

app.get('/categories', (req, res) => {
  res.json({ categories: db.prepare('SELECT c.*, COUNT(p.id) as product_count FROM categories c LEFT JOIN products p ON p.category_id = c.id GROUP BY c.id').all() });
});

app.listen(3000, () => console.log('Products API :3000'));
module.exports = app;
