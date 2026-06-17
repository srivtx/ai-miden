// Blog API — Step 3. Adds: users, posts, comments, slugs, published/draft.
const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE users (id TEXT PRIMARY KEY, username TEXT UNIQUE, email TEXT, bio TEXT)`);
db.exec(`CREATE TABLE posts (id TEXT PRIMARY KEY, user_id TEXT, title TEXT, slug TEXT UNIQUE, body TEXT, published INTEGER DEFAULT 0, created_at TEXT DEFAULT (datetime('now')), updated_at TEXT DEFAULT (datetime('now')))`);
db.exec(`CREATE TABLE comments (id TEXT PRIMARY KEY, post_id TEXT, user_id TEXT, body TEXT, created_at TEXT DEFAULT (datetime('now')))`);
db.exec(`CREATE INDEX idx_posts_user ON posts(user_id)`);
db.exec(`CREATE INDEX idx_posts_slug ON posts(slug)`);
db.exec(`CREATE INDEX idx_comments_post ON comments(post_id)`);

function slugify(text) {
  return text.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 100) || 'post-' + Date.now();
}

function getPost(id) {
  const post = db.prepare('SELECT p.*, u.username, u.bio FROM posts p JOIN users u ON u.id = p.user_id WHERE p.id = ?').get(id);
  if (post) post.comment_count = db.prepare('SELECT COUNT(*) as c FROM comments WHERE post_id = ?').get(id).c;
  return post;
}

// === Public routes (only published) ===
app.get('/posts', (req, res) => {
  const { user, q, limit = 20 } = req.query;
  let query = `SELECT p.id, p.title, p.slug, p.body, p.created_at, u.username FROM posts p JOIN users u ON u.id = p.user_id WHERE p.published = 1`;
  const params = [];
  if (user) { query += ' AND u.username = ?'; params.push(user); }
  if (q) { query += ' AND (p.title LIKE ? OR p.body LIKE ?)'; params.push('%' + q + '%', '%' + q + '%'); }
  query += ' ORDER BY p.created_at DESC LIMIT ?';
  params.push(parseInt(limit));
  res.json({ posts: db.prepare(query).all(...params) });
});

app.get('/posts/:slug', (req, res) => {
  const post = db.prepare('SELECT p.*, u.username, u.bio FROM posts p JOIN users u ON u.id = p.user_id WHERE p.slug = ? AND p.published = 1').get(req.params.slug);
  if (!post) return res.status(404).json({ error: 'not_found' });
  post.comments = db.prepare('SELECT c.*, u.username FROM comments c JOIN users u ON u.id = c.user_id WHERE c.post_id = ? ORDER BY c.created_at ASC').all(post.id);
  res.json(post);
});

app.get('/users/:username', (req, res) => {
  const user = db.prepare('SELECT id, username, bio FROM users WHERE username = ?').get(req.params.username);
  if (!user) return res.status(404).json({ error: 'not_found' });
  user.posts = db.prepare('SELECT id, title, slug, created_at FROM posts WHERE user_id = ? AND published = 1 ORDER BY created_at DESC').all(user.id);
  res.json(user);
});

// === Auth (simple — just a header for demo) ===
app.use((req, res, next) => { req.userId = req.headers['x-user-id']; next(); });
function requireUser(req, res, next) { if (!req.userId) return res.status(401).json({ error: 'auth_required', hint: 'X-User-Id header' }); next(); }

// === Create user (no auth needed for first user) ===
app.post('/users', (req, res) => {
  if (!req.body.username || !req.body.email) return res.status(422).json({ error: 'missing_fields' });
  const id = 'u_' + crypto.randomBytes(4).toString('hex');
  try { db.prepare('INSERT INTO users (id, username, email, bio) VALUES (?, ?, ?, ?)').run(id, req.body.username, req.body.email, req.body.bio || ''); res.status(201).json({ id, username: req.body.username }); }
  catch (e) { res.status(409).json({ error: 'username_taken' }); }
});

// === Author routes ===
app.post('/posts', requireUser, (req, res) => {
  if (!req.body.title) return res.status(422).json({ error: 'missing_title' });
  const id = 'p_' + crypto.randomBytes(4).toString('hex');
  const slug = req.body.slug || slugify(req.body.title);
  const published = req.body.published ? 1 : 0;
  db.prepare('INSERT INTO posts (id, user_id, title, slug, body, published) VALUES (?, ?, ?, ?, ?, ?)').run(id, req.userId, req.body.title, slug, req.body.body || '', published);
  res.status(201).json(getPost(id));
});

app.patch('/posts/:id', requireUser, (req, res) => {
  const post = getPost(req.params.id);
  if (!post) return res.status(404).json({ error: 'not_found' });
  if (post.user_id !== req.userId) return res.status(403).json({ error: 'forbidden' });
  const updates = [];
  const params = [];
  for (const f of ['title', 'body']) if (req.body[f] !== undefined) { updates.push(`${f} = ?`); params.push(req.body[f]); }
  if (req.body.published !== undefined) { updates.push('published = ?'); params.push(req.body.published ? 1 : 0); }
  if (updates.length) {
    updates.push("updated_at = datetime('now')");
    params.push(req.params.id);
    db.prepare(`UPDATE posts SET ${updates.join(', ')} WHERE id = ?`).run(...params);
  }
  res.json(getPost(req.params.id));
});

app.delete('/posts/:id', requireUser, (req, res) => {
  const post = getPost(req.params.id);
  if (!post) return res.status(404).json({ error: 'not_found' });
  if (post.user_id !== req.userId) return res.status(403).json({ error: 'forbidden' });
  db.prepare('DELETE FROM comments WHERE post_id = ?').run(req.params.id);
  db.prepare('DELETE FROM posts WHERE id = ?').run(req.params.id);
  res.status(204).end();
});

app.post('/posts/:id/comments', requireUser, (req, res) => {
  if (!req.body.body) return res.status(422).json({ error: 'missing_body' });
  const post = db.prepare('SELECT id FROM posts WHERE id = ? AND published = 1').get(req.params.id);
  if (!post) return res.status(404).json({ error: 'post_not_found' });
  const id = 'c_' + crypto.randomBytes(4).toString('hex');
  db.prepare('INSERT INTO comments (id, post_id, user_id, body) VALUES (?, ?, ?, ?)').run(id, req.params.id, req.userId, req.body.body);
  res.status(201).json(db.prepare('SELECT c.*, u.username FROM comments c JOIN users u ON u.id = c.user_id WHERE c.id = ?').get(id));
});

app.listen(3000, () => console.log('Blog API :3000 — X-User-Id header for auth'));
module.exports = app;
