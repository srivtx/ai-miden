// 35 — Pomodoro Timer
// Each session: task, duration (in minutes), completedAt.
const express = require('express');
const app = express();
app.use(express.json());

const sessions = [];

app.get('/sessions', (req, res) => {
  res.json({ count: sessions.length, sessions });
});

app.post('/sessions', (req, res) => {
  const { task, duration } = req.body;
  const session = { id: sessions.length + 1, task, duration: duration || 25, completedAt: new Date().toISOString() };
  sessions.push(session);
  res.status(201).json(session);
});

// Total time focused
app.get('/stats', (req, res) => {
  const totalMinutes = sessions.reduce((s, x) => s + x.duration, 0);
  const totalHours = (totalMinutes / 60).toFixed(2);
  res.json({ sessions: sessions.length, totalMinutes, totalHours });
});

app.listen(3000, () => console.log('Pomodoro on http://localhost:3000'));
