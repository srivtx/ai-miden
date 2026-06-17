// 02_crud_sqlite.js — Full CRUD with real SQL. Pagination, constraints, transactions.

const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE products (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  price REAL NOT NULL CHECK(price > 0),
  stock INTEGER DEFAULT 0,
  created TEXT DEFAULT (datetime('now'))
)`);

// CREATE
app.post('/products', (req, res) => {
  const { name, price, stock } = req.body;
  if (!name || !price) return res.status(400).json({ error: 'name and price required' });
  const stmt = db.prepare('INSERT INTO products (name, price, stock) VALUES (?, ?, ?)');
  const { lastInsertRowid } = stmt.run(name, price, stock || 0);
  res.status(201).json(db.prepare('SELECT * FROM products WHERE id = ?').get(lastInsertRowid));
});

// READ all with pagination
app.get('/products', (req, res) => {
  const { page = 1, limit = 10, sort = 'id' } = req.query;
  const offset = (parseInt(page) - 1) * parseInt(limit);
  const allowedSorts = ['id', 'name', 'price'];
  const col = allowedSorts.includes(sort) ? sort : 'id';
  const rows = db.prepare(`SELECT * FROM products ORDER BY ${col} LIMIT ? OFFSET ?`).all(parseInt(limit), offset);
  const { count } = db.prepare('SELECT COUNT(*) as count FROM products').get();
  res.json({ page: parseInt(page), limit: parseInt(limit), total: count, data: rows });
});

// READ one
app.get('/products/:id', (req, res) => {
  const row = db.prepare('SELECT * FROM products WHERE id = ?').get(req.params.id);
  row ? res.json(row) : res.status(404).json({ error: 'Not found' });
});

// UPDATE (partial)
app.patch('/products/:id', (req, res) => {
  const { name, price, stock } = req.body;
  const row = db.prepare('SELECT * FROM products WHERE id = ?').get(req.params.id);
  if (!row) return res.status(404).json({ error: 'Not found' });
  db.prepare('UPDATE products SET name = COALESCE(?, name), price = COALESCE(?, price), stock = COALESCE(?, stock) WHERE id = ?')
    .run(name ?? null, price ?? null, stock ?? null, req.params.id);
  res.json(db.prepare('SELECT * FROM products WHERE id = ?').get(req.params.id));
});

// DELETE
app.delete('/products/:id', (req, res) => {
  const { changes } = db.prepare('DELETE FROM products WHERE id = ?').run(req.params.id);
  changes ? res.status(204).send() : res.status(404).json({ error: 'Not found' });
});

// Bulk create (transaction)
app.post('/products/bulk', (req, res) => {
  const items = req.body;
  if (!Array.isArray(items) || !items.length) return res.status(400).json({ error: 'Array required' });
  const insert = db.prepare('INSERT INTO products (name, price, stock) VALUES (?, ?, ?)');
  const tx = db.transaction((items) => items.map(i => insert.run(i.name, i.price, i.stock || 0).lastInsertRowid));
  const ids = tx(items);
  res.status(201).json({ count: ids.length, ids });
});

app.listen(3000, () => console.log('SQLite CRUD :3000'));
