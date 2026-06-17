// 20 — URL Shortener
// You give it a long URL, it gives you a short code.
// When someone visits the short code, they get redirected to the long URL.
// NEW: redirect (302) and a "lookup by code" pattern.
const express = require('express');
const crypto = require('crypto');
const app = express();
app.use(express.json());

// Each entry: { code, longUrl, createdAt, clicks }
const urls = [];

function makeCode() {
  // 6 random characters from base36. 36^6 = 2 billion possible codes.
  return crypto.randomBytes(4).toString('hex').slice(0, 6);
}

app.post('/urls', (req, res) => {
  const { longUrl } = req.body;
  if (!longUrl) return res.status(422).json({ error: 'longUrl is required' });

  // Make a unique code. If we get a collision (very rare), try again.
  let code;
  do {
    code = makeCode();
  } while (urls.some(u => u.code === code));

  const entry = { code, longUrl, createdAt: new Date().toISOString(), clicks: 0 };
  urls.push(entry);
  res.status(201).json({ code, longUrl, shortUrl: `http://localhost:3000/${code}` });
});

app.get('/urls', (req, res) => {
  res.json({ count: urls.length, urls });
});

// THE BIG ONE: redirect. When someone visits /:code, send them to the long URL.
app.get('/:code', (req, res) => {
  const entry = urls.find(u => u.code === req.params.code);
  if (!entry) return res.status(404).json({ error: 'Code not found' });
  entry.clicks += 1;
  res.redirect(entry.longUrl);  // 302 Found — go to the long URL
});

app.listen(3000, () => console.log('URL shortener on http://localhost:3000'));
