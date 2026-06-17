// Forum / Discussion Board — Categories, threads, replies, likes, views.
const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const app = express();
app.use(express.json());
const SECRET = 'dev-secret';

const users = []; const categories = []; const threads = []; const replies = []; const likes = new Set();
let cId = 1, tId = 1, rId = 1;
function auth(req, res, next) { try { req.user = jwt.verify((req.headers.authorization || '').split(' ')[1], SECRET); next(); } catch { res.status(401).json({ error: 'Auth required' }); } }

app.post('/auth/register', async (req, res) => {
  const { name, email, password } = req.body;
  if (!email || !password) return res.status(400).json({ error: 'email, password required' });
  if (users.find(u => u.email === email)) return res.status(409).json({ error: 'Email exists' });
  users.push({ id: users.length + 1, name, email, password: await bcrypt.hash(password, 10), postCount: 0, reputation: 0 });
  res.status(201).json({ token: jwt.sign({ id: users.length }, SECRET, { expiresIn: '24h' }) });
});
app.post('/auth/login', async (req, res) => {
  const user = users.find(u => u.email === req.body.email);
  if (!user || !(await bcrypt.compare(req.body.password, user.password))) return res.status(401).json({ error: 'Invalid' });
  res.json({ token: jwt.sign({ id: user.id }, SECRET, { expiresIn: '24h' }) });
});

// Categories
app.post('/categories', auth, (req, res) => {
  const { name, description, color } = req.body;
  if (!name) return res.status(400).json({ error: 'name required' });
  const c = { id: cId++, slug: name.toLowerCase().replace(/\s+/g, '-'), name, description: description || '', color: color || '#3b82f6', threadCount: 0, createdAt: new Date().toISOString() };
  categories.push(c);
  res.status(201).json(c);
});

app.get('/categories', (req, res) => res.json(categories));

// Threads
app.post('/categories/:slug/threads', auth, (req, res) => {
  const cat = categories.find(c => c.slug === req.params.slug);
  if (!cat) return res.status(404).json({ error: 'Category not found' });
  const { title, content, tags } = req.body;
  if (!title || !content) return res.status(400).json({ error: 'title and content required' });
  const t = { id: tId++, categoryId: cat.id, authorId: req.user.id, title, content, tags: tags || [], pinned: false, locked: false, viewCount: 0, likeCount: 0, replyCount: 0, lastReplyAt: new Date().toISOString(), createdAt: new Date().toISOString() };
  threads.push(t);
  cat.threadCount++;
  const u = users.find(u => u.id === req.user.id); u.postCount++; u.reputation += 5;
  res.status(201).json(t);
});

app.get('/categories/:slug/threads', (req, res) => {
  const cat = categories.find(c => c.slug === req.params.slug);
  if (!cat) return res.status(404).json({ error: 'Not found' });
  let result = threads.filter(t => t.categoryId === cat.id);
  if (req.query.search) { const q = req.query.search.toLowerCase(); result = result.filter(t => t.title.toLowerCase().includes(q) || t.content.toLowerCase().includes(q) || t.tags.some(tag => tag.toLowerCase().includes(q))); }
  if (req.query.tag) result = result.filter(t => t.tags.includes(req.query.tag));
  if (req.query.sort === 'popular') result.sort((a, b) => b.likeCount + b.replyCount - (a.likeCount + a.replyCount));
  else if (req.query.sort === 'views') result.sort((a, b) => b.viewCount - a.viewCount);
  else result.sort((a, b) => new Date(b.lastReplyAt) - new Date(a.lastReplyAt));
  // Pinned first
  result.sort((a, b) => (b.pinned ? 1 : 0) - (a.pinned ? 1 : 0));
  res.json(result.map(t => ({ ...t, author: users.find(u => u.id === t.authorId)?.name })));
});

app.get('/threads/:id', (req, res) => {
  const t = threads.find(t => t.id === parseInt(req.params.id));
  if (!t) return res.status(404).json({ error: 'Not found' });
  t.viewCount++;
  res.json({ ...t, author: users.find(u => u.id === t.authorId)?.name, replies: replies.filter(r => r.threadId === t.id).map(r => ({ ...r, author: users.find(u => u.id === r.authorId)?.name })) });
});

app.post('/threads/:id/replies', auth, (req, res) => {
  const t = threads.find(t => t.id === parseInt(req.params.id));
  if (!t) return res.status(404).json({ error: 'Not found' });
  if (t.locked) return res.status(403).json({ error: 'Thread is locked' });
  if (!req.body.content) return res.status(400).json({ error: 'content required' });
  const r = { id: rId++, threadId: t.id, authorId: req.user.id, content: req.body.content, parentReplyId: req.body.parentReplyId || null, likeCount: 0, createdAt: new Date().toISOString() };
  replies.push(r);
  t.replyCount++; t.lastReplyAt = r.createdAt;
  res.status(201).json(r);
});

app.post('/threads/:id/like', auth, (req, res) => {
  const t = threads.find(t => t.id === parseInt(req.params.id));
  if (!t) return res.status(404).json({ error: 'Not found' });
  const key = `thread_${t.id}_${req.user.id}`;
  if (likes.has(key)) { likes.delete(key); t.likeCount--; return res.json({ liked: false }); }
  likes.add(key); t.likeCount++;
  res.json({ liked: true });
});

app.listen(3000, () => console.log('Forum :3000'));
module.exports = app;
