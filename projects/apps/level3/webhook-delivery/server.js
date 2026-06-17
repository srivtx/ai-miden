// Webhook Delivery Service — Outbound webhooks with retry, signing, dead letter queue.
const express = require('express');
const crypto = require('crypto');
const https = require('https');
const http = require('http');
const { URL } = require('url');
const app = express();
app.use(express.json());

const endpoints = []; // subscriptions: { id, targetUrl, secret, events, ownerId }
const deliveries = []; // { id, subscriptionId, event, payload, status, attempts, lastAttemptAt, responseCode, responseBody }
const deadLetters = []; let eId = 1, dId = 1, dlqId = 1;

const MAX_ATTEMPTS = 5;

// Simple webhook delivery (in real app: use a queue like Bull/RabbitMQ)
async function deliver(delivery) {
  const sub = endpoints.find(s => s.id === delivery.subscriptionId);
  if (!sub) return;

  // Sign the payload with HMAC-SHA256
  const signature = crypto.createHmac('sha256', sub.secret).update(delivery.payload).digest('hex');
  const headers = {
    'Content-Type': 'application/json',
    'X-Webhook-Signature': signature,
    'X-Webhook-Event': delivery.event,
    'X-Webhook-Delivery-Id': String(delivery.id),
    'X-Webhook-Attempt': String(delivery.attempts + 1),
  };

  const url = new URL(sub.targetUrl);
  const lib = url.protocol === 'https:' ? https : http;
  const body = JSON.stringify(JSON.parse(delivery.payload));

  return new Promise((resolve) => {
    const start = Date.now();
    const req = lib.request({ method: 'POST', hostname: url.hostname, port: url.port || (url.protocol === 'https:' ? 443 : 80), path: url.pathname, headers: { ...headers, 'Content-Length': Buffer.byteLength(body) } }, (res) => {
      let responseBody = '';
      res.on('data', c => responseBody += c);
      res.on('end', () => {
        delivery.attempts++;
        delivery.lastAttemptAt = new Date().toISOString();
        delivery.responseCode = res.statusCode;
        delivery.responseBody = responseBody.slice(0, 500);
        delivery.durationMs = Date.now() - start;
        delivery.status = (res.statusCode >= 200 && res.statusCode < 300) ? 'success' : 'failed';
        if (delivery.status === 'failed' && delivery.attempts < MAX_ATTEMPTS) delivery.nextRetryAt = new Date(Date.now() + Math.pow(2, delivery.attempts) * 1000).toISOString();
        if (delivery.attempts >= MAX_ATTEMPTS && delivery.status === 'failed') { delivery.status = 'dead_letter'; deadLetters.push({ id: dlqId++, deliveryId: delivery.id, subscriptionId: delivery.subscriptionId, failedAt: new Date().toISOString() }); }
        resolve();
      });
    });
    req.on('error', (e) => { delivery.attempts++; delivery.lastAttemptAt = new Date().toISOString(); delivery.status = 'failed'; delivery.error = e.message; resolve(); });
    req.write(body);
    req.end();
  });
}

// Register endpoint
app.post('/webhook-endpoints', (req, res) => {
  const { targetUrl, secret, events } = req.body;
  if (!targetUrl || !secret) return res.status(400).json({ error: 'targetUrl and secret required' });
  try { new URL(targetUrl); } catch { return res.status(400).json({ error: 'Invalid URL' }); }
  const ep = { id: eId++, targetUrl, secret, events: events || ['*'], active: true, createdAt: new Date().toISOString() };
  endpoints.push(ep);
  res.status(201).json(ep);
});

app.get('/webhook-endpoints', (req, res) => res.json(endpoints));

// Trigger event (delivers to all matching endpoints)
app.post('/trigger/:event', async (req, res) => {
  const eventName = req.params.event;
  const matching = endpoints.filter(e => e.active && (e.events.includes('*') || e.events.includes(eventName)));
  if (!matching.length) return res.json({ delivered: 0 });
  const payload = JSON.stringify({ event: eventName, data: req.body, timestamp: new Date().toISOString() });
  // Create delivery records and attempt
  const results = [];
  for (const sub of matching) {
    const delivery = { id: dId++, subscriptionId: sub.id, event: eventName, payload, status: 'pending', attempts: 0, createdAt: new Date().toISOString() };
    deliveries.push(delivery);
    await deliver(delivery); // await sequentially to demonstrate (in real app, parallel)
    results.push({ id: delivery.id, status: delivery.status, attempts: delivery.attempts });
  }
  res.json({ event: eventName, attempts: results });
});

// View deliveries
app.get('/deliveries', (req, res) => {
  let result = [...deliveries];
  if (req.query.status) result = result.filter(d => d.status === req.query.status);
  if (req.query.subscription) result = result.filter(d => d.subscriptionId === parseInt(req.query.subscription));
  if (req.query.event) result = result.filter(d => d.event === req.query.event);
  result.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
  res.json({ total: result.length, data: result.slice(0, 100) });
});

// Retry a failed delivery
app.post('/deliveries/:id/retry', async (req, res) => {
  const d = deliveries.find(d => d.id === parseInt(req.params.id));
  if (!d) return res.status(404).json({ error: 'Not found' });
  d.attempts = 0; d.status = 'pending';
  await deliver(d);
  res.json(d);
});

// Dead letter queue
app.get('/dead-letters', (req, res) => res.json(deadLetters));

// Stats
app.get('/stats', (req, res) => {
  const total = deliveries.length;
  const success = deliveries.filter(d => d.status === 'success').length;
  const failed = deliveries.filter(d => d.status === 'failed').length;
  const dead = deliveries.filter(d => d.status === 'dead_letter').length;
  res.json({ total, success, failed, dead, successRate: total ? (success / total * 100).toFixed(1) + '%' : '0%' });
});

app.listen(3000, () => console.log('Webhook Delivery :3000'));
module.exports = app;
