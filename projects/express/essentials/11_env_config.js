// 11_env_config.js — Environment-based configuration. .env, per-environment defaults, secrets.
const express = require('express');
const path = require('path');

// Load .env file (put sensitive values in .env, never commit it)
require('dotenv').config({ path: path.join(__dirname, '.env') });

const config = {
  // Server
  port: parseInt(process.env.PORT) || 3000,
  nodeEnv: process.env.NODE_ENV || 'development',

  // Database
  dbUrl: process.env.DATABASE_URL || 'sqlite::memory:',
  dbPoolMin: parseInt(process.env.DB_POOL_MIN) || 2,
  dbPoolMax: parseInt(process.env.DB_POOL_MAX) || 10,

  // Auth
  jwtSecret: process.env.JWT_SECRET || 'dev-secret-CHANGE-IN-PRODUCTION',
  jwtExpiry: process.env.JWT_EXPIRY || '15m',

  // Redis
  redisUrl: process.env.REDIS_URL || 'redis://localhost:6379',

  // External APIs
  stripeKey: process.env.STRIPE_SECRET_KEY || '',
  awsRegion: process.env.AWS_REGION || 'us-east-1',

  // Feature flags (toggle features per environment)
  features: {
    newUI: process.env.FEATURE_NEW_UI === 'true',
    betaAPI: process.env.FEATURE_BETA_API === 'true',
  },
};

// Log config at startup (mask secrets)
const masked = { ...config };
masked.jwtSecret = '***';
masked.stripeKey = '***';
console.log(`Config (${config.nodeEnv}):`, masked);

const app = express();

app.get('/config', (req, res) => {
  // Never expose secrets to clients!
  res.json({
    env: config.nodeEnv,
    features: config.features,
    version: process.env.APP_VERSION || '0.0.0',
  });
});

// Feature flag example
app.get('/dashboard', (req, res) => {
  if (config.features.newUI) return res.json({ ui: 'v2', layout: 'grid' });
  res.json({ ui: 'v1', layout: 'list' });
});

app.listen(config.port, () => console.log(`Server on :${config.port} (${config.nodeEnv})`));
