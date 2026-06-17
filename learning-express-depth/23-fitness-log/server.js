// 23 — Fitness Log
// Each entry: exercise, sets, reps, weight. Add up total volume.
const express = require('express');
const app = express();
app.use(express.json());

const logs = [];

app.get('/logs', (req, res) => {
  res.json({ count: logs.length, logs });
});

app.post('/logs', (req, res) => {
  const { exercise, sets, reps, weight } = req.body;
  const log = { id: logs.length + 1, exercise, sets, reps, weight: weight || 0, date: new Date().toISOString() };
  logs.push(log);
  res.status(201).json(log);
});

app.delete('/logs/:id', (req, res) => {
  const index = logs.findIndex(l => l.id === parseInt(req.params.id));
  if (index === -1) return res.status(404).json({ error: 'Not found' });
  logs.splice(index, 1);
  res.status(204).end();
});

// Volume = sets * reps * weight
app.get('/volume', (req, res) => {
  const total = logs.reduce((s, l) => s + l.sets * l.reps * (l.weight || 0), 0);
  res.json({ totalVolume: total, count: logs.length });
});

app.listen(3000, () => console.log('Fitness log on http://localhost:3000'));
