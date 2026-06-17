// Event Scheduler — Create events, RSVPs, recurring events, calendar views, reminders.
const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const app = express();
app.use(express.json());
const SECRET = 'dev-secret';

const users = []; const events = []; const rsvps = []; let evtId = 1;

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

// CREATE event
app.post('/events', auth, (req, res) => {
  const { title, description, startTime, endTime, location, recurring } = req.body;
  if (!title || !startTime) return res.status(400).json({ error: 'Title and startTime required' });
  const event = { id: evtId++, organizerId: req.user.id, title, description: description || '', startTime, endTime: endTime || startTime, location: location || '', recurring: recurring || null, createdAt: new Date().toISOString() };
  events.push(event);
  res.status(201).json(event);
});

// LIST (with calendar views)
app.get('/events', auth, (req, res) => {
  let result = [...events];
  const view = req.query.view || 'upcoming'; // upcoming, day, week, month, past
  const now = new Date();
  if (view === 'upcoming') result = result.filter(e => new Date(e.startTime) >= now);
  else if (view === 'past') result = result.filter(e => new Date(e.startTime) < now);
  else if (view === 'day') { const day = req.query.date || now.toISOString().split('T')[0]; result = result.filter(e => e.startTime.startsWith(day)); }
  else if (view === 'week') { const start = new Date(now); start.setDate(now.getDate() - now.getDay()); const end = new Date(start); end.setDate(start.getDate() + 7); result = result.filter(e => { const d = new Date(e.startTime); return d >= start && d < end; }); }
  else if (view === 'month') { const m = parseInt(req.query.month) || now.getMonth(); const y = parseInt(req.query.year) || now.getFullYear(); result = result.filter(e => { const d = new Date(e.startTime); return d.getMonth() === m && d.getFullYear() === y; }); }
  if (req.query.search) { const q = req.query.search.toLowerCase(); result = result.filter(e => e.title.toLowerCase().includes(q) || e.description.toLowerCase().includes(q) || e.location.toLowerCase().includes(q)); }
  result.sort((a, b) => new Date(a.startTime) - new Date(b.startTime));
  const page = Math.max(1, parseInt(req.query.page) || 1); const limit = parseInt(req.query.limit) || 50;
  const total = result.length; result = result.slice((page - 1) * limit, page * limit);
  const enriched = result.map(e => ({ ...e, rsvpCount: rsvps.filter(r => r.eventId === e.id).length, organizer: users.find(u => u.id === e.organizerId)?.name }));
  res.json({ total, page, view, data: enriched });
});

app.get('/events/:id', auth, (req, res) => {
  const event = events.find(e => e.id === parseInt(req.params.id));
  if (!event) return res.status(404).json({ error: 'Not found' });
  const attendees = rsvps.filter(r => r.eventId === event.id).map(r => ({ status: r.status, user: users.find(u => u.id === r.userId)?.name }));
  res.json({ ...event, organizer: users.find(u => u.id === event.organizerId)?.name, attendees, rsvpCount: attendees.length });
});

// RSVP
app.post('/events/:id/rsvp', auth, (req, res) => {
  const event = events.find(e => e.id === parseInt(req.params.id));
  if (!event) return res.status(404).json({ error: 'Not found' });
  const status = ['going', 'maybe', 'declined'].includes(req.body.status) ? req.body.status : 'going';
  const existing = rsvps.findIndex(r => r.eventId === event.id && r.userId === req.user.id);
  if (existing >= 0) { rsvps[existing].status = status; return res.json({ updated: true, status }); }
  rsvps.push({ eventId: event.id, userId: req.user.id, status, createdAt: new Date().toISOString() });
  res.status(201).json({ status, user: users.find(u => u.id === req.user.id)?.name });
});

// MY RSVPs
app.get('/my-rsvps', auth, (req, res) => {
  const myRsvps = rsvps.filter(r => r.userId === req.user.id).map(r => ({ ...r, event: events.find(e => e.id === r.eventId) }));
  res.json(myRsvps);
});

app.listen(3000, () => console.log('Event Scheduler :3000'));
module.exports = app;
