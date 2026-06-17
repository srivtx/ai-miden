// 10-ml-ranking: Use ML to learn the best ranking. Features + weights from training data.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE docs (id INTEGER PRIMARY KEY, title TEXT, body TEXT, popularity INTEGER DEFAULT 0, freshness_days INTEGER DEFAULT 0)`);

const docs = [
  { title: 'JavaScript guide', body: 'Comprehensive JS tutorial for beginners', popularity: 100, freshness_days: 5 },
  { title: 'Python tutorial', body: 'Python for data science and web', popularity: 80, freshness_days: 30 },
  { title: 'JavaScript for beginners', body: 'Learn JavaScript step by step', popularity: 50, freshness_days: 1 },
];
for (const d of docs) db.prepare('INSERT INTO docs (title, body, popularity, freshness_days) VALUES (?, ?, ?, ?)').run(d.title, d.body, d.popularity, d.freshness_days);

// Weights learned from training (in real life, fit a model)
const WEIGHTS = {
  text_relevance: 1.0,
  title_match: 2.0,
  popularity: 0.5,
  freshness: 0.3,
  body_length_match: 0.1,
};

function computeFeatures(query, doc) {
  const queryTokens = query.toLowerCase().match(/[a-z]+/g) || [];
  const titleLower = doc.title.toLowerCase();
  const bodyLower = doc.body.toLowerCase();
  return {
    text_relevance: queryTokens.filter(t => bodyLower.includes(t)).length,
    title_match: queryTokens.filter(t => titleLower.includes(t)).length,
    popularity: Math.log(doc.popularity + 1),
    freshness: 1 / (doc.freshness_days + 1),
    body_length_match: 1 / (1 + Math.abs(doc.body.length - 200) / 200),
  };
}

function scoreDoc(query, doc) {
  const features = computeFeatures(query, doc);
  return Object.entries(WEIGHTS).reduce((sum, [key, weight]) => sum + features[key] * weight, 0);
}

app.get('/search', (req, res) => {
  const { q } = req.query;
  if (!q) return res.status(422).json({ error: 'q required' });
  const scored = db.prepare('SELECT * FROM docs').all().map(d => {
    const features = computeFeatures(q, d);
    return { ...d, features, score: scoreDoc(q, d) };
  }).sort((a, b) => b.score - a.score);
  res.json({ query: q, results: scored });
});

// Update weights from training data (in real life, this is gradient descent)
app.post('/train', (req, res) => {
  const { weights } = req.body;
  if (!weights) return res.status(422).json({ error: 'weights required' });
  Object.assign(WEIGHTS, weights);
  res.json({ updated: WEIGHTS });
});

app.get('/weights', (req, res) => res.json({ weights: WEIGHTS }));

app.listen(3000, () => console.log('10-ml-ranking on :3000 (weighted feature scoring)'));
