// 03-funnels: Track a sequence of events. "Of people who visited /home, how many signed up?"
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE events (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, event_name TEXT, ts TEXT DEFAULT (datetime('now')))`);

// Funnel definition: ordered list of event names
const FUNNELS = {
  signup: ['page_view', 'click_signup', 'fill_form', 'submit_form', 'account_created'],
  purchase: ['view_product', 'add_to_cart', 'checkout', 'payment', 'order_placed'],
};

// Compute a funnel for a time range
app.get('/funnels/:name', (req, res) => {
  const funnel = FUNNELS[req.params.name];
  if (!funnel) return res.status(404).json({ error: 'unknown funnel' });
  const since = req.query.since || new Date(Date.now() - 7 * 86400000).toISOString();

  const steps = funnel.map((event, i) => {
    // Count unique users who did this event AND all previous events
    const prevEvents = funnel.slice(0, i + 1);
    const placeholders = prevEvents.map(() => '?').join(',');
    const result = db.prepare(`
      SELECT COUNT(DISTINCT user_id) as count
      FROM events
      WHERE user_id IS NOT NULL
        AND event_name IN (${placeholders})
        AND ts > ?
        AND user_id IN (
          SELECT user_id FROM events
          WHERE event_name = ? AND ts > ?
          GROUP BY user_id
          HAVING COUNT(*) >= 1
        )
    `).get(...prevEvents, since, event, since);

    return { step: i + 1, event, count: result.count };
  });

  // Calculate drop-off
  let prevCount = steps[0]?.count || 0;
  for (const step of steps) {
    step.conversion_from_first = steps[0].count ? Math.round(step.count / steps[0].count * 1000) / 10 : 0;
    step.conversion_from_previous = prevCount ? Math.round(step.count / prevCount * 1000) / 10 : 0;
    step.drop_off = prevCount - step.count;
    prevCount = step.count;
  }

  res.json({ funnel: req.params.name, since, steps });
});

app.listen(3000, () => console.log('03-funnels on :3000'));
