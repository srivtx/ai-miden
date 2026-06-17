// 32 — Bug Tracker
// Bugs have a status (open/in_progress/closed) and priority (low/medium/high).
const express = require('express');
const app = express();
app.use(express.json());

const bugs = [];

app.get('/bugs', (req, res) => {
  const { status, priority } = req.query;
  let result = bugs;
  if (status) result = result.filter(b => b.status === status);
  if (priority) result = result.filter(b => b.priority === priority);
  res.json({ count: result.length, bugs: result });
});

app.post('/bugs', (req, res) => {
  const { title, description, priority } = req.body;
  const bug = { id: bugs.length + 1, title, description: description || '', status: 'open', priority: priority || 'medium', createdAt: new Date().toISOString() };
  bugs.push(bug);
  res.status(201).json(bug);
});

app.patch('/bugs/:id', (req, res) => {
  const bug = bugs.find(b => b.id === parseInt(req.params.id));
  if (!bug) return res.status(404).json({ error: 'Bug not found' });
  if (req.body.status) bug.status = req.body.status;
  if (req.body.priority) bug.priority = req.body.priority;
  res.json(bug);
});

app.listen(3000, () => console.log('Bug tracker on http://localhost:3000'));
