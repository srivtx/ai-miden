// Wiki / Knowledge Base — Pages, version history, search, collaboration.
const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const app = express();
app.use(express.json());
const SECRET = 'dev-secret';

const users = []; const pages = []; const versions = []; const collaborations = []; let pId = 1, vId = 1, cId = 1;
function auth(req, res, next) { try { req.user = jwt.verify((req.headers.authorization || '').split(' ')[1], SECRET); next(); } catch { res.status(401).json({ error: 'Auth required' }); } }

app.post('/auth/register', async (req, res) => {
  const { name, email, password } = req.body;
  if (!email || !password) return res.status(400).json({ error: 'email, password required' });
  if (users.find(u => u.email === email)) return res.status(409).json({ error: 'Email exists' });
  users.push({ id: users.length + 1, name, email, password: await bcrypt.hash(password, 10) });
  res.status(201).json({ token: jwt.sign({ id: users.length }, SECRET, { expiresIn: '24h' }) });
});
app.post('/auth/login', async (req, res) => {
  const user = users.find(u => u.email === req.body.email);
  if (!user || !(await bcrypt.compare(req.body.password, user.password))) return res.status(401).json({ error: 'Invalid' });
  res.json({ token: jwt.sign({ id: user.id }, SECRET, { expiresIn: '24h' }) });
});

// Pages
app.post('/pages', auth, (req, res) => {
  const { title, slug, content, tags, isPublic, collaborators } = req.body;
  if (!title) return res.status(400).json({ error: 'title required' });
  const pageSlug = slug || title.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');
  if (pages.find(p => p.slug === pageSlug)) return res.status(409).json({ error: 'slug exists' });
  const p = { id: pId++, slug: pageSlug, title, content: content || '', tags: tags || [], isPublic: !!isPublic, collaborators: collaborators || [req.user.id], viewCount: 0, version: 1, authorId: req.user.id, createdAt: new Date().toISOString(), updatedAt: new Date().toISOString() };
  pages.push(p);
  // Save initial version
  versions.push({ id: vId++, pageId: p.id, content: p.content, editorId: req.user.id, version: 1, createdAt: new Date().toISOString() });
  res.status(201).json(p);
});

app.get('/pages', (req, res) => {
  let result = pages.filter(p => p.isPublic || (req.user && p.collaborators.includes(req.user?.id)));
  if (req.query.search) { const q = req.query.search.toLowerCase(); result = result.filter(p => p.title.toLowerCase().includes(q) || p.content.toLowerCase().includes(q) || p.tags.some(t => t.toLowerCase().includes(q))); }
  if (req.query.tag) result = result.filter(p => p.tags.includes(req.query.tag));
  result.sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt));
  res.json(result.map(p => ({ id: p.id, slug: p.slug, title: p.title, tags: p.tags, version: p.version, viewCount: p.viewCount, updatedAt: p.updatedAt, isPublic: p.isPublic })));
});

app.get('/pages/:idOrSlug', (req, res) => {
  const p = pages.find(p => p.id === parseInt(req.params.idOrSlug) || p.slug === req.params.idOrSlug);
  if (!p) return res.status(404).json({ error: 'Not found' });
  if (!p.isPublic && (!req.user || !p.collaborators.includes(req.user?.id))) return res.status(403).json({ error: 'Access denied' });
  p.viewCount++;
  res.json(p);
});

// Edit (creates new version)
app.put('/pages/:id', auth, (req, res) => {
  const p = pages.find(p => p.id === parseInt(req.params.id));
  if (!p) return res.status(404).json({ error: 'Not found' });
  if (!p.collaborators.includes(req.user.id)) return res.status(403).json({ error: 'Not a collaborator' });
  if (req.body.title) p.title = req.body.title;
  if (req.body.content !== undefined) {
    p.content = req.body.content;
    p.version++;
    versions.push({ id: vId++, pageId: p.id, content: p.content, editorId: req.user.id, version: p.version, createdAt: new Date().toISOString() });
  }
  if (req.body.tags) p.tags = req.body.tags;
  if (req.body.isPublic !== undefined) p.isPublic = req.body.isPublic;
  p.updatedAt = new Date().toISOString();
  res.json(p);
});

// History
app.get('/pages/:id/history', (req, res) => {
  const p = pages.find(p => p.id === parseInt(req.params.id));
  if (!p) return res.status(404).json({ error: 'Not found' });
  const history = versions.filter(v => v.pageId === p.id).map(v => ({ version: v.version, editor: users.find(u => u.id === v.editorId)?.name || 'Unknown', createdAt: v.createdAt }));
  res.json({ current: p.version, history });
});

app.get('/pages/:id/versions/:version', (req, res) => {
  const v = versions.find(v => v.pageId === parseInt(req.params.id) && v.version === parseInt(req.params.version));
  v ? res.json(v) : res.status(404).json({ error: 'Version not found' });
});

// Collaborators
app.post('/pages/:id/collaborators', auth, (req, res) => {
  const p = pages.find(p => p.id === parseInt(req.params.id));
  if (!p) return res.status(404).json({ error: 'Not found' });
  if (p.authorId !== req.user.id) return res.status(403).json({ error: 'Only author can add collaborators' });
  const userId = parseInt(req.body.userId);
  if (p.collaborators.includes(userId)) return res.status(409).json({ error: 'Already collaborator' });
  p.collaborators.push(userId);
  res.json({ collaborators: p.collaborators.map(id => users.find(u => u.id === id)?.name) });
});

app.delete('/pages/:id', auth, (req, res) => {
  const idx = pages.findIndex(p => p.id === parseInt(req.params.id));
  if (idx === -1) return res.status(404).json({ error: 'Not found' });
  if (pages[idx].authorId !== req.user.id) return res.status(403).json({ error: 'Only author can delete' });
  pages.splice(idx, 1);
  res.status(204).send();
});

app.listen(3000, () => console.log('Wiki :3000'));
module.exports = app;
