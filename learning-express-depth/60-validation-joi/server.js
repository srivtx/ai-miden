// 60 — Validation with Joi
// NEW CONCEPT: use a real validation library.
// We wrote a simple validator in project 5. Joi is more powerful.
const express = require('express');
const Joi = require('joi');
const app = express();
app.use(express.json());

// Define schemas
const userSchema = Joi.object({
  name: Joi.string().min(2).max(50).required(),
  email: Joi.string().email().required(),
  age: Joi.number().integer().min(13).max(120),
  role: Joi.string().valid('user', 'admin', 'moderator').default('user'),
});

const productSchema = Joi.object({
  name: Joi.string().min(1).max(200).required(),
  price: Joi.number().positive().precision(2).required(),
  category: Joi.string().valid('electronics', 'books', 'clothing').required(),
  tags: Joi.array().items(Joi.string()).max(5),
});

// Validation middleware
function validate(schema) {
  return (req, res, next) => {
    const { error, value } = schema.validate(req.body, { abortEarly: false });
    if (error) {
      const errors = error.details.map(d => ({
        field: d.path.join('.'),
        message: d.message,
      }));
      return res.status(422).json({ error: 'validation_failed', errors });
    }
    req.body = value;  // Use the cleaned/coerced values
    next();
  };
}

// Routes
app.post('/users', validate(userSchema), (req, res) => {
  res.status(201).json(req.body);
});

app.post('/products', validate(productSchema), (req, res) => {
  res.status(201).json(req.body);
});

app.listen(3000, () => console.log('Joi validation on http://localhost:3000'));
