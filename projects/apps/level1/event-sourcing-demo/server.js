// Event Sourcing Demo — Append-only events, project to current state, replay history.
const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE events (id TEXT PRIMARY KEY, aggregate_id TEXT, type TEXT, data TEXT, version INTEGER, ts INTEGER)`);
db.exec(`CREATE INDEX idx_events_agg ON events(aggregate_id, version)`);

let nextVersion = {};

// === Append an event ===
function appendEvent(aggregateId, type, data) {
  if (!nextVersion[aggregateId]) nextVersion[aggregateId] = 0;
  nextVersion[aggregateId]++;
  const id = 'evt_' + crypto.randomBytes(6).toString('hex');
  db.prepare('INSERT INTO events (id, aggregate_id, type, data, version, ts) VALUES (?, ?, ?, ?, ?, ?)').run(id, aggregateId, type, JSON.stringify(data), nextVersion[aggregateId], Date.now());
  return { id, aggregateId, type, data, version: nextVersion[aggregateId] };
}

// === Project events to current state ===
function getState(aggregateId) {
  const events = db.prepare('SELECT * FROM events WHERE aggregate_id = ? ORDER BY version ASC').all(aggregateId);
  if (events.length === 0) return null;
  let state = { id: aggregateId, type: 'unknown', created: false };
  for (const event of events) {
    state = applyEvent(state, event);
  }
  state.version = events[events.length - 1].version;
  return state;
}

function applyEvent(state, event) {
  const data = JSON.parse(event.data);
  switch (event.type) {
    case 'AccountCreated': return { ...state, type: 'account', email: data.email, name: data.name, balance: 0, status: 'active' };
    case 'MoneyDeposited': return { ...state, balance: state.balance + data.amount };
    case 'MoneyWithdrawn': return { ...state, balance: state.balance - data.amount };
    case 'AccountClosed': return { ...state, status: 'closed' };
    case 'NameChanged': return { ...state, name: data.newName };
    default: return state;
  }
}

// === Business logic (commits events, never mutates state directly) ===
function createAccount(id, email, name) {
  if (getState(id)) throw new Error('account already exists');
  appendEvent(id, 'AccountCreated', { email, name });
}

function deposit(id, amount) {
  const state = getState(id);
  if (!state) throw new Error('account not found');
  if (state.status !== 'active') throw new Error('account not active');
  if (amount <= 0) throw new Error('amount must be positive');
  appendEvent(id, 'MoneyDeposited', { amount });
}

function withdraw(id, amount) {
  const state = getState(id);
  if (!state) throw new Error('account not found');
  if (state.balance < amount) throw new Error('insufficient funds');
  appendEvent(id, 'MoneyWithdrawn', { amount });
}

function changeName(id, newName) {
  const state = getState(id);
  if (!state) throw new Error('account not found');
  appendEvent(id, 'NameChanged', { newName });
}

// === Routes ===
app.post('/accounts', (req, res) => {
  const id = 'acc_' + crypto.randomBytes(4).toString('hex');
  try { createAccount(id, req.body.email, req.body.name); res.status(201).json({ id, state: getState(id) }); }
  catch (e) { res.status(400).json({ error: e.message }); }
});

app.post('/accounts/:id/deposit', (req, res) => {
  try { deposit(req.params.id, parseFloat(req.body.amount)); res.json(getState(req.params.id)); }
  catch (e) { res.status(400).json({ error: e.message }); }
});

app.post('/accounts/:id/withdraw', (req, res) => {
  try { withdraw(req.params.id, parseFloat(req.body.amount)); res.json(getState(req.params.id)); }
  catch (e) { res.status(400).json({ error: e.message }); }
});

app.post('/accounts/:id/change-name', (req, res) => {
  try { changeName(req.params.id, req.body.name); res.json(getState(req.params.id)); }
  catch (e) { res.status(400).json({ error: e.message }); }
});

app.get('/accounts/:id', (req, res) => {
  const state = getState(req.params.id);
  state ? res.json(state) : res.status(404).json({ error: 'not_found' });
});

app.get('/accounts/:id/events', (req, res) => {
  const events = db.prepare('SELECT * FROM events WHERE aggregate_id = ? ORDER BY version ASC').all(req.params.id);
  res.json({ count: events.length, events: events.map(e => ({ ...e, data: JSON.parse(e.data) })) });
});

app.get('/accounts/:id/events/at/:version', (req, res) => {
  const targetVersion = parseInt(req.params.version);
  const events = db.prepare('SELECT * FROM events WHERE aggregate_id = ? AND version <= ? ORDER BY version ASC').all(req.params.id, targetVersion);
  let state = { id: req.params.id };
  for (const e of events) state = applyEvent(state, e);
  res.json({ version: targetVersion, state });
});

app.listen(3000, () => console.log('Event sourcing demo :3000 — append-only events, project to state'));
module.exports = app;
