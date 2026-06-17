// Migration Demo — Versioned schema migrations with up/down and tracking in SQLite.
const express = require('express');
const Database = require('better-sqlite3');
const fs = require('fs');
const path = require('path');
const app = express();
app.use(express.json());

const MIGRATIONS_DIR = path.join(__dirname, 'migrations');
if (!fs.existsSync(MIGRATIONS_DIR)) fs.mkdirSync(MIGRATIONS_DIR);

const db = new Database(':memory:');
db.exec(`CREATE TABLE schema_migrations (version INTEGER PRIMARY KEY, name TEXT, applied_at INTEGER)`);

// === Define migrations inline (in real apps, separate .sql files) ===
const migrations = [
  { version: 1, name: 'create_users', up: `CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE NOT NULL, created_at TEXT DEFAULT (datetime('now')))`, down: `DROP TABLE users` },
  { version: 2, name: 'create_posts', up: `CREATE TABLE posts (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL REFERENCES users(id), title TEXT NOT NULL, body TEXT, created_at TEXT DEFAULT (datetime('now')))`, down: `DROP TABLE posts` },
  { version: 3, name: 'add_user_name', up: `ALTER TABLE users ADD COLUMN name TEXT`, down: `-- SQLite doesn't support DROP COLUMN easily; recreating would be needed` },
  { version: 4, name: 'create_comments', up: `CREATE TABLE comments (id INTEGER PRIMARY KEY AUTOINCREMENT, post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE, user_id INTEGER NOT NULL REFERENCES users(id), body TEXT NOT NULL, created_at TEXT DEFAULT (datetime('now')))`, down: `DROP TABLE comments` },
  { version: 5, name: 'index_posts_user', up: `CREATE INDEX idx_posts_user ON posts(user_id)`, down: `DROP INDEX idx_posts_user` },
];

// === Run pending migrations ===
function migrate() {
  const applied = new Set(db.prepare('SELECT version FROM schema_migrations').all().map(r => r.version));
  const pending = migrations.filter(m => !applied.has(m.version)).sort((a, b) => a.version - b.version);
  const appliedNow = [];
  for (const m of pending) {
    db.exec('BEGIN');
    try {
      db.exec(m.up);
      db.prepare('INSERT INTO schema_migrations (version, name, applied_at) VALUES (?, ?, ?)').run(m.version, m.name, Date.now());
      db.exec('COMMIT');
      appliedNow.push(m);
    } catch (e) {
      db.exec('ROLLBACK');
      throw new Error(`Migration ${m.version} (${m.name}) failed: ${e.message}`);
    }
  }
  return appliedNow;
}

function rollback(steps = 1) {
  const applied = db.prepare('SELECT * FROM schema_migrations ORDER BY version DESC').all();
  const toRevert = applied.slice(0, steps);
  for (const m of toRevert) {
    const def = migrations.find(x => x.version === m.version);
    if (!def || !def.down) throw new Error(`No down migration for version ${m.version}`);
    db.exec('BEGIN');
    try { db.exec(def.down); db.prepare('DELETE FROM schema_migrations WHERE version = ?').run(m.version); db.exec('COMMIT'); }
    catch (e) { db.exec('ROLLBACK'); throw e; }
  }
  return toRevert;
}

// === Routes ===
app.post('/migrate', (req, res) => {
  try {
    const applied = migrate();
    res.json({ applied: applied.length, migrations: applied.map(m => ({ version: m.version, name: m.name })) });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

app.post('/rollback', (req, res) => {
  try {
    const steps = parseInt(req.query.steps) || 1;
    const reverted = rollback(steps);
    res.json({ reverted: reverted.length, versions: reverted.map(m => m.version) });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

app.get('/migrations', (req, res) => {
  const applied = db.prepare('SELECT * FROM schema_migrations ORDER BY version').all();
  const all = migrations.map(m => ({ ...m, applied: applied.some(a => a.version === m.version), appliedAt: applied.find(a => a.version === m.version)?.applied_at }));
  res.json({ total: migrations.length, applied: applied.length, pending: migrations.length - applied.length, migrations: all });
});

app.get('/schema', (req, res) => {
  const tables = db.prepare("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name").all();
  res.json({ tables: tables.map(t => t.name) });
});

app.listen(3000, () => console.log('Migrations demo :3000 — POST /migrate, POST /rollback?steps=N, GET /migrations, GET /schema'));
module.exports = app;
