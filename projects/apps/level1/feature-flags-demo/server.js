// Feature Flags Demo — Rollout percentages, user targeting, A/B variants, kill switch.
const express = require('express');
const app = express();
app.use(express.json());

// === Flag definitions ===
const flags = {
  new_checkout: { type: 'boolean', default: false, rollout: 25, description: 'New checkout flow' },
  beta_search: { type: 'boolean', default: false, rollout: 10 },
  dark_mode: { type: 'boolean', default: true, rollout: 100 },
  pricing_tier: { type: 'variant', variants: ['control', 'discount_10', 'discount_20'], weights: [70, 20, 10] },
  new_recommendation: { type: 'boolean', default: false, rollout: 50, killSwitch: true },
};

// === Persistent state ===
const overrides = new Map(); // flag -> { users: Set, percentage }
const evaluations = []; // history

// === Evaluation logic ===
function evaluate(flagName, { userId = 'anonymous' } = {}) {
  const flag = flags[flagName];
  if (!flag) return { value: null, reason: 'unknown_flag' };
  const override = overrides.get(flagName);

  // Kill switch
  if (flag.killSwitch && override?.killSwitch) {
    return { value: flag.type === 'boolean' ? false : flag.default, reason: 'killed' };
  }

  // User-specific override
  if (override?.users?.has(userId)) {
    return { value: override.value, reason: 'user_override' };
  }

  // Percentage rollout (deterministic based on userId hash)
  if (flag.rollout !== undefined) {
    const hash = simpleHash(userId + flagName);
    const bucket = hash % 100;
    if (bucket >= (flag.rollout ?? 0)) {
      return { value: flag.type === 'boolean' ? false : (flag.variants?.[0] || flag.default), reason: 'not_in_rollout' };
    }
  }

  // Variant with weights
  if (flag.type === 'variant') {
    const hash = simpleHash(userId + flagName);
    let cumulative = 0;
    const totalWeight = flag.weights.reduce((a, b) => a + b, 0);
    const pick = (hash % 100) * totalWeight / 100;
    for (let i = 0; i < flag.variants.length; i++) {
      cumulative += flag.weights[i];
      if (pick < cumulative) return { value: flag.variants[i], reason: 'variant' };
    }
  }

  return { value: flag.type === 'boolean' ? flag.default : flag.default, reason: 'default' };
}

function simpleHash(str) {
  let h = 0;
  for (let i = 0; i < str.length; i++) h = ((h << 5) - h + str.charCodeAt(i)) | 0;
  return Math.abs(h);
}

// === Middleware: add evaluation to request ===
app.use((req, res, next) => {
  req.userId = req.headers['x-user-id'] || 'anonymous';
  req.flags = new Proxy({}, { get: (_, name) => evaluate(name, { userId: req.userId }).value });
  next();
});

// === Routes ===
app.get('/flags', (req, res) => res.json({ flags }));
app.get('/flags/evaluate', (req, res) => {
  const result = {};
  for (const name of Object.keys(flags)) result[name] = evaluate(name, { userId: req.userId });
  res.json({ userId: req.userId, evaluations: result });
});

app.post('/admin/flags/:name/override', (req, res) => {
  const { users, value, killSwitch } = req.body;
  if (!flags[req.params.name]) return res.status(404).json({ error: 'unknown_flag' });
  overrides.set(req.params.name, { users: new Set(users || []), value, killSwitch: !!killSwitch });
  res.json({ flag: req.params.name, override: overrides.get(req.params.name) });
});

app.post('/admin/flags/:name/rollout', (req, res) => {
  if (!flags[req.params.name]) return res.status(404).json({ error: 'unknown_flag' });
  const pct = parseInt(req.body.percentage);
  if (isNaN(pct) || pct < 0 || pct > 100) return res.status(422).json({ error: 'invalid_percentage' });
  flags[req.params.name].rollout = pct;
  res.json({ flag: req.params.name, rollout: pct });
});

// === Endpoints that USE flags ===
app.get('/checkout', (req, res) => {
  if (req.flags.new_checkout) return res.json({ version: 'v2', items: [] });
  res.json({ version: 'v1', items: [] });
});

app.get('/pricing', (req, res) => {
  const tier = req.flags.pricing_tier;
  const prices = { control: 100, discount_10: 90, discount_20: 80 };
  res.json({ userId: req.userId, variant: tier, price: prices[tier] });
});

app.get('/search', (req, res) => {
  if (req.flags.beta_search) return res.json({ version: 'beta', results: [] });
  res.json({ version: 'classic', results: [] });
});

app.listen(3000, () => console.log('Feature flags demo :3000 — X-User-Id header for targeting'));
module.exports = app;
