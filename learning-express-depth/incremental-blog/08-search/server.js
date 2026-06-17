// 08-search: Full-text search using FTS5. Ranked by relevance.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE VIRTUAL TABLE posts_fts USING fts5(id UNINDEXED, title, body, tags)`);
db.exec(`CREATE TABLE posts (id INTEGER PRIMARY KEY, slug TEXT UNIQUE, title TEXT, body TEXT, excerpt TEXT, status TEXT, tags TEXT, author_id TEXT, created_at TEXT DEFAULT (datetime('now')))`);
db.exec(`CREATE TRIGGER posts_ai AFTER INSERT ON posts BEGIN INSERT INTO posts_fts (id, title, body, tags) VALUES (new.id, new.title, new.body, new.tags); END`);
db.exec(`CREATE TRIGGER posts_au AFTER UPDATE ON posts BEGIN UPDATE posts_fts SET title = new.title, body = new.body, tags = new.tags WHERE id = new.id; END`);
db.exec(`CREATE TRIGGER posts_ad AFTER DELETE ON posts BEGIN DELETE FROM posts_fts WHERE id = old.id; END`);

// Create a post (only published are indexed for search)
app.post('/posts', (req, res) => {
  if (!req.body.title) return res.status(422).json({ error: 'title required' });
  const slug = req.body.title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
  const r = db.prepare('INSERT INTO posts (slug, title, body, excerpt, status, tags, author_id) VALUES (?, ?, ?, ?, ?, ?, ?)').run(slug, req.body.title, req.body.body || '', req.body.excerpt || '', req.body.status || 'draft', req.body.tags || '', req.body.author_id);
  res.status(201).json(db.prepare('SELECT * FROM posts WHERE id = ?').get(r.lastInsertRowid));
});

// Search
app.get('/search', (req, res) => {
  const { q, status = 'published' } = req.query;
  if (!q) return res.status(422).json({ error: 'q required' });
  // Combine FTS search with status filter
  const results = db.prepare(`
    SELECT p.*, rank
    FROM posts_fts f
    JOIN posts p ON p.id = f.id
    WHERE posts_fts MATCH ? AND p.status = ?
    ORDER BY rank
    LIMIT 20
  `).all(q, status);
  res.json({ query: q, count: results.length, results });
});

// Suggestions (autocomplete)
app.get('/suggest', (req, res) => {
  const { q } = req.query;
  if (!q || q.length < 2) return res.json({ suggestions: [] });
  const suggestions = db.prepare(`
    SELECT DISTINCT title FROM posts_fts
    WHERE posts_fts MATCH ?
    LIMIT 5
  `).all(q + '*');
  res.json({ suggestions: suggestions.map(s => s.title) });
});

app.listen(3000, () => console.log('08-search on :3000'));
