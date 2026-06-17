// 22 — Mood Journal
// Each entry has a mood (1-5), a note, and a date.
// NEW: average mood across all entries.
const express = require('express');
const app = express();
app.use(express.json());

const entries = [];

app.get('/entries', (req, res) => {
  res.json({ count: entries.length, entries });
});

app.post('/entries', (req, res) => {
  const { mood, note } = req.body;
  if (mood < 1 || mood > 5) return res.status(422).json({ error: 'mood must be between 1 and 5' });
  const entry = { id: entries.length + 1, mood, note: note || '', date: new Date().toISOString() };
  entries.push(entry);
  res.status(201).json(entry);
});

app.delete('/entries/:id', (req, res) => {
  const index = entries.findIndex(e => e.id === parseInt(req.params.id));
  if (index === -1) return res.status(404).json({ error: 'Entry not found' });
  entries.splice(index, 1);
  res.status(204).end();
});

// Summary: average mood
app.get('/summary', (req, res) => {
  if (entries.length === 0) return res.json({ average: 0, count: 0 });
  const sum = entries.reduce((s, e) => s + e.mood, 0);
  res.json({ average: (sum / entries.length).toFixed(2), count: entries.length });
});

app.listen(3000, () => console.log('Mood journal on http://localhost:3000'));
