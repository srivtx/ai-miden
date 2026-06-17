// 17_image_resize.js — Sharp: resize, crop, format, watermark, thumbnail, optimization.
const express = require('express');
const multer = require('multer');
const sharp = require('sharp');
const path = require('path');
const fs = require('fs');
const app = express();

const upload = multer({ storage: multer.memoryStorage(), limits: { fileSize: 10 * 1024 * 1024 } });

function ensureDir(dir) { if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true }); }

app.post('/upload/photo', upload.single('image'), async (req, res) => {
  if (!req.file) return res.status(400).json({ error: 'No file' });
  const id = Date.now();
  const base = `uploads/${id}`;
  ensureDir('uploads');

  // Original (optimized)
  await sharp(req.file.buffer).jpeg({ quality: 85 }).toFile(`${base}_full.jpg`);

  // Thumbnail (200x200, cover)
  await sharp(req.file.buffer).resize(200, 200, { fit: 'cover', position: 'center' }).jpeg({ quality: 80 }).toFile(`${base}_thumb.jpg`);

  // Medium (600px wide, maintain aspect ratio)
  await sharp(req.file.buffer).resize(600).jpeg({ quality: 82 }).toFile(`${base}_med.jpg`);

  // WebP version for web
  await sharp(req.file.buffer).resize(800).webp({ quality: 75 }).toFile(`${base}.webp`);

  // Metadata
  const meta = await sharp(req.file.buffer).metadata();

  res.json({
    id,
    original: { size: req.file.size, format: meta.format, width: meta.width, height: meta.height },
    variants: { thumb: `${base}_thumb.jpg`, med: `${base}_med.jpg`, webp: `${base}.webp` },
  });
});

// Resize on-the-fly: /image/1234?w=300&h=200&fit=cover
app.get('/image/:id', async (req, res) => {
  const { w, h, fit = 'cover' } = req.query;
  const file = `uploads/${req.params.id}_full.jpg`;
  if (!fs.existsSync(file)) return res.status(404).json({ error: 'Not found' });

  let pipeline = sharp(file);
  if (w || h) pipeline = pipeline.resize(parseInt(w) || null, parseInt(h) || null, { fit, withoutEnlargement: true });
  if (req.query.fmt === 'webp') { pipeline = pipeline.webp(); res.type('webp'); }
  else if (req.query.fmt === 'png') { pipeline = pipeline.png(); res.type('png'); }
  else { pipeline = pipeline.jpeg({ quality: 80 }); res.type('jpg'); }

  pipeline.pipe(res);
});

app.listen(3000, () => console.log('Image :3000'));
