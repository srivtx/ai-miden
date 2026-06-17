// Audit Log Service — Track every action, who did it, when, from where.
const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const app = express();
app.use(express.json());
const SECRET = 'dev-secret';

const users = []; const auditLogs = []; let aId = 1;
function auth(req, res, next) { try { req.user = jwt.verify((req.headers.authorization || '').split(' ')[1], SECRET); next(); } catch { res.status(401).json({ error: 'Auth required' }); } }

app.post('/auth/register', async (req, res) => {
  const { name, email, password } = req.body;
  if (!email || !password) return res.status(400).json({ error: 'email, password required' });
  if (users.find(u => u.email === email)) return res.status(409).json({ error: 'Email exists' });
  users.push({ id: users.length + 1, name, email, password: await bcrypt.hash(password, 10), role: 'user' });
  res.status(201).json({ token: jwt.sign({ id: users.length, role: 'user' }, SECRET, { expiresIn: '24h' }) });
});
app.post('/auth/login', async (req, res) => {
  const user = users.find(u => u.email === req.body.email);
  if (!user || !(await bcrypt.compare(req.body.password, user.password))) return res.status(401).json({ error: 'Invalid' });
  res.json({ token: jwt.sign({ id: user.id, role: user.role }, SECRET, { expiresIn: '24h' }) });
});

// Audit log middleware — logs every request
app.use((req, res, next) => {
  const start = Date.now();
  res.on('finish', () => {
    auditLogs.push({
      id: aId++, timestamp: new Date().toISOString(),
      userId: req.user?.id || null, method: req.method, path: req.path,
      status: res.statusCode, durationMs: Date.now() - start,
      ip: req.ip, userAgent: req.get('user-agent') || '',
      requestBody: req.body && Object.keys(req.body).length < 10 ? JSON.stringify(req.body) : null,
    });
    if (auditLogs.length > 10000) auditLogs.shift(); // cap memory
  });
  next();
});

// Record specific events
app.post('/audit', auth, (req, res) => {
  const { action, resource, resourceId, details } = req.body;
  if (!action) return res.status(400).json({ error: 'action required' });
  const entry = { id: aId++, timestamp: new Date().toISOString(), userId: req.user.id, action, resource, resourceId, details: details || {}, ip: req.ip, userAgent: req.get('user-agent') || '' };
  auditLogs.push(entry);
  res.status(201).json(entry);
});

// Search
app.get('/audit', auth, (req, res) => {
  let result = [...auditLogs];
  if (req.query.userId) result = result.filter(l => l.userId === parseInt(req.query.userId));
  if (req.query.action) result = result.filter(l => l.action.includes(req.query.action));
  if (req.query.resource) result = result.filter(l => l.resource === req.query.resource);
  if (req.query.startDate) result = result.filter(l => l.timestamp >= req.query.startDate);
  if (req.query.endDate) result = result.filter(l => l.timestamp <= req.query.endDate);
  if (req.query.status) result = result.filter(l => l.status === parseInt(req.query.status));
  if (req.query.minDuration) result = result.filter(l => l.durationMs >= parseInt(req.query.minDuration));
  result.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
  const page = Math.max(1, parseInt(req.query.page) || 1); const limit = parseInt(req.query.limit) || 50;
  res.json({ total: result.length, page, data: result.slice((page - 1) * limit, page * limit) });
});

// User activity (one user's actions)
app.get('/audit/users/:id/activity', auth, (req, res) => {
  const userId = parseInt(req.params.id);
  const userLogs = auditLogs.filter(l => l.userId === userId).sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
  res.json({ user: users.find(u => u.id === userId)?.name, total: userLogs.length, recent: userLogs.slice(0, 20) });
});

// Statistics
app.get('/audit/stats', auth, (req, res) => {
  const last24h = auditLogs.filter(l => Date.now() - new Date(l.timestamp).getTime() < 24 * 3600000);
  const actionCounts = {}; auditLogs.forEach(l => { if (l.action) actionCounts[l.action] = (actionCounts[l.action] || 0) + 1; });
  res.json({
    totalLogs: auditLogs.length, last24h: last24h.length,
    uniqueUsers: new Set(auditLogs.map(l => l.userId).filter(Boolean)).size,
    topActions: Object.entries(actionCounts).sort((a, b) => b[1] - a[1]).slice(0, 10),
    errorRate: auditLogs.length ? auditLogs.filter(l => l.status >= 400).length / auditLogs.length : 0,
  });
});

app.listen(3000, () => console.log('Audit Log :3000'));
module.exports = app;
