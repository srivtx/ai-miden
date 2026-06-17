// File Upload Demo — Multipart parsing, validation, storage, download. No multer (manual).
const express = require('express');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const app = express();

const UPLOAD_DIR = path.join(__dirname, 'uploads');
if (!fs.existsSync(UPLOAD_DIR)) fs.mkdirSync(UPLOAD_DIR);

const ALLOWED_TYPES = { 'image/png': '.png', 'image/jpeg': '.jpg', 'image/gif': '.gif', 'text/plain': '.txt' };
const MAX_SIZE = 5 * 1024 * 1024; // 5MB

// === Tiny multipart parser (single file) ===
function parseMultipart(req) {
  return new Promise((resolve, reject) => {
    const ct = req.headers['content-type'] || '';
    if (!ct.startsWith('multipart/form-data')) return reject(new Error('Not multipart'));
    const boundary = '--' + ct.split('boundary=')[1];
    const chunks = [];
    req.on('data', c => chunks.push(c));
    req.on('end', () => {
      const body = Buffer.concat(chunks).toString('binary');
      const parts = body.split(boundary).filter(p => p && p !== '--\r\n' && p !== '--');
      const file = { filename: null, type: null, data: Buffer.alloc(0) };
      for (const part of parts) {
        const headerEnd = part.indexOf('\r\n\r\n');
        if (headerEnd === -1) continue;
        const headers = part.slice(0, headerEnd);
        const content = part.slice(headerEnd + 4, part.endsWith('\r\n') ? -2 : undefined);
        const fnMatch = headers.match(/filename="([^"]+)"/);
        if (fnMatch) {
          file.filename = fnMatch[1];
          file.type = (headers.match(/Content-Type:\s*([^\r\n]+)/i) || [])[1] || 'application/octet-stream';
          file.data = Buffer.from(content, 'binary');
        }
      }
      resolve(file);
    });
    req.on('error', reject);
  });
}

// === Routes ===
app.post('/upload', async (req, res) => {
  try {
    const file = await parseMultipart(req);
    if (!file.filename) return res.status(400).json({ error: 'no_file' });
    if (file.data.length > MAX_SIZE) return res.status(413).json({ error: 'too_large', size: file.data.length, max: MAX_SIZE });
    if (!ALLOWED_TYPES[file.type]) return res.status(415).json({ error: 'unsupported_type', type: file.type, allowed: Object.keys(ALLOWED_TYPES) });
    const id = crypto.randomBytes(8).toString('hex');
    const ext = ALLOWED_TYPES[file.type];
    const stored = `${id}${ext}`;
    fs.writeFileSync(path.join(UPLOAD_DIR, stored), file.data);
    res.status(201).json({ id, filename: file.filename, type: file.type, size: file.data.length, url: `/files/${stored}` });
  } catch (e) {
    res.status(400).json({ error: e.message });
  }
});

app.get('/files/:id', (req, res) => {
  const safe = path.basename(req.params.id);
  const filePath = path.join(UPLOAD_DIR, safe);
  if (!fs.existsSync(filePath)) return res.status(404).json({ error: 'not_found' });
  res.sendFile(filePath);
});

app.get('/admin/files', (req, res) => {
  const files = fs.readdirSync(UPLOAD_DIR).map(f => ({ name: f, size: fs.statSync(path.join(UPLOAD_DIR, f)).size }));
  res.json({ count: files.length, files });
});

app.listen(3000, () => console.log('File upload demo :3000 — POST /upload with form-data file field'));
module.exports = app;
