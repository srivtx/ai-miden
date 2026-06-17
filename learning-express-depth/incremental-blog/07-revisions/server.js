// 07-revisions: Every save creates a revision. See history, restore old versions, diff.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`
  CREATE TABLE posts (id INTEGER PRIMARY KEY, title TEXT, body TEXT, current_revision_id INTEGER);
  CREATE TABLE revisions (id INTEGER PRIMARY KEY AUTOINCREMENT, post_id INTEGER, title TEXT, body TEXT, author_id TEXT, message TEXT, created_at TEXT DEFAULT (datetime('now')));
`);

function saveRevision(postId, title, body, authorId, message = null) {
  // Save the current state as a revision
  const r = db.prepare('INSERT INTO revisions (post_id, title, body, author_id, message) VALUES (?, ?, ?, ?, ?)').run(postId, title, body, authorId, message);
  db.prepare('UPDATE posts SET title = ?, body = ?, current_revision_id = ? WHERE id = ?').run(title, body, r.lastInsertRowid, postId);
  return r.lastInsertRowid;
}

// Create a post
app.post('/posts', (req, res) => {
  const r = db.prepare('INSERT INTO posts (title, body) VALUES (?, ?)').run(req.body.title || '', req.body.body || '');
  const id = r.lastInsertRowid;
  saveRevision(id, req.body.title || '', req.body.body || '', req.body.author_id, 'initial');
  res.status(201).json(db.prepare('SELECT * FROM posts WHERE id = ?').get(id));
});

// Update (saves a new revision)
app.patch('/posts/:id', (req, res) => {
  const id = parseInt(req.params.id);
  const post = db.prepare('SELECT * FROM posts WHERE id = ?').get(id);
  if (!post) return res.status(404).json({ error: 'not found' });
  const newTitle = req.body.title !== undefined ? req.body.title : post.title;
  const newBody = req.body.body !== undefined ? req.body.body : post.body;
  saveRevision(id, newTitle, newBody, req.body.author_id, req.body.message);
  res.json(db.prepare('SELECT * FROM posts WHERE id = ?').get(id));
});

// List all revisions
app.get('/posts/:id/revisions', (req, res) => {
  const revisions = db.prepare('SELECT id, author_id, message, created_at FROM revisions WHERE post_id = ? ORDER BY created_at DESC').all(parseInt(req.params.id));
  res.json({ count: revisions.length, revisions });
});

// Get a specific revision
app.get('/posts/:id/revisions/:revId', (req, res) => {
  const rev = db.prepare('SELECT * FROM revisions WHERE id = ? AND post_id = ?').get(parseInt(req.params.revId), parseInt(req.params.id));
  rev ? res.json(rev) : res.status(404).json({ error: 'not found' });
});

// Restore an old revision
app.post('/posts/:id/restore/:revId', (req, res) => {
  const id = parseInt(req.params.id);
  const revId = parseInt(req.params.revId);
  const rev = db.prepare('SELECT * FROM revisions WHERE id = ? AND post_id = ?').get(revId, id);
  if (!rev) return res.status(404).json({ error: 'revision not found' });
  saveRevision(id, rev.title, rev.body, req.body.author_id, `restored from revision ${revId}`);
  res.json(db.prepare('SELECT * FROM posts WHERE id = ?').get(id));
});

// Diff two revisions
app.get('/posts/:id/diff', (req, res) => {
  const { from, to } = req.query;
  if (!from || !to) return res.status(422).json({ error: 'from and to query params required' });
  const a = db.prepare('SELECT * FROM revisions WHERE id = ? AND post_id = ?').get(parseInt(from), parseInt(req.params.id));
  const b = db.prepare('SELECT * FROM revisions WHERE id = ? AND post_id = ?').get(parseInt(to), parseInt(req.params.id));
  if (!a || !b) return res.status(404).json({ error: 'revision not found' });
  res.json({
    from: { id: a.id, title: a.title, body: a.body, created_at: a.created_at },
    to: { id: b.id, title: b.title, body: b.body, created_at: b.created_at },
    titleChanged: a.title !== b.title,
    bodyChanged: a.body !== b.body,
  });
});

app.listen(3000, () => console.log('07-revisions on :3000'));
