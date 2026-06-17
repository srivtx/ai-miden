// 02-relevance: Rank results by score. Title matches count more. Word frequency matters.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();

const db = new Database(':memory:');
db.exec(`CREATE TABLE documents (id INTEGER PRIMARY KEY, title TEXT, body TEXT)`);
const docs = [
  { title: 'How to learn JavaScript', body: 'JavaScript is a programming language. To learn JavaScript, practice every day. JavaScript is used in web development.' },
  { title: 'Python tutorial', body: 'Python is a popular language. Python is great for data science. Python is easy to learn.' },
  { title: 'Web development', body: 'Web development involves HTML, CSS, and JavaScript. JavaScript is essential for web development.' },
  { title: 'Data science basics', body: 'Data science uses Python, R, and statistics. Python is the most popular tool for data science.' },
];
for (const d of docs) db.prepare('INSERT INTO documents (title, body) VALUES (?, ?)').run(d.title, d.body);

function tokenize(text) {
  return text.toLowerCase().match(/[a-z0-9]+/g) || [];
}

function score(doc, queryTokens) {
  let score = 0;
  const docTokens = tokenize(doc.title + ' ' + doc.body);
  for (const term of queryTokens) {
    const count = docTokens.filter(t => t === term).length;
    score += count;
  }
  // Title boost
  const titleLower = doc.title.toLowerCase();
  for (const term of queryTokens) {
    if (titleLower.includes(term)) score += 5;
  }
  return score;
}

app.get('/search', (req, res) => {
  const { q } = req.query;
  if (!q) return res.status(422).json({ error: 'q required' });
  const queryTokens = tokenize(q);
  const scored = db.prepare('SELECT * FROM documents').all().map(d => ({ ...d, score: score(d, queryTokens) })).filter(d => d.score > 0).sort((a, b) => b.score - a.score);
  res.json({ query: q, count: scored.length, results: scored });
});

app.listen(3000, () => console.log('02-relevance on :3000 (title boost, frequency)'));
