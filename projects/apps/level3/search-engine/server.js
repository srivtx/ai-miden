// Search Engine — Inverted index, full-text search, relevance ranking, suggestions.
const express = require('express');
const app = express();
app.use(express.json());

const documents = []; // { id, title, content, tags, url, createdAt }
const invertedIndex = new Map(); // term -> Set<docId>
const docFrequency = new Map(); // term -> number of docs containing it

// Indexing
function tokenize(text) {
  return (text || '').toLowerCase().replace(/[^\w\s]/g, ' ').split(/\s+/).filter(t => t.length > 1 && !['the', 'a', 'an', 'is', 'and', 'or', 'but', 'in', 'on', 'at'].includes(t));
}

function indexDocument(doc) {
  const terms = new Set([...tokenize(doc.title), ...tokenize(doc.content), ...(doc.tags || [])]);
  for (const term of terms) {
    if (!invertedIndex.has(term)) invertedIndex.set(term, new Set());
    invertedIndex.get(term).add(doc.id);
    docFrequency.set(term, (docFrequency.get(term) || 0) + 1);
  }
}

function removeFromIndex(docId, doc) {
  for (const term of doc.indexedTerms || []) {
    invertedIndex.get(term)?.delete(docId);
  }
}

// Index a document
app.post('/documents', (req, res) => {
  const { title, content, tags, url } = req.body;
  if (!title || !content) return res.status(400).json({ error: 'title and content required' });
  const doc = { id: documents.length + 1, title, content, tags: tags || [], url: url || null, indexedTerms: [], createdAt: new Date().toISOString() };
  doc.indexedTerms = [...new Set([...tokenize(title), ...tokenize(content), ...(tags || [])])];
  documents.push(doc);
  indexDocument(doc);
  res.status(201).json({ id: doc.id, title, indexedTerms: doc.indexedTerms.length });
});

app.get('/documents/:id', (req, res) => {
  const doc = documents.find(d => d.id === parseInt(req.params.id));
  doc ? res.json(doc) : res.status(404).json({ error: 'Not found' });
});

// Search
app.get('/search', (req, res) => {
  const { q, limit = 10, tags } = req.query;
  if (!q) return res.status(400).json({ error: 'q (query) required' });
  const queryTerms = tokenize(q);
  if (!queryTerms.length) return res.json({ results: [] });

  // TF-IDF scoring
  const scores = new Map(); // docId -> score
  const totalDocs = documents.length;
  for (const term of queryTerms) {
    const docs = invertedIndex.get(term);
    if (!docs) continue;
    const df = docFrequency.get(term) || 1;
    const idf = Math.log(totalDocs / (df + 1)) + 1;
    for (const docId of docs) {
      const doc = documents.find(d => d.id === docId);
      if (!doc) continue;
      // Term frequency in this doc
      const tf = (doc.content.toLowerCase().match(new RegExp(term, 'g')) || []).length + (doc.title.toLowerCase().match(new RegExp(term, 'g')) || []).length * 5;
      const score = tf * idf;
      // Boost if in title or tags
      if (doc.title.toLowerCase().includes(term)) score += 10;
      if ((doc.tags || []).some(t => t.toLowerCase().includes(term))) score += 5;
      scores.set(docId, (scores.get(docId) || 0) + score);
    }
  }

  // Tag filter
  let results = [...scores.entries()].map(([id, score]) => ({ id, score, doc: documents.find(d => d.id === id) }));
  if (tags) {
    const filterTags = tags.split(',');
    results = results.filter(r => filterTags.some(t => (r.doc.tags || []).includes(t)));
  }

  results.sort((a, b) => b.score - a.score);
  results = results.slice(0, parseInt(limit));
  res.json({ query: q, total: results.length, results: results.map(r => ({ id: r.id, score: r.score.toFixed(2), title: r.doc.title, snippet: r.doc.content.slice(0, 200), url: r.doc.url, tags: r.doc.tags })) });
});

// Autocomplete
app.get('/suggest', (req, res) => {
  const prefix = (req.query.q || '').toLowerCase().trim();
  if (prefix.length < 2) return res.json({ suggestions: [] });
  const matches = [];
  for (const term of invertedIndex.keys()) {
    if (term.startsWith(prefix)) matches.push({ term, count: docFrequency.get(term) });
  }
  matches.sort((a, b) => b.count - a.count);
  res.json({ suggestions: matches.slice(0, 10) });
});

// Index stats
app.get('/stats', (req, res) => {
  res.json({ documents: documents.length, uniqueTerms: invertedIndex.size, totalPostings: [...invertedIndex.values()].reduce((a, s) => a + s.size, 0) });
});

app.listen(3000, () => console.log('Search Engine :3000'));
module.exports = app;
