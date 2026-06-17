// Search Demo — In-memory full-text search (tokenize, index, score, rank).
const express = require('express');
const app = express();
app.use(express.json());

// === In-memory documents ===
const docs = [
  { id: 1, title: 'Express basics', body: 'Express is a Node.js web framework. It is minimal and unopinionated.', category: 'tutorial' },
  { id: 2, title: 'SQL injection', body: 'SQL injection is a code injection technique that exploits security vulnerabilities.', category: 'security' },
  { id: 3, title: 'Rate limiting', body: 'Rate limiting protects your API from abuse. Token bucket is a common algorithm.', category: 'patterns' },
  { id: 4, title: 'Caching strategies', body: 'Cache-aside, write-through, write-behind — three common caching patterns.', category: 'patterns' },
  { id: 5, title: 'Database indexing', body: 'Indexes speed up queries. Composite indexes matter for multi-column WHERE clauses.', category: 'database' },
  { id: 6, title: 'JWT authentication', body: 'JSON Web Tokens are a compact, URL-safe means of representing claims between two parties.', category: 'security' },
  { id: 7, title: 'Pagination patterns', body: 'Offset pagination is simple but slow. Cursor pagination is O(1) per page.', category: 'patterns' },
  { id: 8, title: 'Docker for Node apps', body: 'Docker packages your app and dependencies. Multi-stage builds keep images small.', category: 'devops' },
];

// === Build inverted index ===
function tokenize(text) {
  return text.toLowerCase().match(/[a-z0-9]+/g) || [];
}

const index = new Map(); // term -> [{docId, count}]
for (const doc of docs) {
  const tokens = tokenize(doc.title + ' ' + doc.body);
  for (const t of tokens) {
    if (!index.has(t)) index.set(t, []);
    const list = index.get(t);
    const existing = list.find(x => x.docId === doc.id);
    if (existing) existing.count++;
    else list.push({ docId: doc.id, count: 1 });
  }
}

// Boost title matches (title weight = 3, body weight = 1)
for (const doc of docs) {
  const titleTokens = tokenize(doc.title);
  for (const t of titleTokens) {
    const list = index.get(t) || [];
    const existing = list.find(x => x.docId === doc.id);
    if (existing) existing.count += 2; // extra weight
  }
}

// === Search ===
function search(query, { category, limit = 10 } = {}) {
  const queryTokens = tokenize(query);
  const scores = new Map();
  for (const t of queryTokens) {
    const postings = index.get(t) || [];
    for (const { docId, count } of postings) {
      const doc = docs.find(d => d.id === docId);
      if (category && doc.category !== category) continue;
      scores.set(docId, (scores.get(docId) || 0) + count);
    }
  }
  return Array.from(scores.entries())
    .sort((a, b) => b[1] - a[1])
    .slice(0, limit)
    .map(([docId, score]) => ({ ...docs.find(d => d.id === docId), score, snippet: makeSnippet(docs.find(d => d.id === docId).body, queryTokens) }));
}

function makeSnippet(body, queryTokens) {
  const lower = body.toLowerCase();
  for (const t of queryTokens) {
    const idx = lower.indexOf(t);
    if (idx !== -1) {
      const start = Math.max(0, idx - 30);
      const end = Math.min(body.length, idx + 80);
      return (start > 0 ? '...' : '') + body.slice(start, end) + (end < body.length ? '...' : '');
    }
  }
  return body.slice(0, 80);
}

// === Routes ===
app.get('/search', (req, res) => {
  if (!req.query.q) return res.status(422).json({ error: 'missing_q' });
  const start = process.hrtime.bigint();
  const results = search(req.query.q, { category: req.query.category, limit: parseInt(req.query.limit) || 10 });
  const ms = Number(process.hrtime.bigint() - start) / 1e6;
  res.json({ query: req.query.q, count: results.length, ms: ms.toFixed(2), results });
});

app.get('/admin/index-stats', (req, res) => {
  res.json({
    documentCount: docs.length,
    termCount: index.size,
    topTerms: Array.from(index.entries()).sort((a, b) => b[1].length - a[1].length).slice(0, 10).map(([t, p]) => ({ term: t, docCount: p.length })),
  });
});

app.listen(3000, () => console.log('Search demo :3000'));
module.exports = app;
