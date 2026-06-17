// 02-comments: Threaded comments. Top-level and nested replies. Moderation (approved/hidden).
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`
  CREATE TABLE posts (id INTEGER PRIMARY KEY, slug TEXT, title TEXT, body TEXT, status TEXT);
  CREATE TABLE comments (id INTEGER PRIMARY KEY AUTOINCREMENT, post_id INTEGER, parent_id INTEGER, author TEXT, body TEXT, status TEXT DEFAULT 'pending', created_at TEXT DEFAULT (datetime('now')));
  CREATE INDEX idx_comments_post ON comments(post_id, created_at);
`);

db.prepare('INSERT INTO posts VALUES (1, ?, ?, ?, ?)').run('hello', 'Hello', 'First post', 'published');

// List comments for a post (threaded)
app.get('/posts/:slug/comments', (req, res) => {
  const post = db.prepare('SELECT * FROM posts WHERE slug = ?').get(req.params.slug);
  if (!post) return res.status(404).json({ error: 'post not found' });
  const all = db.prepare("SELECT * FROM comments WHERE post_id = ? AND status = 'approved' ORDER BY created_at ASC").all(post.id);
  // Build a tree
  const byId = new Map();
  const roots = [];
  for (const c of all) byId.set(c.id, { ...c, replies: [] });
  for (const c of all) {
    if (c.parent_id && byId.has(c.parent_id)) byId.get(c.parent_id).replies.push(byId.get(c.id));
    else roots.push(byId.get(c.id));
  }
  res.json({ count: all.length, comments: roots });
});

// Add a comment (top-level or reply)
app.post('/posts/:slug/comments', (req, res) => {
  const post = db.prepare('SELECT * FROM posts WHERE slug = ?').get(req.params.slug);
  if (!post) return res.status(404).json({ error: 'post not found' });
  const { author, body, parent_id } = req.body;
  if (!author || !body) return res.status(422).json({ error: 'author and body required' });
  if (parent_id) {
    const parent = db.prepare('SELECT * FROM comments WHERE id = ? AND post_id = ?').get(parent_id, post.id);
    if (!parent) return res.status(422).json({ error: 'parent comment not found' });
  }
  const r = db.prepare('INSERT INTO comments (post_id, parent_id, author, body, status) VALUES (?, ?, ?, ?, ?)').run(post.id, parent_id || null, author, body, 'pending');
  res.status(201).json({ id: r.lastInsertRowid, status: 'pending', note: 'awaiting moderation' });
});

// Moderate (approve or hide)
app.patch('/comments/:id', (req, res) => {
  if (req.headers['x-role'] !== 'admin') return res.status(403).json({ error: 'admin only' });
  const { status } = req.body;
  if (!['approved', 'hidden', 'pending'].includes(status)) return res.status(422).json({ error: 'invalid status' });
  const r = db.prepare('UPDATE comments SET status = ? WHERE id = ?').run(status, parseInt(req.params.id));
  r.changes ? res.json({ id: req.params.id, status }) : res.status(404).json({ error: 'not found' });
});

app.listen(3000, () => console.log('02-comments on :3000 (use X-Role: admin to moderate)'));
