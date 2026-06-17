// Notification System — Multi-channel (in-app, email, push), preferences, batching.
const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const app = express();
app.use(express.json());
const SECRET = 'dev-secret';

const users = []; const notifications = []; const preferences = []; const templates = []; let nId = 1, pId = 1, tId = 1;

function auth(req, res, next) { try { req.user = jwt.verify((req.headers.authorization || '').split(' ')[1], SECRET); next(); } catch { res.status(401).json({ error: 'Auth required' }); } }
function getPrefs(userId) { return preferences.find(p => p.userId === userId) || { userId, channels: { inApp: true, email: true, push: false }, categories: { orders: true, social: true, system: true, marketing: false } }; }

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

// Templates (admin)
app.post('/templates', auth, (req, res) => {
  if (req.user.role !== 'admin') return res.status(403).json({ error: 'Admin only' });
  const { name, subject, body, channel, category } = req.body;
  if (!name || !body || !channel) return res.status(400).json({ error: 'name, body, channel required' });
  templates.push({ id: tId++, name, subject: subject || name, body, channel, category: category || 'system', createdAt: new Date().toISOString() });
  res.status(201).json(templates[templates.length - 1]);
});

// Send notification (internal API)
app.post('/send', auth, (req, res) => {
  const { userId, category, title, message, data, channels } = req.body;
  if (!userId || !title) return res.status(400).json({ error: 'userId and title required' });
  const user = users.find(u => u.id === parseInt(userId));
  if (!user) return res.status(404).json({ error: 'User not found' });
  const prefs = getPrefs(user.id);
  const sendChannels = channels || (prefs.categories[category || 'system'] ? Object.keys(prefs.channels).filter(c => prefs.channels[c]) : []);
  const notif = { id: nId++, userId, category: category || 'system', title, message, data: data || {}, channels: sendChannels, read: false, createdAt: new Date().toISOString() };
  notifications.push(notif);
  // In real app: queue email, push notification, etc.
  res.status(201).json(notif);
});

// In-app inbox
app.get('/inbox', auth, (req, res) => {
  let result = notifications.filter(n => n.userId === req.user.id && (n.channels || []).includes('inApp'));
  if (req.query.unread === 'true') result = result.filter(n => !n.read);
  if (req.query.category) result = result.filter(n => n.category === req.query.category);
  result.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
  const page = Math.max(1, parseInt(req.query.page) || 1); const limit = parseInt(req.query.limit) || 20;
  res.json({ total: result.length, unread: result.filter(n => !n.read).length, data: result.slice((page - 1) * limit, page * limit) });
});

app.post('/inbox/:id/read', auth, (req, res) => {
  const n = notifications.find(n => n.id === parseInt(req.params.id) && n.userId === req.user.id);
  if (!n) return res.status(404).json({ error: 'Not found' });
  n.read = true; n.readAt = new Date().toISOString();
  res.json(n);
});

app.post('/inbox/read-all', auth, (req, res) => {
  let count = 0;
  notifications.forEach(n => { if (n.userId === req.user.id && !n.read) { n.read = true; count++; } });
  res.json({ marked: count });
});

// Preferences
app.get('/preferences', auth, (req, res) => res.json(getPrefs(req.user.id)));

app.put('/preferences', auth, (req, res) => {
  let pref = preferences.find(p => p.userId === req.user.id);
  if (!pref) { pref = { userId: req.user.id, channels: { inApp: true, email: true, push: false }, categories: { orders: true, social: true, system: true, marketing: false } }; preferences.push(pref); }
  if (req.body.channels) pref.channels = { ...pref.channels, ...req.body.channels };
  if (req.body.categories) pref.categories = { ...pref.categories, ...req.body.categories };
  res.json(pref);
});

// Mark all as read in category
app.post('/inbox/read-category', auth, (req, res) => {
  let count = 0;
  notifications.forEach(n => { if (n.userId === req.user.id && !n.read && (!req.body.category || n.category === req.body.category)) { n.read = true; count++; } });
  res.json({ marked: count });
});

app.listen(3000, () => console.log('Notification System :3000'));
module.exports = app;
