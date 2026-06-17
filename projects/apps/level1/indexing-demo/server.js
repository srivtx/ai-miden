// Database Indexing Demo — Compare query time with/without indexes on SQLite.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();

const db = new Database(':memory:');

// === STEP 1: Create a large table WITHOUT indexes ===
db.exec(`CREATE TABLE users_no_idx (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT, name TEXT, age INTEGER, created_at TEXT
)`);

// === STEP 2: Create the same table WITH indexes ===
db.exec(`CREATE TABLE users_with_idx (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT UNIQUE, name TEXT, age INTEGER, created_at TEXT
)`);
db.exec('CREATE INDEX idx_users_age ON users_with_idx(age)');
db.exec('CREATE INDEX idx_users_created ON users_with_idx(created_at DESC)');

// === STEP 3: Insert 50K rows into each ===
console.log('Inserting 50K rows into each table...');
const insert1 = db.prepare('INSERT INTO users_no_idx (email, name, age, created_at) VALUES (?, ?, ?, ?)');
const insert2 = db.prepare('INSERT INTO users_with_idx (email, name, age, created_at) VALUES (?, ?, ?, ?)');
const tx1 = db.transaction(() => { for (let i = 0; i < 50000; i++) insert1.run(`user${i}@x.com`, `User ${i}`, 20 + i % 50, new Date().toISOString()); });
const tx2 = db.transaction(() => { for (let i = 0; i < 50000; i++) insert2.run(`user${i}@x.com`, `User ${i}`, 20 + i % 50, new Date().toISOString()); });
tx1(); tx2();
console.log('Done.');

// === STEP 4: Compare query times ===
function timeQuery(label, table, where, params) {
  const start = process.hrtime.bigint();
  const result = db.prepare(`SELECT * FROM ${table} ${where}`).all(params);
  const end = process.hrtime.bigint();
  const ms = Number(end - start) / 1e6;
  console.log(`  ${label}: ${ms.toFixed(2)}ms (${result.length} results)`);
  return { ms, count: result.length };
}

app.get('/benchmark', (req, res) => {
  const results = {};
  // Email lookup
  results.email_lookup = {
    no_index: timeQuery('Without index', 'users_no_idx', 'WHERE email = ?', [`user25000@x.com`]),
    with_index: timeQuery('With index', 'users_with_idx', 'WHERE email = ?', [`user25000@x.com`]),
  };
  // Range query
  results.age_range = {
    no_index: timeQuery('Without index', 'users_no_idx', 'WHERE age BETWEEN ? AND ?', [25, 30]),
    with_index: timeQuery('With index', 'users_with_idx', 'WHERE age BETWEEN ? AND ?', [25, 30]),
  };
  // Sort
  results.sort_recent = {
    no_index: timeQuery('Without index', 'users_no_idx', 'ORDER BY created_at DESC LIMIT 20', []),
    with_index: timeQuery('With index', 'users_with_idx', 'ORDER BY created_at DESC LIMIT 20', []),
  };
  res.json(results);
});

// === STEP 5: Show the query plan ===
app.get('/explain/:table/:type', (req, res) => {
  const { table, type } = req.params;
  let sql;
  if (type === 'email') sql = `SELECT * FROM ${table} WHERE email = 'user25000@x.com'`;
  else if (type === 'age') sql = `SELECT * FROM ${table} WHERE age = 30`;
  else if (type === 'sort') sql = `SELECT * FROM ${table} ORDER BY created_at DESC LIMIT 20`;
  else return res.status(400).json({ error: 'type must be email, age, or sort' });
  const plan = db.prepare(`EXPLAIN QUERY PLAN ${sql}`).all();
  res.json({ table, type, plan });
});

// === STEP 6: List indexes on a table ===
app.get('/indexes/:table', (req, res) => {
  const indexes = db.prepare(`PRAGMA index_list(?)`).all(req.params.table);
  res.json(indexes);
});

app.listen(3000, () => console.log('Indexing demo :3000 (GET /benchmark)'));
module.exports = app;
