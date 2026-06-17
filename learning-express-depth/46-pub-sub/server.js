// 46 — Pub/Sub
// NEW CONCEPT: publish/subscribe.
// One part of the app publishes an event. Other parts subscribe to events.
// The publisher doesn't know who's listening. The subscribers don't know who's publishing.
const express = require('express');
const app = express();
app.use(express.json());

// Event bus: topic -> array of handler functions
const subscribers = new Map();
const eventLog = [];

function subscribe(topic, handler) {
  if (!subscribers.has(topic)) subscribers.set(topic, []);
  subscribers.get(topic).push(handler);
  return () => {
    // Return an unsubscribe function
    const arr = subscribers.get(topic);
    const i = arr.indexOf(handler);
    if (i !== -1) arr.splice(i, 1);
  };
}

async function publish(topic, data) {
  const handlers = subscribers.get(topic) || [];
  const event = { id: Date.now(), topic, data, ts: new Date().toISOString() };
  eventLog.push(event);
  if (eventLog.length > 100) eventLog.shift();
  await Promise.all(handlers.map(h => Promise.resolve().then(() => h(event)).catch(e => console.error('Handler error:', e))));
  return { eventId: event.id, subscriberCount: handlers.length };
}

// Built-in subscribers
subscribe('user.created', (event) => {
  console.log(`[email] Sending welcome to ${event.data.email}`);
});
subscribe('user.created', (event) => {
  console.log(`[analytics] Recording signup: ${event.data.email}`);
});
subscribe('order.created', (event) => {
  console.log(`[inventory] Reserving stock for order ${event.data.id}`);
});

// API: trigger events
app.post('/publish/:topic', async (req, res) => {
  const result = await publish(req.params.topic, req.body);
  res.status(202).json(result);
});

app.get('/events', (req, res) => {
  res.json({ count: eventLog.length, events: eventLog.slice(-20) });
});

app.get('/admin/subscribers', (req, res) => {
  const out = {};
  for (const [topic, handlers] of subscribers) out[topic] = handlers.length;
  res.json(out);
});

app.listen(3000, () => console.log('Pub/Sub on http://localhost:3000'));
