// Pub/Sub Demo — In-process event bus with topics, subscribers, and persistence.
const express = require('express');
const crypto = require('crypto');
const app = express();
app.use(express.json());

// === Event bus ===
const subscribers = new Map(); // topic -> Set<{id, handler}>
const eventLog = []; // last 100 events
const dlq = []; // failed deliveries

function subscribe(topic, handler) {
  if (!subscribers.has(topic)) subscribers.set(topic, new Set());
  const sub = { id: 'sub_' + crypto.randomBytes(4).toString('hex'), handler };
  subscribers.get(topic).add(sub);
  return sub.id;
}

function unsubscribe(topic, subId) {
  const subs = subscribers.get(topic);
  if (!subs) return false;
  for (const s of subs) {
    if (s.id === subId) { subs.delete(s); return true; }
  }
  return false;
}

async function publish(topic, data, { maxRetries = 3 } = {}) {
  const event = { id: 'evt_' + crypto.randomBytes(6).toString('hex'), topic, data, ts: Date.now(), retries: 0 };
  const subs = subscribers.get(topic) || new Set();
  const results = [];
  for (const sub of subs) {
    let success = false;
    let lastErr = null;
    for (let attempt = 1; attempt <= maxRetries && !success; attempt++) {
      try {
        await sub.handler(event);
        success = true;
        results.push({ subscriber: sub.id, status: 'delivered', attempts: attempt });
      } catch (e) {
        lastErr = e;
        event.retries = attempt;
      }
    }
    if (!success) {
      results.push({ subscriber: sub.id, status: 'failed', error: lastErr?.message });
      dlq.push({ event, subscriber: sub.id, error: lastErr?.message, ts: Date.now() });
    }
  }
  eventLog.unshift({ ...event, results });
  if (eventLog.length > 100) eventLog.pop();
  return { eventId: event.id, delivered: results.filter(r => r.status === 'delivered').length, failed: results.filter(r => r.status === 'failed').length };
}

// === Wildcard subscription: 'user.*' matches 'user.created', 'user.updated' ===
function matchesPattern(topic, pattern) {
  if (!pattern.includes('*')) return topic === pattern;
  const regex = new RegExp('^' + pattern.replace(/\./g, '\\.').replace(/\*/g, '[^.]+') + '$');
  return regex.test(topic);
}

const wildcardSubs = []; // { id, pattern, handler }
function subscribePattern(pattern, handler) {
  const sub = { id: 'wsub_' + crypto.randomBytes(4).toString('hex'), pattern, handler };
  wildcardSubs.push(sub);
  return sub.id;
}

// === Built-in subscribers ===
subscribe('user.created', async (event) => {
  console.log(`[email] Sending welcome email to user ${event.data.email}`);
});
subscribe('user.created', async (event) => {
  console.log(`[analytics] Recording signup: ${event.data.email}`);
});
subscribe('order.created', async (event) => {
  console.log(`[inventory] Reserving stock for order ${event.data.id}`);
});
subscribePattern('user.*', async (event) => {
  console.log(`[audit] User event: ${event.topic} - ${JSON.stringify(event.data)}`);
});

// === Routes ===
app.post('/subscribe/:topic', (req, res) => {
  const id = subscribe(req.params.topic, async (event) => {
    if (req.body.failRate && Math.random() < req.body.failRate) throw new Error('simulated failure');
    console.log(`[custom-sub ${id}] Got ${event.topic}: ${JSON.stringify(event.data)}`);
  });
  res.status(201).json({ subscriptionId: id, topic: req.params.topic });
});

app.post('/publish/:topic', async (req, res) => {
  const result = await publish(req.params.topic, req.body);
  res.status(202).json(result);
});

app.get('/events', (req, res) => {
  const { topic, limit = 20 } = req.query;
  let events = eventLog;
  if (topic) events = events.filter(e => e.topic === topic || matchesPattern(e.topic, topic));
  res.json({ count: Math.min(events.length, limit), events: events.slice(0, parseInt(limit)) });
});

app.get('/dlq', (req, res) => res.json({ count: dlq.length, items: dlq.slice(0, 20) }));
app.get('/admin/subscribers', (req, res) => {
  const out = {};
  for (const [topic, subs] of subscribers) out[topic] = subs.size;
  res.json({ byTopic: out, wildcardSubs: wildcardSubs.length });
});

app.listen(3000, () => console.log('Pub/Sub demo :3000 — POST /publish/:topic, GET /events'));
module.exports = app;
