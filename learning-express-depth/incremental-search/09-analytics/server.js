// 09-analytics: Track search queries. Top queries, no-result queries, click-through.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE search_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, query TEXT, results_count INTEGER, clicked_position INTEGER, ts TEXT DEFAULT (datetime('now')))`);

// Log a search
app.post('/log/search', (req, res) => {
  const { query, results_count } = req.body;
  if (!query) return res.status(422).json({ error: 'query required' });
  db.prepare('INSERT INTO search_logs (query, results_count) VALUES (?, ?)').run(query, results_count || 0);
  res.json({ logged: true });
});

// Log a click
app.post('/log/click', (req, res) => {
  const { query, position } = req.body;
  if (!query) return res.status(422).json({ error: 'query required' });
  db.prepare('UPDATE search_logs SET clicked_position = ? WHERE id = (SELECT MAX(id) FROM search_logs WHERE query = ?)').run(position, query);
  res.json({ logged: true });
});

// Top queries
app.get('/analytics/top-queries', (req, res) => {
  const top = db.prepare(`
    SELECT query, COUNT(*) as count, AVG(results_count) as avg_results
    FROM search_logs
    GROUP BY query
    ORDER BY count DESC
    LIMIT 20
  `).all();
  res.json({ top });
});

// Queries with no results (improvement opportunities)
app.get('/analytics/no-results', (req, res) => {
  const queries = db.prepare(`
    SELECT query, COUNT(*) as count
    FROM search_logs
    WHERE results_count = 0
    GROUP BY query
    ORDER BY count DESC
    LIMIT 20
  `).all();
  res.json({ no_result_queries: queries });
});

// Click-through rate
app.get('/analytics/ctr', (req, res) => {
  const total = db.prepare('SELECT COUNT(*) as c FROM search_logs').get().c;
  const withClicks = db.prepare('SELECT COUNT(*) as c FROM search_logs WHERE clicked_position IS NOT NULL').get().c;
  res.json({ total_searches: total, with_clicks: withClicks, ctr: total ? (withClicks / total * 100).toFixed(1) : 0 });
});

app.listen(3000, () => console.log('09-analytics on :3000'));
