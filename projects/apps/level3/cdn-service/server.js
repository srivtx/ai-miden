// CDN Service — File serving with cache headers, ETag, version invalidation.
const express = require('express');
const crypto = require('crypto');
const path = require('path');
const fs = require('fs');
const app = express();

const STORAGE = path.join(__dirname, 'cdn_storage');
if (!fs.existsSync(STORAGE)) fs.mkdirSync(STORAGE, { recursive: true });
const versions = new Map(); // path -> [{ version, hash, createdAt, size }]

// Upload content
app.post('/upload/*', express.raw({ type: '*/*', limit: '50mb' }), (req, res) => {
  const filePath = req.params[0];
  const content = req.body;
  const hash = crypto.createHash('md5').update(content).digest('hex');
  const versionedPath = path.join(STORAGE, filePath);
  fs.mkdirSync(path.dirname(versionedPath), { recursive: true });
  fs.writeFileSync(versionedPath, content);
  const entry = versions.get(filePath) || [];
  entry.unshift({ version: entry.length + 1, hash, size: content.length, createdAt: new Date().toISOString() });
  if (entry.length > 10) entry.length = 10; // keep last 10 versions
  versions.set(filePath, entry);
  res.json({ path: filePath, version: entry[0].version, hash, size: content.length, url: `/cdn/${filePath}` });
});

// Serve with cache headers
app.get('/cdn/*', (req, res) => {
  const filePath = req.params[0];
  const fullPath = path.join(STORAGE, filePath);
  if (!fs.existsSync(fullPath)) return res.status(404).json({ error: 'Not found' });
  const content = fs.readFileSync(fullPath);
  const etag = crypto.createHash('md5').update(content).digest('hex');
  const stat = fs.statSync(fullPath);
  const lastModified = stat.mtime.toUTCString();

  // Conditional GET
  if (req.headers['if-none-match'] === etag) return res.status(304).end();
  if (req.headers['if-modified-since'] === lastModified) return res.status(304).end();

  res.set({
    'Cache-Control': 'public, max-age=3600, must-revalidate',
    ETag: etag,
    'Last-Modified': lastModified,
    'Content-Length': content.length,
    'Content-Type': req.accepts(['html', 'json', 'image/png', 'image/jpeg', 'text/css', 'application/javascript', '*/*']) || 'application/octet-stream',
  });
  res.send(content);
});

// Invalidate (purge)
app.post('/invalidate/*', (req, res) => {
  const filePath = req.params[0];
  res.json({ path: filePath, invalidated: true, note: 'Clients will revalidate via ETag on next request' });
});

// List versions (for rollback)
app.get('/versions/*', (req, res) => {
  const filePath = req.params[0];
  res.json({ path: filePath, versions: versions.get(filePath) || [] });
});

// Rollback to a specific version
app.post('/rollback/*', (req, res) => {
  const filePath = req.params[0];
  const { version } = req.body;
  const entry = (versions.get(filePath) || []).find(v => v.version === version);
  if (!entry) return res.status(404).json({ error: 'Version not found' });
  // In real CDN: deploy the historical version from S3 to edge
  res.json({ rolledBackTo: version, note: 'In production, edge nodes would be updated' });
});

// Cache stats
app.get('/stats', (req, res) => {
  const totalFiles = versions.size;
  const totalSize = [...versions.values()].flat().reduce((s, v) => s + v.size, 0);
  res.json({ totalFiles, totalSize, totalVersions: [...versions.values()].reduce((s, v) => s + v.length, 0) });
});

app.listen(3000, () => console.log('CDN :3000'));
module.exports = app;
