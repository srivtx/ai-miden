// Contact Book / Address Book API
const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const app = express();
app.use(express.json());
const SECRET = 'dev-secret';

const users = []; const contacts = []; let cId = 1;
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

app.post('/contacts', auth, (req, res) => {
  const { name, email, phone, company, address, notes, tags, birthday } = req.body;
  if (!name) return res.status(400).json({ error: 'name required' });
  const c = { id: cId++, userId: req.user.id, name, email: email || null, phone: phone || null, company: company || null, address: address || null, notes: notes || '', tags: tags || [], birthday: birthday || null, createdAt: new Date().toISOString(), updatedAt: new Date().toISOString() };
  contacts.push(c);
  res.status(201).json(c);
});

app.get('/contacts', auth, (req, res) => {
  let result = contacts.filter(c => c.userId === req.user.id);
  if (req.query.search) { const q = req.query.search.toLowerCase(); result = result.filter(c => c.name.toLowerCase().includes(q) || (c.email || '').toLowerCase().includes(q) || (c.company || '').toLowerCase().includes(q)); }
  if (req.query.tag) result = result.filter(c => c.tags.includes(req.query.tag));
  if (req.query.company) result = result.filter(c => c.company === req.query.company);
  if (req.query.upcoming_birthdays === 'true') {
    const now = new Date(); const monthFromNow = new Date(now.getTime() + 30 * 86400000);
    result = result.filter(c => { if (!c.birthday) return false; const bd = new Date(c.birthday); return bd.getMonth() === now.getMonth() || bd.getMonth() === monthFromNow.getMonth(); });
  }
  const sort = req.query.sort === 'name' ? 'name' : 'createdAt';
  result.sort((a, b) => a[sort].localeCompare(b[sort]));
  res.json(result);
});

app.get('/contacts/tags', auth, (req, res) => {
  const tagCount = {}; contacts.filter(c => c.userId === req.user.id).forEach(c => c.tags.forEach(t => tagCount[t] = (tagCount[t] || 0) + 1));
  res.json(Object.entries(tagCount).map(([tag, count]) => ({ tag, count })).sort((a, b) => b.count - a.count));
});

app.get('/contacts/:id', auth, (req, res) => {
  const c = contacts.find(c => c.id === parseInt(req.params.id) && c.userId === req.user.id);
  c ? res.json(c) : res.status(404).json({ error: 'Not found' });
});

app.patch('/contacts/:id', auth, (req, res) => {
  const c = contacts.find(c => c.id === parseInt(req.params.id) && c.userId === req.user.id);
  if (!c) return res.status(404).json({ error: 'Not found' });
  Object.assign(c, req.body, { updatedAt: new Date().toISOString() });
  res.json(c);
});

app.delete('/contacts/:id', auth, (req, res) => {
  const idx = contacts.findIndex(c => c.id === parseInt(req.params.id) && c.userId === req.user.id);
  if (idx === -1) return res.status(404).json({ error: 'Not found' });
  contacts.splice(idx, 1);
  res.status(204).send();
});

app.listen(3000, () => console.log('Contact Book :3000'));
module.exports = app;
