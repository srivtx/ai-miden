// 19 — Habit Tracker
// A habit has a name and a list of completions (dates when it was done).
// Mark it done for today. See the streak.
const express = require('express');
const app = express();
app.use(express.json());

const habits = [];

app.get('/habits', (req, res) => {
  res.json({ count: habits.length, habits });
});

app.post('/habits', (req, res) => {
  const { name } = req.body;
  const habit = { id: habits.length + 1, name, completions: [] };
  habits.push(habit);
  res.status(201).json(habit);
});

// Mark habit done for today
app.post('/habits/:id/complete', (req, res) => {
  const habit = habits.find(h => h.id === parseInt(req.params.id));
  if (!habit) return res.status(404).json({ error: 'Habit not found' });
  const today = new Date().toISOString().slice(0, 10);
  if (!habit.completions.includes(today)) {
    habit.completions.push(today);
  }
  res.json(habit);
});

// Get the streak (consecutive days)
app.get('/habits/:id/streak', (req, res) => {
  const habit = habits.find(h => h.id === parseInt(req.params.id));
  if (!habit) return res.status(404).json({ error: 'Habit not found' });
  const dates = new Set(habit.completions);
  let streak = 0;
  let day = new Date();
  while (dates.has(day.toISOString().slice(0, 10))) {
    streak++;
    day.setDate(day.getDate() - 1);
  }
  res.json({ habit: habit.name, streak, completions: habit.completions });
});

app.listen(3000, () => console.log('Habit server on http://localhost:3000'));
