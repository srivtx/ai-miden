// Food Delivery API — Step 20. Adds: multiple restaurants, customers, drivers, delivery tracking.
const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE restaurants (id TEXT PRIMARY KEY, name TEXT, address TEXT, cuisine TEXT, rating REAL DEFAULT 0, delivery_fee_cents INTEGER DEFAULT 500)`);
db.exec(`CREATE TABLE menu_items (id TEXT PRIMARY KEY, restaurant_id TEXT, name TEXT, price_cents INTEGER, available INTEGER DEFAULT 1)`);
db.exec(`CREATE TABLE drivers (id TEXT PRIMARY KEY, name TEXT, phone TEXT, vehicle TEXT, current_lat REAL, current_lng REAL, available INTEGER DEFAULT 1, rating REAL DEFAULT 5.0)`);
db.exec(`CREATE TABLE orders (id TEXT PRIMARY KEY, customer_id TEXT, restaurant_id TEXT, driver_id TEXT, items_json TEXT, subtotal_cents INTEGER, delivery_fee_cents INTEGER, total_cents INTEGER, status TEXT DEFAULT 'pending', delivery_address TEXT, created_at TEXT DEFAULT (datetime('now')), picked_up_at TEXT, delivered_at TEXT)`);
db.exec(`CREATE INDEX idx_orders_status ON orders(status)`);
db.exec(`CREATE INDEX idx_orders_driver ON orders(driver_id, status)`);

app.post('/restaurants', (req, res) => {
  if (!req.body.name) return res.status(422).json({ error: 'missing_name' });
  const id = 'r_' + crypto.randomBytes(4).toString('hex');
  db.prepare('INSERT INTO restaurants (id, name, address, cuisine, delivery_fee_cents) VALUES (?, ?, ?, ?, ?)').run(id, req.body.name, req.body.address || '', req.body.cuisine || '', req.body.delivery_fee_cents || 500);
  res.status(201).json({ id });
});

app.get('/restaurants', (req, res) => {
  const { cuisine } = req.query;
  let query = 'SELECT * FROM restaurants WHERE 1=1';
  const params = [];
  if (cuisine) { query += ' AND cuisine = ?'; params.push(cuisine); }
  res.json({ restaurants: db.prepare(query).all(...params) });
});

app.post('/restaurants/:id/menu', (req, res) => {
  const { name, price_cents } = req.body;
  if (!name || price_cents === undefined) return res.status(422).json({ error: 'missing_fields' });
  const id = 'mi_' + crypto.randomBytes(4).toString('hex');
  db.prepare('INSERT INTO menu_items (id, restaurant_id, name, price_cents) VALUES (?, ?, ?, ?)').run(id, req.params.id, name, price_cents);
  res.status(201).json({ id });
});

app.get('/restaurants/:id/menu', (req, res) => {
  res.json({ items: db.prepare('SELECT * FROM menu_items WHERE restaurant_id = ? AND available = 1').all(req.params.id) });
});

app.post('/drivers', (req, res) => {
  const { name, phone, vehicle, current_lat, current_lng } = req.body;
  if (!name || !phone) return res.status(422).json({ error: 'missing_fields' });
  const id = 'd_' + crypto.randomBytes(4).toString('hex');
  db.prepare('INSERT INTO drivers (id, name, phone, vehicle, current_lat, current_lng) VALUES (?, ?, ?, ?, ?, ?)').run(id, name, phone, vehicle || 'car', current_lat, current_lng);
  res.status(201).json({ id });
});

app.patch('/drivers/:id/location', (req, res) => {
  const { lat, lng } = req.body;
  if (lat === undefined || lng === undefined) return res.status(422).json({ error: 'missing_latlng' });
  const result = db.prepare('UPDATE drivers SET current_lat = ?, current_lng = ? WHERE id = ?').run(lat, lng, req.params.id);
  result.changes ? res.json({ updated: true }) : res.status(404).json({ error: 'not_found' });
});

// === Place an order ===
app.post('/orders', (req, res) => {
  const { customer_id, restaurant_id, items, delivery_address } = req.body;
  if (!customer_id || !restaurant_id || !Array.isArray(items) || !items.length || !delivery_address) return res.status(422).json({ error: 'missing_fields' });
  const restaurant = db.prepare('SELECT * FROM restaurants WHERE id = ?').get(restaurant_id);
  if (!restaurant) return res.status(404).json({ error: 'restaurant_not_found' });
  // Calculate subtotal
  let subtotal = 0;
  for (const i of items) {
    const item = db.prepare('SELECT * FROM menu_items WHERE id = ? AND restaurant_id = ?').get(i.menu_item_id, restaurant_id);
    if (!item) return res.status(422).json({ error: 'invalid_menu_item', id: i.menu_item_id });
    subtotal += item.price_cents * (i.quantity || 1);
  }
  const id = 'o_' + crypto.randomBytes(4).toString('hex');
  db.prepare('INSERT INTO orders (id, customer_id, restaurant_id, items_json, subtotal_cents, delivery_fee_cents, total_cents, delivery_address) VALUES (?, ?, ?, ?, ?, ?, ?, ?)').run(id, customer_id, restaurant_id, JSON.stringify(items), subtotal, restaurant.delivery_fee_cents, subtotal + restaurant.delivery_fee_cents, delivery_address);
  res.status(201).json({ id, subtotal_cents: subtotal, delivery_fee_cents: restaurant.delivery_fee_cents, total_cents: subtotal + restaurant.delivery_fee_cents, status: 'pending' });
});

// === Restaurant accepts the order ===
app.post('/orders/:id/accept', (req, res) => {
  if (!req.restaurantId) return res.status(401).json({ error: 'restaurant_auth_required' });
  const order = db.prepare('SELECT * FROM orders WHERE id = ?').get(req.params.id);
  if (!order) return res.status(404).json({ error: 'not_found' });
  if (order.status !== 'pending') return res.status(422).json({ error: 'cannot_accept', current_status: order.status });
  db.prepare('UPDATE orders SET status = ? WHERE id = ?').run('preparing', order.id);
  res.json({ status: 'preparing' });
});

// === Driver claims a ready order ===
app.post('/orders/:id/claim', (req, res) => {
  if (!req.driverId) return res.status(401).json({ error: 'driver_auth_required' });
  const order = db.prepare('SELECT * FROM orders WHERE id = ? AND status = "ready"').get(req.params.id);
  if (!order) return res.status(404).json({ error: 'not_ready' });
  db.prepare('UPDATE orders SET driver_id = ?, status = ? WHERE id = ?').run(req.driverId, 'delivering', order.id);
  res.json({ status: 'delivering', driver_id: req.driverId });
});

// === Driver marks order ready (after picking up) ===
app.post('/orders/:id/pickup', (req, res) => {
  if (!req.driverId) return res.status(401).json({ error: 'driver_auth_required' });
  const order = db.prepare('SELECT * FROM orders WHERE id = ? AND driver_id = ?').get(req.params.id, req.driverId);
  if (!order) return res.status(404).json({ error: 'not_your_order' });
  db.prepare('UPDATE orders SET status = ?, picked_up_at = ? WHERE id = ?').run('delivering', new Date().toISOString(), order.id);
  res.json({ status: 'delivering' });
});

app.post('/orders/:id/deliver', (req, res) => {
  if (!req.driverId) return res.status(401).json({ error: 'driver_auth_required' });
  const order = db.prepare('SELECT * FROM orders WHERE id = ? AND driver_id = ?').get(req.params.id, req.driverId);
  if (!order) return res.status(404).json({ error: 'not_your_order' });
  db.prepare('UPDATE orders SET status = ?, delivered_at = ? WHERE id = ?').run('delivered', new Date().toISOString(), order.id);
  res.json({ status: 'delivered' });
});

app.get('/orders/:id', (req, res) => {
  const order = db.prepare('SELECT o.*, r.name as restaurant_name, d.name as driver_name, d.phone as driver_phone FROM orders o JOIN restaurants r ON r.id = o.restaurant_id LEFT JOIN drivers d ON d.id = o.driver_id WHERE o.id = ?').get(req.params.id);
  if (!order) return res.status(404).json({ error: 'not_found' });
  order.items = JSON.parse(order.items_json);
  res.json(order);
});

app.get('/orders/customer/:id', (req, res) => {
  const orders = db.prepare('SELECT o.*, r.name as restaurant_name FROM orders o JOIN restaurants r ON r.id = o.restaurant_id WHERE o.customer_id = ? ORDER BY o.created_at DESC').all(req.params.id);
  for (const o of orders) o.items = JSON.parse(o.items_json);
  res.json({ orders });
});

app.use((req, res, next) => { req.driverId = req.headers['x-driver-id']; req.restaurantId = req.headers['x-restaurant-id']; next(); });

app.listen(3000, () => console.log('Food delivery API :3000 — X-Driver-Id or X-Restaurant-Id header'));
module.exports = app;
