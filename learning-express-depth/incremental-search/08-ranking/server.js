// 08-ranking: Learn from clicks. Pages that get clicked more rank higher (CTR-based).
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE VIRTUAL TABLE docs USING fts5(title, body)`);
db.exec(`CREATE TABLE doc_stats (doc_id INTEGER PRIMARY KEY, impressions INTEGER DEFAULT 0, clicks INTEGER DEFAULT 0, ctr REAL DEFAULT 0)`);

const docs = ['JavaScript guide', 'Python tutorial', 'JavaScript for beginners'];
for (const d of docs) db.prepare('INSERT INTO docs (rowid, title, body) VALUES (last_insert_rowid(), ?, ?)').run(d, d);
for (let i = 1; i <= docs.length; i++) db.prepare('INSERT INTO doc_stats (doc_id) VALUES (?)').run(i);

// Track impression (shown in results)
app.post('/track/impression', (req, res) => {
  const { doc_ids } = req.body;
  if (!Array.isArray(doc_ids)) return res.status(422).json({ error: 'doc_ids required' });
  for (const id of doc_ids) {
    db.prepare('UPDATE doc_stats SET impressions = impressions + 1 WHERE doc_id = ?').run(id);
  }
  res.json({ tracked: doc_ids.length });
});

// Track click (user clicked on a result)
app.post('/track/click', (req, res) => {
  const { doc_id } = req.body;
  if (!doc_id) return res.status(422).json({ error: 'doc_id required' });
  db.prepare('UPDATE doc_stats SET clicks = clicks + 1, ctr = (clicks + 1.0) / MAX(impressions, 1) WHERE doc_id = ?').run(doc_id);
  res.json({ tracked: true });
});

// Search with CTR-based boost
app.get('/search', (req, res) => {
  const { q } = req.query;
  if (!q) return res.status(422).json({ error: 'q required' });
  const ftsResults = db.prepare('SELECT rowid as id, title FROM docs WHERE docs MATCH ? ORDER BY rank').all(q);
  // Boost by CTR
  const boosted = ftsResults.map(r => {
    const stats = db.prepare('SELECT impressions, clicks, ctr FROM doc_stats WHERE doc_id = ?').get(r.id) || { ctr: 0 };
    return { ...r, ctr: stats.ctr, score: (1 - (r.ctr || 0)) + (stats.ctr || 0) * 2 };  // higher CTR = higher score
  }).sort((a, b) => b.score - a.score);
  res.json({ query: q, results: boosted });
});

app.get('/admin/stats', (req, res) => {
  res.json({ stats: db.prepare('SELECT * FROM doc_stats').all() });
});

app.listen(3000, () => console.log('08-ranking on :3000 (CTR-based boost)'));
