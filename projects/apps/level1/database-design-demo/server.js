// Database Design Demo — Normalized 3NF schema with users, products, orders.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');

// === 3NF Schema with foreign keys, indexes ===
db.pragma('foreign_keys = ON');
db.exec(`
  CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    created_at TEXT DEFAULT (datetime('now'))
  );
  CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
  );
  CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price_cents INTEGER NOT NULL,
    category_id INTEGER REFERENCES categories(id),
    created_at TEXT DEFAULT (datetime('now'))
  );
  CREATE INDEX idx_products_category ON products(category_id);
  CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    total_cents INTEGER NOT NULL,
    status TEXT DEFAULT 'pending',
    created_at TEXT DEFAULT (datetime('now'))
  );
  CREATE INDEX idx_orders_user ON orders(user_id);
  CREATE INDEX idx_orders_status ON orders(status);
  CREATE TABLE order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id),
    quantity INTEGER NOT NULL,
    price_cents INTEGER NOT NULL
  );
  CREATE INDEX idx_order_items_order ON order_items(order_id);
`);

// Seed
const insertUser = db.prepare('INSERT INTO users (name, email) VALUES (?, ?)');
const insertCat = db.prepare('INSERT INTO categories (name) VALUES (?)');
const insertProduct = db.prepare('INSERT INTO products (name, price_cents, category_id) VALUES (?, ?, ?)');
const insertOrder = db.prepare('INSERT INTO orders (user_id, total_cents) VALUES (?, ?)');
const insertItem = db.prepare('INSERT INTO order_items (order_id, product_id, quantity, price_cents) VALUES (?, ?, ?, ?)');

const alice = insertUser.run('Alice', 'alice@example.com').lastInsertRowid;
const bob = insertUser.run('Bob', 'bob@example.com').lastInsertRowid;
const electronics = insertCat.run('Electronics').lastInsertRowid;
const books = insertCat.run('Books').lastInsertRowid;
const laptop = insertProduct.run('Laptop', 99900, electronics).lastInsertRowid;
const phone = insertProduct.run('Phone', 49900, electronics).lastInsertRowid;
const book1 = insertProduct.run('SQL Book', 2900, books).lastInsertRowid;
const order1 = insertOrder.run(alice, 102800).lastInsertRowid;
insertItem.run(order1, laptop, 1, 99900);
insertItem.run(order1, book1, 1, 2900);
const order2 = insertOrder.run(bob, 49900).lastInsertRowid;
insertItem.run(order2, phone, 1, 49900);

// === Endpoints (the 4 query patterns that show 3NF working) ===
// Pattern 1: Simple lookup with index
app.get('/users', (req, res) => {
  const rows = db.prepare('SELECT * FROM users ORDER BY id').all();
  res.json(rows);
});

// Pattern 2: Filter with index, sort with index
app.get('/orders', (req, res) => {
  const status = req.query.status;
  const rows = status
    ? db.prepare('SELECT * FROM orders WHERE status = ? ORDER BY created_at DESC').all(status)
    : db.prepare('SELECT * FROM orders ORDER BY created_at DESC').all();
  res.json(rows);
});

// Pattern 3: Join (3 tables, the killer demo)
app.get('/orders/full', (req, res) => {
  const rows = db.prepare(`
    SELECT
      o.id AS order_id,
      u.name AS user_name,
      u.email AS user_email,
      p.name AS product_name,
      c.name AS category_name,
      oi.quantity,
      oi.price_cents,
      o.status,
      o.created_at
    FROM orders o
    JOIN users u ON o.user_id = u.id
    JOIN order_items oi ON oi.order_id = o.id
    JOIN products p ON oi.product_id = p.id
    JOIN categories c ON p.category_id = c.id
    ORDER BY o.created_at DESC
  `).all();
  res.json(rows);
});

// Pattern 4: Aggregate with JOIN
app.get('/stats', (req, res) => {
  const rows = db.prepare(`
    SELECT
      c.name AS category,
      COUNT(DISTINCT o.id) AS order_count,
      SUM(oi.price_cents * oi.quantity) / 100.0 AS revenue_dollars
    FROM categories c
    LEFT JOIN products p ON p.category_id = c.id
    LEFT JOIN order_items oi ON oi.product_id = p.id
    LEFT JOIN orders o ON oi.order_id = o.id
    GROUP BY c.id
    ORDER BY revenue_dollars DESC
  `).all();
  res.json(rows);
});

// === Demonstrate integrity (FK enforcement) ===
app.get('/test/fk', (req, res) => {
  try {
    db.prepare('INSERT INTO orders (user_id, total_cents) VALUES (?, ?)').run(9999, 100);
    res.json({ inserted: true });
  } catch (e) {
    res.status(400).json({ error: e.message, code: 'fk_violation' });
  }
});

// === Update anomaly: changing user name ===
app.get('/test/update', (req, res) => {
  db.prepare('UPDATE users SET name = ? WHERE id = ?').run('Alicia', alice);
  const users = db.prepare('SELECT * FROM users WHERE id = ?').get(alice);
  const orders = db.prepare('SELECT * FROM orders WHERE user_id = ?').all(alice);
  res.json({ after_update: { users, orders_note: 'orders table is unchanged (good! 3NF means no duplication)' } });
});

app.listen(3000, () => console.log('DB design demo :3000'));
module.exports = app;
