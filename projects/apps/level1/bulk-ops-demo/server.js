// Bulk Operations Demo — Insert/update/delete many rows in one request, with progress.
const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE items (id TEXT PRIMARY KEY, name TEXT, value INTEGER, updated_at INTEGER)`);
db.exec(`CREATE TABLE bulk_jobs (id TEXT PRIMARY KEY, type TEXT, status TEXT, total INTEGER, processed INTEGER DEFAULT 0, errors INTEGER DEFAULT 0, started_at INTEGER, finished_at INTEGER)`);

const insertItem = db.prepare('INSERT INTO items (id, name, value, updated_at) VALUES (?, ?, ?, ?)');
const updateItem = db.prepare('UPDATE items SET value = ?, updated_at = ? WHERE id = ?');
const deleteItem = db.prepare('DELETE FROM items WHERE id = ?');
const getItem = db.prepare('SELECT * FROM items WHERE id = ?');

function updateJob(id, fields) {
  const keys = Object.keys(fields);
  const sets = keys.map(k => `${k} = ?`).join(', ');
  db.prepare(`UPDATE bulk_jobs SET ${sets} WHERE id = ?`).run(...keys.map(k => fields[k]), id);
}

async function runBulk(jobId, items, op) {
  const total = items.length;
  updateJob(jobId, { status: 'running', total, started_at: Date.now() });
  let processed = 0, errors = 0;
  const errorDetails = [];
  for (let i = 0; i < items.length; i++) {
    try {
      op(items[i]);
      processed++;
    } catch (e) {
      errors++;
      errorDetails.push({ index: i, error: e.message });
    }
    if (i % 100 === 0) updateJob(jobId, { processed, errors });
  }
  updateJob(jobId, { status: errors > 0 ? 'partial' : 'completed', processed, errors, finished_at: Date.now() });
  return { processed, errors, errorDetails: errorDetails.slice(0, 10) };
}

app.post('/bulk/insert', async (req, res) => {
  if (!Array.isArray(req.body.items)) return res.status(422).json({ error: 'items_must_be_array' });
  const jobId = 'bj_' + crypto.randomBytes(6).toString('hex');
  db.prepare('INSERT INTO bulk_jobs (id, type) VALUES (?, ?)').run(jobId, 'insert');
  // Run async; client polls for status
  setImmediate(async () => {
    await runBulk(jobId, req.body.items, (item) => {
      if (!item.id) item.id = 'it_' + crypto.randomBytes(4).toString('hex');
      if (!item.name) throw new Error('missing name');
      insertItem.run(item.id, item.name, item.value || 0, Date.now());
    });
  });
  res.status(202).json({ jobId, statusUrl: '/bulk/jobs/' + jobId });
});

app.post('/bulk/update', async (req, res) => {
  if (!Array.isArray(req.body.updates)) return res.status(422).json({ error: 'updates_must_be_array' });
  const jobId = 'bj_' + crypto.randomBytes(6).toString('hex');
  db.prepare('INSERT INTO bulk_jobs (id, type) VALUES (?, ?)').run(jobId, 'update');
  setImmediate(async () => {
    await runBulk(jobId, req.body.updates, (u) => {
      if (!u.id) throw new Error('missing id');
      if (!getItem.get(u.id)) throw new Error('not found: ' + u.id);
      updateItem.run(u.value, Date.now(), u.id);
    });
  });
  res.status(202).json({ jobId, statusUrl: '/bulk/jobs/' + jobId });
});

app.post('/bulk/delete', async (req, res) => {
  if (!Array.isArray(req.body.ids)) return res.status(422).json({ error: 'ids_must_be_array' });
  const jobId = 'bj_' + crypto.randomBytes(6).toString('hex');
  db.prepare('INSERT INTO bulk_jobs (id, type) VALUES (?, ?)').run(jobId, 'delete');
  setImmediate(async () => {
    await runBulk(jobId, req.body.ids, (id) => { deleteItem.run(id); });
  });
  res.status(202).json({ jobId, statusUrl: '/bulk/jobs/' + jobId });
});

app.get('/bulk/jobs/:id', (req, res) => {
  const job = db.prepare('SELECT * FROM bulk_jobs WHERE id = ?').get(req.params.id);
  job ? res.json(job) : res.status(404).json({ error: 'not_found' });
});

app.get('/items', (req, res) => {
  const items = db.prepare('SELECT * FROM items LIMIT 100').all();
  res.json({ count: items.length, items });
});

app.get('/items/count', (req, res) => res.json({ count: db.prepare('SELECT COUNT(*) as c FROM items').get().c }));

app.listen(3000, () => console.log('Bulk ops demo :3000 — POST /bulk/insert with { items: [...] }'));
module.exports = app;
