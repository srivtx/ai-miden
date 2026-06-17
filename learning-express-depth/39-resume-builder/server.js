// 39 — Resume Builder
// A resume has sections: experience, education, skills. PUT replaces the whole thing.
const express = require('express');
const app = express();
app.use(express.json());

// One resume, in memory. Real apps would have one per user.
let resume = { name: '', email: '', experience: [], education: [], skills: [] };

app.get('/resume', (req, res) => {
  res.json(resume);
});

// PUT /resume — replace the whole resume
app.put('/resume', (req, res) => {
  const { name, email, experience, education, skills } = req.body;
  resume = {
    name: name || '',
    email: email || '',
    experience: experience || [],
    education: education || [],
    skills: skills || [],
  };
  res.json(resume);
});

// PATCH /resume — update just one section
app.patch('/resume/:section', (req, res) => {
  const valid = ['experience', 'education', 'skills'];
  if (!valid.includes(req.params.section)) {
    return res.status(422).json({ error: `section must be one of: ${valid.join(', ')}` });
  }
  resume[req.params.section] = req.body;
  res.json(resume);
});

app.listen(3000, () => console.log('Resume builder on http://localhost:3000'));
