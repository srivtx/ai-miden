// Library API — Step 14. Combines books + movies + music into one catalog with a unified search.
const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE items (id TEXT PRIMARY KEY, type TEXT CHECK(type IN ('book', 'movie', 'album')), title TEXT, creator TEXT, year INTEGER, genre TEXT, description TEXT, created_at TEXT DEFAULT (datetime('now')))`);
db.exec(`CREATE TABLE reviews (id TEXT PRIMARY KEY, item_id TEXT, item_type TEXT, user_id TEXT, rating INTEGER, body TEXT, created_at TEXT DEFAULT (datetime('now')))`);
db.exec(`CREATE TABLE user_collections (user_id TEXT, item_id TEXT, status TEXT DEFAULT 'planned', added_at TEXT DEFAULT (datetime('now')), PRIMARY KEY (user_id, item_id))`);
db.exec(`CREATE INDEX idx_items_type ON items(type)`);

app.get('/items', (req, res) => {
  const { type, q, genre, year, sort = 'recent' } = req.query;
  let query = `SELECT i.*, AVG(r.rating) as avg_rating, COUNT(r.id) as review_count FROM items i LEFT JOIN reviews r ON r.item_id = i.id AND r.item_type = i.type WHERE 1=1`;
  const params = [];
  if (type) { query += ' AND i.type = ?'; params.push(type); }
  if (q) { query += ' AND (i.title LIKE ? OR i.creator LIKE ? OR i.description LIKE ?)'; params.push('%' + q + '%', '%' + q + '%', '%' + q + '%'); }
  if (genre) { query += ' AND i.genre = ?'; params.push(genre); }
  if (year) { query += ' AND i.year = ?'; params.push(parseInt(year)); }
  query += ' GROUP BY i.id';
  if (sort === 'rating') query += ' ORDER BY avg_rating DESC';
  else if (sort === 'year') query += ' ORDER BY i.year DESC';
  else if (sort === 'title') query += ' ORDER BY i.title ASC';
  else query += ' ORDER BY i.created_at DESC';
  res.json({ items: db.prepare(query).all(...params) });
});

app.get('/items/:type/:id', (req, res) => {
  const item = db.prepare('SELECT * FROM items WHERE id = ? AND type = ?').get(req.params.id, req.params.type);
  if (!item) return res.status(404).json({ error: 'not_found' });
  item.reviews = db.prepare('SELECT * FROM reviews WHERE item_id = ? AND item_type = ?').all(item.id, item.type);
  item.avg_rating = item.reviews.length ? item.reviews.reduce((s, r) => s + r.rating, 0) / item.reviews.length : null;
  res.json(item);
});

app.post('/items', (req, res) => {
  const { type, title, creator, year, genre, description } = req.body;
  if (!['book', 'movie', 'album'].includes(type) || !title) return res.status(422).json({ error: 'missing_or_invalid_type' });
  const id = type[0] + '_' + crypto.randomBytes(4).toString('hex');
  db.prepare('INSERT INTO items (id, type, title, creator, year, genre, description) VALUES (?, ?, ?, ?, ?, ?, ?)').run(id, type, title, creator, year, genre, description || '');
  res.status(201).json({ id, type, title });
});

app.post('/items/:type/:id/reviews', (req, res) => {
  if (!req.userId) return res.status(401).json({ error: 'auth_required' });
  const { rating, body } = req.body;
  if (!rating || rating < 1 || rating > 5) return res.status(422).json({ error: 'invalid_rating' });
  const id = 'rv_' + crypto.randomBytes(4).toString('hex');
  db.prepare('INSERT INTO reviews (id, item_id, item_type, user_id, rating, body) VALUES (?, ?, ?, ?, ?, ?)').run(id, req.params.id, req.params.type, req.userId, rating, body || '');
  res.status(201).json({ id });
});

// === User collection (planned, in_progress, completed) ===
app.post('/collection/:type/:id', (req, res) => {
  if (!req.userId) return res.status(401).json({ error: 'auth_required' });
  const status = req.body.status || 'planned';
  if (!['planned', 'in_progress', 'completed', 'dropped'].includes(status)) return res.status(422).json({ error: 'invalid_status' });
  db.prepare('INSERT OR REPLACE INTO user_collections (user_id, item_id, status) VALUES (?, ?, ?)').run(req.userId, req.params.id, status);
  res.json({ item_id: req.params.id, status });
});

app.get('/collection', (req, res) => {
  if (!req.userId) return res.status(401).json({ error: 'auth_required' });
  const items = db.prepare('SELECT i.*, c.status, c.added_at FROM user_collections c JOIN items i ON i.id = c.item_id WHERE c.user_id = ? ORDER BY c.added_at DESC').all(req.userId);
  res.json({ collection: items });
});

app.get('/genres', (req, res) => {
  const genres = db.prepare('SELECT type, genre, COUNT(*) as count FROM items WHERE genre IS NOT NULL GROUP BY type, genre ORDER BY type, count DESC').all();
  res.json({ genres });
});

app.use((req, res, next) => { req.userId = req.headers['x-user-id']; next(); });

app.listen(3000, () => console.log('Library API :3000 — /items, /items/book|film|album'));
module.exports = app;
