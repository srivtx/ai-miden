// 02-sms: Send SMS. Twilio-like. Phone number, message, status.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE sms (id TEXT PRIMARY KEY, to_phone TEXT, message TEXT, status TEXT DEFAULT 'queued', attempts INTEGER DEFAULT 0, provider_message_id TEXT, last_error TEXT, created_at TEXT DEFAULT (datetime('now')), sent_at TEXT)`);

async function sendSMS(to, message) {
  await new Promise(r => setTimeout(r, 50));
  // Validate phone
  if (!/^\+\d{10,15}$/.test(to)) return { success: false, error: 'invalid_phone' };
  return { success: true, messageId: 'sms_' + Date.now() };
}

app.post('/sms', async (req, res) => {
  const { to, message } = req.body;
  if (!to || !message) return res.status(422).json({ error: 'to and message required' });
  const id = 'sms_' + Math.random().toString(36).slice(2, 10);
  db.prepare('INSERT INTO sms (id, to_phone, message) VALUES (?, ?, ?)').run(id, to, message);
  setImmediate(processSMS.bind(null, id));
  res.status(202).json({ id, status: 'queued' });
});

async function processSMS(id) {
  const sms = db.prepare('SELECT * FROM sms WHERE id = ?').get(id);
  if (!sms) return;
  const result = await sendSMS(sms.to_phone, sms.message);
  if (result.success) {
    db.prepare("UPDATE sms SET status = 'sent', attempts = attempts + 1, provider_message_id = ?, sent_at = datetime('now') WHERE id = ?").run(result.messageId, id);
    console.log(`[sms] sent ${id} to ${sms.to_phone}`);
  } else {
    db.prepare("UPDATE sms SET status = 'failed', attempts = attempts + 1, last_error = ? WHERE id = ?").run(result.error, id);
  }
}

app.get('/sms/:id', (req, res) => {
  const sms = db.prepare('SELECT * FROM sms WHERE id = ?').get(req.params.id);
  sms ? res.json(sms) : res.status(404).json({ error: 'not found' });
});

app.listen(3000, () => console.log('02-sms on :3000 (E.164 format: +15551234567)'));
