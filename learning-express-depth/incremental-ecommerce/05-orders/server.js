// 05-orders: Order lifecycle. Status transitions, history, tracking.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`
  CREATE TABLE orders (id TEXT PRIMARY KEY, user_id TEXT, total_cents INTEGER, status TEXT DEFAULT 'pending', tracking TEXT, created_at TEXT DEFAULT (datetime('now')), updated_at TEXT DEFAULT (datetime('now')));
  CREATE TABLE order_events (id INTEGER PRIMARY KEY AUTOINCREMENT, order_id TEXT, from_status TEXT, to_status TEXT, ts TEXT DEFAULT (datetime('now')));
`);

const VALID_TRANSITIONS = {
  pending: ['paid', 'cancelled'],
  paid: ['shipped', 'cancelled', 'refunded'],
  shipped: ['delivered', 'returned'],
  delivered: ['returned'],
  cancelled: [],
  refunded: [],
  returned: [],
};

function logEvent(orderId, from, to) {
  db.prepare('INSERT INTO order_events (order_id, from_status, to_status) VALUES (?, ?, ?)').run(orderId, from, to);
}

function generateTracking() {
  return 'TRK' + Date.now() + Math.random().toString(36).slice(2, 8).toUpperCase();
}

// Seed
db.prepare('INSERT INTO orders (id, user_id, total_cents, status) VALUES (?, ?, ?, ?)').run('ord_001', 'alice', 10000, 'pending');

// List orders
app.get('/orders', (req, res) => {
  const { user_id, status } = req.query;
  let query = 'SELECT * FROM orders WHERE 1=1';
  const params = [];
  if (user_id) { query += ' AND user_id = ?'; params.push(user_id); }
  if (status) { query += ' AND status = ?'; params.push(status); }
  query += ' ORDER BY created_at DESC';
  res.json({ orders: db.prepare(query).all(...params) });
});

// Get order
app.get('/orders/:id', (req, res) => {
  const order = db.prepare('SELECT * FROM orders WHERE id = ?').get(req.params.id);
  if (!order) return res.status(404).json({ error: 'not found' });
  order.events = db.prepare('SELECT * FROM order_events WHERE order_id = ? ORDER BY ts ASC').all(order.id);
  res.json(order);
});

// Transition: pay
app.post('/orders/:id/pay', (req, res) => {
  const order = db.prepare('SELECT * FROM orders WHERE id = ?').get(req.params.id);
  if (!order) return res.status(404).json({ error: 'not found' });
  if (!VALID_TRANSITIONS[order.status].includes('paid')) {
    return res.status(409).json({ error: 'cannot transition', from: order.status, to: 'paid', allowed: VALID_TRANSITIONS[order.status] });
  }
  db.prepare('UPDATE orders SET status = ?, updated_at = datetime("now") WHERE id = ?').run('paid', order.id);
  logEvent(order.id, order.status, 'paid');
  res.json({ order_id: order.id, status: 'paid' });
});

// Transition: ship
app.post('/orders/:id/ship', (req, res) => {
  const order = db.prepare('SELECT * FROM orders WHERE id = ?').get(req.params.id);
  if (!order) return res.status(404).json({ error: 'not found' });
  if (!VALID_TRANSITIONS[order.status].includes('shipped')) {
    return res.status(409).json({ error: 'cannot ship', from: order.status, allowed: VALID_TRANSITIONS[order.status] });
  }
  const tracking = generateTracking();
  db.prepare('UPDATE orders SET status = ?, tracking = ?, updated_at = datetime("now") WHERE id = ?').run('shipped', tracking, order.id);
  logEvent(order.id, order.status, 'shipped');
  res.json({ order_id: order.id, status: 'shipped', tracking });
});

// Transition: deliver
app.post('/orders/:id/deliver', (req, res) => {
  const order = db.prepare('SELECT * FROM orders WHERE id = ?').get(req.params.id);
  if (!order) return res.status(404).json({ error: 'not found' });
  if (!VALID_TRANSITIONS[order.status].includes('delivered')) {
    return res.status(409).json({ error: 'cannot deliver', from: order.status });
  }
  db.prepare('UPDATE orders SET status = ?, updated_at = datetime("now") WHERE id = ?').run('delivered', order.id);
  logEvent(order.id, order.status, 'delivered');
  res.json({ order_id: order.id, status: 'delivered' });
});

// Cancel
app.post('/orders/:id/cancel', (req, res) => {
  const order = db.prepare('SELECT * FROM orders WHERE id = ?').get(req.params.id);
  if (!order) return res.status(404).json({ error: 'not found' });
  if (!VALID_TRANSITIONS[order.status].includes('cancelled')) {
    return res.status(409).json({ error: 'cannot cancel', from: order.status });
  }
  db.prepare('UPDATE orders SET status = ?, updated_at = datetime("now") WHERE id = ?').run('cancelled', order.id);
  logEvent(order.id, order.status, 'cancelled');
  res.json({ order_id: order.id, status: 'cancelled' });
});

app.listen(3000, () => console.log('05-orders on :3000'));
