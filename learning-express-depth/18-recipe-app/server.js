// 18 — Recipe App
// A recipe has: name, ingredients (list), steps (list), cookTime.
// NEW: nested data — ingredients and steps are arrays inside the recipe.
const express = require('express');
const app = express();
app.use(express.json());

const recipes = [];

app.get('/recipes', (req, res) => {
  res.json({ count: recipes.length, recipes });
});

app.post('/recipes', (req, res) => {
  const { name, ingredients, steps, cookTime } = req.body;
  const recipe = {
    id: recipes.length + 1,
    name,
    ingredients: ingredients || [],
    steps: steps || [],
    cookTime: cookTime || 0,
  };
  recipes.push(recipe);
  res.status(201).json(recipe);
});

app.get('/recipes/:id', (req, res) => {
  const recipe = recipes.find(r => r.id === parseInt(req.params.id));
  if (!recipe) return res.status(404).json({ error: 'Recipe not found' });
  res.json(recipe);
});

app.delete('/recipes/:id', (req, res) => {
  const index = recipes.findIndex(r => r.id === parseInt(req.params.id));
  if (index === -1) return res.status(404).json({ error: 'Recipe not found' });
  recipes.splice(index, 1);
  res.status(204).end();
});

app.listen(3000, () => console.log('Recipe server on http://localhost:3000'));
