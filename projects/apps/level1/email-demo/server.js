// Email Demo — Templates, queue, send tracking, bounce handling. No external email lib.
const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE emails (id TEXT PRIMARY KEY, to_email TEXT, subject TEXT, body TEXT, status TEXT DEFAULT 'queued', sent_at INTEGER, error TEXT)`);
db.exec(`CREATE TABLE templates (name TEXT PRIMARY KEY, subject TEXT, body TEXT)`);

// === Templates ===
const TEMPLATES = {
  welcome: { subject: 'Welcome to {{app}}!', body: 'Hi {{name}},\n\nWelcome aboard. Get started at https://{{app}}/start\n\n— The team' },
  reset_password: { subject: 'Reset your password', body: 'Click here to reset: https://{{app}}/reset?token={{token}}\n\nExpires in 1 hour.' },
  invoice: { subject: 'Invoice {{number}}', body: 'Hi {{name}},\n\nYour invoice for ${{amount}} is attached.\n\n— Billing' },
  verify_email: { subject: 'Verify your email', body: 'Click to verify: https://{{app}}/verify?token={{token}}' },
};

for (const [name, t] of Object.entries(TEMPLATES)) {
  db.prepare('INSERT INTO templates (name, subject, body) VALUES (?, ?, ?)').run(name, t.subject, t.body);
}

// === Render template ===
function render(str, vars) {
  return str.replace(/\{\{(\w+)\}\}/g, (_, k) => vars[k] || '{{' + k + '}}');
}

// === Fake send (in real life, use nodemailer, SendGrid, SES) ===
async function fakeSend(to, subject, body) {
  await new Promise(r => setTimeout(r, 100 + Math.random() * 200));
  if (Math.random() < 0.05) throw new Error('SMTP timeout');
  if (to.includes('bounce@')) throw new Error('Mailbox does not exist');
  return { messageId: 'msg_' + crypto.randomBytes(4).toString('hex') };
}

// === Send queue (process in background) ===
const queue = [];
let processing = false;
async function processQueue() {
  if (processing) return;
  const id = queue.shift();
  if (!id) return;
  processing = true;
  const email = db.prepare('SELECT * FROM emails WHERE id = ?').get(id);
  if (!email) { processing = false; return; }
  try {
    const result = await fakeSend(email.to_email, email.subject, email.body);
    db.prepare('UPDATE emails SET status = ?, sent_at = ? WHERE id = ?').run('sent', Date.now(), id);
    console.log(`[email] sent ${id} to ${email.to_email} (${result.messageId})`);
  } catch (e) {
    db.prepare('UPDATE emails SET status = ?, error = ? WHERE id = ?').run('failed', e.message, id);
    console.error(`[email] failed ${id}: ${e.message}`);
  }
  processing = false;
  if (queue.length) setImmediate(processQueue);
}

// === Routes ===
app.get('/templates', (req, res) => res.json({ templates: db.prepare('SELECT name FROM templates').all() }));
app.get('/templates/:name', (req, res) => {
  const t = db.prepare('SELECT * FROM templates WHERE name = ?').get(req.params.name);
  t ? res.json(t) : res.status(404).json({ error: 'not_found' });
});
app.post('/templates/:name/render', (req, res) => {
  const t = db.prepare('SELECT * FROM templates WHERE name = ?').get(req.params.name);
  if (!t) return res.status(404).json({ error: 'template_not_found' });
  res.json({ subject: render(t.subject, req.body), body: render(t.body, req.body) });
});

app.post('/send', (req, res) => {
  const { to, template, vars, subject, body } = req.body;
  if (!to) return res.status(422).json({ error: 'missing_to' });
  let finalSubject = subject, finalBody = body;
  if (template) {
    const t = db.prepare('SELECT * FROM templates WHERE name = ?').get(template);
    if (!t) return res.status(404).json({ error: 'template_not_found' });
    finalSubject = render(t.subject, vars || {});
    finalBody = render(t.body, vars || {});
  }
  if (!finalSubject || !finalBody) return res.status(422).json({ error: 'missing_subject_or_body' });
  const id = 'em_' + crypto.randomBytes(6).toString('hex');
  db.prepare('INSERT INTO emails (id, to_email, subject, body) VALUES (?, ?, ?, ?)').run(id, to, finalSubject, finalBody);
  queue.push(id);
  processQueue();
  res.status(202).json({ id, status: 'queued', subject: finalSubject });
});

app.get('/emails', (req, res) => {
  const status = req.query.status;
  const rows = status ? db.prepare('SELECT * FROM emails WHERE status = ? ORDER BY sent_at DESC LIMIT 50').all(status) : db.prepare('SELECT * FROM emails ORDER BY sent_at DESC LIMIT 50').all();
  res.json({ count: rows.length, emails: rows });
});

app.get('/emails/:id', (req, res) => {
  const email = db.prepare('SELECT * FROM emails WHERE id = ?').get(req.params.id);
  email ? res.json(email) : res.status(404).json({ error: 'not_found' });
});

app.listen(3000, () => console.log('Email demo :3000 — GET /templates, POST /send'));
module.exports = app;
