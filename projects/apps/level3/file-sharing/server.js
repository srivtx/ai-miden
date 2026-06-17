// File Sharing — Upload, download, share links with password, expiry, preview, search.
const express = require('express');
const multer = require('multer');
const crypto = require('crypto');
const path = require('path');
const fs = require('fs');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const app = express();

app.use(express.json());
const SECRET = 'dev-secret';

// Setup
const uploadDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadDir)) fs.mkdirSync(uploadDir, { recursive: true });

const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    const userDir = path.join(uploadDir, String(req.user?.id || 'anon'));
    if (!fs.existsSync(userDir)) fs.mkdirSync(userDir, { recursive: true });
    cb(null, userDir);
  },
  filename: (req, file, cb) => cb(null, Date.now() + '-' + Math.random().toString(36).slice(2) + path.extname(file.originalname)),
});
const upload = multer({ storage, limits: { fileSize: 50 * 1024 * 1024 } });

// In-memory DB
const users = [];
const files = []; // { id, name, originalName, path, size, mimeType, userId, shared: [{code, password, expiresAt}] }
let fileId = 1;

// Auth
function auth(req, res, next) { try { req.user = jwt.verify((req.headers.authorization || '').split(' ')[1], SECRET); next(); } catch { next(); } } // optional auth

app.post('/auth/register', async (req, res) => {
  const { name, email, password } = req.body;
  if (!email || !password) return res.status(400).json({ error: 'email and password required' });
  if (users.find(u => u.email === email)) return res.status(409).json({ error: 'Email exists' });
  const user = { id: users.length + 1, name, email, password: await bcrypt.hash(password, 10), usedStorage: 0 };
  users.push(user);
  res.status(201).json({ user: { id: user.id, name, email }, token: jwt.sign({ id: user.id }, SECRET, { expiresIn: '24h' }) });
});

app.post('/auth/login', async (req, res) => {
  const user = users.find(u => u.email === req.body.email);
  if (!user || !(await bcrypt.compare(req.body.password, user.password))) return res.status(401).json({ error: 'Invalid credentials' });
  res.json({ token: jwt.sign({ id: user.id }, SECRET, { expiresIn: '24h' }) });
});

// UPLOAD
app.post('/files', auth, upload.single('file'), (req, res) => {
  if (!req.file) return res.status(400).json({ error: 'No file' });
  const user = users.find(u => u.id === req.user.id);
  user.usedStorage += req.file.size;
  const file = { id: fileId++, name: req.file.filename, originalName: req.file.originalname, path: req.file.path, size: req.file.size, mimeType: req.file.mimetype, userId: req.user.id, uploadedAt: new Date().toISOString(), shared: [] };
  files.push(file);
  res.status(201).json({ id: file.id, name: file.originalName, size: file.size, type: file.mimeType, storageUsed: user.usedStorage });
});

// LIST my files
app.get('/files', auth, (req, res) => {
  let result = files.filter(f => f.userId === req.user.id);
  if (req.query.search) { const q = req.query.search.toLowerCase(); result = result.filter(f => f.originalName.toLowerCase().includes(q)); }
  if (req.query.type) result = result.filter(f => f.mimeType.startsWith(req.query.type));
  result.sort((a, b) => new Date(b.uploadedAt) - new Date(a.uploadedAt));
  res.json({ count: result.length, storageUsed: users.find(u => u.id === req.user.id)?.usedStorage || 0, files: result.map(f => ({ id: f.id, name: f.originalName, size: f.size, type: f.mimeType, uploadedAt: f.uploadedAt, shareCount: f.shared.length })) });
});

// DOWNLOAD
app.get('/files/:id/download', auth, (req, res) => {
  const file = files.find(f => f.id === parseInt(req.params.id));
  if (!file) return res.status(404).json({ error: 'Not found' });
  if (file.userId !== req.user.id) return res.status(403).json({ error: 'Forbidden' });
  res.download(file.path, file.originalName);
});

// DELETE
app.delete('/files/:id', auth, (req, res) => {
  const idx = files.findIndex(f => f.id === parseInt(req.params.id));
  if (idx === -1) return res.status(404).json({ error: 'Not found' });
  if (files[idx].userId !== req.user.id) return res.status(403).json({ error: 'Forbidden' });
  try { fs.unlinkSync(files[idx].path); } catch {}
  const user = users.find(u => u.id === req.user.id);
  user.usedStorage -= files[idx].size;
  files.splice(idx, 1);
  res.status(204).send();
});

// SHARE (generate share link)
app.post('/files/:id/share', auth, (req, res) => {
  const file = files.find(f => f.id === parseInt(req.params.id));
  if (!file) return res.status(404).json({ error: 'Not found' });
  if (file.userId !== req.user.id) return res.status(403).json({ error: 'Forbidden' });
  const code = crypto.randomBytes(6).toString('base64url');
  file.shared.push({
    code, password: req.body.password || null,
    expiresAt: req.body.expiresIn ? new Date(Date.now() + req.body.expiresIn * 3600000).toISOString() : null,
    createdAt: new Date().toISOString(), downloads: 0,
  });
  res.json({ shareUrl: `http://localhost:3000/shared/${code}`, code, hasPassword: !!req.body.password });
});

// ACCESS SHARED FILE (public — no auth needed)
app.get('/shared/:code', (req, res) => {
  for (const file of files) {
    const share = file.shared.find(s => s.code === req.params.code);
    if (!share) continue;
    if (share.expiresAt && new Date() > new Date(share.expiresAt)) return res.status(410).json({ error: 'Share link expired' });
    if (share.password) {
      if (req.query.password !== share.password) return res.status(401).json({ error: 'Password required. Add ?password=... to URL' });
    }
    share.downloads++;
    return res.download(file.path, file.originalName);
  }
  res.status(404).json({ error: 'Share link not found' });
});

app.listen(3000, () => console.log('File Sharing :3000'));
module.exports = app;
