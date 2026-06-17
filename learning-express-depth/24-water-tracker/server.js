// 24 — Water Tracker
// Each entry: amount (in ml). Sum for today.
const express = require('express');
const app = express();
app.use(express.json());

const entries = [];

app.get('/entries', (req, res) => {
  res.json({ count: entries.length, entries });
});

app.post('/entries', (req, res) => {
  const { amount } = req.body;
  if (typeof amount !== 'number' || amount <= 0) return res.status(422).json({ error: 'amount must be a positive number' });
  const entry = { id: entries.length + 1, amount, date: new Date().toISOString() };
  entries.push(entry);
  res.status(201).json(entry);
});

// Total for today
app.get('/today', (req, res) => {
  const today = new Date().toISOString().slice(0, 10);
  const todayEntries = entries.filter(e => e.date.startsWith(today));
  const total = todayEntries.reduce((s, e) => s + e.amount, 0);
  res.json({ date: today, total, count: todayEntries.length, entries: todayEntries });
});

app.listen(3000, () => console.log('Water tracker on http://localhost:3000'));
