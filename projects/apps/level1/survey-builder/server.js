// Survey/Form Builder API — Create surveys, collect responses, analytics.
const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const app = express();
app.use(express.json());
const SECRET = 'dev-secret';

const users = []; const surveys = []; const responses = []; let svId = 1, respId = 1;
function auth(req, res, next) { try { req.user = jwt.verify((req.headers.authorization || '').split(' ')[1], SECRET); next(); } catch { res.status(401).json({ error: 'Auth required' }); } }

app.post('/auth/register', async (req, res) => {
  const { name, email, password } = req.body;
  if (!email || !password) return res.status(400).json({ error: 'email, password required' });
  if (users.find(u => u.email === email)) return res.status(409).json({ error: 'Email exists' });
  const user = { id: users.length + 1, name, email, password: await bcrypt.hash(password, 10) };
  users.push(user);
  res.status(201).json({ token: jwt.sign({ id: user.id }, SECRET, { expiresIn: '24h' }) });
});
app.post('/auth/login', async (req, res) => {
  const user = users.find(u => u.email === req.body.email);
  if (!user || !(await bcrypt.compare(req.body.password, user.password))) return res.status(401).json({ error: 'Invalid' });
  res.json({ token: jwt.sign({ id: user.id }, SECRET, { expiresIn: '24h' }) });
});

// Create survey with questions
app.post('/surveys', auth, (req, res) => {
  const { title, description, questions } = req.body;
  if (!title || !Array.isArray(questions) || !questions.length) return res.status(400).json({ error: 'title and questions[] required' });
  // Each question: { text, type: 'text'|'rating'|'multiple_choice'|'yes_no', options?: [] }
  const sv = { id: svId++, ownerId: req.user.id, title, description: description || '', questions, responseCount: 0, createdAt: new Date().toISOString(), published: false };
  surveys.push(sv);
  res.status(201).json(sv);
});

app.get('/surveys', (req, res) => {
  res.json(surveys.filter(s => s.published).map(s => ({ id: s.id, title: s.title, description: s.description, questionCount: s.questions.length, responseCount: s.responseCount })));
});

app.get('/surveys/:id', (req, res) => {
  const sv = surveys.find(s => s.id === parseInt(req.params.id));
  sv ? res.json(sv) : res.status(404).json({ error: 'Not found' });
});

app.post('/surveys/:id/publish', auth, (req, res) => {
  const sv = surveys.find(s => s.id === parseInt(req.params.id));
  if (!sv || sv.ownerId !== req.user.id) return res.status(404).json({ error: 'Not found' });
  sv.published = true;
  res.json(sv);
});

// Submit response (no auth — public)
app.post('/surveys/:id/responses', (req, res) => {
  const sv = surveys.find(s => s.id === parseInt(req.params.id) && s.published);
  if (!sv) return res.status(404).json({ error: 'Not found or not published' });
  if (!Array.isArray(req.body.answers) || req.body.answers.length !== sv.questions.length) return res.status(400).json({ error: `Expected ${sv.questions.length} answers` });
  const resp = { id: respId++, surveyId: sv.id, answers: req.body.answers, submittedAt: new Date().toISOString() };
  responses.push(resp);
  sv.responseCount++;
  res.status(201).json({ submitted: true });
});

// Analytics (owner only)
app.get('/surveys/:id/analytics', auth, (req, res) => {
  const sv = surveys.find(s => s.id === parseInt(req.params.id));
  if (!sv || sv.ownerId !== req.user.id) return res.status(404).json({ error: 'Not found' });
  const surveyResponses = responses.filter(r => r.surveyId === sv.id);
  const questionStats = sv.questions.map((q, idx) => {
    const stats = { question: q.text, type: q.type, count: surveyResponses.length };
    if (q.type === 'rating') { const ratings = surveyResponses.map(r => parseInt(r.answers[idx])).filter(n => !isNaN(n)); stats.average = ratings.length ? (ratings.reduce((a, b) => a + b, 0) / ratings.length).toFixed(2) : null; stats.distribution = [1,2,3,4,5].map(r => ratings.filter(x => x === r).length); }
    else if (q.type === 'multiple_choice') { const counts = {}; surveyResponses.forEach(r => { const a = r.answers[idx]; counts[a] = (counts[a] || 0) + 1; }); stats.options = q.options.map(opt => ({ option: opt, count: counts[opt] || 0 })); }
    else if (q.type === 'yes_no') { const counts = { yes: 0, no: 0 }; surveyResponses.forEach(r => { const a = String(r.answers[idx]).toLowerCase(); if (a === 'yes' || a === 'true') counts.yes++; else counts.no++; }); stats.yes = counts.yes; stats.no = counts.no; }
    else { const samples = surveyResponses.slice(0, 5).map(r => r.answers[idx]); stats.samples = samples; }
    return stats;
  });
  res.json({ total: surveyResponses.length, questions: questionStats });
});

app.listen(3000, () => console.log('Survey Builder :3000'));
module.exports = app;
