// Forum API — Step 7. Adds: threads, replies (nested), votes, categories, moderation.
const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE users (id TEXT PRIMARY KEY, username TEXT UNIQUE, role TEXT DEFAULT 'user')`);
db.exec(`CREATE TABLE categories (id TEXT PRIMARY KEY, name TEXT, slug TEXT UNIQUE)`);
db.exec(`CREATE TABLE threads (id TEXT PRIMARY KEY, category_id TEXT, user_id TEXT, title TEXT, body TEXT, score INTEGER DEFAULT 0, pinned INTEGER DEFAULT 0, locked INTEGER DEFAULT 0, created_at TEXT DEFAULT (datetime('now')))`);
db.exec(`CREATE TABLE replies (id TEXT PRIMARY KEY, thread_id TEXT, user_id TEXT, parent_id TEXT, body TEXT, score INTEGER DEFAULT 0, created_at TEXT DEFAULT (datetime('now')))`);
db.exec(`CREATE TABLE votes (user_id TEXT, target_id TEXT, target_type TEXT, value INTEGER, PRIMARY KEY (user_id, target_id, target_type))`);
db.exec(`CREATE INDEX idx_threads_category ON threads(category_id)`);
db.exec(`CREATE INDEX idx_replies_thread ON replies(thread_id)`);

// Seed
const cats = [{ name: 'General', slug: 'general' }, { name: 'Help', slug: 'help' }];
for (const c of cats) { const id = 'c_' + crypto.randomBytes(3).toString('hex'); db.prepare('INSERT INTO categories (id, name, slug) VALUES (?, ?, ?)').run(id, c.name, c.slug); }
const user = 'u_alice'; db.prepare('INSERT INTO users (id, username) VALUES (?, ?)').run(user, 'alice');

// === Public ===
app.get('/categories', (req, res) => res.json({ categories: db.prepare('SELECT c.*, COUNT(t.id) as thread_count FROM categories c LEFT JOIN threads t ON t.category_id = c.id GROUP BY c.id').all() }));

app.get('/threads', (req, res) => {
  const { category, sort = 'recent', limit = 20 } = req.query;
  let query = `SELECT t.*, u.username, c.name as category_name FROM threads t JOIN users u ON u.id = t.user_id JOIN categories c ON c.id = t.category_id WHERE 1=1`;
  const params = [];
  if (category) { query += ' AND c.slug = ?'; params.push(category); }
  if (sort === 'top') query += ' ORDER BY t.score DESC, t.created_at DESC';
  else if (sort === 'new') query += ' ORDER BY t.created_at DESC';
  else query += ' ORDER BY t.pinned DESC, t.created_at DESC';
  query += ' LIMIT ?'; params.push(parseInt(limit));
  const threads = db.prepare(query).all(...params);
  for (const t of threads) { t.reply_count = db.prepare('SELECT COUNT(*) as c FROM replies WHERE thread_id = ?').get(t.id).c; }
  res.json({ threads });
});

app.get('/threads/:id', (req, res) => {
  const thread = db.prepare('SELECT t.*, u.username, c.name as category_name FROM threads t JOIN users u ON u.id = t.user_id JOIN categories c ON c.id = t.category_id WHERE t.id = ?').get(req.params.id);
  if (!thread) return res.status(404).json({ error: 'not_found' });
  thread.replies = db.prepare('SELECT r.*, u.username FROM replies r JOIN users u ON u.id = r.user_id WHERE r.thread_id = ? ORDER BY r.created_at ASC').all(thread.id);
  res.json(thread);
});

app.post('/threads', (req, res) => {
  if (!req.userId) return res.status(401).json({ error: 'auth_required' });
  const { category_id, title, body } = req.body;
  if (!category_id || !title) return res.status(422).json({ error: 'missing_fields' });
  const id = 't_' + crypto.randomBytes(4).toString('hex');
  db.prepare('INSERT INTO threads (id, category_id, user_id, title, body) VALUES (?, ?, ?, ?, ?)').run(id, category_id, req.userId, title, body || '');
  res.status(201).json(db.prepare('SELECT * FROM threads WHERE id = ?').get(id));
});

app.post('/threads/:id/replies', (req, res) => {
  if (!req.userId) return res.status(401).json({ error: 'auth_required' });
  const { body, parent_id } = req.body;
  if (!body) return res.status(422).json({ error: 'missing_body' });
  const id = 'r_' + crypto.randomBytes(4).toString('hex');
  db.prepare('INSERT INTO replies (id, thread_id, user_id, parent_id, body) VALUES (?, ?, ?, ?, ?)').run(id, req.params.id, req.userId, parent_id || null, body);
  res.status(201).json(db.prepare('SELECT * FROM replies WHERE id = ?').get(id));
});

app.post('/vote', (req, res) => {
  if (!req.userId) return res.status(401).json({ error: 'auth_required' });
  const { target_id, target_type, value } = req.body;
  if (!['thread', 'reply'].includes(target_type) || ![1, -1, 0].includes(value)) return res.status(422).json({ error: 'invalid_vote' });
  if (value === 0) db.prepare('DELETE FROM votes WHERE user_id = ? AND target_id = ? AND target_type = ?').run(req.userId, target_id, target_type);
  else db.prepare('INSERT OR REPLACE INTO votes (user_id, target_id, target_type, value) VALUES (?, ?, ?, ?)').run(req.userId, target_id, target_type, value);
  // Recalculate score
  const score = db.prepare('SELECT COALESCE(SUM(value), 0) as s FROM votes WHERE target_id = ? AND target_type = ?').get(target_id, target_type).s;
  if (target_type === 'thread') db.prepare('UPDATE threads SET score = ? WHERE id = ?').run(score, target_id);
  else db.prepare('UPDATE replies SET score = ? WHERE id = ?').run(score, target_id);
  res.json({ target_id, score });
});

app.use((req, res, next) => { req.userId = req.headers['x-user-id']; next(); });

app.listen(3000, () => console.log('Forum API :3000 — X-User-Id header for auth'));
module.exports = app;
