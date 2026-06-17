// 02-cart: Add a cart. Each user has a cart with line items.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`
  CREATE TABLE products (id INTEGER PRIMARY KEY, sku TEXT, name TEXT, price_cents INTEGER, stock INTEGER);
  CREATE TABLE carts (id TEXT PRIMARY KEY, user_id TEXT, created_at TEXT DEFAULT (datetime('now')));
  CREATE TABLE cart_items (cart_id TEXT, product_id INTEGER, quantity INTEGER, PRIMARY KEY (cart_id, product_id));
`);

// Seed one product
db.prepare('INSERT INTO products (id, sku, name, price_cents, stock) VALUES (1, ?, ?, ?, ?)').run('LP-001', 'Laptop', 99900, 50);
db.prepare('INSERT INTO products (id, sku, name, price_cents, stock) VALUES (2, ?, ?, ?, ?)').run('PH-001', 'Phone', 49900, 100);

function getOrCreateCart(userId) {
  let cart = db.prepare('SELECT * FROM carts WHERE user_id = ?').get(userId);
  if (!cart) {
    const id = 'c_' + Math.random().toString(36).slice(2, 10);
    db.prepare('INSERT INTO carts (id, user_id) VALUES (?, ?)').run(id, userId);
    cart = { id, user_id: userId };
  }
  return cart;
}

function getCart(userId) {
  const cart = getOrCreateCart(userId);
  const items = db.prepare(`
    SELECT ci.product_id, ci.quantity, p.name, p.price_cents, (ci.quantity * p.price_cents) as subtotal_cents
    FROM cart_items ci JOIN products p ON p.id = ci.product_id
    WHERE ci.cart_id = ?
  `).all(cart.id);
  const total = items.reduce((s, i) => s + i.subtotal_cents, 0);
  return { ...cart, items, total_cents: total, total: (total / 100).toFixed(2), count: items.length };
}

// Get cart
app.get('/cart', (req, res) => {
  const userId = req.headers['x-user-id'] || 'guest';
  res.json(getCart(userId));
});

// Add to cart
app.post('/cart/items', (req, res) => {
  const userId = req.headers['x-user-id'] || 'guest';
  const { product_id, quantity = 1 } = req.body;
  if (!product_id) return res.status(422).json({ error: 'product_id required' });

  const product = db.prepare('SELECT * FROM products WHERE id = ?').get(product_id);
  if (!product) return res.status(404).json({ error: 'product not found' });
  if (product.stock < quantity) return res.status(409).json({ error: 'not enough stock', available: product.stock });

  const cart = getOrCreateCart(userId);
  // Upsert: if exists, add to quantity; else insert
  const existing = db.prepare('SELECT * FROM cart_items WHERE cart_id = ? AND product_id = ?').get(cart.id, product_id);
  if (existing) {
    db.prepare('UPDATE cart_items SET quantity = quantity + ? WHERE cart_id = ? AND product_id = ?').run(quantity, cart.id, product_id);
  } else {
    db.prepare('INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (?, ?, ?)').run(cart.id, product_id, quantity);
  }
  res.status(201).json(getCart(userId));
});

// Update quantity
app.patch('/cart/items/:productId', (req, res) => {
  const userId = req.headers['x-user-id'] || 'guest';
  const { quantity } = req.body;
  if (quantity < 1) return res.status(422).json({ error: 'quantity must be at least 1' });
  const cart = getOrCreateCart(userId);
  db.prepare('UPDATE cart_items SET quantity = ? WHERE cart_id = ? AND product_id = ?').run(quantity, cart.id, parseInt(req.params.productId));
  res.json(getCart(userId));
});

// Remove from cart
app.delete('/cart/items/:productId', (req, res) => {
  const userId = req.headers['x-user-id'] || 'guest';
  const cart = getOrCreateCart(userId);
  db.prepare('DELETE FROM cart_items WHERE cart_id = ? AND product_id = ?').run(cart.id, parseInt(req.params.productId));
  res.json(getCart(userId));
});

// Clear cart
app.delete('/cart', (req, res) => {
  const userId = req.headers['x-user-id'] || 'guest';
  const cart = getOrCreateCart(userId);
  db.prepare('DELETE FROM cart_items WHERE cart_id = ?').run(cart.id);
  res.json(getCart(userId));
});

app.listen(3000, () => console.log('02-cart on :3000'));
