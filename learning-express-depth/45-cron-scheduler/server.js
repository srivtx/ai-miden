// 45 — Cron Scheduler
// NEW CONCEPT: run tasks on a schedule.
// Cron is the standard format: minute hour day month weekday
const express = require('express');
const app = express();

// Parse a cron field ("*", "5", "*/10", "1,3,5")
function parseField(field, min, max) {
  if (field === '*') return Array.from({ length: max - min + 1 }, (_, i) => i + min);
  if (field.includes(',')) return field.split(',').flatMap(f => parseField(f, min, max));
  if (field.includes('/')) {
    const [range, step] = field.split('/');
    const start = range === '*' ? min : parseInt(range);
    return Array.from({ length: Math.floor((max - start) / parseInt(step)) + 1 }, (_, i) => start + i * parseInt(step));
  }
  if (field.includes('-')) {
    const [a, b] = field.split('-').map(Number);
    return Array.from({ length: b - a + 1 }, (_, i) => i + a);
  }
  return [parseInt(field)];
}

// Check if a cron schedule matches the current time
function shouldRun(schedule) {
  const [m, h, d, mo, w] = schedule.split(' ');
  const now = new Date();
  return (
    parseField(m, 0, 59).includes(now.getMinutes()) &&
    parseField(h, 0, 23).includes(now.getHours()) &&
    parseField(d, 1, 31).includes(now.getDate()) &&
    parseField(mo, 1, 12).includes(now.getMonth() + 1) &&
    parseField(w, 0, 6).includes(now.getDay())
  );
}

// Task registry: name -> function
const tasks = {
  'log-time': () => console.log(`[cron] Current time: ${new Date().toISOString()}`),
  'send-digest': () => console.log('[cron] Sending daily digest...'),
  'cleanup': () => console.log('[cron] Cleaning up old data...'),
};

// Schedule: name -> cron expression
const schedules = {
  'log-time': '* * * * *',      // every minute
  'send-digest': '0 9 * * *',   // every day at 9am
  'cleanup': '0 3 * * *',       // every day at 3am
};

// Check schedules every 10 seconds
setInterval(() => {
  for (const [name, schedule] of Object.entries(schedules)) {
    if (shouldRun(schedule) && tasks[name]) {
      tasks[name]();
    }
  }
}, 10000);

// API to manage schedules
app.get('/schedules', (req, res) => res.json(schedules));

app.post('/schedules/:name', (req, res) => {
  const { schedule } = req.body;
  if (!schedule) return res.status(422).json({ error: 'schedule required' });
  // Validate by trying to parse
  try {
    schedule.split(' ').forEach((field, i) => {
      const [min, max] = [[0, 59], [0, 23], [1, 31], [1, 12], [0, 6]][i];
      parseField(field, min, max);
    });
  } catch (e) {
    return res.status(422).json({ error: 'invalid schedule' });
  }
  schedules[req.params.name] = schedule;
  res.json({ name: req.params.name, schedule });
});

app.listen(3000, () => console.log('Cron scheduler on http://localhost:3000'));
