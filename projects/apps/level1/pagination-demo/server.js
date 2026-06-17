// Pagination Demo — Offset vs Cursor, both with SQLite backend.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  category TEXT,
  created_at TEXT DEFAULT (datetime('now'))
)`);
db.exec('CREATE INDEX idx_items_created ON items(created_at DESC)');
db.exec('CREATE INDEX idx_items_category ON items(category)');

// Seed
const insert = db.prepare('INSERT INTO items (name, category) VALUES (?, ?)');
const cats = ['electronics', 'books', 'clothing', 'food'];
for (let i = 1; i <= 500; i++) insert.run(`Item ${i}`, cats[i % 4]);

// === OFFSET pagination (simple but slow at scale) ===
app.get('/offset', (req, res) => {
  const limit = Math.min(50, parseInt(req.query.limit) || 20);
  const offset = Math.max(0, parseInt(req.query.offset) || 0);
  const start = process.hrtime.bigint();
  const rows = db.prepare('SELECT * FROM items ORDER BY id LIMIT ? OFFSET ?').all(limit, offset);
  const total = db.prepare('SELECT COUNT(*) as c FROM items').get().c;
  const ms = Number(process.hrtime.bigint() - start) / 1e6;
  res.json({
    pagination: { type: 'offset', limit, offset, total, totalPages: Math.ceil(total / limit) },
    timing: { ms: ms.toFixed(2) },
    data: rows,
  });
});

// === CURSOR pagination (constant speed at scale) ===
app.get('/cursor', (req, res) => {
  const limit = Math.min(50, parseInt(req.query.limit) || 20);
  const cursor = parseInt(req.query.cursor) || 0;
  const start = process.hrtime.bigint();
  const rows = db.prepare('SELECT * FROM items WHERE id > ? ORDER BY id LIMIT ?').all(cursor, limit);
  const ms = Number(process.hrtime.bigint() - start) / 1e6;
  const nextCursor = rows.length === limit ? rows[rows.length - 1].id : null;
  res.json({
    pagination: { type: 'cursor', limit, cursor, nextCursor, hasMore: nextCursor !== null },
    timing: { ms: ms.toFixed(2) },
    data: rows,
  });
});

// === CURSOR with filter (cursor-paginated by category) ===
app.get('/cursor/category/:cat', (req, res) => {
  const limit = Math.min(50, parseInt(req.query.limit) || 20);
  const cursor = parseInt(req.query.cursor) || 0;
  const start = process.hrtime.bigint();
  const rows = db.prepare('SELECT * FROM items WHERE category = ? AND id > ? ORDER BY id LIMIT ?').all(req.params.cat, cursor, limit);
  const ms = Number(process.hrtime.bigint() - start) / 1e6;
  res.json({
    pagination: { type: 'cursor', category: req.params.cat, limit, cursor, nextCursor: rows.length === limit ? rows[rows.length - 1].id : null },
    timing: { ms: ms.toFixed(2) },
    data: rows,
  });
});

// === Benchmark: compare speed at deep pages ===
app.get('/benchmark', (req, res) => {
  const results = {};
  // Page 1
  results.page1 = {
    offset_ms: timeQuery('offset', 'SELECT * FROM items ORDER BY id LIMIT 20 OFFSET 0'),
    cursor_ms: timeQuery('cursor', 'SELECT * FROM items WHERE id > 0 ORDER BY id LIMIT 20'),
  };
  // Page 1000 (offset = 20000, cursor = 20000)
  results.page1000 = {
    offset_ms: timeQuery('offset', 'SELECT * FROM items ORDER BY id LIMIT 20 OFFSET 20000'),
    cursor_ms: timeQuery('cursor', 'SELECT * FROM items WHERE id > 20000 ORDER BY id LIMIT 20'),
  };
  res.json(results);
});

function timeQuery(label, sql, ...params) {
  const start = process.hrtime.bigint();
  db.prepare(sql).all(...params);
  return Number(process.hrtime.bigint() - start) / 1e6;
}

app.listen(3000, () => console.log('Pagination demo :3000'));
module.exports = app;
