// 05-autocomplete: As the user types, suggest completions. FTS5 prefix matching.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();

const db = new Database(':memory:');
db.exec(`CREATE VIRTUAL TABLE products_fts USING fts5(name, description)`);
db.exec(`CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, description TEXT)`);

const products = [
  'iPhone 15 Pro Max', 'iPhone 15', 'iPhone 14', 'iPad Pro', 'iPad Air',
  'Galaxy S24 Ultra', 'Galaxy S24', 'Galaxy Tab', 'Google Pixel 8', 'Google Pixel Buds',
  'MacBook Pro', 'MacBook Air', 'Apple Watch', 'AirPods Pro', 'Apple TV',
];
for (const p of products) db.prepare('INSERT INTO products (name, description) VALUES (?, ?)').run(p, 'Sample description for ' + p);
for (const p of products) db.prepare("INSERT INTO products_fts (name, description) VALUES (?, ?)").run(p, 'Sample description for ' + p);

// Autocomplete: get suggestions as the user types
app.get('/autocomplete', (req, res) => {
  const { q, limit = 5 } = req.query;
  if (!q || q.length < 1) return res.json({ suggestions: [] });
  const suggestions = db.prepare(`
    SELECT DISTINCT name FROM products_fts
    WHERE products_fts MATCH ?
    ORDER BY rank
    LIMIT ?
  `).all(`${q}*`, parseInt(limit));
  res.json({ query: q, suggestions: suggestions.map(s => s.name) });
});

// Popular searches (could be from a log)
const popular = ['iPhone', 'MacBook', 'Galaxy', 'Pixel', 'iPad'];
app.get('/popular', (req, res) => res.json({ popular }));

app.listen(3000, () => console.log('05-autocomplete on :3000'));
