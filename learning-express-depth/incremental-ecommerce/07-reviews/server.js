// 07-reviews: Customers rate and review products. Aggregate ratings, only verified buyers.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`
  CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, price_cents INTEGER);
  CREATE TABLE orders (id TEXT PRIMARY KEY, user_id TEXT, status TEXT);
  CREATE TABLE order_items (order_id TEXT, product_id INTEGER, quantity INTEGER);
  CREATE TABLE reviews (id INTEGER PRIMARY KEY AUTOINCREMENT, product_id INTEGER, user_id TEXT, rating INTEGER CHECK(rating BETWEEN 1 AND 5), title TEXT, body TEXT, verified INTEGER DEFAULT 0, created_at TEXT DEFAULT (datetime('now')));
  CREATE INDEX idx_reviews_product ON reviews(product_id);
`);

db.prepare('INSERT INTO products VALUES (1, ?, ?)').run('Laptop', 99900);
db.prepare('INSERT INTO products VALUES (2, ?, ?)').run('Phone', 49900);

// A previous order for alice (for verified-purchase check)
db.prepare('INSERT INTO orders VALUES (?, ?, ?)').run('ord_001', 'alice', 'delivered');
db.prepare('INSERT INTO order_items VALUES (?, ?, ?)').run('ord_001', 1, 1);

// Add a review
app.post('/products/:id/reviews', (req, res) => {
  const productId = parseInt(req.params.id);
  const { user_id, rating, title, body } = req.body;
  if (!user_id || !rating) return res.status(422).json({ error: 'user_id and rating required' });
  if (rating < 1 || rating > 5) return res.status(422).json({ error: 'rating must be 1-5' });

  // Verified purchase: did this user buy this product in a delivered order?
  const verified = db.prepare(`
    SELECT 1 FROM order_items oi JOIN orders o ON o.id = oi.order_id
    WHERE o.user_id = ? AND oi.product_id = ? AND o.status = 'delivered' LIMIT 1
  `).get(user_id, productId);

  if (!verified) {
    return res.status(403).json({ error: 'only verified purchasers can review' });
  }

  // One review per user per product
  const existing = db.prepare('SELECT id FROM reviews WHERE product_id = ? AND user_id = ?').get(productId, user_id);
  if (existing) {
    db.prepare('UPDATE reviews SET rating = ?, title = ?, body = ?, verified = 1 WHERE id = ?').run(rating, title, body, existing.id);
    return res.json({ id: existing.id, updated: true });
  }

  const r = db.prepare('INSERT INTO reviews (product_id, user_id, rating, title, body, verified) VALUES (?, ?, ?, ?, ?, 1)').run(productId, user_id, rating, title, body);
  res.status(201).json({ id: r.lastInsertRowid });
});

// Get reviews for a product
app.get('/products/:id/reviews', (req, res) => {
  const productId = parseInt(req.params.id);
  const reviews = db.prepare('SELECT * FROM reviews WHERE product_id = ? ORDER BY created_at DESC').all(productId);
  res.json({ count: reviews.length, reviews });
});

// Aggregate rating for a product
app.get('/products/:id/rating', (req, res) => {
  const productId = parseInt(req.params.id);
  const stats = db.prepare(`
    SELECT
      COUNT(*) as count,
      AVG(rating) as average,
      SUM(CASE WHEN rating = 5 THEN 1 ELSE 0 END) as five,
      SUM(CASE WHEN rating = 4 THEN 1 ELSE 0 END) as four,
      SUM(CASE WHEN rating = 3 THEN 1 ELSE 0 END) as three,
      SUM(CASE WHEN rating = 2 THEN 1 ELSE 0 END) as two,
      SUM(CASE WHEN rating = 1 THEN 1 ELSE 0 END) as one
    FROM reviews WHERE product_id = ?
  `).get(productId);
  res.json({
    product_id: productId,
    count: stats.count,
    average: stats.count ? Math.round(stats.average * 10) / 10 : null,
    distribution: { 5: stats.five, 4: stats.four, 3: stats.three, 2: stats.two, 1: stats.one },
  });
});

app.listen(3000, () => console.log('07-reviews on :3000'));
