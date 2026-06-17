// Restaurant API — Step 19. Adds: menu, tables, reservations, orders with items.
const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE menu_categories (id TEXT PRIMARY KEY, name TEXT, position INTEGER DEFAULT 0)`);
db.exec(`CREATE TABLE menu_items (id TEXT PRIMARY KEY, category_id TEXT, name TEXT, description TEXT, price_cents INTEGER, available INTEGER DEFAULT 1)`);
db.exec(`CREATE TABLE tables (id TEXT PRIMARY KEY, number INTEGER UNIQUE, seats INTEGER, location TEXT)`);
db.exec(`CREATE TABLE reservations (id TEXT PRIMARY KEY, table_id TEXT, customer_name TEXT, customer_phone TEXT, party_size INTEGER, reserved_at TEXT, duration_min INTEGER DEFAULT 90, status TEXT DEFAULT 'confirmed', created_at TEXT DEFAULT (datetime('now')))`);
db.exec(`CREATE TABLE orders (id TEXT PRIMARY KEY, table_id TEXT, reservation_id TEXT, status TEXT DEFAULT 'open', total_cents INTEGER DEFAULT 0, created_at TEXT DEFAULT (datetime('now')))`);
db.exec(`CREATE TABLE order_items (id TEXT PRIMARY KEY, order_id TEXT, menu_item_id TEXT, quantity INTEGER, price_cents INTEGER, notes TEXT, status TEXT DEFAULT 'pending')`);

app.post('/menu/categories', (req, res) => {
  if (!req.body.name) return res.status(422).json({ error: 'missing_name' });
  const id = 'cat_' + crypto.randomBytes(3).toString('hex');
  db.prepare('INSERT INTO menu_categories (id, name, position) VALUES (?, ?, ?)').run(id, req.body.name, req.body.position || 0);
  res.status(201).json({ id });
});

app.post('/menu/items', (req, res) => {
  const { category_id, name, description, price_cents } = req.body;
  if (!category_id || !name || price_cents === undefined) return res.status(422).json({ error: 'missing_fields' });
  const id = 'mi_' + crypto.randomBytes(4).toString('hex');
  db.prepare('INSERT INTO menu_items (id, category_id, name, description, price_cents) VALUES (?, ?, ?, ?, ?)').run(id, category_id, name, description || '', price_cents);
  res.status(201).json({ id });
});

app.get('/menu', (req, res) => {
  const categories = db.prepare('SELECT * FROM menu_categories ORDER BY position').all();
  for (const c of categories) c.items = db.prepare('SELECT * FROM menu_items WHERE category_id = ? AND available = 1').all(c.id);
  res.json({ menu: categories });
});

app.post('/tables', (req, res) => {
  const { number, seats, location } = req.body;
  if (!number || !seats) return res.status(422).json({ error: 'missing_fields' });
  const id = 't_' + crypto.randomBytes(3).toString('hex');
  try { db.prepare('INSERT INTO tables (id, number, seats, location) VALUES (?, ?, ?, ?)').run(id, number, seats, location); res.status(201).json({ id }); }
  catch { res.status(409).json({ error: 'table_number_taken' }); }
});

app.post('/reservations', (req, res) => {
  const { table_id, customer_name, customer_phone, party_size, reserved_at, duration_min } = req.body;
  if (!table_id || !customer_name || !reserved_at) return res.status(422).json({ error: 'missing_fields' });
  // Check table availability
  const conflict = db.prepare('SELECT id FROM reservations WHERE table_id = ? AND status = "confirmed" AND reserved_at BETWEEN datetime(?, "-1 hour") AND datetime(?, "1 hour")').get(table_id, reserved_at, reserved_at);
  if (conflict) return res.status(409).json({ error: 'table_unavailable' });
  const id = 'r_' + crypto.randomBytes(4).toString('hex');
  db.prepare('INSERT INTO reservations (id, table_id, customer_name, customer_phone, party_size, reserved_at, duration_min) VALUES (?, ?, ?, ?, ?, ?, ?)').run(id, table_id, customer_name, customer_phone, party_size, reserved_at, duration_min || 90);
  res.status(201).json({ id });
});

app.get('/reservations', (req, res) => {
  const { date, table_id } = req.query;
  let query = 'SELECT r.*, t.number as table_number, t.seats FROM reservations r JOIN tables t ON t.id = r.table_id WHERE 1=1';
  const params = [];
  if (date) { query += ' AND date(r.reserved_at) = date(?)'; params.push(date); }
  if (table_id) { query += ' AND r.table_id = ?'; params.push(table_id); }
  query += ' ORDER BY r.reserved_at ASC';
  res.json({ reservations: db.prepare(query).all(...params) });
});

app.post('/orders', (req, res) => {
  if (!req.body.table_id) return res.status(422).json({ error: 'missing_table' });
  const id = 'o_' + crypto.randomBytes(4).toString('hex');
  db.prepare('INSERT INTO orders (id, table_id, reservation_id) VALUES (?, ?, ?)').run(id, req.body.table_id, req.body.reservation_id || null);
  res.status(201).json({ id });
});

app.post('/orders/:id/items', (req, res) => {
  const { menu_item_id, quantity, notes } = req.body;
  if (!menu_item_id || !quantity) return res.status(422).json({ error: 'missing_fields' });
  const order = db.prepare('SELECT * FROM orders WHERE id = ?').get(req.params.id);
  if (!order || order.status !== 'open') return res.status(404).json({ error: 'order_not_open' });
  const item = db.prepare('SELECT * FROM menu_items WHERE id = ?').get(menu_item_id);
  if (!item) return res.status(404).json({ error: 'menu_item_not_found' });
  const id = 'oi_' + crypto.randomBytes(4).toString('hex');
  const price = item.price_cents * quantity;
  db.prepare('INSERT INTO order_items (id, order_id, menu_item_id, quantity, price_cents, notes) VALUES (?, ?, ?, ?, ?, ?)').run(id, order.id, menu_item_id, quantity, price, notes || '');
  db.prepare('UPDATE orders SET total_cents = total_cents + ? WHERE id = ?').run(price, order.id);
  res.status(201).json({ id, price_cents: price });
});

app.get('/orders/:id', (req, res) => {
  const order = db.prepare('SELECT * FROM orders WHERE id = ?').get(req.params.id);
  if (!order) return res.status(404).json({ error: 'not_found' });
  order.items = db.prepare('SELECT oi.*, mi.name FROM order_items oi JOIN menu_items mi ON mi.id = oi.menu_item_id WHERE oi.order_id = ?').all(order.id);
  res.json(order);
});

app.listen(3000, () => console.log('Restaurant API :3000'));
module.exports = app;
