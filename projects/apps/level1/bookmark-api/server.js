// Bookmark API — Save URLs with tags, search, filter, deduplicate.
const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const app = express();
app.use(express.json());
const SECRET = 'dev-secret';

const users = []; const bookmarks = []; let bmId = 1;

function auth(req, res, next) { try { req.user = jwt.verify((req.headers.authorization || '').split(' ')[1], SECRET); next(); } catch { res.status(401).json({ error: 'Auth required' }); } }

app.post('/auth/register', async (req, res) => {
  const { name, email, password } = req.body;
  if (!email || !password) return res.status(400).json({ error: 'email, password required' });
  if (users.find(u => u.email === email)) return res.status(409).json({ error: 'Email exists' });
  const user = { id: users.length + 1, name, email, password: await bcrypt.hash(password, 10) };
  users.push(user);
  res.status(201).json({ user: { id: user.id, name, email }, token: jwt.sign({ id: user.id }, SECRET, { expiresIn: '24h' }) });
});
app.post('/auth/login', async (req, res) => {
  const user = users.find(u => u.email === req.body.email);
  if (!user || !(await bcrypt.compare(req.body.password, user.password))) return res.status(401).json({ error: 'Invalid' });
  res.json({ token: jwt.sign({ id: user.id }, SECRET, { expiresIn: '24h' }) });
});

app.post('/bookmarks', auth, (req, res) => {
  const { url, title, tags, description } = req.body;
  if (!url || !url.startsWith('http')) return res.status(400).json({ error: 'Valid URL required (must start with http)' });
  if (!title) return res.status(400).json({ error: 'Title required' });
  if (bookmarks.find(b => b.userId === req.user.id && b.url === url)) return res.status(409).json({ error: 'URL already bookmarked' });
  const bm = { id: bmId++, userId: req.user.id, url, title, tags: tags || [], description: description || '', clickCount: 0, createdAt: new Date().toISOString() };
  bookmarks.push(bm);
  res.status(201).json(bm);
});

app.get('/bookmarks', auth, (req, res) => {
  let result = bookmarks.filter(b => b.userId === req.user.id);
  if (req.query.tag) result = result.filter(b => b.tags.includes(req.query.tag));
  if (req.query.tags) { const filterTags = req.query.tags.split(','); result = result.filter(b => filterTags.some(t => b.tags.includes(t))); }
  if (req.query.search) { const q = req.query.search.toLowerCase(); result = result.filter(b => b.title.toLowerCase().includes(q) || b.url.toLowerCase().includes(q) || b.description.toLowerCase().includes(q) || b.tags.some(t => t.includes(q))); }
  const sort = req.query.sort === 'title' ? 'title' : 'createdAt';
  const order = req.query.order === 'asc' ? 1 : -1;
  result.sort((a, b) => (a[sort] > b[sort] ? 1 : -1) * order);
  const page = Math.max(1, parseInt(req.query.page) || 1); const limit = Math.min(100, parseInt(req.query.limit) || 20);
  const total = result.length; result = result.slice((page - 1) * limit, page * limit);
  res.json({ total, page, pages: Math.ceil(total / limit), data: result });
});

app.get('/bookmarks/tags', auth, (req, res) => {
  const tagCount = {};
  bookmarks.filter(b => b.userId === req.user.id).forEach(b => b.tags.forEach(t => tagCount[t] = (tagCount[t] || 0) + 1));
  res.json(Object.entries(tagCount).map(([tag, count]) => ({ tag, count })).sort((a, b) => b.count - a.count));
});

app.get('/bookmarks/:id', auth, (req, res) => {
  const bm = bookmarks.find(b => b.id === parseInt(req.params.id) && b.userId === req.user.id);
  bm ? (bm.clickCount++, res.json(bm)) : res.status(404).json({ error: 'Not found' });
});

app.patch('/bookmarks/:id', auth, (req, res) => {
  const bm = bookmarks.find(b => b.id === parseInt(req.params.id) && b.userId === req.user.id);
  if (!bm) return res.status(404).json({ error: 'Not found' });
  if (req.body.title !== undefined) bm.title = req.body.title;
  if (req.body.url !== undefined && req.body.url.startsWith('http')) bm.url = req.body.url;
  if (req.body.tags !== undefined) bm.tags = req.body.tags;
  if (req.body.description !== undefined) bm.description = req.body.description;
  res.json(bm);
});

app.delete('/bookmarks/:id', auth, (req, res) => {
  const idx = bookmarks.findIndex(b => b.id === parseInt(req.params.id) && b.userId === req.user.id);
  if (idx === -1) return res.status(404).json({ error: 'Not found' });
  bookmarks.splice(idx, 1);
  res.status(204).send();
});

app.listen(3000, () => console.log('Bookmark API :3000'));
module.exports = app;
