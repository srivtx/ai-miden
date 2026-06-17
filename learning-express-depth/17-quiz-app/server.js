// 17 — Quiz App
// A quiz has questions, each with options and a correct answer.
// Submit answers, get a score.
const express = require('express');
const app = express();
app.use(express.json());

const quizzes = [];

app.get('/quizzes', (req, res) => {
  // Don't send the correct answers to the client!
  res.json({
    count: quizzes.length,
    quizzes: quizzes.map(q => ({
      id: q.id,
      title: q.title,
      questions: q.questions.map(question => ({
        text: question.text,
        options: question.options,
      })),
    })),
  });
});

app.post('/quizzes', (req, res) => {
  const { title, questions } = req.body;
  const quiz = { id: quizzes.length + 1, title, questions, createdAt: new Date().toISOString() };
  quizzes.push(quiz);
  res.status(201).json(quiz);
});

// Submit answers: { answers: [0, 2, 1] } (indices of chosen options)
app.post('/quizzes/:id/submit', (req, res) => {
  const quiz = quizzes.find(q => q.id === parseInt(req.params.id));
  if (!quiz) return res.status(404).json({ error: 'Quiz not found' });
  const { answers } = req.body;
  let score = 0;
  for (let i = 0; i < quiz.questions.length; i++) {
    if (answers[i] === quiz.questions[i].correctIndex) score++;
  }
  res.json({ score, total: quiz.questions.length, percent: Math.round((score / quiz.questions.length) * 100) });
});

app.listen(3000, () => console.log('Quiz server on http://localhost:3000'));
