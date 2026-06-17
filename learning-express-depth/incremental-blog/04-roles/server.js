// 04-roles: Three roles: reader, author, admin. Different permissions for each.
const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const jwt = require('jsonwebtoken');
const app = express();
app.use(express.json());

const SECRET = 'dev-secret';
const db = new Database(':memory:');
db.exec(`CREATE TABLE users (id TEXT PRIMARY KEY, email TEXT UNIQUE, password_hash TEXT, salt TEXT, role TEXT DEFAULT 'reader')`);

function auth(req, res, next) {
  const token = (req.headers.authorization || '').replace(/^Bearer\s+/i, '');
  try {
    req.user = jwt.verify(token, SECRET);
    const user = db.prepare('SELECT id, role FROM users WHERE id = ?').get(req.user.sub);
    if (user) req.user.role = user.role;
    next();
  } catch { res.status(401).json({ error: 'unauthorized' }); }
}

function requireRole(...roles) {
  return (req, res, next) => {
    if (!req.user || !roles.includes(req.user.role)) return res.status(403).json({ error: 'forbidden', requiredRoles: roles });
    next();
  };
}

// Posts
db.exec(`CREATE TABLE posts (id INTEGER PRIMARY KEY AUTOINCREMENT, slug TEXT UNIQUE, title TEXT, body TEXT, status TEXT DEFAULT 'draft', author_id TEXT)`);

app.get('/posts', (req, res) => {
  const status = req.query.status || 'published';
  const posts = db.prepare('SELECT * FROM posts WHERE status = ?').all(status);
  res.json({ posts });
});

app.post('/posts', auth, requireRole('author', 'admin'), (req, res) => {
  const { title, body } = req.body;
  if (!title) return res.status(422).json({ error: 'title required' });
  const slug = title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
  const r = db.prepare('INSERT INTO posts (slug, title, body, author_id) VALUES (?, ?, ?, ?)').run(slug, title, body || '', req.user.sub);
  res.status(201).json(db.prepare('SELECT * FROM posts WHERE id = ?').get(r.lastInsertRowid));
});

app.patch('/posts/:id', auth, (req, res) => {
  const post = db.prepare('SELECT * FROM posts WHERE id = ?').get(parseInt(req.params.id));
  if (!post) return res.status(404).json({ error: 'not found' });
  // Authors can only edit their own; admins can edit any
  if (req.user.role !== 'admin' && post.author_id !== req.user.sub) return res.status(403).json({ error: 'forbidden' });
  db.prepare('UPDATE posts SET title = ?, body = ?, status = ? WHERE id = ?').run(
    req.body.title !== undefined ? req.body.title : post.title,
    req.body.body !== undefined ? req.body.body : post.body,
    req.body.status !== undefined ? req.body.status : post.status,
    post.id
  );
  res.json(db.prepare('SELECT * FROM posts WHERE id = ?').get(post.id));
});

app.delete('/posts/:id', auth, requireRole('admin'), (req, res) => {
  const r = db.prepare('DELETE FROM posts WHERE id = ?').run(parseInt(req.params.id));
  r.changes ? res.status(204).end() : res.status(404).json({ error: 'not found' });
});

// Admin: change a user's role
app.patch('/users/:id/role', auth, requireRole('admin'), (req, res) => {
  const { role } = req.body;
  if (!['reader', 'author', 'admin'].includes(role)) return res.status(422).json({ error: 'invalid role' });
  const r = db.prepare('UPDATE users SET role = ? WHERE id = ?').run(role, req.params.id);
  r.changes ? res.json({ id: req.params.id, role }) : res.status(404).json({ error: 'not found' });
});

app.listen(3000, () => console.log('04-roles on :3000 (roles: reader, author, admin)'));
