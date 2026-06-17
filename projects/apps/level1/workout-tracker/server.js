// Workout / Fitness Tracker
const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const app = express();
app.use(express.json());
const SECRET = 'dev-secret';

const users = []; const workouts = []; const exercises = []; let wId = 1, exId = 1;
function auth(req, res, next) { try { req.user = jwt.verify((req.headers.authorization || '').split(' ')[1], SECRET); next(); } catch { res.status(401).json({ error: 'Auth required' }); } }

app.post('/auth/register', async (req, res) => {
  const { name, email, password } = req.body;
  if (!email || !password) return res.status(400).json({ error: 'email, password required' });
  if (users.find(u => u.email === email)) return res.status(409).json({ error: 'Email exists' });
  users.push({ id: users.length + 1, name, email, password: await bcrypt.hash(password, 10), weight: null, height: null, goal: 'maintain' });
  res.status(201).json({ token: jwt.sign({ id: users.length }, SECRET, { expiresIn: '24h' }) });
});
app.post('/auth/login', async (req, res) => {
  const user = users.find(u => u.email === req.body.email);
  if (!user || !(await bcrypt.compare(req.body.password, user.password))) return res.status(401).json({ error: 'Invalid' });
  res.json({ token: jwt.sign({ id: user.id }, SECRET, { expiresIn: '24h' }) });
});

// Profile
app.put('/profile', auth, (req, res) => {
  const user = users.find(u => u.id === req.user.id);
  ['weight', 'height', 'goal'].forEach(k => { if (req.body[k] !== undefined) user[k] = req.body[k]; });
  res.json({ weight: user.weight, height: user.height, goal: user.goal, bmi: user.weight && user.height ? (user.weight / Math.pow(user.height / 100, 2)).toFixed(1) : null });
});

// Workouts
app.post('/workouts', auth, (req, res) => {
  const { name, date, duration, notes, type } = req.body;
  if (!name) return res.status(400).json({ error: 'name required' });
  const w = { id: wId++, userId: req.user.id, name, type: type || 'strength', date: date || new Date().toISOString(), duration: duration || 0, notes: notes || '', calories: 0, createdAt: new Date().toISOString() };
  workouts.push(w);
  res.status(201).json(w);
});

app.get('/workouts', auth, (req, res) => {
  let result = workouts.filter(w => w.userId === req.user.id);
  if (req.query.type) result = result.filter(w => w.type === req.query.type);
  if (req.query.startDate) result = result.filter(w => w.date >= req.query.startDate);
  if (req.query.endDate) result = result.filter(w => w.date <= req.query.endDate);
  result.sort((a, b) => new Date(b.date) - new Date(a.date));
  res.json(result.map(w => ({ ...w, exerciseCount: exercises.filter(e => e.workoutId === w.id).length })));
});

app.get('/workouts/:id', auth, (req, res) => {
  const w = workouts.find(w => w.id === parseInt(req.params.id) && w.userId === req.user.id);
  if (!w) return res.status(404).json({ error: 'Not found' });
  res.json({ ...w, exercises: exercises.filter(e => e.workoutId === w.id) });
});

app.delete('/workouts/:id', auth, (req, res) => {
  const idx = workouts.findIndex(w => w.id === parseInt(req.params.id) && w.userId === req.user.id);
  if (idx === -1) return res.status(404).json({ error: 'Not found' });
  workouts.splice(idx, 1);
  res.status(204).send();
});

// Exercises within a workout
app.post('/workouts/:id/exercises', auth, (req, res) => {
  const w = workouts.find(w => w.id === parseInt(req.params.id) && w.userId === req.user.id);
  if (!w) return res.status(404).json({ error: 'Workout not found' });
  const { name, sets, reps, weight, duration, distance } = req.body;
  if (!name) return res.status(400).json({ error: 'name required' });
  const ex = { id: exId++, workoutId: w.id, name, sets: sets || null, reps: reps || null, weight: weight || null, duration: duration || null, distance: distance || null, calories: weight && sets && reps ? Math.round(weight * sets * reps * 0.1) : 0 };
  exercises.push(ex);
  w.calories += ex.calories;
  res.status(201).json(ex);
});

// Stats
app.get('/stats', auth, (req, res) => {
  const myWorkouts = workouts.filter(w => w.userId === req.user.id);
  const myExercises = exercises.filter(e => myWorkouts.find(w => w.id === e.workoutId));
  const totalCalories = myWorkouts.reduce((s, w) => s + w.calories, 0);
  const totalDuration = myWorkouts.reduce((s, w) => s + w.duration, 0);
  // Weekly breakdown
  const now = new Date(); const weekStart = new Date(now); weekStart.setDate(now.getDate() - 7);
  const thisWeek = myWorkouts.filter(w => new Date(w.date) >= weekStart);
  // Personal records
  const prs = {}; myExercises.forEach(e => { if (e.weight && (!prs[e.name] || e.weight > prs[e.name].weight)) prs[e.name] = { weight: e.weight, reps: e.reps, sets: e.sets }; });
  res.json({ totalWorkouts: myWorkouts.length, totalExercises: myExercises.length, totalCalories, totalDuration, thisWeek: { workouts: thisWeek.length, calories: thisWeek.reduce((s, w) => s + w.calories, 0) }, personalRecords: prs });
});

app.listen(3000, () => console.log('Workout Tracker :3000'));
module.exports = app;
