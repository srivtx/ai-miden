// 06-spellcheck: "javscript" should match "javascript". Suggest corrections.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();

const db = new Database(':memory:');
db.exec(`CREATE VIRTUAL TABLE docs USING fts5(title, body)`);

const docs = [
  'JavaScript is a programming language', 'Python is great for data science', 'JavaScript frameworks include React',
];
for (const d of docs) db.prepare('INSERT INTO docs (title, body) VALUES (?, ?)').run(d, d);

// Levenshtein distance
function levenshtein(a, b) {
  if (a.length === 0) return b.length;
  if (b.length === 0) return a.length;
  const matrix = Array.from({ length: a.length + 1 }, () => Array(b.length + 1).fill(0));
  for (let i = 0; i <= a.length; i++) matrix[i][0] = i;
  for (let j = 0; j <= b.length; j++) matrix[0][j] = j;
  for (let i = 1; i <= a.length; i++) {
    for (let j = 1; j <= b.length; j++) {
      const cost = a[i - 1] === b[j - 1] ? 0 : 1;
      matrix[i][j] = Math.min(matrix[i - 1][j] + 1, matrix[i][j - 1] + 1, matrix[i - 1][j - 1] + cost);
    }
  }
  return matrix[a.length][b.length];
}

// Build vocabulary from indexed docs
const vocab = new Set();
for (const d of docs) for (const word of d.toLowerCase().match(/[a-z]+/g) || []) vocab.add(word);

// Spell check: find closest words
function spellCheck(query) {
  const queryWords = query.toLowerCase().match(/[a-z]+/g) || [];
  const corrected = [];
  for (const qWord of queryWords) {
    if (vocab.has(qWord)) { corrected.push(qWord); continue; }
    // Find closest match
    let best = qWord, bestDist = Infinity;
    for (const word of vocab) {
      if (Math.abs(word.length - qWord.length) > 3) continue;  // skip very different lengths
      const dist = levenshtein(qWord, word);
      if (dist < bestDist) { bestDist = dist; best = word; }
    }
    corrected.push(bestDist <= 2 ? best : qWord);
  }
  return corrected.join(' ');
}

app.get('/search', (req, res) => {
  const { q } = req.query;
  if (!q) return res.status(422).json({ error: 'q required' });
  const corrected = spellCheck(q);
  const didCorrect = corrected !== q.toLowerCase();
  const results = db.prepare('SELECT * FROM docs WHERE docs MATCH ? ORDER BY rank').all(corrected);
  res.json({ query: q, corrected_query: corrected, did_correct: didCorrect, results });
});

app.listen(3000, () => console.log('06-spellcheck on :3000 (typo correction via Levenshtein)'));
