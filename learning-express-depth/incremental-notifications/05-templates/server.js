// 05-templates: Reusable notification templates. Placeholders like {{name}}.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE templates (id TEXT PRIMARY KEY, name TEXT UNIQUE, channel TEXT, subject TEXT, body TEXT, variables TEXT)`);

// Seed
const seeds = [
  { name: 'welcome', channel: 'email', subject: 'Welcome to {{app}}, {{name}}!', body: 'Hi {{name}},\n\nWelcome aboard! Get started at https://{{app}}/start.' },
  { name: 'reset_password', channel: 'email', subject: 'Reset your password', body: 'Click here: https://{{app}}/reset?token={{token}}\n\nExpires in 1 hour.' },
  { name: 'new_follower', channel: 'push', subject: '{{follower}} followed you', body: '' },
  { name: 'order_shipped', channel: 'email', subject: 'Your order has shipped', body: 'Order #{{order_id}} is on its way. Track at https://{{app}}/track/{{tracking}}.' },
];
for (const t of seeds) {
  const vars = extractVars(t.subject + ' ' + t.body);
  db.prepare('INSERT INTO templates VALUES (?, ?, ?, ?, ?, ?)').run('tpl_' + t.name, t.name, t.channel, t.subject, t.body, JSON.stringify(vars));
}

function extractVars(text) {
  return [...text.matchAll(/\{\{(\w+)\}\}/g)].map(m => m[1]);
}

function render(template, vars) {
  let out = template;
  for (const [k, v] of Object.entries(vars)) {
    out = out.replaceAll('{{' + k + '}}', v);
  }
  return out;
}

app.get('/templates', (req, res) => res.json({ templates: db.prepare('SELECT name, channel, variables FROM templates').all() }));

app.post('/templates/:name/render', (req, res) => {
  const tpl = db.prepare('SELECT * FROM templates WHERE name = ?').get(req.params.name);
  if (!tpl) return res.status(404).json({ error: 'not found' });
  res.json({
    channel: tpl.channel,
    subject: render(tpl.subject, req.body),
    body: render(tpl.body, req.body),
  });
});

app.listen(3000, () => console.log('05-templates on :3000 (try welcome, reset_password)'));
