// 03-filters: Combine search with filters. Search "phone" + filter category=electronics + min_price.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, description TEXT, category TEXT, price_cents INTEGER, brand TEXT)`);

const products = [
  { name: 'iPhone 15', description: 'Latest Apple smartphone with great camera', category: 'electronics', price_cents: 99900, brand: 'apple' },
  { name: 'Galaxy S24', description: 'Samsung flagship phone with AI features', category: 'electronics', price_cents: 89900, brand: 'samsung' },
  { name: 'Pixel 8', description: 'Google phone with amazing camera', category: 'electronics', price_cents: 69900, brand: 'google' },
  { name: 'MacBook Pro', description: 'Powerful laptop for professionals', category: 'computers', price_cents: 249900, brand: 'apple' },
  { name: 'ThinkPad', description: 'Business laptop with great keyboard', category: 'computers', price_cents: 129900, brand: 'lenovo' },
];
for (const p of products) db.prepare('INSERT INTO products (name, description, category, price_cents, brand) VALUES (?, ?, ?, ?, ?)').run(p.name, p.description, p.category, p.price_cents, p.brand);

app.get('/search', (req, res) => {
  const { q, category, brand, min_price, max_price } = req.query;
  let query = 'SELECT * FROM products WHERE 1=1';
  const params = [];

  if (q) {
    const term = `%${q.toLowerCase()}%`;
    query += ' AND (LOWER(name) LIKE ? OR LOWER(description) LIKE ?)';
    params.push(term, term);
  }
  if (category) { query += ' AND category = ?'; params.push(category); }
  if (brand) { query += ' AND brand = ?'; params.push(brand); }
  if (min_price) { query += ' AND price_cents >= ?'; params.push(parseInt(min_price)); }
  if (max_price) { query += ' AND price_cents <= ?'; params.push(parseInt(max_price)); }
  query += ' ORDER BY price_cents';
  res.json({ query: q, filters: { category, brand, min_price, max_price }, results: db.prepare(query).all(...params) });
});

app.listen(3000, () => console.log('03-filters on :3000'));
