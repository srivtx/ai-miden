// 34 — Survey App
// A survey has questions, each with options. Track responses.
const express = require('express');
const app = express();
app.use(express.json());

const surveys = [];
const responses = [];

// Create a survey
app.post('/surveys', (req, res) => {
  const { title, questions } = req.body;
  const survey = { id: surveys.length + 1, title, questions, createdAt: new Date().toISOString() };
  surveys.push(survey);
  res.status(201).json(survey);
});

app.get('/surveys', (req, res) => {
  res.json({ count: surveys.length, surveys });
});

app.get('/surveys/:id', (req, res) => {
  const survey = surveys.find(s => s.id === parseInt(req.params.id));
  if (!survey) return res.status(404).json({ error: 'Survey not found' });
  res.json(survey);
});

// Submit responses: { answers: [0, 2, 1] } (indices of chosen options per question)
app.post('/surveys/:id/responses', (req, res) => {
  const survey = surveys.find(s => s.id === parseInt(req.params.id));
  if (!survey) return res.status(404).json({ error: 'Survey not found' });
  const { answers, respondent } = req.body;
  const response = { id: responses.length + 1, surveyId: survey.id, answers, respondent: respondent || 'anonymous', submittedAt: new Date().toISOString() };
  responses.push(response);
  res.status(201).json(response);
});

// Survey results: count of each option per question
app.get('/surveys/:id/results', (req, res) => {
  const survey = surveys.find(s => s.id === parseInt(req.params.id));
  if (!survey) return res.status(404).json({ error: 'Survey not found' });
  const surveyResponses = responses.filter(r => r.surveyId === survey.id);
  const results = survey.questions.map((q, qi) => {
    const counts = q.options.map(() => 0);
    for (const r of surveyResponses) {
      if (r.answers[qi] !== undefined) counts[r.answers[qi]]++;
    }
    return { question: q.text, options: q.options, counts };
  });
  res.json({ survey: survey.title, responseCount: surveyResponses.length, results });
});

app.listen(3000, () => console.log('Survey app on http://localhost:3000'));
