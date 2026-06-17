// 01-products: The foundation. Products with categories, search, filter, sort.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`
  CREATE TABLE categories (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL, slug TEXT UNIQUE NOT NULL);
  CREATE TABLE products (id INTEGER PRIMARY KEY AUTOINCREMENT, sku TEXT UNIQUE NOT NULL, name TEXT NOT NULL, description TEXT, price_cents INTEGER NOT NULL, category_id INTEGER, stock INTEGER DEFAULT 0, created_at TEXT DEFAULT (datetime('now')));
  CREATE INDEX idx_products_category ON products(category_id);
  CREATE INDEX idx_products_price ON products(price_cents);
`);

const insertCategory = db.prepare('INSERT INTO categories (name, slug) VALUES (?, ?)');
const insertProduct = db.prepare('INSERT INTO products (sku, name, description, price_cents, category_id, stock) VALUES (?, ?, ?, ?, ?, ?)');
const selectAll = db.prepare(`SELECT p.*, c.name as category_name, c.slug as category_slug FROM products p LEFT JOIN categories c ON c.id = p.category_id`);
const selectOne = db.prepare(`SELECT p.*, c.name as category_name FROM products p LEFT JOIN categories c ON c.id = p.category_id WHERE p.id = ?`);

// Categories
app.post('/categories', (req, res) => {
  const { name, slug } = req.body;
  if (!name || !slug) return res.status(422).json({ error: 'name and slug required' });
  try {
    const r = insertCategory.run(name, slug);
    res.status(201).json({ id: r.lastInsertRowid, name, slug });
  } catch (e) { res.status(409).json({ error: 'category exists' }); }
});

app.get('/categories', (req, res) => res.json({ categories: db.prepare('SELECT * FROM categories').all() }));

// Products
app.get('/products', (req, res) => {
  const { q, category, min_price, max_price, in_stock, sort = 'created_at', order = 'desc', limit = 20, offset = 0 } = req.query;
  let query = selectAll;
  let countQuery = 'SELECT COUNT(*) as c FROM products p WHERE 1=1';
  const params = [];
  const conds = [];
  if (q) { conds.push('(p.name LIKE ? OR p.description LIKE ? OR p.sku LIKE ?)'); params.push('%' + q + '%', '%' + q + '%', '%' + q + '%'); }
  if (category) { conds.push('c.slug = ?'); params.push(category); }
  if (min_price) { conds.push('p.price_cents >= ?'); params.push(parseInt(min_price)); }
  if (max_price) { conds.push('p.price_cents <= ?'); params.push(parseInt(max_price)); }
  if (in_stock === 'true') conds.push('p.stock > 0');
  if (conds.length) {
    const where = ' WHERE ' + conds.join(' AND ');
    query += where;
    countQuery += where;
  }
  const validSorts = { created_at: 'p.created_at', price_cents: 'p.price_cents', name: 'p.name' };
  query += ` ORDER BY ${validSorts[sort] || 'p.created_at'} ${order === 'asc' ? 'ASC' : 'DESC'} LIMIT ? OFFSET ?`;
  params.push(parseInt(limit), parseInt(offset));

  const items = query.all(...params).map(p => ({ ...p, price: (p.price_cents / 100).toFixed(2) }));
  const total = db.prepare(countQuery).get(...params.slice(0, -2)).c;
  res.json({ count: total, items, pagination: { limit: parseInt(limit), offset: parseInt(offset) } });
});

app.get('/products/:id', (req, res) => {
  const p = selectOne.get(parseInt(req.params.id));
  if (!p) return res.status(404).json({ error: 'not found' });
  res.json({ ...p, price: (p.price_cents / 100).toFixed(2) });
});

app.post('/products', (req, res) => {
  const { sku, name, description, price_cents, category_id, stock } = req.body;
  if (!sku || !name || price_cents === undefined) return res.status(422).json({ error: 'missing fields' });
  try {
    const r = insertProduct.run(sku, name, description || '', price_cents, category_id, stock || 0);
    res.status(201).json(selectOne.get(r.lastInsertRowid));
  } catch (e) { res.status(409).json({ error: 'sku taken' }); }
});

app.patch('/products/:id/stock', (req, res) => {
  const delta = parseInt(req.body.delta || 0);
  const r = db.prepare('UPDATE products SET stock = MAX(0, stock + ?) WHERE id = ?').run(delta, parseInt(req.params.id));
  r.changes ? res.json(db.prepare('SELECT id, stock FROM products WHERE id = ?').get(parseInt(req.params.id))) : res.status(404).json({ error: 'not found' });
});

app.listen(3000, () => console.log('01-products on :3000'));
