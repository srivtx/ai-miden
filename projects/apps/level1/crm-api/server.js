// CRM API — Step 18. Adds: contacts, companies, deals, pipeline stages, activity log.
const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE companies (id TEXT PRIMARY KEY, name TEXT, industry TEXT, size TEXT, website TEXT, created_at TEXT DEFAULT (datetime('now')))`);
db.exec(`CREATE TABLE contacts (id TEXT PRIMARY KEY, company_id TEXT, first_name TEXT, last_name TEXT, email TEXT, phone TEXT, title TEXT, owner_id TEXT, created_at TEXT DEFAULT (datetime('now')))`);
db.exec(`CREATE TABLE deals (id TEXT PRIMARY KEY, contact_id TEXT, owner_id TEXT, title TEXT, value_cents INTEGER, stage TEXT DEFAULT 'lead', probability INTEGER DEFAULT 10, expected_close TEXT, created_at TEXT DEFAULT (datetime('now')))`);
db.exec(`CREATE TABLE activities (id TEXT PRIMARY KEY, contact_id TEXT, deal_id TEXT, type TEXT CHECK(type IN ('call', 'email', 'meeting', 'note')), subject TEXT, body TEXT, owner_id TEXT, created_at TEXT DEFAULT (datetime('now')))`);
db.exec(`CREATE INDEX idx_deals_stage ON deals(stage)`);
db.exec(`CREATE INDEX idx_contacts_company ON contacts(company_id)`);

const STAGES = ['lead', 'qualified', 'proposal', 'negotiation', 'won', 'lost'];

app.post('/companies', (req, res) => {
  if (!req.body.name) return res.status(422).json({ error: 'missing_name' });
  const id = 'co_' + crypto.randomBytes(4).toString('hex');
  db.prepare('INSERT INTO companies (id, name, industry, size, website) VALUES (?, ?, ?, ?, ?)').run(id, req.body.name, req.body.industry, req.body.size, req.body.website);
  res.status(201).json({ id });
});

app.get('/companies', (req, res) => {
  const companies = db.prepare('SELECT c.*, COUNT(DISTINCT ct.id) as contact_count, COUNT(DISTINCT d.id) as deal_count FROM companies c LEFT JOIN contacts ct ON ct.company_id = c.id LEFT JOIN deals d ON d.contact_id = ct.id GROUP BY c.id').all();
  res.json({ companies });
});

app.post('/contacts', (req, res) => {
  const { company_id, first_name, last_name, email, phone, title } = req.body;
  if (!first_name || !last_name) return res.status(422).json({ error: 'missing_name' });
  const id = 'ct_' + crypto.randomBytes(4).toString('hex');
  db.prepare('INSERT INTO contacts (id, company_id, first_name, last_name, email, phone, title, owner_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)').run(id, company_id, first_name, last_name, email, phone, title, req.userId);
  res.status(201).json({ id });
});

app.get('/contacts', (req, res) => {
  const contacts = db.prepare('SELECT ct.*, co.name as company_name FROM contacts ct LEFT JOIN companies co ON co.id = ct.company_id ORDER BY ct.last_name').all();
  res.json({ contacts });
});

app.get('/contacts/:id', (req, res) => {
  const contact = db.prepare('SELECT ct.*, co.name as company_name FROM contacts ct LEFT JOIN companies co ON co.id = ct.company_id WHERE ct.id = ?').get(req.params.id);
  if (!contact) return res.status(404).json({ error: 'not_found' });
  contact.deals = db.prepare('SELECT * FROM deals WHERE contact_id = ? ORDER BY created_at DESC').all(contact.id);
  contact.activities = db.prepare('SELECT * FROM activities WHERE contact_id = ? ORDER BY created_at DESC LIMIT 20').all(contact.id);
  res.json(contact);
});

app.post('/deals', (req, res) => {
  if (!req.body.contact_id || !req.body.title) return res.status(422).json({ error: 'missing_fields' });
  const id = 'd_' + crypto.randomBytes(4).toString('hex');
  db.prepare('INSERT INTO deals (id, contact_id, owner_id, title, value_cents, stage, probability, expected_close) VALUES (?, ?, ?, ?, ?, ?, ?, ?)').run(id, req.body.contact_id, req.userId, req.body.title, req.body.value_cents || 0, req.body.stage || 'lead', req.body.probability || 10, req.body.expected_close);
  res.status(201).json({ id });
});

app.patch('/deals/:id/stage', (req, res) => {
  if (!STAGES.includes(req.body.stage)) return res.status(422).json({ error: 'invalid_stage', allowed: STAGES });
  const result = db.prepare('UPDATE deals SET stage = ? WHERE id = ?').run(req.body.stage, req.params.id);
  result.changes ? res.json({ stage: req.body.stage }) : res.status(404).json({ error: 'not_found' });
});

app.get('/pipeline', (req, res) => {
  const deals = db.prepare('SELECT d.*, ct.first_name, ct.last_name, ct.email FROM deals d JOIN contacts ct ON ct.id = d.contact_id ORDER BY d.stage, d.value_cents DESC').all();
  const grouped = {};
  for (const s of STAGES) grouped[s] = [];
  for (const d of deals) grouped[d.stage].push(d);
  const summary = STAGES.map(stage => {
    const list = grouped[stage];
    return { stage, count: list.length, total_value_cents: list.reduce((s, d) => s + d.value_cents, 0), weighted_value_cents: list.reduce((s, d) => s + d.value_cents * d.probability / 100, 0) };
  });
  res.json({ stages: STAGES, summary, deals: grouped });
});

app.post('/activities', (req, res) => {
  const { contact_id, deal_id, type, subject, body } = req.body;
  if (!['call', 'email', 'meeting', 'note'].includes(type) || !contact_id) return res.status(422).json({ error: 'invalid_activity' });
  const id = 'ac_' + crypto.randomBytes(4).toString('hex');
  db.prepare('INSERT INTO activities (id, contact_id, deal_id, type, subject, body, owner_id) VALUES (?, ?, ?, ?, ?, ?, ?)').run(id, contact_id, deal_id || null, type, subject || '', body || '', req.userId);
  res.status(201).json({ id });
});

app.use((req, res, next) => { req.userId = req.headers['x-user-id']; next(); });

app.listen(3000, () => console.log('CRM API :3000 — X-User-Id header'));
module.exports = app;
