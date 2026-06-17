// Note API — User-owned notes with search, tags, pagination.
const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const app = express();
app.use(express.json());

const SECRET = 'dev-secret';
const users = []; const notes = []; let noteId = 1;

function auth(req, res, next) {
  try { req.user = jwt.verify((req.headers.authorization || '').split(' ')[1], SECRET); next(); }
  catch { res.status(401).json({ error: 'Auth required' }); }
}

// AUTH
app.post('/auth/register', async (req, res) => {
  const { name, email, password } = req.body;
  if (!email || !password) return res.status(400).json({ error: 'email and password required' });
  if (users.find(u => u.email === email)) return res.status(409).json({ error: 'Email exists' });
  const user = { id: users.length + 1, name, email, password: await bcrypt.hash(password, 10) };
  users.push(user);
  const token = jwt.sign({ id: user.id }, SECRET, { expiresIn: '1h' });
  res.status(201).json({ user: { id: user.id, name, email }, token });
});

app.post('/auth/login', async (req, res) => {
  const user = users.find(u => u.email === req.body.email);
  if (!user || !(await bcrypt.compare(req.body.password, user.password))) return res.status(401).json({ error: 'Invalid' });
  res.json({ user: { id: user.id, name: user.name, email: user.email }, token: jwt.sign({ id: user.id }, SECRET, { expiresIn: '1h' }) });
});

// NOTES
app.post('/notes', auth, (req, res) => {
  const { title, content, tags } = req.body;
  if (!title) return res.status(400).json({ error: 'title required' });
  const note = { id: noteId++, userId: req.user.id, title, content: content || '', tags: tags || [], createdAt: new Date().toISOString(), updatedAt: new Date().toISOString() };
  notes.push(note);
  res.status(201).json(note);
});

app.get('/notes', auth, (req, res) => {
  let result = notes.filter(n => n.userId === req.user.id);
  if (req.query.tag) result = result.filter(n => n.tags.includes(req.query.tag));
  if (req.query.search) {
    const q = req.query.search.toLowerCase();
    result = result.filter(n => n.title.toLowerCase().includes(q) || n.content.toLowerCase().includes(q));
  }
  result.sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt));
  const page = Math.max(1, parseInt(req.query.page) || 1); const limit = Math.min(50, parseInt(req.query.limit) || 10);
  const total = result.length;
  res.json({ total, page, pages: Math.ceil(total / limit), data: result.slice((page - 1) * limit, page * limit) });
});

app.get('/notes/:id', auth, (req, res) => {
  const note = notes.find(n => n.id === parseInt(req.params.id) && n.userId === req.user.id);
  note ? res.json(note) : res.status(404).json({ error: 'Not found' });
});

app.patch('/notes/:id', auth, (req, res) => {
  const note = notes.find(n => n.id === parseInt(req.params.id) && n.userId === req.user.id);
  if (!note) return res.status(404).json({ error: 'Not found' });
  if (req.body.title !== undefined) note.title = req.body.title;
  if (req.body.content !== undefined) note.content = req.body.content;
  if (req.body.tags !== undefined) note.tags = req.body.tags;
  note.updatedAt = new Date().toISOString();
  res.json(note);
});

app.delete('/notes/:id', auth, (req, res) => {
  const idx = notes.findIndex(n => n.id === parseInt(req.params.id) && n.userId === req.user.id);
  if (idx === -1) return res.status(404).json({ error: 'Not found' });
  notes.splice(idx, 1);
  res.status(204).send();
});

app.listen(3000, () => console.log('Note API :3000'));
module.exports = app;
