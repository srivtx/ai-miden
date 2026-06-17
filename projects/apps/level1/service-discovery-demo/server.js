// Service Discovery Demo — In-memory registry with health checks, TTL, heartbeats.
const express = require('express');
const crypto = require('crypto');
const app = express();
app.use(express.json());

// === Service registry ===
// Each service: { id, name, host, port, metadata, health, lastHeartbeat, ttl }
const registry = new Map();
const services = {}; // name -> Set<id>

function registerService({ name, host, port, metadata = {}, ttl = 30000 }) {
  const id = name + '-' + crypto.randomBytes(4).toString('hex');
  const now = Date.now();
  const service = { id, name, host, port, metadata, ttl, health: 'unknown', lastHeartbeat: now, registeredAt: now };
  registry.set(id, service);
  if (!services[name]) services[name] = new Set();
  services[name].add(id);
  return service;
}

function heartbeat(id) {
  const svc = registry.get(id);
  if (!svc) return null;
  svc.lastHeartbeat = Date.now();
  return svc;
}

function deregister(id) {
  const svc = registry.get(id);
  if (!svc) return false;
  registry.delete(id);
  services[svc.name]?.delete(id);
  if (services[svc.name]?.size === 0) delete services[svc.name];
  return true;
}

function discover(name) {
  const ids = services[name];
  if (!ids) return [];
  return Array.from(ids).map(id => registry.get(id)).filter(s => {
    const alive = Date.now() - s.lastHeartbeat < s.ttl;
    return alive;
  });
}

// === Health check loop: marks services as healthy/unhealthy ===
setInterval(() => {
  const now = Date.now();
  for (const svc of registry.values()) {
    if (now - svc.lastHeartbeat < svc.ttl / 2) svc.health = 'healthy';
    else if (now - svc.lastHeartbeat < svc.ttl) svc.health = 'degraded';
    else svc.health = 'unhealthy';
  }
}, 5000);

// === Routes ===
app.post('/registry/services', (req, res) => {
  const { name, host, port, metadata, ttl } = req.body;
  if (!name || !host || !port) return res.status(422).json({ error: 'missing_fields' });
  const svc = registerService({ name, host, port, metadata, ttl });
  res.status(201).json(svc);
});

app.post('/registry/services/:id/heartbeat', (req, res) => {
  const svc = heartbeat(req.params.id);
  svc ? res.json(svc) : res.status(404).json({ error: 'not_found' });
});

app.delete('/registry/services/:id', (req, res) => {
  deregister(req.params.id) ? res.status(204).end() : res.status(404).json({ error: 'not_found' });
});

app.get('/registry/services', (req, res) => {
  const { health } = req.query;
  let all = Array.from(registry.values());
  if (health) all = all.filter(s => s.health === health);
  res.json({ count: all.length, services: all });
});

app.get('/registry/discover/:name', (req, res) => {
  const found = discover(req.params.name);
  res.json({ service: req.params.name, instances: found, count: found.length });
});

app.get('/registry/services-by-name', (req, res) => {
  const out = {};
  for (const [name, ids] of Object.entries(services)) out[name] = Array.from(ids).length;
  res.json(out);
});

// === Seed ===
const seed = registerService({ name: 'user-service', host: '10.0.0.1', port: 3001, metadata: { version: '1.0' } });
const seed2 = registerService({ name: 'user-service', host: '10.0.0.2', port: 3001, metadata: { version: '1.0' } });
registerService({ name: 'order-service', host: '10.0.0.3', port: 3002, metadata: { version: '2.1' } });

app.listen(3000, () => console.log('Service discovery demo :3000 — GET /registry/discover/:name'));
module.exports = app;
