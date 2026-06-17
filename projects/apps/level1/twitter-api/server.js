// Twitter API — Step 15. Adds: follow graph, timeline, likes, retweets, mentions.
const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE users (id TEXT PRIMARY KEY, username TEXT UNIQUE, display_name TEXT, bio TEXT, created_at TEXT DEFAULT (datetime('now')))`);
db.exec(`CREATE TABLE follows (follower_id TEXT, followee_id TEXT, created_at TEXT DEFAULT (datetime('now')), PRIMARY KEY (follower_id, followee_id))`);
db.exec(`CREATE TABLE posts (id TEXT PRIMARY KEY, user_id TEXT, body TEXT, reply_to TEXT, retweet_of TEXT, created_at TEXT DEFAULT (datetime('now')))`);
db.exec(`CREATE TABLE likes (user_id TEXT, post_id TEXT, created_at TEXT DEFAULT (datetime('now')), PRIMARY KEY (user_id, post_id))`);
db.exec(`CREATE INDEX idx_posts_user ON posts(user_id, created_at)`);
db.exec(`CREATE INDEX idx_follows_follower ON follows(follower_id)`);
db.exec(`CREATE INDEX idx_follows_followee ON follows(followee_id)`);

app.get('/users/:username', (req, res) => {
  const user = db.prepare('SELECT id, username, display_name, bio, created_at FROM users WHERE username = ?').get(req.params.username);
  if (!user) return res.status(404).json({ error: 'not_found' });
  user.followers = db.prepare('SELECT COUNT(*) as c FROM follows WHERE followee_id = ?').get(user.id).c;
  user.following = db.prepare('SELECT COUNT(*) as c FROM follows WHERE follower_id = ?').get(user.id).c;
  user.posts = db.prepare('SELECT COUNT(*) as c FROM posts WHERE user_id = ?').get(user.id).c;
  res.json(user);
});

app.post('/users', (req, res) => {
  const { username, display_name, bio } = req.body;
  if (!username) return res.status(422).json({ error: 'missing_username' });
  const id = 'u_' + crypto.randomBytes(4).toString('hex');
  try { db.prepare('INSERT INTO users (id, username, display_name, bio) VALUES (?, ?, ?, ?)').run(id, username, display_name || username, bio || ''); res.status(201).json({ id, username }); }
  catch { res.status(409).json({ error: 'username_taken' }); }
});

app.post('/follow/:username', (req, res) => {
  if (!req.userId) return res.status(401).json({ error: 'auth_required' });
  const target = db.prepare('SELECT id FROM users WHERE username = ?').get(req.params.username);
  if (!target) return res.status(404).json({ error: 'user_not_found' });
  if (target.id === req.userId) return res.status(422).json({ error: 'cannot_follow_self' });
  try { db.prepare('INSERT INTO follows (follower_id, followee_id) VALUES (?, ?)').run(req.userId, target.id); res.status(201).json({ following: true }); }
  catch { res.json({ following: false, reason: 'already_following' }); }
});

app.delete('/follow/:username', (req, res) => {
  if (!req.userId) return res.status(401).json({ error: 'auth_required' });
  const target = db.prepare('SELECT id FROM users WHERE username = ?').get(req.params.username);
  if (!target) return res.status(404).json({ error: 'user_not_found' });
  db.prepare('DELETE FROM follows WHERE follower_id = ? AND followee_id = ?').run(req.userId, target.id);
  res.json({ unfollowed: true });
});

app.post('/posts', (req, res) => {
  if (!req.userId) return res.status(401).json({ error: 'auth_required' });
  if (!req.body.body || req.body.body.length > 280) return res.status(422).json({ error: 'invalid_body', max: 280 });
  const id = 'p_' + crypto.randomBytes(4).toString('hex');
  db.prepare('INSERT INTO posts (id, user_id, body, reply_to, retweet_of) VALUES (?, ?, ?, ?, ?)').run(id, req.userId, req.body.body, req.body.reply_to || null, req.body.retweet_of || null);
  res.status(201).json(db.prepare('SELECT * FROM posts WHERE id = ?').get(id));
});

app.post('/like/:postId', (req, res) => {
  if (!req.userId) return res.status(401).json({ error: 'auth_required' });
  try { db.prepare('INSERT INTO likes (user_id, post_id) VALUES (?, ?)').run(req.userId, req.params.postId); res.status(201).json({ liked: true }); }
  catch { res.json({ liked: false, reason: 'already_liked' }); }
});

// === Timeline: posts from people you follow, plus your own, newest first ===
app.get('/timeline', (req, res) => {
  if (!req.userId) return res.status(401).json({ error: 'auth_required' });
  const limit = parseInt(req.query.limit) || 20;
  const posts = db.prepare(`SELECT p.*, u.username, u.display_name, (SELECT COUNT(*) FROM likes WHERE post_id = p.id) as like_count, EXISTS(SELECT 1 FROM likes WHERE post_id = p.id AND user_id = ?) as liked_by_me FROM posts p JOIN users u ON u.id = p.user_id WHERE p.user_id IN (SELECT followee_id FROM follows WHERE follower_id = ?) OR p.user_id = ? ORDER BY p.created_at DESC LIMIT ?`).all(req.userId, req.userId, req.userId, limit);
  res.json({ count: posts.length, posts });
});

app.get('/users/:username/posts', (req, res) => {
  const user = db.prepare('SELECT id FROM users WHERE username = ?').get(req.params.username);
  if (!user) return res.status(404).json({ error: 'not_found' });
  const posts = db.prepare('SELECT p.*, (SELECT COUNT(*) FROM likes WHERE post_id = p.id) as like_count FROM posts p WHERE p.user_id = ? ORDER BY p.created_at DESC LIMIT 50').all(user.id);
  res.json({ posts });
});

app.use((req, res, next) => { req.userId = req.headers['x-user-id']; next(); });

app.listen(3000, () => console.log('Twitter API :3000 — X-User-Id header'));
module.exports = app;
