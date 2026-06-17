// Validation Demo — Schema-based validation (no external deps).
const express = require('express');
const app = express();
app.use(express.json());

// === Mini schema validator ===
function validate(schema) {
  return (req, res, next) => {
    const errors = [];
    for (const [field, rules] of Object.entries(schema)) {
      const value = req.body[field];
      if (rules.required && (value === undefined || value === null || value === '')) {
        errors.push({ field, code: 'required', message: `${field} is required` });
        continue;
      }
      if (value === undefined || value === null) continue;
      if (rules.type && typeof value !== rules.type) errors.push({ field, code: 'wrong_type', expected: rules.type, got: typeof value });
      if (rules.minLength && value.length < rules.minLength) errors.push({ field, code: 'too_short', min: rules.minLength });
      if (rules.maxLength && value.length > rules.maxLength) errors.push({ field, code: 'too_long', max: rules.maxLength });
      if (rules.min !== undefined && value < rules.min) errors.push({ field, code: 'too_small', min: rules.min });
      if (rules.max !== undefined && value > rules.max) errors.push({ field, code: 'too_big', max: rules.max });
      if (rules.pattern && !rules.pattern.test(value)) errors.push({ field, code: 'pattern_mismatch' });
      if (rules.enum && !rules.enum.includes(value)) errors.push({ field, code: 'not_in_enum', allowed: rules.enum });
      if (rules.custom) {
        const err = rules.custom(value, req.body);
        if (err) errors.push({ field, code: 'custom', message: err });
      }
    }
    if (errors.length) return res.status(422).json({ error: 'validation_failed', errors });
    next();
  };
}

// === Schemas ===
const userSchema = {
  email: { required: true, type: 'string', pattern: /^[^@]+@[^@]+\.[^@]+$/, maxLength: 255 },
  password: { required: true, type: 'string', minLength: 8, maxLength: 128 },
  age: { type: 'number', min: 13, max: 120, custom: v => v >= 18 ? null : 'must be 18 or older' },
  role: { type: 'string', enum: ['user', 'admin', 'moderator'] },
};

const productSchema = {
  name: { required: true, type: 'string', minLength: 1, maxLength: 200 },
  price_cents: { required: true, type: 'number', min: 0, max: 100000000 },
  category: { required: true, type: 'string', enum: ['electronics', 'books', 'clothing', 'food'] },
  description: { type: 'string', maxLength: 5000 },
};

// === Routes ===
app.post('/users', validate(userSchema), (req, res) => res.status(201).json({ id: 'u_' + Math.random().toString(36).slice(2, 8), ...req.body }));
app.post('/products', validate(productSchema), (req, res) => res.status(201).json({ id: 'p_' + Math.random().toString(36).slice(2, 8), ...req.body }));

// === Inspect (so you can see what the validator does) ===
app.post('/validate-test', validate({ x: { required: true, type: 'string' }, y: { type: 'number', min: 0 } }), (req, res) => res.json({ ok: true, body: req.body }));

app.listen(3000, () => console.log('Validation demo :3000'));
module.exports = app;
