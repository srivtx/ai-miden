// 06-drafts: Auto-save as you type, schedule for later publication, draft list.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`
  CREATE TABLE posts (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, body TEXT, slug TEXT UNIQUE, status TEXT DEFAULT 'draft', scheduled_for TEXT, last_autosave_at TEXT, author_id TEXT, created_at TEXT DEFAULT (datetime('now')), published_at TEXT);
`);

// List posts by status
app.get('/posts', (req, res) => {
  const status = req.query.status;
  const authorId = req.query.author_id;
  let query = 'SELECT * FROM posts WHERE 1=1';
  const params = [];
  if (status) { query += ' AND status = ?'; params.push(status); }
  if (authorId) { query += ' AND author_id = ?'; params.push(authorId); }
  query += ' ORDER BY created_at DESC';
  res.json({ posts: db.prepare(query).all(...params) });
});

// Create a new post (always starts as draft)
app.post('/posts', (req, res) => {
  const { title, body, author_id } = req.body;
  const slug = (title || 'untitled').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') + '-' + Date.now();
  const r = db.prepare('INSERT INTO posts (title, body, slug, status, author_id) VALUES (?, ?, ?, ?, ?)').run(title || 'Untitled', body || '', slug, 'draft', author_id);
  res.status(201).json(db.prepare('SELECT * FROM posts WHERE id = ?').get(r.lastInsertRowid));
});

// Auto-save (called every few seconds by the editor)
app.patch('/posts/:id/autosave', (req, res) => {
  const id = parseInt(req.params.id);
  const post = db.prepare('SELECT * FROM posts WHERE id = ?').get(id);
  if (!post) return res.status(404).json({ error: 'not found' });
  if (post.status === 'published') return res.status(409).json({ error: 'cannot autosave published post' });
  db.prepare('UPDATE posts SET title = ?, body = ?, last_autosave_at = datetime("now") WHERE id = ?').run(
    req.body.title !== undefined ? req.body.title : post.title,
    req.body.body !== undefined ? req.body.body : post.body,
    id
  );
  res.json(db.prepare('SELECT * FROM posts WHERE id = ?').get(id));
});

// Schedule for future publication
app.post('/posts/:id/schedule', (req, res) => {
  const id = parseInt(req.params.id);
  const { scheduled_for } = req.body;
  if (!scheduled_for) return res.status(422).json({ error: 'scheduled_for required (ISO date)' });
  if (new Date(scheduled_for) < new Date()) return res.status(422).json({ error: 'scheduled_for must be in the future' });
  db.prepare("UPDATE posts SET status = 'scheduled', scheduled_for = ? WHERE id = ?").run(scheduled_for, id);
  res.json({ id, status: 'scheduled', scheduled_for });
});

// Publish now
app.post('/posts/:id/publish', (req, res) => {
  const id = parseInt(req.params.id);
  db.prepare("UPDATE posts SET status = 'published', published_at = datetime('now') WHERE id = ?").run(id);
  res.json({ id, status: 'published' });
});

// Unpublish back to draft
app.post('/posts/:id/unpublish', (req, res) => {
  const id = parseInt(req.params.id);
  db.prepare("UPDATE posts SET status = 'draft' WHERE id = ?").run(id);
  res.json({ id, status: 'draft' });
});

app.listen(3000, () => console.log('06-drafts on :3000'));
