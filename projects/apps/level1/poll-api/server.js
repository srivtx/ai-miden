// Poll API — Create polls, vote, view results, expiration, duplicate prevention.
const express = require('express');
const app = express();
app.use(express.json());

const polls = new Map(); // id -> { question, options:Map, voters:Set, expiresAt, createdAt }

// Create poll
app.post('/polls', (req, res) => {
  const { question, options, expiresIn } = req.body;
  if (!question || !options || !Array.isArray(options) || options.length < 2) return res.status(400).json({ error: 'question and options[] (min 2) required' });
  const id = Date.now().toString(36);
  polls.set(id, {
    question, options: new Map(options.map(o => [o, 0])), voters: new Set(),
    createdAt: new Date().toISOString(),
    expiresAt: expiresIn ? new Date(Date.now() + expiresIn * 3600000).toISOString() : null,
  });
  res.status(201).json({ id, link: `/polls/${id}` });
});

// Get poll
app.get('/polls/:id', (req, res) => {
  const poll = polls.get(req.params.id);
  if (!poll) return res.status(404).json({ error: 'Not found' });
  if (poll.expiresAt && new Date() > new Date(poll.expiresAt)) { polls.delete(req.params.id); return res.status(410).json({ error: 'Expired' }); }
  const totalVotes = [...poll.options.values()].reduce((a, b) => a + b, 0);
  const results = Object.fromEntries([...poll.options.entries()].map(([opt, count]) => [opt, { count, percentage: totalVotes ? ((count / totalVotes) * 100).toFixed(1) : '0.0' }]));
  res.json({ id: req.params.id, question: poll.question, options: results, totalVotes, isExpired: false });
});

// Vote
app.post('/polls/:id/vote', (req, res) => {
  const poll = polls.get(req.params.id);
  if (!poll) return res.status(404).json({ error: 'Not found' });
  if (poll.expiresAt && new Date() > new Date(poll.expiresAt)) return res.status(410).json({ error: 'Poll expired' });

  const { option, voterId } = req.body;
  if (!option || !poll.options.has(option)) return res.status(400).json({ error: 'Invalid option' });
  const voter = voterId || req.ip;
  if (poll.voters.has(voter)) return res.status(409).json({ error: 'Already voted' });

  poll.options.set(option, poll.options.get(option) + 1);
  poll.voters.add(voter);
  res.json({ voted: option, voterCount: poll.voters.size });
});

// List active polls
app.get('/polls', (req, res) => {
  const now = new Date();
  const active = [...polls.entries()]
    .filter(([, p]) => !p.expiresAt || now <= new Date(p.expiresAt))
    .map(([id, p]) => ({ id, question: p.question, votes: poll.voters.size, createdAt: p.createdAt }));
  res.json({ count: active.length, polls: active });
});

app.listen(3000, () => console.log('Poll API :3000'));
module.exports = app;
