// 10-newsletter: Subscribe by email. When a post is published, send to all subscribers.
const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`
  CREATE TABLE subscribers (id TEXT PRIMARY KEY, email TEXT UNIQUE, status TEXT DEFAULT 'pending', confirm_token TEXT, created_at TEXT DEFAULT (datetime('now')));
  CREATE TABLE posts (id INTEGER PRIMARY KEY, slug TEXT, title TEXT, body TEXT, excerpt TEXT, status TEXT, published_at TEXT);
  CREATE TABLE newsletters (id INTEGER PRIMARY KEY AUTOINCREMENT, post_id INTEGER, sent_at TEXT DEFAULT (datetime('now')), recipient_count INTEGER);
  CREATE TABLE newsletter_sends (id INTEGER PRIMARY KEY AUTOINCREMENT, newsletter_id INTEGER, subscriber_id TEXT, status TEXT);
`);

// Subscribe
app.post('/newsletter/subscribe', (req, res) => {
  const { email } = req.body;
  if (!email || !email.includes('@')) return res.status(422).json({ error: 'valid email required' });
  const id = 'sub_' + crypto.randomBytes(4).toString('hex');
  const token = crypto.randomBytes(16).toString('hex');
  try {
    db.prepare('INSERT INTO subscribers (id, email, confirm_token) VALUES (?, ?, ?)').run(id, email.toLowerCase(), token);
    // In real apps: send confirmation email with link
    res.status(201).json({ id, email, status: 'pending', confirm_url: `/newsletter/confirm?token=${token}` });
  } catch { res.status(409).json({ error: 'already subscribed' }); }
});

// Confirm
app.get('/newsletter/confirm', (req, res) => {
  const { token } = req.query;
  if (!token) return res.status(422).json({ error: 'token required' });
  const r = db.prepare("UPDATE subscribers SET status = 'active', confirm_token = NULL WHERE confirm_token = ?").run(token);
  r.changes ? res.json({ confirmed: true }) : res.status(404).json({ error: 'invalid token' });
});

// Unsubscribe
app.post('/newsletter/unsubscribe', (req, res) => {
  const { email } = req.body;
  const r = db.prepare('DELETE FROM subscribers WHERE email = ?').run(email.toLowerCase());
  r.changes ? res.json({ unsubscribed: true }) : res.status(404).json({ error: 'not found' });
});

// Publish a post — this should trigger sending
function sendNewsletter(post) {
  const subscribers = db.prepare("SELECT * FROM subscribers WHERE status = 'active'").all();
  // In real apps: send actual emails via SES, SendGrid, etc.
  const newsletterId = db.prepare('INSERT INTO newsletters (post_id, recipient_count) VALUES (?, ?)').run(post.id, subscribers.length).lastInsertRowid;
  for (const sub of subscribers) {
    db.prepare('INSERT INTO newsletter_sends (newsletter_id, subscriber_id, status) VALUES (?, ?, ?)').run(newsletterId, sub.id, 'sent');
    console.log(`[email] To ${sub.email}: New post: ${post.title}`);
  }
  return newsletterId;
}

app.post('/posts', (req, res) => {
  if (!req.body.title) return res.status(422).json({ error: 'title required' });
  const slug = req.body.title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
  const r = db.prepare("INSERT INTO posts (slug, title, body, excerpt, status, published_at) VALUES (?, ?, ?, ?, ?, ?)").run(slug, req.body.title, req.body.body || '', req.body.excerpt || '', req.body.status || 'draft', req.body.published_at);
  const post = db.prepare('SELECT * FROM posts WHERE id = ?').get(r.lastInsertRowid);
  if (post.status === 'published') sendNewsletter(post);
  res.status(201).json(post);
});

app.patch('/posts/:id/publish', (req, res) => {
  const id = parseInt(req.params.id);
  db.prepare("UPDATE posts SET status = 'published', published_at = datetime('now') WHERE id = ?").run(id);
  const post = db.prepare('SELECT * FROM posts WHERE id = ?').get(id);
  const nlId = sendNewsletter(post);
  res.json({ id, status: 'published', newsletter_id: nlId });
});

app.get('/admin/newsletters', (req, res) => {
  const newsletters = db.prepare('SELECT * FROM newsletters ORDER BY id DESC LIMIT 20').all();
  res.json({ newsletters });
});

app.listen(3000, () => console.log('10-newsletter on :3000'));
