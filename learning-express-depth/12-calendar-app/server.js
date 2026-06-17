// 12 — Calendar App
// Events have: id, title, startTime, endTime.
// NEW: we support range queries. ?from=2024-01-01&to=2024-12-31 returns events in that range.
const express = require('express');
const app = express();
app.use(express.json());

const events = [];

app.get('/events', (req, res) => {
  const { from, to } = req.query;
  let result = events;
  if (from) {
    const fromDate = new Date(from);
    result = result.filter(e => new Date(e.startTime) >= fromDate);
  }
  if (to) {
    const toDate = new Date(to);
    result = result.filter(e => new Date(e.startTime) <= toDate);
  }
  res.json({ count: result.length, events: result });
});

app.post('/events', (req, res) => {
  const { title, startTime, endTime } = req.body;
  const event = { id: events.length + 1, title, startTime, endTime, createdAt: new Date().toISOString() };
  events.push(event);
  res.status(201).json(event);
});

app.delete('/events/:id', (req, res) => {
  const index = events.findIndex(e => e.id === parseInt(req.params.id));
  if (index === -1) return res.status(404).json({ error: 'Event not found' });
  events.splice(index, 1);
  res.status(204).end();
});

app.listen(3000, () => console.log('Calendar server on http://localhost:3000'));
