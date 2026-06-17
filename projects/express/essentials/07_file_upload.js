// 07_file_upload.js — Multer: single, multiple, field validation, size limits, disk storage.
const express = require('express');
const multer = require('multer');
const path = require('path');
const app = express();

const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, 'uploads/'),
  filename: (req, file, cb) => cb(null, Date.now() + '-' + Math.round(Math.random() * 1E9) + path.extname(file.originalname)),
});

const fileFilter = (req, file, cb) => {
  const allowed = ['image/jpeg', 'image/png', 'image/webp', 'application/pdf', 'text/plain'];
  allowed.includes(file.mimetype) ? cb(null, true) : cb(new Error(`Invalid type: ${file.mimetype}`), false);
};

const upload = multer({ storage, fileFilter, limits: { fileSize: 5 * 1024 * 1024 } });

// Single file (field name: 'avatar')
app.post('/avatar', (req, res) => {
  upload.single('avatar')(req, res, (err) => {
    if (err) return res.status(400).json({ error: err.message });
    if (!req.file) return res.status(400).json({ error: 'No file' });
    res.json({ filename: req.file.filename, size: req.file.size, type: req.file.mimetype });
  });
});

// Multiple files (field name: 'photos', max 5)
app.post('/photos', (req, res) => {
  upload.array('photos', 5)(req, res, (err) => {
    if (err) return res.status(400).json({ error: err.message });
    res.json({ count: req.files.length, files: req.files.map(f => f.filename) });
  });
});

// Mixed fields (avatar + document)
app.post('/profile', (req, res) => {
  const fields = upload.fields([{ name: 'avatar', maxCount: 1 }, { name: 'docs', maxCount: 3 }]);
  fields(req, res, (err) => {
    if (err) return res.status(400).json({ error: err.message });
    res.json({ avatar: req.files?.avatar?.[0]?.filename, docs: req.files?.docs?.map(f => f.filename) });
  });
});

app.listen(3000, () => console.log('Upload :3000'));
