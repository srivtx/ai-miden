// 40 — Event RSVP
// Events have a list of attendees. People RSVP yes/no.
const express = require('express');
const app = express();
app.use(express.json());

const events = [];

app.get('/events', (req, res) => {
  res.json({ count: events.length, events });
});

app.post('/events', (req, res) => {
  const { title, date, location } = req.body;
  const event = { id: events.length + 1, title, date, location: location || '', attendees: [] };
  events.push(event);
  res.status(201).json(event);
});

app.get('/events/:id', (req, res) => {
  const event = events.find(e => e.id === parseInt(req.params.id));
  if (!event) return res.status(404).json({ error: 'Event not found' });
  res.json(event);
});

// RSVP: { name, status: 'yes' | 'no' | 'maybe' }
app.post('/events/:id/rsvp', (req, res) => {
  const event = events.find(e => e.id === parseInt(req.params.id));
  if (!event) return res.status(404).json({ error: 'Event not found' });
  const { name, status } = req.body;
  if (!['yes', 'no', 'maybe'].includes(status)) {
    return res.status(422).json({ error: 'status must be yes, no, or maybe' });
  }
  // Remove existing RSVP from this person (if any), then add the new one
  event.attendees = event.attendees.filter(a => a.name !== name);
  event.attendees.push({ name, status, rsvpAt: new Date().toISOString() });
  res.json(event);
});

app.listen(3000, () => console.log('Event RSVP on http://localhost:3000'));
