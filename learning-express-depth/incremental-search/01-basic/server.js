// 01-basic: Simple search. Substring match on title and body. No ranking.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();

const db = new Database(':memory:');
db.exec(`CREATE TABLE documents (id INTEGER PRIMARY KEY, title TEXT, body TEXT)`);

// Seed
const docs = [
  { title: 'How to learn JavaScript', body: 'JavaScript is a programming language. To learn JavaScript, practice every day.' },
  { title: 'Python tutorial', body: 'Python is a popular language. Python is great for data science.' },
  { title: 'Web development', body: 'Web development involves HTML, CSS, and JavaScript.' },
  { title: 'Data science basics', body: 'Data science uses Python, R, and statistics.' },
];
for (const d of docs) db.prepare('INSERT INTO documents (title, body) VALUES (?, ?)').run(d.title, d.body);

app.get('/search', (req, res) => {
  const { q } = req.query;
  if (!q) return res.status(422).json({ error: 'q required' });
  const term = `%${q.toLowerCase()}%`;
  const results = db.prepare('SELECT * FROM documents WHERE LOWER(title) LIKE ? OR LOWER(body) LIKE ?').all(term, term);
  res.json({ query: q, count: results.length, results });
});

app.listen(3000, () => console.log('01-basic on :3000'));
