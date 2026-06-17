// 03-checkout: Convert cart to order. Calculate tax, shipping, total. Clear the cart.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`
  CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, price_cents INTEGER, stock INTEGER);
  CREATE TABLE carts (id TEXT PRIMARY KEY, user_id TEXT);
  CREATE TABLE cart_items (cart_id TEXT, product_id INTEGER, quantity INTEGER, PRIMARY KEY (cart_id, product_id));
  CREATE TABLE orders (id TEXT PRIMARY KEY, user_id TEXT, subtotal_cents INTEGER, tax_cents INTEGER, shipping_cents INTEGER, total_cents INTEGER, status TEXT DEFAULT 'pending', shipping_address TEXT, created_at TEXT DEFAULT (datetime('now')));
  CREATE TABLE order_items (id INTEGER PRIMARY KEY AUTOINCREMENT, order_id TEXT, product_id INTEGER, quantity INTEGER, price_cents INTEGER);
`);

db.prepare('INSERT INTO products VALUES (1, ?, ?, ?)').run('Laptop', 99900, 50);
db.prepare('INSERT INTO products VALUES (2, ?, ?, ?)').run('Phone', 49900, 100);

function getOrCreateCart(userId) {
  let cart = db.prepare('SELECT * FROM carts WHERE user_id = ?').get(userId);
  if (!cart) {
    cart = { id: 'c_' + Math.random().toString(36).slice(2, 10), user_id: userId };
    db.prepare('INSERT INTO carts VALUES (?, ?)').run(cart.id, userId);
  }
  return cart;
}

function calcCart(userId) {
  const cart = getOrCreateCart(userId);
  const items = db.prepare(`SELECT ci.product_id, ci.quantity, p.name, p.price_cents FROM cart_items ci JOIN products p ON p.id = ci.product_id WHERE ci.cart_id = ?`).all(cart.id);
  const subtotal = items.reduce((s, i) => s + i.price_cents * i.quantity, 0);
  return { cart, items, subtotal };
}

const TAX_RATE = 0.08;  // 8% tax
const FREE_SHIPPING_THRESHOLD = 5000;  // cents
const FLAT_SHIPPING = 999;  // cents

// Cart (same as before, simplified)
app.get('/cart', (req, res) => res.json(calcCart(req.headers['x-user-id'] || 'guest')));

app.post('/cart/items', (req, res) => {
  const userId = req.headers['x-user-id'] || 'guest';
  const cart = getOrCreateCart(userId);
  const { product_id, quantity = 1 } = req.body;
  const existing = db.prepare('SELECT * FROM cart_items WHERE cart_id = ? AND product_id = ?').get(cart.id, product_id);
  if (existing) db.prepare('UPDATE cart_items SET quantity = quantity + ? WHERE cart_id = ? AND product_id = ?').run(quantity, cart.id, product_id);
  else db.prepare('INSERT INTO cart_items VALUES (?, ?, ?)').run(cart.id, product_id, quantity);
  res.status(201).json(calcCart(userId));
});

// Checkout: turn cart into an order
app.post('/checkout', (req, res) => {
  const userId = req.headers['x-user-id'] || 'guest';
  const { cart, items, subtotal } = calcCart(userId);

  if (items.length === 0) return res.status(422).json({ error: 'cart is empty' });
  if (!req.body.shipping_address) return res.status(422).json({ error: 'shipping_address required' });

  // Calculate totals
  const tax = Math.round(subtotal * TAX_RATE);
  const shipping = subtotal >= FREE_SHIPPING_THRESHOLD ? 0 : FLAT_SHIPPING;
  const total = subtotal + tax + shipping;

  // Create the order
  const orderId = 'ord_' + Date.now() + '_' + Math.random().toString(36).slice(2, 6);
  const insertOrder = db.prepare('INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?, ?, ?)');
  insertOrder.run(orderId, userId, subtotal, tax, shipping, total, 'pending', req.body.shipping_address);

  // Add order items
  for (const item of items) {
    db.prepare('INSERT INTO order_items (order_id, product_id, quantity, price_cents) VALUES (?, ?, ?, ?)').run(orderId, item.product_id, item.quantity, item.price_cents * item.quantity);
  }

  // Clear the cart
  db.prepare('DELETE FROM cart_items WHERE cart_id = ?').run(cart.id);

  res.status(201).json({
    order_id: orderId,
    status: 'pending',
    items,
    subtotal_cents: subtotal,
    tax_cents: tax,
    shipping_cents: shipping,
    total_cents: total,
    total: (total / 100).toFixed(2),
  });
});

app.get('/orders/:id', (req, res) => {
  const order = db.prepare('SELECT * FROM orders WHERE id = ?').get(req.params.id);
  if (!order) return res.status(404).json({ error: 'not found' });
  order.items = db.prepare('SELECT * FROM order_items WHERE order_id = ?').all(req.params.id);
  res.json(order);
});

app.listen(3000, () => console.log('03-checkout on :3000'));
