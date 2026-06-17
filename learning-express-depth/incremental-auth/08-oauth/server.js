// 08-oauth: Login with third-party providers (Google, GitHub). The OAuth 2.0 flow.
const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const jwt = require('jsonwebtoken');
const app = express();
app.use(express.json());

const SECRET = 'dev-secret';
const db = new Database(':memory:');
db.exec(`CREATE TABLE users (id TEXT PRIMARY KEY, email TEXT UNIQUE, provider TEXT, provider_id TEXT, created_at TEXT DEFAULT (datetime('now')))`);
db.exec(`CREATE TABLE oauth_codes (code TEXT PRIMARY KEY, user_id TEXT, expires_at TEXT, used INTEGER DEFAULT 0)`);

const PROVIDERS = {
  google: { auth_url: 'https://accounts.google.com/o/oauth2/v2/auth', token_url: 'https://oauth2.googleapis.com/token', client_id: 'YOUR_CLIENT_ID' },
  github: { auth_url: 'https://github.com/login/oauth/authorize', token_url: 'https://github.com/login/oauth/access_token', client_id: 'YOUR_CLIENT_ID' },
};

// 1. Redirect user to provider's login page
app.get('/auth/:provider/login', (req, res) => {
  const provider = PROVIDERS[req.params.provider];
  if (!provider) return res.status(404).json({ error: 'unknown_provider' });
  const state = crypto.randomBytes(16).toString('hex');
  // In real apps: store state in session to verify on callback
  const redirectUrl = `${provider.auth_url}?client_id=${provider.client_id}&redirect_uri=http://localhost:3000/auth/${req.params.provider}/callback&response_type=code&state=${state}&scope=email`;
  res.json({ redirect_url: redirectUrl, state });
});

// 2. Provider redirects back with a code. We exchange it for a token, get the user's email.
app.get('/auth/:provider/callback', async (req, res) => {
  const { code, state } = req.query;
  if (!code) return res.status(422).json({ error: 'code required' });
  // In real apps: POST to provider.token_url with the code, get an access token, GET the user's profile
  // For demo, we simulate: any code starting with "valid_" gives a fake user
  if (!String(code).startsWith('valid_')) return res.status(400).json({ error: 'invalid_code' });
  const providerUser = {
    email: `user_${code.slice(6, 12)}@example.com`,
    provider_id: code,
  };
  // Find or create local user
  let user = db.prepare('SELECT * FROM users WHERE provider = ? AND provider_id = ?').get(req.params.provider, providerUser.provider_id);
  if (!user) {
    const id = 'u_' + crypto.randomBytes(8).toString('hex');
    db.prepare('INSERT INTO users (id, email, provider, provider_id) VALUES (?, ?, ?, ?)').run(id, providerUser.email, req.params.provider, providerUser.provider_id);
    user = { id, email: providerUser.email };
  }
  // Issue a JWT
  const token = jwt.sign({ sub: user.id, email: user.email, provider: req.params.provider }, SECRET, { expiresIn: '1h' });
  res.json({ user, token });
});

// Link an existing account to a provider
app.post('/auth/:provider/link', (req, res) => {
  const { user_id, code } = req.body;
  if (!user_id || !code) return res.status(422).json({ error: 'user_id and code required' });
  const user = db.prepare('SELECT * FROM users WHERE id = ?').get(user_id);
  if (!user) return res.status(404).json({ error: 'user not found' });
  db.prepare('UPDATE users SET provider = ?, provider_id = ? WHERE id = ?').run(req.params.provider, code, user_id);
  res.json({ linked: true });
});

app.listen(3000, () => console.log('08-oauth on :3000'));
