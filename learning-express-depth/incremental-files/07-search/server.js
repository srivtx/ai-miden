// 07-search: Full-text search on filenames and content. SQLite FTS5.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE files (id TEXT PRIMARY KEY, name TEXT, content TEXT, mime_type TEXT, owner_id TEXT, deleted_at TEXT)`);
db.exec(`CREATE VIRTUAL TABLE files_fts USING fts5(id UNINDEXED, name, content)`);
db.exec(`CREATE TRIGGER files_ai AFTER INSERT ON files BEGIN INSERT INTO files_fts (id, name, content) VALUES (new.id, new.name, new.content); END`);
db.exec(`CREATE TRIGGER files_au AFTER UPDATE ON files BEGIN UPDATE files_fts SET name = new.name, content = new.content WHERE id = new.id; END`);
db.exec(`CREATE TRIGGER files_ad AFTER DELETE ON files BEGIN DELETE FROM files_fts WHERE id = old.id; END`);

app.post('/files', (req, res) => {
  const { name, content, mime_type, owner_id } = req.body;
  if (!name) return res.status(422).json({ error: 'name required' });
  const id = 'f_' + Math.random().toString(36).slice(2, 10);
  db.prepare('INSERT INTO files VALUES (?, ?, ?, ?, ?, NULL)').run(id, name, content || '', mime_type, owner_id);
  res.status(201).json({ id });
});

app.get('/search', (req, res) => {
  const { q } = req.query;
  if (!q) return res.status(422).json({ error: 'q required' });
  const results = db.prepare(`
    SELECT f.id, f.name, f.mime_type, f.owner_id, rank
    FROM files_fts fts JOIN files f ON f.id = fts.id
    WHERE files_fts MATCH ? AND f.deleted_at IS NULL
    ORDER BY rank LIMIT 20
  `).all(q);
  res.json({ query: q, count: results.length, results });
});

app.get('/suggest', (req, res) => {
  const { q } = req.query;
  if (!q || q.length < 2) return res.json({ suggestions: [] });
  const suggestions = db.prepare(`SELECT DISTINCT name FROM files_fts WHERE files_fts MATCH ? LIMIT 5`).all(q + '*');
  res.json({ suggestions: suggestions.map(s => s.name) });
});

app.listen(3000, () => console.log('07-search on :3000'));
