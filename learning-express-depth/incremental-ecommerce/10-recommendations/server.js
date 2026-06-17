// 10-recommendations: "Customers who bought X also bought Y." Two approaches: co-occurrence and popularity.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`
  CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, price_cents INTEGER, view_count INTEGER DEFAULT 0, purchase_count INTEGER DEFAULT 0);
  CREATE TABLE orders (id TEXT PRIMARY KEY, user_id TEXT);
  CREATE TABLE order_items (order_id TEXT, product_id INTEGER, quantity INTEGER);
  CREATE TABLE product_views (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, product_id INTEGER, ts TEXT DEFAULT (datetime('now')));
`);

// Seed
db.prepare('INSERT INTO products VALUES (1, ?, ?, 0, 0)').run('Laptop', 99900);
db.prepare('INSERT INTO products VALUES (2, ?, ?, 0, 0)').run('Laptop Bag', 2900);
db.prepare('INSERT INTO products VALUES (3, ?, ?, 0, 0)').run('Mouse', 2900);
db.prepare('INSERT INTO products VALUES (4, ?, ?, 0, 0)').run('Keyboard', 7900);
db.prepare('INSERT INTO products VALUES (5, ?, ?, 0, 0)').run('Monitor', 29900);

// Seed some orders (Laptop and Bag bought together; Mouse and Keyboard bought together)
function seedOrder(userId, productIds) {
  const orderId = 'ord_' + Math.random().toString(36).slice(2, 8);
  db.prepare('INSERT INTO orders VALUES (?, ?)').run(orderId, userId);
  for (const pid of productIds) {
    db.prepare('INSERT INTO order_items VALUES (?, ?, 1)').run(orderId, pid);
    db.prepare('UPDATE products SET purchase_count = purchase_count + 1 WHERE id = ?').run(pid);
  }
}
seedOrder('u1', [1, 2]);
seedOrder('u2', [1, 2]);
seedOrder('u3', [1, 2, 3]);
seedOrder('u4', [3, 4]);
seedOrder('u5', [3, 4, 5]);

// Track a view
app.post('/track/view', (req, res) => {
  const { user_id, product_id } = req.body;
  if (!user_id || !product_id) return res.status(422).json({ error: 'missing fields' });
  db.prepare('INSERT INTO product_views (user_id, product_id) VALUES (?, ?)').run(user_id, product_id);
  db.prepare('UPDATE products SET view_count = view_count + 1 WHERE id = ?').run(product_id);
  res.json({ tracked: true });
});

// Recommendations: "People who bought X also bought Y"
app.get('/products/:id/recommendations', (req, res) => {
  const productId = parseInt(req.params.id);

  // Find all orders containing this product
  const coOccurring = db.prepare(`
    SELECT oi2.product_id, COUNT(*) as count
    FROM order_items oi1
    JOIN order_items oi2 ON oi1.order_id = oi2.order_id AND oi2.product_id != oi1.product_id
    WHERE oi1.product_id = ?
    GROUP BY oi2.product_id
    ORDER BY count DESC
    LIMIT 5
  `).all(productId);

  if (coOccurring.length > 0) {
    const ids = coOccurring.map(c => c.product_id);
    const products = db.prepare(`SELECT * FROM products WHERE id IN (${ids.map(() => '?').join(',')})`).all(...ids);
    // Sort by co-occurrence count
    products.sort((a, b) => ids.indexOf(a.id) - ids.indexOf(b.id));
    return res.json({ product_id: productId, type: 'co_occurrence', recommendations: products });
  }

  // Fallback: most popular
  const popular = db.prepare('SELECT * FROM products WHERE id != ? ORDER BY purchase_count DESC LIMIT 5').all(productId);
  res.json({ product_id: productId, type: 'popularity', recommendations: popular });
});

// Trending now (most viewed in last hour, simulated)
app.get('/trending', (req, res) => {
  const trending = db.prepare('SELECT * FROM products ORDER BY view_count DESC LIMIT 5').all();
  res.json({ trending });
});

// Recently viewed by this user
app.get('/users/:userId/recently-viewed', (req, res) => {
  const views = db.prepare(`
    SELECT p.*, MAX(pv.ts) as last_viewed
    FROM product_views pv JOIN products p ON p.id = pv.product_id
    WHERE pv.user_id = ?
    GROUP BY p.id
    ORDER BY last_viewed DESC LIMIT 10
  `).all(req.params.userId);
  res.json({ user_id: req.params.userId, recently_viewed: views });
});

app.listen(3000, () => console.log('10-recommendations on :3000'));
