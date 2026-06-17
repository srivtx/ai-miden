// 06-inventory: Track stock. Reserve on order, release on cancel. Don't oversell.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`
  CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, price_cents INTEGER, stock INTEGER, reserved INTEGER DEFAULT 0);
  CREATE TABLE orders (id TEXT PRIMARY KEY, user_id TEXT, status TEXT DEFAULT 'pending');
  CREATE TABLE order_items (id INTEGER PRIMARY KEY AUTOINCREMENT, order_id TEXT, product_id INTEGER, quantity INTEGER);
`);

db.prepare('INSERT INTO products VALUES (1, ?, ?, 10, 0)').run('Laptop', 99900);
db.prepare('INSERT INTO products VALUES (2, ?, ?, 5, 0)').run('Phone', 49900);

// Inventory operations
function reserveStock(productId, quantity) {
  // Atomic check-and-decrement
  const r = db.prepare('UPDATE products SET stock = stock - ?, reserved = reserved + ? WHERE id = ? AND stock >= ?').run(quantity, quantity, productId, quantity);
  return r.changes > 0;
}
function releaseStock(productId, quantity) {
  db.prepare('UPDATE products SET stock = stock + ?, reserved = reserved - ? WHERE id = ?').run(quantity, quantity, productId);
}
function commitStock(productId, quantity) {
  // Order is paid: reserved stock becomes "sold" (no more available, no more reserved)
  db.prepare('UPDATE products SET reserved = reserved - ? WHERE id = ?').run(quantity, productId);
}
function availableStock(productId) {
  return db.prepare('SELECT stock FROM products WHERE id = ?').get(productId);
}

app.get('/products', (req, res) => {
  const products = db.prepare('SELECT id, name, price_cents, stock, reserved, (stock) as available FROM products').all();
  res.json({ products });
});

app.post('/orders', (req, res) => {
  const { user_id, items } = req.body;  // items: [{ product_id, quantity }]
  if (!user_id || !items || !items.length) return res.status(422).json({ error: 'missing fields' });

  // Check and reserve stock for all items
  for (const item of items) {
    if (!reserveStock(item.product_id, item.quantity)) {
      // Rollback already-reserved items
      for (const done of items.slice(0, items.indexOf(item))) {
        releaseStock(done.product_id, done.quantity);
      }
      return res.status(409).json({ error: 'insufficient stock', product_id: item.product_id });
    }
  }

  // Create the order
  const orderId = 'ord_' + Date.now();
  db.prepare('INSERT INTO orders VALUES (?, ?, ?)').run(orderId, user_id, 'pending');
  for (const item of items) {
    db.prepare('INSERT INTO order_items (order_id, product_id, quantity) VALUES (?, ?, ?)').run(orderId, item.product_id, item.quantity);
  }
  res.status(201).json({ order_id: orderId, status: 'pending', items });
});

// Pay: commit the reserved stock
app.post('/orders/:id/pay', (req, res) => {
  const order = db.prepare('SELECT * FROM orders WHERE id = ?').get(req.params.id);
  if (!order) return res.status(404).json({ error: 'not found' });
  if (order.status !== 'pending') return res.status(409).json({ error: 'not pending' });

  const items = db.prepare('SELECT * FROM order_items WHERE order_id = ?').all(req.params.id);
  for (const item of items) commitStock(item.product_id, item.quantity);
  db.prepare('UPDATE orders SET status = ? WHERE id = ?').run('paid', req.params.id);
  res.json({ order_id: order.id, status: 'paid' });
});

// Cancel: release the reserved stock
app.post('/orders/:id/cancel', (req, res) => {
  const order = db.prepare('SELECT * FROM orders WHERE id = ?').get(req.params.id);
  if (!order) return res.status(404).json({ error: 'not found' });
  if (order.status !== 'pending') return res.status(409).json({ error: 'not pending' });

  const items = db.prepare('SELECT * FROM order_items WHERE order_id = ?').all(req.params.id);
  for (const item of items) releaseStock(item.product_id, item.quantity);
  db.prepare('UPDATE orders SET status = ? WHERE id = ?').run('cancelled', req.params.id);
  res.json({ order_id: order.id, status: 'cancelled' });
});

app.listen(3000, () => console.log('06-inventory on :3000'));
