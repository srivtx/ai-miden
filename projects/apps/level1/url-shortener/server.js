// URL Shortener — Create short links, redirect, track clicks, expiry.
const express = require('express');
const crypto = require('crypto');
const app = express();
app.use(express.json());

const links = {}; // shortCode -> { url, clicks, createdAt, expiresAt }

function generateCode() { return crypto.randomBytes(3).toString('base64url'); }

// Create short link
app.post('/links', (req, res) => {
  const { url, expiresIn } = req.body; // expiresIn: hours
  if (!url) return res.status(400).json({ error: 'url required' });
  const code = generateCode();
  links[code] = {
    url, clicks: 0, createdAt: new Date().toISOString(),
    expiresAt: expiresIn ? new Date(Date.now() + expiresIn * 3600000).toISOString() : null,
  };
  res.status(201).json({ shortUrl: `http://localhost:3000/${code}`, code, ...links[code] });
});

// Redirect (track click)
app.get('/:code', (req, res) => {
  const link = links[req.params.code];
  if (!link) return res.status(404).json({ error: 'Not found' });
  if (link.expiresAt && new Date() > new Date(link.expiresAt)) {
    delete links[req.params.code];
    return res.status(410).json({ error: 'Expired' });
  }
  link.clicks++;
  res.redirect(link.url);
});

// Analytics
app.get('/links/:code/stats', (req, res) => {
  const link = links[req.params.code];
  link ? res.json(link) : res.status(404).json({ error: 'Not found' });
});

// List all (with optional expiry filter)
app.get('/links', (req, res) => {
  const result = Object.entries(links).map(([code, data]) => ({ code, ...data, isExpired: data.expiresAt ? new Date() > new Date(data.expiresAt) : false }));
  res.json({ total: result.length, data: result });
});

// Delete
app.delete('/links/:code', (req, res) => {
  if (!links[req.params.code]) return res.status(404).json({ error: 'Not found' });
  delete links[req.params.code];
  res.status(204).send();
});

app.listen(3000, () => console.log('URL Shortener :3000'));
module.exports = app;
