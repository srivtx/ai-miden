// Analytics API — Track events, aggregate metrics, date ranges, dashboards.
const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const app = express();
app.use(express.json());
const SECRET = 'dev-secret';

const users = []; const events = []; const apps = new Map(); // appId -> { name, apiKey }

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

// Create an app (gets an API key for tracking)
app.post('/apps', auth, (req, res) => {
  const appId = `app_${Date.now()}`;
  const apiKey = `key_${Math.random().toString(36).slice(2)}_${Date.now()}`;
  apps.set(appId, { name: req.body.name, userId: req.user.id, apiKey, createdAt: new Date().toISOString() });
  res.status(201).json({ appId, apiKey, name: req.body.name });
});

// INGEST event (from client app — uses API key, not JWT)
app.post('/track', (req, res) => {
  const { appId, apiKey, event: eventName, properties } = req.body;
  const app = apps.get(appId);
  if (!app || app.apiKey !== apiKey) return res.status(401).json({ error: 'Invalid appId or apiKey' });
  if (!eventName) return res.status(400).json({ error: 'event name required' });
  events.push({ appId, event: eventName, properties: properties || {}, timestamp: new Date().toISOString() });
  res.status(201).json({ tracked: true });
});

// ANALYTICS DASHBOARD
app.get('/analytics/:appId', auth, (req, res) => {
  const app = apps.get(req.params.appId);
  if (!app || app.userId !== req.user.id) return res.status(404).json({ error: 'Not found' });
  const appEvents = events.filter(e => e.appId === req.params.appId);

  // Date range
  const now = new Date();
  const range = req.query.range || '7d';
  const ranges = { '1d': 1, '7d': 7, '30d': 30, '90d': 90 };
  const days = ranges[range] || 7;
  const start = new Date(now); start.setDate(now.getDate() - days);
  const filtered = appEvents.filter(e => new Date(e.timestamp) >= start);

  // Total events by name
  const byEvent = {};
  filtered.forEach(e => { byEvent[e.event] = (byEvent[e.event] || 0) + 1; });

  // Daily breakdown
  const byDay = {};
  for (let i = 0; i < days; i++) {
    const d = new Date(now); d.setDate(now.getDate() - i);
    const key = d.toISOString().split('T')[0];
    byDay[key] = filtered.filter(e => e.timestamp.startsWith(key)).length;
  }

  // Unique users (by properties.userId)
  const uniqueUsers = new Set(filtered.map(e => e.properties.userId).filter(Boolean));

  // Top property values
  const propCounts = {};
  filtered.forEach(e => {
    Object.entries(e.properties).forEach(([k, v]) => {
      if (!propCounts[k]) propCounts[k] = {};
      propCounts[k][String(v)] = (propCounts[k][String(v)] || 0) + 1;
    });
  });

  res.json({
    app: app.name,
    range: `${days} days`,
    total: filtered.length,
    uniqueUsers: uniqueUsers.size,
    events: Object.entries(byEvent).map(([name, count]) => ({ name, count, pct: ((count / filtered.length) * 100).toFixed(1) })).sort((a, b) => b.count - a.count),
    byDay: Object.entries(byDay).map(([date, count]) => ({ date, count })).sort((a, b) => a.date.localeCompare(b.date)),
    topProperties: Object.fromEntries(Object.entries(propCounts).map(([k, v]) => [k, Object.entries(v).sort((a, b) => b[1] - a[1]).slice(0, 5)])),
  });
});

// FUNNEL: track sequence of events
app.get('/funnel/:appId', auth, (req, res) => {
  const app = apps.get(req.params.appId);
  if (!app || app.userId !== req.user.id) return res.status(404).json({ error: 'Not found' });
  const steps = (req.query.steps || '').split(',');
  if (steps.length < 2) return res.status(400).json({ error: 'Provide steps (comma-separated event names)' });

  const appEvents = events.filter(e => e.appId === req.params.appId);
  const funnel = [];
  let prevUsers = null;
  steps.forEach(step => {
    const usersWhoDid = new Set(appEvents.filter(e => e.event === step).map(e => e.properties.userId || e.properties.sessionId).filter(Boolean));
    funnel.push({ step, users: usersWhoDid.size, fromPrevious: prevUsers ? ((usersWhoDid.size / prevUsers.size) * 100).toFixed(1) + '%' : '-' });
    prevUsers = usersWhoDid;
  });

  res.json({ funnel, steps });
});

app.listen(3000, () => console.log('Analytics :3000'));
module.exports = app;
