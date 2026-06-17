// 09-compression: Compress text files on upload. Save 70-90% on text. Track savings.
const express = require('express');
const Database = require('better-sqlite3');
const zlib = require('zlib');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE files (id TEXT PRIMARY KEY, name TEXT, original_size INTEGER, stored_size INTEGER, compression_ratio REAL, compressed INTEGER DEFAULT 1)`);

app.post('/files', (req, res) => {
  const { name, content } = req.body;
  if (!name) return res.status(422).json({ error: 'name required' });
  if (typeof content !== 'string') return res.status(422).json({ error: 'content must be string' });
  const originalSize = Buffer.byteLength(content);
  const compressed = zlib.gzipSync(content);
  const storedSize = compressed.length;
  const ratio = originalSize / storedSize;
  const id = 'f_' + Math.random().toString(36).slice(2, 10);
  db.prepare('INSERT INTO files VALUES (?, ?, ?, ?, ?, 1)').run(id, name, originalSize, storedSize, ratio);
  res.status(201).json({ id, name, original_size: originalSize, stored_size: storedSize, ratio: Math.round(ratio * 100) / 100 });
});

app.get('/files/:id', (req, res) => {
  const f = db.prepare('SELECT id, name, original_size, stored_size, compression_ratio, compressed FROM files WHERE id = ?').get(req.params.id);
  f ? res.json(f) : res.status(404).json({ error: 'not found' });
});

// Total savings
app.get('/stats', (req, res) => {
  const totals = db.prepare('SELECT SUM(original_size) as original, SUM(stored_size) as stored FROM files').get();
  const ratio = totals.original && totals.stored ? totals.original / totals.stored : 1;
  res.json({ total_original: totals.original, total_stored: totals.stored, ratio: Math.round(ratio * 100) / 100 });
});

app.listen(3000, () => console.log('09-compression on :3000 (gzip text files)'));
