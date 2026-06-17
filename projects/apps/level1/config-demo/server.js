// Configuration Demo — Env vars, config files, secrets, feature flags.
const express = require('express');
const fs = require('fs');
const path = require('path');
const app = express();
app.use(express.json());

// === Load .env (simple parser, no dotenv) ===
function loadEnv() {
  const env = {};
  try {
    const text = fs.readFileSync(path.join(__dirname, '.env'), 'utf8');
    for (const line of text.split('\n')) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith('#')) continue;
      const [key, ...rest] = trimmed.split('=');
      env[key.trim()] = rest.join('=').trim().replace(/^["']|["']$/g, '');
    }
  } catch (e) { /* .env is optional */ }
  return env;
}

const fileEnv = loadEnv();
const config = {
  port: parseInt(process.env.PORT || fileEnv.PORT || 3000),
  nodeEnv: process.env.NODE_ENV || fileEnv.NODE_ENV || 'development',
  dbUrl: process.env.DATABASE_URL || fileEnv.DATABASE_URL || 'sqlite::memory:',
  apiKey: process.env.API_KEY || fileEnv.API_KEY || 'dev-key-not-for-prod',
  jwtSecret: process.env.JWT_SECRET || fileEnv.JWT_SECRET || 'change-me',
  // === Feature flags ===
  features: {
    newCheckout: (process.env.FEATURE_NEW_CHECKOUT || fileEnv.FEATURE_NEW_CHECKOUT || 'false') === 'true',
    betaSearch: (process.env.FEATURE_BETA_SEARCH || fileEnv.FEATURE_BETA_SEARCH || 'false') === 'true',
    rateLimit: (process.env.FEATURE_RATE_LIMIT || fileEnv.FEATURE_RATE_LIMIT || 'true') === 'true',
  },
  // === Per-environment overrides ===
  limits: { development: { max: 1000 }, production: { max: 100 }, test: { max: 10 } }[(process.env.NODE_ENV || 'development')] || { max: 1000 },
};

app.get('/config', (req, res) => {
  const safe = { ...config };
  safe.apiKey = safe.apiKey.slice(0, 4) + '***';
  safe.jwtSecret = safe.jwtSecret.slice(0, 4) + '***';
  res.json(safe);
});

app.get('/features', (req, res) => res.json(config.features));

app.get('/checkout', (req, res) => {
  if (config.features.newCheckout) return res.json({ version: 'v2', note: 'new flow' });
  res.json({ version: 'v1', note: 'legacy flow' });
});

app.get('/search', (req, res) => {
  if (config.features.betaSearch) return res.json({ results: [], version: 'beta', relevance: 'ml-ranked' });
  res.json({ results: [], version: 'classic' });
});

// === Show which env vars would be loaded (redacted) ===
app.get('/env', (req, res) => {
  res.json({
    loaded: Object.keys({ ...process.env, ...fileEnv }).filter(k => k.match(/^(PORT|NODE_ENV|DATABASE_URL|API_KEY|JWT_SECRET|FEATURE_)/)),
    fileEnvKeys: Object.keys(fileEnv),
  });
});

app.listen(config.port, () => console.log(`Config demo on :${config.port} (NODE_ENV=${config.nodeEnv})`));
module.exports = app;
