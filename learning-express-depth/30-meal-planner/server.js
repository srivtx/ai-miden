// 30 — Meal Planner
// Each day has 3 meals: breakfast, lunch, dinner. Plan a week at a time.
const express = require('express');
const app = express();
app.use(express.json());

// Each day: { date, breakfast, lunch, dinner }
const days = [];

app.get('/days', (req, res) => {
  res.json({ count: days.length, days });
});

app.post('/days', (req, res) => {
  const { date, breakfast, lunch, dinner } = req.body;
  const day = { date, breakfast: breakfast || '', lunch: lunch || '', dinner: dinner || '' };
  days.push(day);
  res.status(201).json(day);
});

app.get('/days/:date', (req, res) => {
  const day = days.find(d => d.date === req.params.date);
  if (!day) return res.status(404).json({ error: 'No plan for that date' });
  res.json(day);
});

app.patch('/days/:date', (req, res) => {
  const day = days.find(d => d.date === req.params.date);
  if (!day) return res.status(404).json({ error: 'No plan for that date' });
  if (req.body.breakfast) day.breakfast = req.body.breakfast;
  if (req.body.lunch) day.lunch = req.body.lunch;
  if (req.body.dinner) day.dinner = req.body.dinner;
  res.json(day);
});

app.listen(3000, () => console.log('Meal planner on http://localhost:3000'));
