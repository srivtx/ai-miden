// 43 — Search with Ranking
// NEW CONCEPT: full-text search with relevance ranking.
// Naive search: substring. Better: score by how well it matches.
const express = require('express');
const app = express();

// Sample documents
const docs = [
  { id: 1, title: 'How to learn JavaScript', body: 'JavaScript is a programming language. To learn JavaScript, practice every day. JavaScript is used in web development.' },
  { id: 2, title: 'Python tutorial', body: 'Python is a popular language. Python is great for data science. Python is easy to learn.' },
  { id: 3, title: 'Web development', body: 'Web development involves HTML, CSS, and JavaScript. JavaScript is essential for web development.' },
  { id: 4, title: 'Data science basics', body: 'Data science uses Python, R, and statistics. Python is the most popular tool for data science.' },
];

// Tokenize: split into words, lowercase
function tokenize(text) {
  return text.toLowerCase().match(/[a-z0-9]+/g) || [];
}

// Score a document against a query
function score(doc, queryTokens) {
  let score = 0;
  const docTokens = tokenize(doc.title + ' ' + doc.body);

  for (const term of queryTokens) {
    // Count occurrences in the doc
    const count = docTokens.filter(t => t === term).length;
    score += count;
  }

  // Boost: matches in the title count more
  const titleLower = doc.title.toLowerCase();
  for (const term of queryTokens) {
    if (titleLower.includes(term)) score += 5;
  }

  return score;
}

// Search endpoint
app.get('/search', (req, res) => {
  const { q } = req.query;
  if (!q) return res.status(422).json({ error: 'q is required' });

  const queryTokens = tokenize(q);
  const scored = docs
    .map(doc => ({ ...doc, score: score(doc, queryTokens) }))
    .filter(d => d.score > 0)
    .sort((a, b) => b.score - a.score);

  res.json({ query: q, count: scored.length, results: scored });
});

app.listen(3000, () => console.log('Search on http://localhost:3000'));
