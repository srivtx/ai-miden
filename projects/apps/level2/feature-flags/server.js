// Feature Flag Service — Toggle features, target by user, percentage rollout.
const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const app = express();
app.use(express.json());
const SECRET = 'dev-secret';

const users = []; const flags = []; const overrides = []; let fId = 1, oId = 1;

function auth(req, res, next) { try { req.user = jwt.verify((req.headers.authorization || '').split(' ')[1], SECRET); next(); } catch { res.status(401).json({ error: 'Auth required' }); } }
function checkFlag(flag, userId) {
  // Check explicit override
  const override = overrides.find(o => o.flagId === flag.id && (o.userId === userId || o.userId === null));
  if (override) return override.value;
  // Check percentage rollout (hash userId to deterministic bucket)
  if (flag.percentage > 0) {
    const hash = [...String(userId)].reduce((acc, c) => acc + c.charCodeAt(0), 0);
    if ((hash % 100) < flag.percentage) return flag.enabled;
  }
  return flag.enabled;
}

app.post('/auth/register', async (req, res) => {
  const { name, email, password, role: r } = req.body;
  if (!email || !password) return res.status(400).json({ error: 'email, password required' });
  if (users.find(u => u.email === email)) return res.status(409).json({ error: 'Email exists' });
  users.push({ id: users.length + 1, name, email, password: await bcrypt.hash(password, 10), role: r === 'admin' ? 'admin' : 'user' });
  res.status(201).json({ token: jwt.sign({ id: users.length, role: r === 'admin' ? 'admin' : 'user' }, SECRET, { expiresIn: '24h' }) });
});
app.post('/auth/login', async (req, res) => {
  const user = users.find(u => u.email === req.body.email);
  if (!user || !(await bcrypt.compare(req.body.password, user.password))) return res.status(401).json({ error: 'Invalid' });
  res.json({ token: jwt.sign({ id: user.id, role: user.role }, SECRET, { expiresIn: '24h' }) });
});

// Flags
app.post('/flags', auth, (req, res) => {
  if (req.user.role !== 'admin') return res.status(403).json({ error: 'Admin only' });
  const { key, name, description, enabled, percentage, conditions } = req.body;
  if (!key || !name) return res.status(400).json({ error: 'key and name required' });
  if (flags.find(f => f.key === key)) return res.status(409).json({ error: 'Flag key exists' });
  const flag = { id: fId++, key, name, description: description || '', enabled: enabled !== false, percentage: percentage || 0, conditions: conditions || null, createdBy: req.user.id, createdAt: new Date().toISOString() };
  flags.push(flag);
  res.status(201).json(flag);
});

app.get('/flags', auth, (req, res) => res.json(flags));

app.patch('/flags/:id', auth, (req, res) => {
  if (req.user.role !== 'admin') return res.status(403).json({ error: 'Admin only' });
  const f = flags.find(f => f.id === parseInt(req.params.id));
  if (!f) return res.status(404).json({ error: 'Not found' });
  if (req.body.enabled !== undefined) f.enabled = req.body.enabled;
  if (req.body.percentage !== undefined) f.percentage = req.body.percentage;
  if (req.body.description) f.description = req.body.description;
  f.updatedAt = new Date().toISOString();
  res.json(f);
});

app.delete('/flags/:id', auth, (req, res) => {
  if (req.user.role !== 'admin') return res.status(403).json({ error: 'Admin only' });
  const idx = flags.findIndex(f => f.id === parseInt(req.params.id));
  if (idx === -1) return res.status(404).json({ error: 'Not found' });
  flags.splice(idx, 1);
  res.status(204).send();
});

// Overrides (force ON/OFF for specific users)
app.post('/flags/:id/overrides', auth, (req, res) => {
  if (req.user.role !== 'admin') return res.status(403).json({ error: 'Admin only' });
  const f = flags.find(f => f.id === parseInt(req.params.id));
  if (!f) return res.status(404).json({ error: 'Not found' });
  const { userId, value } = req.body;
  if (!userId || typeof value !== 'boolean') return res.status(400).json({ error: 'userId and boolean value required' });
  const existing = overrides.find(o => o.flagId === f.id && o.userId === parseInt(userId));
  if (existing) { existing.value = value; return res.json(existing); }
  const o = { id: oId++, flagId: f.id, userId: parseInt(userId), value, createdBy: req.user.id, createdAt: new Date().toISOString() };
  overrides.push(o);
  res.status(201).json(o);
});

// EVALUATE (this is what your app calls to check a flag)
app.get('/flags/:key/evaluate', auth, (req, res) => {
  const f = flags.find(f => f.key === req.params.key);
  if (!f) return res.status(404).json({ error: 'Flag not found' });
  const value = checkFlag(f, req.user.id);
  res.json({ key: f.key, value, reason: 'override' + (overrides.find(o => o.flagId === f.id && o.userId === req.user.id) ? '_user' : '') || (f.percentage > 0 ? 'rollout' : 'default') });
});

// Bulk evaluate (avoid round trips)
app.post('/flags/evaluate', auth, (req, res) => {
  const { keys } = req.body;
  if (!Array.isArray(keys)) return res.status(400).json({ error: 'keys[] required' });
  const result = {};
  keys.forEach(key => { const f = flags.find(f => f.key === key); result[key] = f ? checkFlag(f, req.user.id) : false; });
  res.json(result);
});

app.listen(3000, () => console.log('Feature Flags :3000'));
module.exports = app;
