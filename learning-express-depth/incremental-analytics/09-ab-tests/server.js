// 09-ab-tests: A/B testing. Assign users to variants. Measure conversion per variant.
const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE experiments (id TEXT PRIMARY KEY, name TEXT, variants TEXT, status TEXT DEFAULT 'running', created_at TEXT DEFAULT (datetime('now')))`);
db.exec(`CREATE TABLE assignments (user_id TEXT, experiment_id TEXT, variant TEXT, assigned_at TEXT DEFAULT (datetime('now')), PRIMARY KEY (user_id, experiment_id))`);
db.exec(`CREATE TABLE conversions (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, experiment_id TEXT, variant TEXT, ts TEXT DEFAULT (datetime('now')))`);

// Create an experiment
app.post('/experiments', (req, res) => {
  const { name, variants } = req.body;
  if (!name || !Array.isArray(variants) || variants.length < 2) return res.status(422).json({ error: 'name and 2+ variants required' });
  const id = 'e_' + crypto.randomBytes(4).toString('hex');
  db.prepare('INSERT INTO experiments (id, name, variants) VALUES (?, ?, ?)').run(id, name, JSON.stringify(variants));
  res.status(201).json({ id, name, variants });
});

// Assign a user to a variant (deterministic by hash)
app.get('/experiments/:id/assignment', (req, res) => {
  const { user_id } = req.query;
  if (!user_id) return res.status(422).json({ error: 'user_id required' });
  const exp = db.prepare('SELECT * FROM experiments WHERE id = ?').get(req.params.id);
  if (!exp) return res.status(404).json({ error: 'not found' });

  // Check existing assignment
  const existing = db.prepare('SELECT * FROM assignments WHERE user_id = ? AND experiment_id = ?').get(user_id, exp.id);
  if (existing) return res.json({ user_id, experiment: exp.name, variant: existing.variant });

  // Deterministic assignment by hash
  const variants = JSON.parse(exp.variants);
  const hash = crypto.createHash('md5').update(user_id + exp.id).digest('hex');
  const index = parseInt(hash.slice(0, 8), 16) % variants.length;
  const variant = variants[index];
  db.prepare('INSERT INTO assignments VALUES (?, ?, ?, datetime("now"))').run(user_id, exp.id, variant);
  res.json({ user_id, experiment: exp.name, variant });
});

// Track a conversion for the user
app.post('/experiments/:id/conversions', (req, res) => {
  const { user_id } = req.body;
  if (!user_id) return res.status(422).json({ error: 'user_id required' });
  const assignment = db.prepare('SELECT * FROM assignments WHERE user_id = ? AND experiment_id = ?').get(user_id, req.params.id);
  if (!assignment) return res.status(404).json({ error: 'user not assigned' });
  db.prepare('INSERT INTO conversions (user_id, experiment_id, variant) VALUES (?, ?, ?)').run(user_id, req.params.id, assignment.variant);
  res.status(201).json({ converted: true });
});

// Results: conversion rate per variant
app.get('/experiments/:id/results', (req, res) => {
  const exp = db.prepare('SELECT * FROM experiments WHERE id = ?').get(req.params.id);
  if (!exp) return res.status(404).json({ error: 'not found' });
  const variants = JSON.parse(exp.variants);
  const results = variants.map(v => {
    const assigned = db.prepare('SELECT COUNT(*) as c FROM assignments WHERE experiment_id = ? AND variant = ?').get(exp.id, v).c;
    const converted = db.prepare('SELECT COUNT(*) as c FROM conversions WHERE experiment_id = ? AND variant = ?').get(exp.id, v).c;
    return { variant: v, assigned, converted, conversion_rate: assigned ? Math.round(converted / assigned * 1000) / 10 : 0 };
  });
  res.json({ experiment: exp.name, results });
});

app.listen(3000, () => console.log('09-ab-tests on :3000'));
