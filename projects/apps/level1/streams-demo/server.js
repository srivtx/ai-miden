// Streams Demo — Read large data in chunks, backpressure, pipe patterns.
const express = require('express');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const app = express();

const DATA_DIR = path.join(__dirname, 'data');
if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR);

// Generate a 10MB file to stream
const bigFile = path.join(DATA_DIR, 'big.txt');
if (!fs.existsSync(bigFile)) {
  const ws = fs.createWriteStream(bigFile);
  for (let i = 0; i < 100000; i++) ws.write(`Line ${i}: ${crypto.randomBytes(20).toString('hex')}\n`);
  ws.end();
}

// === Stream a file to response (backpressure aware) ===
app.get('/stream/file', (req, res) => {
  res.set('Content-Type', 'text/plain');
  const stream = fs.createReadStream(bigFile);
  stream.pipe(res);
});

// === Stream a generated response (NDJSON, one JSON per line) ===
app.get('/stream/ndjson', (req, res) => {
  res.set('Content-Type', 'application/x-ndjson');
  let i = 0;
  const interval = setInterval(() => {
    if (i >= 100) { clearInterval(interval); return res.end(); }
    const ok = res.write(JSON.stringify({ i, ts: Date.now(), data: crypto.randomBytes(8).toString('hex') }) + '\n');
    i++;
    if (!ok) { clearInterval(interval); res.once('drain', () => { /* would resume here */ }); }
  }, 10);
});

// === Stream a CSV (large export) ===
app.get('/stream/csv', (req, res) => {
  res.set('Content-Type', 'text/csv');
  res.set('Content-Disposition', 'attachment; filename=export.csv');
  res.write('id,name,email,score\n');
  for (let i = 1; i <= 10000; i++) {
    res.write(`${i},User ${i},user${i}@example.com,${(i * 7) % 100}\n`);
  }
  res.end();
});

// === Server-Sent Events (one-way streaming) ===
app.get('/stream/sse', (req, res) => {
  res.set({
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
  });
  res.flushHeaders();
  let n = 0;
  const interval = setInterval(() => {
    n++;
    res.write(`event: tick\ndata: {"n":${n},"ts":${Date.now()}}\n\n`);
    if (n >= 20) { clearInterval(interval); res.end(); }
  }, 200);
  req.on('close', () => clearInterval(interval));
});

// === Receive a stream (large upload) ===
app.put('/stream/upload', (req, res) => {
  let bytes = 0;
  const out = fs.createWriteStream(path.join(DATA_DIR, 'uploaded.bin'));
  req.on('data', chunk => { bytes += chunk.length; out.write(chunk); });
  req.on('end', () => { out.end(); res.json({ received: bytes }); });
  req.on('error', e => res.status(500).json({ error: e.message }));
});

// === File info ===
app.get('/admin/file-info', (req, res) => {
  const stat = fs.existsSync(bigFile) ? fs.statSync(bigFile) : null;
  res.json({ bigFile: stat ? { size: stat.size, lines: '~100000' } : null });
});

app.listen(3000, () => console.log('Streams demo :3000'));
module.exports = app;
