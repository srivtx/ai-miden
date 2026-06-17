// 25 — Sleep Tracker
// Each entry: bedtime, wakeTime. Compute duration.
const express = require('express');
const app = express();
app.use(express.json());

const entries = [];

app.get('/entries', (req, res) => {
  res.json({ count: entries.length, entries });
});

app.post('/entries', (req, res) => {
  const { bedtime, wakeTime } = req.body;
  const bed = new Date(bedtime);
  const wake = new Date(wakeTime);
  const durationHours = (wake - bed) / (1000 * 60 * 60);
  const entry = { id: entries.length + 1, bedtime, wakeTime, durationHours: durationHours.toFixed(2) };
  entries.push(entry);
  res.status(201).json(entry);
});

// Average sleep duration
app.get('/average', (req, res) => {
  if (entries.length === 0) return res.json({ averageHours: 0 });
  const total = entries.reduce((s, e) => s + parseFloat(e.durationHours), 0);
  res.json({ averageHours: (total / entries.length).toFixed(2), count: entries.length });
});

app.listen(3000, () => console.log('Sleep tracker on http://localhost:3000'));
