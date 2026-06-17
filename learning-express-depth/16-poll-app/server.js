// 16 — Poll App
// A poll has a question and a list of options. Users vote on an option.
// NEW: a vote endpoint that increments the count for one option.
const express = require('express');
const app = express();
app.use(express.json());

const polls = [];

app.get('/polls', (req, res) => {
  res.json({ count: polls.length, polls });
});

app.post('/polls', (req, res) => {
  const { question, options } = req.body;
  const poll = {
    id: polls.length + 1,
    question,
    options: options.map(text => ({ text, votes: 0 })),
  };
  polls.push(poll);
  res.status(201).json(poll);
});

app.get('/polls/:id', (req, res) => {
  const poll = polls.find(p => p.id === parseInt(req.params.id));
  if (!poll) return res.status(404).json({ error: 'Poll not found' });
  res.json(poll);
});

// NEW: vote endpoint. POST /polls/:id/vote { optionIndex: 0 }
app.post('/polls/:id/vote', (req, res) => {
  const poll = polls.find(p => p.id === parseInt(req.params.id));
  if (!poll) return res.status(404).json({ error: 'Poll not found' });
  const { optionIndex } = req.body;
  if (optionIndex === undefined || !poll.options[optionIndex]) {
    return res.status(422).json({ error: 'Invalid option' });
  }
  poll.options[optionIndex].votes += 1;
  res.json(poll);
});

app.listen(3000, () => console.log('Poll server on http://localhost:3000'));
