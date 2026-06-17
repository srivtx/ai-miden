// Recipe App — Create recipes, ingredients, steps, search, rate, save.
const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const app = express();
app.use(express.json());
const SECRET = 'dev-secret';

const users = []; const recipes = []; const savedRecipes = []; const ratings = []; let rId = 1, svId = 1, ratId = 1;
function auth(req, res, next) { try { req.user = jwt.verify((req.headers.authorization || '').split(' ')[1], SECRET); next(); } catch { res.status(401).json({ error: 'Auth required' }); } }

app.post('/auth/register', async (req, res) => {
  const { name, email, password } = req.body;
  if (!email || !password) return res.status(400).json({ error: 'email, password required' });
  if (users.find(u => u.email === email)) return res.status(409).json({ error: 'Email exists' });
  users.push({ id: users.length + 1, name, email, password: await bcrypt.hash(password, 10) });
  res.status(201).json({ token: jwt.sign({ id: users.length }, SECRET, { expiresIn: '24h' }) });
});
app.post('/auth/login', async (req, res) => {
  const user = users.find(u => u.email === req.body.email);
  if (!user || !(await bcrypt.compare(req.body.password, user.password))) return res.status(401).json({ error: 'Invalid' });
  res.json({ token: jwt.sign({ id: user.id }, SECRET, { expiresIn: '24h' }) });
});

app.post('/recipes', auth, (req, res) => {
  const { title, description, ingredients, steps, prepTime, cookTime, servings, difficulty, cuisine, tags, image } = req.body;
  if (!title) return res.status(400).json({ error: 'title required' });
  if (!Array.isArray(ingredients) || !ingredients.length) return res.status(400).json({ error: 'ingredients[] required' });
  if (!Array.isArray(steps) || !steps.length) return res.status(400).json({ error: 'steps[] required' });
  const r = { id: rId++, authorId: req.user.id, title, description: description || '', ingredients, steps, prepTime: prepTime || 0, cookTime: cookTime || 0, totalTime: (prepTime || 0) + (cookTime || 0), servings: servings || 1, difficulty: difficulty || 'medium', cuisine: cuisine || 'other', tags: tags || [], image: image || null, avgRating: 0, ratingCount: 0, viewCount: 0, saveCount: 0, createdAt: new Date().toISOString() };
  recipes.push(r);
  res.status(201).json(r);
});

app.get('/recipes', (req, res) => {
  let result = [...recipes];
  if (req.query.search) { const q = req.query.search.toLowerCase(); result = result.filter(r => r.title.toLowerCase().includes(q) || r.description.toLowerCase().includes(q) || r.cuisine.toLowerCase().includes(q) || r.ingredients.some(i => i.toLowerCase().includes(q))); }
  if (req.query.cuisine) result = result.filter(r => r.cuisine === req.query.cuisine);
  if (req.query.difficulty) result = result.filter(r => r.difficulty === req.query.difficulty);
  if (req.query.maxTime) result = result.filter(r => r.totalTime <= parseInt(req.query.maxTime));
  if (req.query.tag) result = result.filter(r => r.tags.includes(req.query.tag));
  if (req.query.ingredient) result = result.filter(r => r.ingredients.some(i => i.toLowerCase().includes(req.query.ingredient.toLowerCase())));
  // Sort
  if (req.query.sort === 'rating') result.sort((a, b) => b.avgRating - a.avgRating);
  else if (req.query.sort === 'time') result.sort((a, b) => a.totalTime - b.totalTime);
  else if (req.query.sort === 'popular') result.sort((a, b) => b.saveCount - a.saveCount);
  else result.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
  const page = Math.max(1, parseInt(req.query.page) || 1); const limit = parseInt(req.query.limit) || 12;
  const total = result.length;
  res.json({ total, page, data: result.slice((page - 1) * limit, page * limit) });
});

app.get('/recipes/:id', (req, res) => {
  const r = recipes.find(r => r.id === parseInt(req.params.id));
  if (!r) return res.status(404).json({ error: 'Not found' });
  r.viewCount++;
  res.json(r);
});

app.post('/recipes/:id/rate', auth, (req, res) => {
  const r = recipes.find(r => r.id === parseInt(req.params.id));
  if (!r) return res.status(404).json({ error: 'Not found' });
  const { rating, review } = req.body;
  if (!rating || rating < 1 || rating > 5) return res.status(400).json({ error: 'Rating 1-5 required' });
  const existing = ratings.find(r => r.userId === req.user.id && r.recipeId === parseInt(req.params.id));
  if (existing) { existing.rating = rating; existing.review = review || ''; }
  else { ratings.push({ id: ratId++, recipeId: r.id, userId: req.user.id, rating, review: review || '', createdAt: new Date().toISOString() }); }
  const recipeRatings = ratings.filter(r => r.recipeId === parseInt(req.params.id));
  r.avgRating = (recipeRatings.reduce((s, r) => s + r.rating, 0) / recipeRatings.length).toFixed(2);
  r.ratingCount = recipeRatings.length;
  res.json({ yourRating: rating, avgRating: r.avgRating });
});

app.post('/recipes/:id/save', auth, (req, res) => {
  const r = recipes.find(r => r.id === parseInt(req.params.id));
  if (!r) return res.status(404).json({ error: 'Not found' });
  if (savedRecipes.find(s => s.userId === req.user.id && s.recipeId === r.id)) return res.status(409).json({ error: 'Already saved' });
  savedRecipes.push({ userId: req.user.id, recipeId: r.id, savedAt: new Date().toISOString() });
  r.saveCount++;
  res.json({ saved: true });
});

app.get('/my-saved', auth, (req, res) => res.json(savedRecipes.filter(s => s.userId === req.user.id).map(s => ({ ...s, recipe: recipes.find(r => r.id === s.recipeId) }))));

app.listen(3000, () => console.log('Recipe App :3000'));
module.exports = app;
