// 06-disputes: Customer disputes a charge with their bank. Track the dispute, respond, win/lose.
const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE charges (id TEXT PRIMARY KEY, amount_cents INTEGER)`);
db.exec(`CREATE TABLE disputes (id TEXT PRIMARY KEY, charge_id TEXT, reason TEXT, status TEXT DEFAULT 'needs_response', amount_cents INTEGER, evidence_due_by TEXT, created_at TEXT DEFAULT (datetime('now')), closed_at TEXT)`);
db.exec(`CREATE TABLE dispute_evidence (id INTEGER PRIMARY KEY AUTOINCREMENT, dispute_id TEXT, type TEXT, content TEXT, submitted_at TEXT DEFAULT (datetime('now')))`);

// Seed a charge
db.prepare("INSERT INTO charges VALUES ('ch_seed', 10000)");

// Open a dispute
app.post('/disputes', (req, res) => {
  const { charge_id, reason, amount_cents } = req.body;
  if (!charge_id || !reason) return res.status(422).json({ error: 'charge_id and reason required' });
  const charge = db.prepare('SELECT * FROM charges WHERE id = ?').get(charge_id);
  if (!charge) return res.status(404).json({ error: 'charge not found' });
  const id = 'dp_' + crypto.randomBytes(4).toString('hex');
  const evidenceDue = new Date(Date.now() + 7 * 86400000).toISOString();
  db.prepare("INSERT INTO disputes (id, charge_id, reason, amount_cents, evidence_due_by) VALUES (?, ?, ?, ?, ?)").run(id, charge_id, reason, amount_cents || charge.amount_cents, evidenceDue);
  res.status(201).json({ id, charge_id, status: 'needs_response', evidence_due_by: evidenceDue });
});

// Submit evidence
app.post('/disputes/:id/evidence', (req, res) => {
  const { type, content } = req.body;
  if (!type || !content) return res.status(422).json({ error: 'type and content required' });
  const dispute = db.prepare('SELECT * FROM disputes WHERE id = ?').get(req.params.id);
  if (!dispute) return res.status(404).json({ error: 'not found' });
  if (dispute.status !== 'needs_response') return res.status(409).json({ error: 'evidence already submitted' });
  const id = 'ev_' + crypto.randomBytes(3).toString('hex');
  db.prepare("INSERT INTO dispute_evidence (dispute_id, type, content) VALUES (?, ?, ?)").run(req.params.id, type, content);
  res.status(201).json({ id, type });
});

// Mark as under review (after evidence submitted)
app.post('/disputes/:id/submit', (req, res) => {
  const r = db.prepare("UPDATE disputes SET status = 'under_review' WHERE id = ?").run(req.params.id);
  r.changes ? res.json({ submitted: true }) : res.status(404).json({ error: 'not found' });
});

// Resolve (won or lost)
app.post('/disputes/:id/resolve', (req, res) => {
  const { outcome } = req.body;  // 'won' or 'lost'
  if (!['won', 'lost'].includes(outcome)) return res.status(422).json({ error: 'outcome must be won or lost' });
  const status = outcome === 'won' ? 'won' : 'lost';
  const r = db.prepare("UPDATE disputes SET status = ?, closed_at = datetime('now') WHERE id = ?").run(status, req.params.id);
  r.changes ? res.json({ status }) : res.status(404).json({ error: 'not found' });
});

app.get('/disputes/:id', (req, res) => {
  const d = db.prepare('SELECT * FROM disputes WHERE id = ?').get(req.params.id);
  if (!d) return res.status(404).json({ error: 'not found' });
  d.evidence = db.prepare('SELECT * FROM dispute_evidence WHERE dispute_id = ?').all(d.id);
  res.json(d);
});

app.listen(3000, () => console.log('06-disputes on :3000 (7 days to respond)'));
