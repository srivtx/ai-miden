// 10-fraud: Detect fraudulent charges. Velocity checks, AVS, 3DS, risk score.
const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE charges (id TEXT PRIMARY KEY, customer_id TEXT, ip TEXT, amount_cents INTEGER, card_last4 TEXT, status TEXT DEFAULT 'pending', risk_score INTEGER DEFAULT 0, fraud_signals TEXT, created_at TEXT DEFAULT (datetime('now')))`);

// Risk signals
const signals = [];

// AVS (Address Verification System) — does billing address match?
function checkAVS(card) {
  return { match: card.zip && card.zip.length === 5, signal: 'avs_mismatch' };
}

// CVV check
function checkCVV(card) {
  return { match: !!card.cvv, signal: 'cvv_missing' };
}

// Velocity: too many charges in a short time
function checkVelocity(customerId, ip) {
  const oneHourAgo = new Date(Date.now() - 3600000).toISOString();
  const recentByCustomer = db.prepare('SELECT COUNT(*) as c FROM charges WHERE customer_id = ? AND created_at > ?').get(customerId, oneHourAgo).c;
  const recentByIp = db.prepare('SELECT COUNT(*) as c FROM charges WHERE ip = ? AND created_at > ?').get(ip, oneHourAgo).c;
  if (recentByCustomer > 5) return { signal: 'velocity_customer_high', score: 30 };
  if (recentByIp > 10) return { signal: 'velocity_ip_high', score: 40 };
  return { signal: null, score: 0 };
}

// Amount check: unusually high?
function checkAmount(amount, customerAvg) {
  if (amount > 100000 && (!customerAvg || amount > customerAvg * 5)) return { signal: 'unusual_amount', score: 25 };
  return { signal: null, score: 0 };
}

// Country check (high-risk countries)
const HIGH_RISK_COUNTRIES = ['XX', 'YY'];  // example
function checkCountry(country) {
  if (HIGH_RISK_COUNTRIES.includes(country)) return { signal: 'high_risk_country', score: 50 };
  return { signal: null, score: 0 };
}

// Run all checks
function assessRisk(charge) {
  let totalScore = 0;
  const foundSignals = [];
  for (const check of [checkAVS(charge.card), checkCVV(charge.card), checkVelocity(charge.customer_id, charge.ip), checkAmount(charge.amount_cents), checkCountry(charge.country)]) {
    if (check.signal) {
      totalScore += check.score || 10;
      foundSignals.push(check.signal);
    }
  }
  return { score: Math.min(totalScore, 100), signals: foundSignals };
}

app.post('/charges', (req, res) => {
  const { customer_id, amount_cents, card, ip, country } = req.body;
  if (!customer_id || !amount_cents || !card) return res.status(422).json({ error: 'missing fields' });

  const risk = assessRisk({ customer_id, amount_cents, card, ip, country });
  const id = 'ch_' + crypto.randomBytes(4).toString('hex');

  // Decide based on risk
  let status = 'succeeded';
  if (risk.score >= 75) status = 'blocked';
  else if (risk.score >= 40) status = 'needs_review';

  db.prepare("INSERT INTO charges VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)").run(id, customer_id, ip, amount_cents, card.last4 || card.number?.slice(-4), status, risk.score, JSON.stringify(risk.signals), new Date().toISOString());
  res.status(201).json({ id, status, risk_score: risk.score, signals: risk.signals });
});

app.get('/admin/charges/flagged', (req, res) => {
  const flagged = db.prepare("SELECT * FROM charges WHERE status IN ('needs_review', 'blocked') ORDER BY created_at DESC").all();
  res.json({ count: flagged.length, charges: flagged });
});

app.listen(3000, () => console.log('10-fraud on :3000 (risk scoring)'));
