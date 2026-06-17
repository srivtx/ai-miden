// Photo Gallery — Upload, organize in albums, tag, search, share.
const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const app = express();
const SECRET = 'dev-secret';

const users = []; const albums = []; const photos = []; let aId = 1, pId = 1;
function auth(req, res, next) { try { req.user = jwt.verify((req.headers.authorization || '').split(' ')[1], SECRET); next(); } catch { res.status(401).json({ error: 'Auth required' }); } }

app.post('/auth/register', async (req, res) => {
  const { name, email, password } = req.body;
  if (!email || !password) return res.status(400).json({ error: 'email, password required' });
  if (users.find(u => u.email === email)) return res.status(409).json({ error: 'Email exists' });
  users.push({ id: users.length + 1, name, email, password: await bcrypt.hash(password, 10) });
  res.status(201).json({ token: jwt.sign({ id: users.length }, SECRET, { expiresIn: '24h' }) });
});
app.post('/auth/login', async (req, res) => {
  const user = users.find(u => u.email === req.body.email);
  if (!user || !(await bcrypt.compare(req.body.password, user.password))) return res.status(401).json({ error: 'Invalid' });
  res.json({ token: jwt.sign({ id: user.id }, SECRET, { expiresIn: '24h' }) });
});

// Albums
app.post('/albums', auth, (req, res) => {
  const { name, description, isPublic } = req.body;
  if (!name) return res.status(400).json({ error: 'name required' });
  const a = { id: aId++, userId: req.user.id, name, description: description || '', isPublic: !!isPublic, photoCount: 0, createdAt: new Date().toISOString() };
  albums.push(a);
  res.status(201).json(a);
});

app.get('/albums', auth, (req, res) => {
  res.json(albums.filter(a => a.userId === req.user.id).map(a => ({ ...a, coverUrl: photos.find(p => p.albumId === a.id)?.url })));
});

const storage = multer.diskStorage({
  destination: (req, file, cb) => { const dir = `uploads/${req.user.id}`; if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true }); cb(null, dir); },
  filename: (req, file, cb) => cb(null, Date.now() + '-' + Math.random().toString(36).slice(2) + path.extname(file.originalname)),
});
const upload = multer({ storage, limits: { fileSize: 20 * 1024 * 1024 } });

// Upload photo
app.post('/photos', auth, upload.single('photo'), (req, res) => {
  if (!req.file) return res.status(400).json({ error: 'No file' });
  const { albumId, title, description, tags } = req.body;
  if (!albums.find(a => a.id === parseInt(albumId) && a.userId === req.user.id)) return res.status(400).json({ error: 'Album not found' });
  const p = { id: pId++, userId: req.user.id, albumId: parseInt(albumId), title: title || req.file.originalname, description: description || '', url: `/photos/${req.user.id}/${req.file.filename}`, filename: req.file.filename, size: req.file.size, tags: tags ? tags.split(',') : [], uploadedAt: new Date().toISOString() };
  photos.push(p);
  albums.find(a => a.id === p.albumId).photoCount++;
  res.status(201).json(p);
});

app.get('/albums/:id/photos', auth, (req, res) => {
  res.json(photos.filter(p => p.albumId === parseInt(req.params.id) && p.userId === req.user.id));
});

app.get('/photos', auth, (req, res) => {
  let result = photos.filter(p => p.userId === req.user.id);
  if (req.query.search) { const q = req.query.search.toLowerCase(); result = result.filter(p => p.title.toLowerCase().includes(q) || p.description.toLowerCase().includes(q) || p.tags.some(t => t.toLowerCase().includes(q))); }
  if (req.query.tag) result = result.filter(p => p.tags.includes(req.query.tag));
  if (req.query.album) result = result.filter(p => p.albumId === parseInt(req.query.album));
  result.sort((a, b) => new Date(b.uploadedAt) - new Date(a.uploadedAt));
  res.json(result);
});

app.use('/photos', express.static('uploads'));

app.listen(3000, () => console.log('Photo Gallery :3000'));
module.exports = app;
