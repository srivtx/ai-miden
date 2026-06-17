// 01-email: Send an email. Queue, status tracking, retry on failure.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE emails (id TEXT PRIMARY KEY, to_email TEXT, subject TEXT, body TEXT, status TEXT DEFAULT 'queued', attempts INTEGER DEFAULT 0, last_error TEXT, created_at TEXT DEFAULT (datetime('now')), sent_at TEXT)`);

// Simulated email send
async function sendEmail(to, subject, body) {
  await new Promise(r => setTimeout(r, 50));
  if (to.includes('@example.com')) return { success: true, messageId: 'msg_' + Date.now() };
  return { success: false, error: 'invalid_recipient' };
}

// Queue an email
app.post('/emails', async (req, res) => {
  const { to, subject, body } = req.body;
  if (!to || !subject) return res.status(422).json({ error: 'to and subject required' });
  const id = 'em_' + Math.random().toString(36).slice(2, 10);
  db.prepare('INSERT INTO emails (id, to_email, subject, body) VALUES (?, ?, ?, ?)').run(id, to, subject, body || '');
  // Process in background
  setImmediate(processEmail.bind(null, id));
  res.status(202).json({ id, status: 'queued' });
});

async function processEmail(id) {
  const email = db.prepare('SELECT * FROM emails WHERE id = ?').get(id);
  if (!email) return;
  const result = await sendEmail(email.to_email, email.subject, email.body);
  if (result.success) {
    db.prepare("UPDATE emails SET status = 'sent', attempts = attempts + 1, sent_at = datetime('now') WHERE id = ?").run(id);
    console.log(`[email] sent ${id} to ${email.to_email}`);
  } else {
    db.prepare("UPDATE emails SET status = 'failed', attempts = attempts + 1, last_error = ? WHERE id = ?").run(result.error, id);
  }
}

// Retry failed
app.post('/emails/:id/retry', (req, res) => {
  const email = db.prepare('SELECT * FROM emails WHERE id = ?').get(req.params.id);
  if (!email) return res.status(404).json({ error: 'not found' });
  if (email.status !== 'failed') return res.status(409).json({ error: 'only retry failed' });
  setImmediate(processEmail.bind(null, email.id));
  res.json({ retrying: true });
});

app.get('/emails/:id', (req, res) => {
  const email = db.prepare('SELECT * FROM emails WHERE id = ?').get(req.params.id);
  email ? res.json(email) : res.status(404).json({ error: 'not found' });
});

app.listen(3000, () => console.log('01-email on :3000 (queue + retry)'));
