// 06-exports: Export events as CSV or JSON. Stream large exports.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();

const db = new Database(':memory:');
db.exec(`CREATE TABLE events (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, event_name TEXT, properties TEXT, ts TEXT DEFAULT (datetime('now')))`);

// JSON export (streamed for large data)
app.get('/export/events.json', (req, res) => {
  res.set('Content-Type', 'application/x-ndjson');
  res.set('Content-Disposition', 'attachment; filename=events.ndjson');
  const stmt = db.prepare('SELECT * FROM events ORDER BY id');
  for (const e of stmt.all()) {
    res.write(JSON.stringify({ ...e, properties: JSON.parse(e.properties || '{}') }) + '\n');
  }
  res.end();
});

// CSV export
app.get('/export/events.csv', (req, res) => {
  res.set('Content-Type', 'text/csv');
  res.set('Content-Disposition', 'attachment; filename=events.csv');
  res.write('id,user_id,event_name,ts,properties\n');
  const stmt = db.prepare('SELECT * FROM events ORDER BY id');
  for (const e of stmt.all()) {
    const props = (e.properties || '').replace(/"/g, '""');  // Escape quotes
    res.write(`${e.id},${e.user_id || ''},${e.event_name},${e.ts},"${props}"\n`);
  }
  res.end();
});

app.listen(3000, () => console.log('06-exports on :3000 (try /export/events.csv)'));
