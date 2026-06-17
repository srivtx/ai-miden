// 33 — Feedback App
// Submissions have a rating (1-5) and a comment. Compute average rating.
const express = require('express');
const app = express();
app.use(express.json());

const submissions = [];

app.get('/feedback', (req, res) => {
  res.json({ count: submissions.length, submissions });
});

app.post('/feedback', (req, res) => {
  const { rating, comment, email } = req.body;
  if (rating < 1 || rating > 5) return res.status(422).json({ error: 'rating must be 1-5' });
  const submission = { id: submissions.length + 1, rating, comment: comment || '', email: email || null, createdAt: new Date().toISOString() };
  submissions.push(submission);
  res.status(201).json(submission);
});

// Average rating
app.get('/feedback/stats', (req, res) => {
  if (submissions.length === 0) return res.json({ average: 0, count: 0, distribution: {} });
  const sum = submissions.reduce((s, f) => s + f.rating, 0);
  const distribution = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 };
  for (const f of submissions) distribution[f.rating]++;
  res.json({ average: (sum / submissions.length).toFixed(2), count: submissions.length, distribution });
});

app.listen(3000, () => console.log('Feedback app on http://localhost:3000'));
