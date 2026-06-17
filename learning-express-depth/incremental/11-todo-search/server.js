// 11-todo-search: Full-text search with ranking. SQLite FTS5 for real search.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
// FTS5 virtual table for full-text search
db.exec(`CREATE VIRTUAL TABLE todos_fts USING fts5(id UNINDEXED, title, body)`);
db.exec(`CREATE TABLE todos (id INTEGER PRIMARY KEY, title TEXT, body TEXT, done INTEGER DEFAULT 0)`);

// Triggers to keep FTS in sync
db.exec(`CREATE TRIGGER todos_ai AFTER INSERT ON todos BEGIN INSERT INTO todos_fts (id, title, body) VALUES (new.id, new.title, new.body); END`);
db.exec(`CREATE TRIGGER todos_ad AFTER DELETE ON todos BEGIN DELETE FROM todos_fts WHERE id = old.id; END`);
db.exec(`CREATE TRIGGER todos_au AFTER UPDATE ON todos BEGIN UPDATE todos_fts SET title = new.title, body = new.body WHERE id = new.id; END`);

app.post('/todos', (req, res) => {
  if (!req.body.title) return res.status(422).json({ error: 'title required' });
  const r = db.prepare('INSERT INTO todos (title, body) VALUES (?, ?)').run(req.body.title, req.body.body || '');
  res.status(201).json(db.prepare('SELECT * FROM todos WHERE rowid = ?').get(r.lastInsertRowid));
});

app.get('/todos', (req, res) => {
  const items = db.prepare('SELECT * FROM todos').all();
  res.json({ count: items.length, todos: items });
});

// Search with FTS — ranked by relevance
app.get('/search', (req, res) => {
  const { q } = req.query;
  if (!q) return res.status(422).json({ error: 'q required' });
  // BM25 ranking: lower is better, so we ORDER BY rank ASC
  const results = db.prepare(`
    SELECT t.*, rank
    FROM todos_fts f
    JOIN todos t ON t.id = f.id
    WHERE todos_fts MATCH ?
    ORDER BY rank
    LIMIT 20
  `).all(q);
  res.json({ query: q, count: results.length, results });
});

app.listen(3000, () => console.log('11-todo-search on :3000'));
