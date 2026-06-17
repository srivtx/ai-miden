// 04-facets: Show counts per category. "12 in electronics, 5 in computers."
const express = require('express');
const Database = require('better-sqlite3');
const app = express();

const db = new Database(':memory:');
db.exec(`CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, category TEXT, brand TEXT, price_cents INTEGER)`);

const products = [
  { name: 'iPhone', category: 'electronics', brand: 'apple', price_cents: 99900 },
  { name: 'Galaxy', category: 'electronics', brand: 'samsung', price_cents: 89900 },
  { name: 'Pixel', category: 'electronics', brand: 'google', price_cents: 69900 },
  { name: 'MacBook', category: 'computers', brand: 'apple', price_cents: 249900 },
  { name: 'ThinkPad', category: 'computers', brand: 'lenovo', price_cents: 129900 },
];
for (const p of products) db.prepare('INSERT INTO products (name, category, brand, price_cents) VALUES (?, ?, ?, ?)').run(p.name, p.category, p.brand, p.price_cents);

app.get('/search', (req, res) => {
  const { q, category, brand } = req.query;
  let query = 'SELECT * FROM products WHERE 1=1';
  const params = [];
  if (q) { query += ' AND LOWER(name) LIKE ?'; params.push(`%${q.toLowerCase()}%`); }
  if (category) { query += ' AND category = ?'; params.push(category); }
  if (brand) { query += ' AND brand = ?'; params.push(brand); }

  const results = db.prepare(query).all(...params);

  // Compute facets from the SAME filtered set (not the whole table)
  const facets = {};
  for (const field of ['category', 'brand']) {
    const counts = {};
    for (const r of results) counts[r[field]] = (counts[r[field]] || 0) + 1;
    facets[field] = Object.entries(counts).map(([value, count]) => ({ value, count })).sort((a, b) => b.count - a.count);
  }

  res.json({ query: q, count: results.length, results, facets });
});

app.listen(3000, () => console.log('04-facets on :3000'));
