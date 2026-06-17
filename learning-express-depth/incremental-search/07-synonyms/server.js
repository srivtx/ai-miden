// 07-synonyms: "phone" should match "mobile". Query expansion.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();

const db = new Database(':memory:');
db.exec(`CREATE VIRTUAL TABLE docs USING fts5(title, body)`);
db.exec(`CREATE TABLE synonyms (word TEXT, synonym TEXT, PRIMARY KEY (word, synonym))`);

// Seed synonyms
const seed = [
  ['phone', 'mobile'], ['phone', 'cellphone'], ['mobile', 'phone'],
  ['car', 'vehicle'], ['car', 'auto'], ['vehicle', 'car'],
  ['tv', 'television'], ['laptop', 'notebook'],
  ['photo', 'picture'], ['photo', 'image'],
];
for (const s of seed) db.prepare('INSERT OR IGNORE INTO synonyms VALUES (?, ?)').run(...s);

const docs = ['Best mobile phones 2024', 'Top cellphone deals', 'Cellphone reviews'];
for (const d of docs) db.prepare('INSERT INTO docs (title, body) VALUES (?, ?)').run(d, d);

function expandQuery(query) {
  const words = query.toLowerCase().match(/[a-z]+/g) || [];
  const expanded = new Set(words);
  for (const w of words) {
    const syns = db.prepare('SELECT synonym FROM synonyms WHERE word = ?').all(w);
    for (const s of syns) expanded.add(s);
  }
  return Array.from(expanded).join(' OR ');
}

app.get('/search', (req, res) => {
  const { q } = req.query;
  if (!q) return res.status(422).json({ error: 'q required' });
  const expanded = expandQuery(q);
  const results = db.prepare('SELECT * FROM docs WHERE docs MATCH ? ORDER BY rank').all(expanded);
  res.json({ query: q, expanded_query: expanded, results });
});

app.get('/admin/synonyms', (req, res) => res.json({ synonyms: db.prepare('SELECT * FROM synonyms').all() }));
app.post('/admin/synonyms', (req, res) => {
  const { word, synonym } = req.body;
  if (!word || !synonym) return res.status(422).json({ error: 'word and synonym required' });
  db.prepare('INSERT OR IGNORE INTO synonyms VALUES (?, ?)').run(word.toLowerCase(), synonym.toLowerCase());
  res.json({ added: true });
});

app.listen(3000, () => console.log('07-synonyms on :3000 (phone ↔ mobile ↔ cellphone)'));
