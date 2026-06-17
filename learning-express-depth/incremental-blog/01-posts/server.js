// 01-posts: Blog posts with slugs, public/private, basic CRUD.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE posts (id INTEGER PRIMARY KEY AUTOINCREMENT, slug TEXT UNIQUE NOT NULL, title TEXT NOT NULL, body TEXT, excerpt TEXT, status TEXT DEFAULT 'draft', author TEXT, tags TEXT, created_at TEXT DEFAULT (datetime('now')), updated_at TEXT DEFAULT (datetime('now')), published_at TEXT)`);

function slugify(text) {
  return text.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 100) || 'post-' + Date.now();
}

const insert = db.prepare('INSERT INTO posts (slug, title, body, excerpt, status, author, tags) VALUES (?, ?, ?, ?, ?, ?, ?)');
const update = db.prepare('UPDATE posts SET title = ?, body = ?, excerpt = ?, status = ?, tags = ?, updated_at = datetime("now"), published_at = CASE WHEN ? = "published" AND published_at IS NULL THEN datetime("now") ELSE published_at END WHERE id = ?');
const selectAll = db.prepare('SELECT * FROM posts');
const selectByStatus = db.prepare('SELECT * FROM posts WHERE status = ?');

// List posts (filter by status; default: only published)
app.get('/posts', (req, res) => {
  const status = req.query.status || 'published';
  const tag = req.query.tag;
  let posts = selectByStatus.all(status);
  if (tag) posts = posts.filter(p => p.tags && p.tags.split(',').includes(tag));
  // Strip body for list (just excerpt)
  const items = posts.map(p => ({ id: p.id, slug: p.slug, title: p.title, excerpt: p.excerpt, status: p.status, author: p.author, tags: p.tags, published_at: p.published_at }));
  res.json({ count: items.length, posts: items });
});

app.get('/posts/:slug', (req, res) => {
  const post = db.prepare('SELECT * FROM posts WHERE slug = ?').get(req.params.slug);
  if (!post) return res.status(404).json({ error: 'not found' });
  if (post.status !== 'published') return res.status(404).json({ error: 'not found' });
  res.json(post);
});

app.post('/posts', (req, res) => {
  const { title, body, excerpt, status, author, tags } = req.body;
  if (!title) return res.status(422).json({ error: 'title required' });
  const slug = req.body.slug || slugify(title);
  try {
    const r = insert.run(slug, title, body || '', excerpt || '', status || 'draft', author || 'Anonymous', tags || '');
    res.status(201).json(db.prepare('SELECT * FROM posts WHERE id = ?').get(r.lastInsertRowid));
  } catch (e) { res.status(409).json({ error: 'slug taken' }); }
});

app.patch('/posts/:id', (req, res) => {
  const post = db.prepare('SELECT * FROM posts WHERE id = ?').get(parseInt(req.params.id));
  if (!post) return res.status(404).json({ error: 'not found' });
  update.run(
    req.body.title !== undefined ? req.body.title : post.title,
    req.body.body !== undefined ? req.body.body : post.body,
    req.body.excerpt !== undefined ? req.body.excerpt : post.excerpt,
    req.body.status !== undefined ? req.body.status : post.status,
    req.body.tags !== undefined ? req.body.tags : post.tags,
    req.body.status || post.status,
    post.id
  );
  res.json(db.prepare('SELECT * FROM posts WHERE id = ?').get(post.id));
});

app.delete('/posts/:id', (req, res) => {
  const r = db.prepare('DELETE FROM posts WHERE id = ?').run(parseInt(req.params.id));
  r.changes ? res.status(204).end() : res.status(404).json({ error: 'not found' });
});

app.listen(3000, () => console.log('01-posts on :3000'));
