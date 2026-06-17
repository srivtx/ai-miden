// 07-webhooks: Stripe-style webhooks. Subscribe to payment events, get notified.
const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const app = express();
app.use(express.json());

const SECRET = 'webhook-secret';
const db = new Database(':memory:');
db.exec(`CREATE TABLE webhook_endpoints (id TEXT PRIMARY KEY, url TEXT, secret TEXT, events TEXT, active INTEGER DEFAULT 1)`);
db.exec(`CREATE TABLE webhook_deliveries (id INTEGER PRIMARY KEY AUTOINCREMENT, endpoint_id TEXT, event TEXT, payload TEXT, status TEXT DEFAULT 'pending', attempts INTEGER DEFAULT 0, last_error TEXT, created_at TEXT DEFAULT (datetime('now')), delivered_at TEXT)`);

function sign(payload) {
  return 'sha256=' + crypto.createHmac('sha256', SECRET).update(payload).digest('hex');
}

// Register a webhook endpoint
app.post('/webhooks', (req, res) => {
  const { url, events } = req.body;
  if (!url) return res.status(422).json({ error: 'url required' });
  const id = 'wh_' + crypto.randomBytes(4).toString('hex');
  const secret = crypto.randomBytes(16).toString('hex');
  db.prepare('INSERT INTO webhook_endpoints VALUES (?, ?, ?, ?, 1)').run(id, url, secret, JSON.stringify(events || ['*']));
  res.status(201).json({ id, url, events: events || ['*'], secret });
});

// Fire an event (called by the rest of the system)
async function fireEvent(event, payload) {
  const endpoints = db.prepare('SELECT * FROM webhook_endpoints WHERE active = 1').all();
  for (const ep of endpoints) {
    const events = JSON.parse(ep.events);
    if (events.includes('*') || events.includes(event)) {
      const body = JSON.stringify({ event, data: payload, ts: Date.now() });
      const sig = sign(body);
      // Simulate delivery
      const deliveryId = db.prepare("INSERT INTO webhook_deliveries (endpoint_id, event, payload, status) VALUES (?, ?, ?, 'pending')").run(ep.id, event, body).lastInsertRowid;
      console.log(`[webhook] Would POST to ${ep.url}: X-Signature: ${sig}`);
      db.prepare("UPDATE webhook_deliveries SET status = 'delivered', attempts = attempts + 1, delivered_at = datetime('now') WHERE id = ?").run(deliveryId);
    }
  }
}

// Test endpoint to fire an event
app.post('/test/fire', (req, res) => {
  fireEvent(req.body.event || 'charge.succeeded', req.body.data || {});
  res.json({ fired: true });
});

app.get('/webhooks/:id/deliveries', (req, res) => {
  const rows = db.prepare('SELECT * FROM webhook_deliveries WHERE endpoint_id = ? ORDER BY id DESC LIMIT 50').all(req.params.id);
  res.json({ deliveries: rows });
});

app.listen(3000, () => console.log('07-webhooks on :3000 (HMAC signed)'));
