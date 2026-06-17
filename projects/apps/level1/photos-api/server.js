// Photos API — Step 13. Adds: image upload, albums, EXIF-like metadata, sharing, public/private.
const express = require('express');
const Database = require('better-sqlite3');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const app = express();
app.use(express.json());

const UPLOAD_DIR = path.join(__dirname, 'uploads');
if (!fs.existsSync(UPLOAD_DIR)) fs.mkdirSync(UPLOAD_DIR);

const db = new Database(':memory:');
db.exec(`CREATE TABLE photos (id TEXT PRIMARY KEY, user_id TEXT, filename TEXT, original_name TEXT, size_bytes INTEGER, mime_type TEXT, width INTEGER, height INTEGER, taken_at TEXT, camera TEXT, location TEXT, is_public INTEGER DEFAULT 0, created_at TEXT DEFAULT (datetime('now')))`);
db.exec(`CREATE TABLE albums (id TEXT PRIMARY KEY, user_id TEXT, name TEXT, description TEXT, cover_photo_id TEXT, created_at TEXT DEFAULT (datetime('now')))`);
db.exec(`CREATE TABLE album_photos (album_id TEXT, photo_id TEXT, position INTEGER, PRIMARY KEY (album_id, photo_id))`);
db.exec(`CREATE TABLE tags (id TEXT PRIMARY KEY, name TEXT UNIQUE)`);
db.exec(`CREATE TABLE photo_tags (photo_id TEXT, tag_id TEXT, PRIMARY KEY (photo_id, tag_id))`);

const ALLOWED_TYPES = { 'image/jpeg': '.jpg', 'image/png': '.png', 'image/gif': '.gif', 'image/webp': '.webp' };

function parseMultipart(req) {
  return new Promise((resolve) => {
    const ct = req.headers['content-type'] || '';
    if (!ct.startsWith('multipart/form-data')) return resolve(null);
    const boundary = '--' + ct.split('boundary=')[1];
    const chunks = [];
    req.on('data', c => chunks.push(c));
    req.on('end', () => {
      const body = Buffer.concat(chunks).toString('binary');
      const parts = body.split(boundary).filter(p => p && p !== '--\r\n' && p !== '--');
      const file = { filename: null, type: null, data: Buffer.alloc(0) };
      const fields = {};
      for (const part of parts) {
        const headerEnd = part.indexOf('\r\n\r\n');
        if (headerEnd === -1) continue;
        const headers = part.slice(0, headerEnd);
        const content = part.slice(headerEnd + 4, part.endsWith('\r\n') ? -2 : undefined);
        const nameMatch = headers.match(/name="([^"]+)"/);
        const fieldName = nameMatch ? nameMatch[1] : null;
        const fnMatch = headers.match(/filename="([^"]+)"/);
        if (fnMatch) {
          file.filename = fnMatch[1];
          file.type = (headers.match(/Content-Type:\s*([^\r\n]+)/i) || [])[1] || 'application/octet-stream';
          file.data = Buffer.from(content, 'binary');
        } else if (fieldName) {
          fields[fieldName] = content.replace(/\r\n$/, '');
        }
      }
      resolve({ file, fields });
    });
  });
}

app.post('/photos', async (req, res) => {
  if (!req.userId) return res.status(401).json({ error: 'auth_required' });
  const parsed = await parseMultipart(req);
  if (!parsed || !parsed.file.filename) return res.status(400).json({ error: 'no_file' });
  const { file, fields } = parsed;
  if (!ALLOWED_TYPES[file.type]) return res.status(415).json({ error: 'unsupported_type' });
  const id = 'p_' + crypto.randomBytes(6).toString('hex');
  const ext = ALLOWED_TYPES[file.type];
  fs.writeFileSync(path.join(UPLOAD_DIR, id + ext), file.data);
  db.prepare('INSERT INTO photos (id, user_id, filename, original_name, size_bytes, mime_type, taken_at, camera, location, is_public) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)').run(id, req.userId, id + ext, file.filename, file.data.length, file.type, fields.taken_at || null, fields.camera || null, fields.location || null, fields.is_public === 'true' ? 1 : 0);
  if (fields.tags) for (const tag of fields.tags.split(',').map(t => t.trim()).filter(Boolean)) {
    let t = db.prepare('SELECT id FROM tags WHERE name = ?').get(tag);
    if (!t) t = db.prepare('INSERT INTO tags (id, name) VALUES (?, ?)').run('t_' + crypto.randomBytes(3).toString('hex'), tag);
    try { db.prepare('INSERT INTO photo_tags (photo_id, tag_id) VALUES (?, ?)').run(id, t.lastInsertRowid || t.id); } catch {}
  }
  res.status(201).json({ id, url: '/files/' + id + ext, size: file.data.length, type: file.type });
});

app.get('/photos/:id', (req, res) => {
  const photo = db.prepare('SELECT * FROM photos WHERE id = ?').get(req.params.id);
  if (!photo) return res.status(404).json({ error: 'not_found' });
  if (!photo.is_public && photo.user_id !== req.userId) return res.status(403).json({ error: 'private' });
  photo.tags = db.prepare('SELECT t.name FROM tags t JOIN photo_tags pt ON pt.tag_id = t.id WHERE pt.photo_id = ?').all(photo.id).map(t => t.name);
  res.json(photo);
});

app.get('/files/:filename', (req, res) => {
  const safe = path.basename(req.params.filename);
  const fp = path.join(UPLOAD_DIR, safe);
  if (!fp.startsWith(UPLOAD_DIR) || !fs.existsSync(fp)) return res.status(404).json({ error: 'not_found' });
  res.sendFile(fp);
});

app.get('/photos', (req, res) => {
  const { user, tag, is_public } = req.query;
  let query = 'SELECT p.* FROM photos p WHERE 1=1';
  const params = [];
  if (is_public === 'true') query += ' AND p.is_public = 1';
  if (user) { query += ' AND p.user_id = ?'; params.push(user); }
  if (tag) { query += ' AND p.id IN (SELECT pt.photo_id FROM photo_tags pt JOIN tags t ON t.id = pt.tag_id WHERE t.name = ?)'; params.push(tag); }
  query += ' ORDER BY p.created_at DESC LIMIT 50';
  res.json({ photos: db.prepare(query).all(...params) });
});

app.post('/albums', (req, res) => {
  if (!req.userId) return res.status(401).json({ error: 'auth_required' });
  if (!req.body.name) return res.status(422).json({ error: 'missing_name' });
  const id = 'a_' + crypto.randomBytes(4).toString('hex');
  db.prepare('INSERT INTO albums (id, user_id, name, description) VALUES (?, ?, ?, ?)').run(id, req.userId, req.body.name, req.body.description || '');
  res.status(201).json({ id });
});

app.post('/albums/:id/photos/:photoId', (req, res) => {
  if (!req.userId) return res.status(401).json({ error: 'auth_required' });
  const pos = db.prepare('SELECT COALESCE(MAX(position), 0) + 1 as p FROM album_photos WHERE album_id = ?').get(req.params.id).p;
  try { db.prepare('INSERT INTO album_photos (album_id, photo_id, position) VALUES (?, ?, ?)').run(req.params.id, req.params.photoId, pos); res.status(201).json({ position: pos }); }
  catch { res.status(409).json({ error: 'already_in_album' }); }
});

app.get('/albums/:id', (req, res) => {
  const album = db.prepare('SELECT * FROM albums WHERE id = ?').get(req.params.id);
  if (!album) return res.status(404).json({ error: 'not_found' });
  album.photos = db.prepare('SELECT p.*, ap.position FROM album_photos ap JOIN photos p ON p.id = ap.photo_id WHERE ap.album_id = ? ORDER BY ap.position').all(album.id);
  res.json(album);
});

app.use((req, res, next) => { req.userId = req.headers['x-user-id']; next(); });

app.listen(3000, () => console.log('Photos API :3000 — POST /photos with multipart form-data'));
module.exports = app;
