// 51 — Streams
// NEW CONCEPT: stream a large file in chunks instead of loading it all at once.
// Useful for big files: don't load 1GB into memory, send it piece by piece.
const express = require('express');
const fs = require('fs');
const path = require('path');
const app = express();

// Generate a large file for testing
const BIG_FILE = path.join(__dirname, 'big.txt');
if (!fs.existsSync(BIG_FILE)) {
  const ws = fs.createWriteStream(BIG_FILE);
  for (let i = 0; i < 100000; i++) ws.write(`Line ${i}: This is some content for testing the stream.\n`);
  ws.end();
}

// Stream a file to the response
app.get('/stream/file', (req, res) => {
  res.set('Content-Type', 'text/plain');
  fs.createReadStream(BIG_FILE).pipe(res);
});

// Stream JSON (one record per line, newline-delimited JSON)
app.get('/stream/ndjson', (req, res) => {
  res.set('Content-Type', 'application/x-ndjson');
  let i = 0;
  const interval = setInterval(() => {
    if (i >= 100) { clearInterval(interval); return res.end(); }
    res.write(JSON.stringify({ id: i, ts: Date.now(), data: `record ${i}` }) + '\n');
    i++;
  }, 50);
});

// Stream a CSV
app.get('/stream/csv', (req, res) => {
  res.set('Content-Type', 'text/csv');
  res.set('Content-Disposition', 'attachment; filename=export.csv');
  res.write('id,name,email\n');
  for (let i = 0; i < 10000; i++) {
    res.write(`${i},User ${i},user${i}@example.com\n`);
  }
  res.end();
});

// Receive a stream (large upload)
app.put('/upload-stream', (req, res) => {
  let bytes = 0;
  req.on('data', chunk => { bytes += chunk.length; });
  req.on('end', () => res.json({ received: bytes }));
  req.on('error', e => res.status(500).json({ error: e.message }));
});

app.listen(3000, () => console.log('Streams on http://localhost:3000'));
