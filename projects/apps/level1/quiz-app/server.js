// Quiz App — Create quizzes, take them, score automatically, leaderboard.
const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const app = express();
app.use(express.json());
const SECRET = 'dev-secret';

const users = []; const quizzes = []; const attempts = []; let qzId = 1, attId = 1;
function auth(req, res, next) { try { req.user = jwt.verify((req.headers.authorization || '').split(' ')[1], SECRET); next(); } catch { res.status(401).json({ error: 'Auth required' }); } }

app.post('/auth/register', async (req, res) => {
  const { name, email, password } = req.body;
  if (!email || !password) return res.status(400).json({ error: 'email, password required' });
  if (users.find(u => u.email === email)) return res.status(409).json({ error: 'Email exists' });
  users.push({ id: users.length + 1, name, email, password: await bcrypt.hash(password, 10), totalScore: 0 });
  res.status(201).json({ token: jwt.sign({ id: users.length }, SECRET, { expiresIn: '24h' }) });
});
app.post('/auth/login', async (req, res) => {
  const user = users.find(u => u.email === req.body.email);
  if (!user || !(await bcrypt.compare(req.body.password, user.password))) return res.status(401).json({ error: 'Invalid' });
  res.json({ token: jwt.sign({ id: user.id }, SECRET, { expiresIn: '24h' }) });
});

// Create quiz
app.post('/quizzes', auth, (req, res) => {
  const { title, category, questions, timeLimit } = req.body;
  if (!title || !Array.isArray(questions) || !questions.length) return res.status(400).json({ error: 'title and questions[] required' });
  if (!questions.every(q => q.question && Array.isArray(q.options) && typeof q.correctIndex === 'number')) return res.status(400).json({ error: 'Each question needs {question, options, correctIndex}' });
  const qz = { id: qzId++, ownerId: req.user.id, title, category: category || 'General', questions, timeLimit: timeLimit || 600, attemptCount: 0, createdAt: new Date().toISOString() };
  quizzes.push(qz);
  res.status(201).json(qz);
});

app.get('/quizzes', (req, res) => {
  let result = quizzes.filter(q => req.query.category ? q.category === req.query.category : true);
  if (req.query.search) { const q = req.query.search.toLowerCase(); result = result.filter(qz => qz.title.toLowerCase().includes(q)); }
  res.json(result.map(q => ({ id: q.id, title: q.title, category: q.category, questionCount: q.questions.length, timeLimit: q.timeLimit, attemptCount: q.attemptCount })));
});

app.get('/quizzes/:id', (req, res) => {
  const qz = quizzes.find(q => q.id === parseInt(req.params.id));
  if (!qz) return res.status(404).json({ error: 'Not found' });
  // Strip correctIndex (don't leak answers)
  res.json({ ...qz, questions: qz.questions.map(q => ({ question: q.question, options: q.options })) });
});

// Take quiz
app.post('/quizzes/:id/attempt', auth, (req, res) => {
  const qz = quizzes.find(q => q.id === parseInt(req.params.id));
  if (!qz) return res.status(404).json({ error: 'Not found' });
  const { answers, timeTaken } = req.body; // array of indices
  if (!Array.isArray(answers) || answers.length !== qz.questions.length) return res.status(400).json({ error: 'answers[] required with same length as questions' });
  let score = 0;
  const breakdown = qz.questions.map((q, idx) => ({ question: q.question, correct: answers[idx] === q.correctIndex, correctIndex: q.correctIndex, yourAnswer: answers[idx] }));
  qz.questions.forEach((q, idx) => { if (answers[idx] === q.correctIndex) score++; });
  const percent = Math.round((score / qz.questions.length) * 100);
  const user = users.find(u => u.id === req.user.id);
  user.totalScore += score;
  const att = { id: attId++, quizId: qz.id, userId: req.user.id, score, percent, timeTaken: timeTaken || 0, breakdown, attemptedAt: new Date().toISOString() };
  attempts.push(att);
  qz.attemptCount++;
  res.status(201).json({ score, percent, correct: score, total: qz.questions.length, breakdown });
});

app.get('/quizzes/:id/leaderboard', (req, res) => {
  const qzAttempts = attempts.filter(a => a.quizId === parseInt(req.params.id)).sort((a, b) => b.score - a.score || a.timeTaken - b.timeTaken).slice(0, 20);
  res.json(qzAttempts.map((a, idx) => ({ rank: idx + 1, user: users.find(u => u.id === a.userId)?.name, score: a.score, percent: a.percent, timeTaken: a.timeTaken, attemptedAt: a.attemptedAt })));
});

app.get('/my-attempts', auth, (req, res) => res.json(attempts.filter(a => a.userId === req.user.id)));

app.listen(3000, () => console.log('Quiz App :3000'));
module.exports = app;
