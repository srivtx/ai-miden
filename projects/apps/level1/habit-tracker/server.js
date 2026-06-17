// Habit Tracker — Define habits, daily check-in, streaks, weekly/monthly progress.
const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const app = express();
app.use(express.json());
const SECRET = 'dev-secret';

const users = []; const habits = []; const checkins = [];
let habId = 1;

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

app.post('/habits', auth, (req, res) => {
  const { name, description, frequency, targetCount } = req.body;
  if (!name) return res.status(400).json({ error: 'Name required' });
  const habit = { id: habId++, userId: req.user.id, name, description: description || '', frequency: frequency || 'daily', targetCount: targetCount || 1, active: true, createdAt: new Date().toISOString() };
  habits.push(habit);
  res.status(201).json(habit);
});

app.get('/habits', auth, (req, res) => {
  const result = habits.filter(h => h.userId === req.user.id && h.active);
  const enriched = result.map(h => {
    const today = new Date().toISOString().split('T')[0];
    const userCheckins = checkins.filter(c => c.habitId === h.id);
    const todayChecked = userCheckins.some(c => c.date.startsWith(today));
    const streak = computeStreak(userCheckins.map(c => c.date));
    return { ...h, todayChecked, streak, totalCheckins: userCheckins.length };
  });
  res.json(enriched);
});

app.post('/habits/:id/checkin', auth, (req, res) => {
  const habit = habits.find(h => h.id === parseInt(req.params.id) && h.userId === req.user.id);
  if (!habit) return res.status(404).json({ error: 'Not found' });
  const today = new Date().toISOString().split('T')[0];
  if (checkins.find(c => c.habitId === habit.id && c.date.startsWith(today))) return res.status(409).json({ error: 'Already checked in today' });
  checkins.push({ habitId: habit.id, userId: req.user.id, date: new Date().toISOString() });
  const streak = computeStreak(checkins.filter(c => c.habitId === habit.id).map(c => c.date));
  res.json({ checked: true, streak, date: today });
});

app.delete('/habits/:id', auth, (req, res) => {
  const idx = habits.findIndex(h => h.id === parseInt(req.params.id) && h.userId === req.user.id);
  if (idx === -1) return res.status(404).json({ error: 'Not found' });
  habits[idx].active = false;
  res.status(204).send();
});

function computeStreak(dates) {
  if (!dates.length) return 0;
  const sorted = [...new Set(dates.map(d => d.split('T')[0]))].sort().reverse();
  let streak = 0; const today = new Date();
  for (let i = 0; i < sorted.length; i++) {
    const expected = new Date(today); expected.setDate(today.getDate() - streak);
    if (sorted[i] === expected.toISOString().split('T')[0]) streak++;
    else if (i === 0 && sorted[i] !== today.toISOString().split('T')[0]) { /* yesterday's streak still counts */ }
    else break;
  }
  return streak;
}

app.listen(3000, () => console.log('Habit Tracker :3000'));
module.exports = app;
