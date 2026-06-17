// 15_mongodb_crud.js — Mongoose: schema, validation, query, populate, indexes.
const express = require('express');
const mongoose = require('mongoose');
const app = express();
app.use(express.json());

mongoose.connect('mongodb://localhost:27017/express_demo');

// Schema + Model
const userSchema = new mongoose.Schema({
  name: { type: String, required: true, minlength: 2, index: true },
  email: { type: String, required: true, unique: true, lowercase: true, match: /.+@.+\..+/ },
  age: { type: Number, min: 0, max: 150, default: null },
  tags: [String],
  active: { type: Boolean, default: true },
}, { timestamps: true });

userSchema.methods.toPublic = function () { return { id: this._id, name: this.name, email: this.email, age: this.age, tags: this.tags }; };

const User = mongoose.model('User', userSchema);

// Post schema with reference (populate)
const postSchema = new mongoose.Schema({
  title: String,
  body: String,
  author: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
}, { timestamps: true });
const Post = mongoose.model('Post', postSchema);

// CRUD
app.post('/users', async (req, res, next) => {
  try { res.status(201).json((await User.create(req.body)).toPublic()); }
  catch (e) { e.name === 'ValidationError' ? res.status(400).json({ errors: Object.values(e.errors).map(er => er.message) }) : next(e); }
});

app.get('/users', async (req, res) => {
  const { page = 1, limit = 10, search } = req.query;
  const query = search ? { $or: [{ name: new RegExp(search, 'i') }, { email: new RegExp(search, 'i') }] } : {};
  const [users, total] = await Promise.all([
    User.find(query).sort('-createdAt').skip((page - 1) * limit).limit(parseInt(limit)),
    User.countDocuments(query),
  ]);
  res.json({ total, page: parseInt(page), data: users.map(u => u.toPublic()) });
});

app.get('/users/:id', async (req, res) => {
  const user = await User.findById(req.params.id);
  user ? res.json(user.toPublic()) : res.status(404).json({ error: 'Not found' });
});

app.patch('/users/:id', async (req, res) => {
  const user = await User.findByIdAndUpdate(req.params.id, req.body, { new: true, runValidators: true });
  user ? res.json(user.toPublic()) : res.status(404).json({ error: 'Not found' });
});

app.delete('/users/:id', async (req, res) => {
  await User.findByIdAndDelete(req.params.id);
  res.status(204).send();
});

// Posts with populate (JOIN)
app.post('/users/:id/posts', async (req, res) => {
  const post = await Post.create({ ...req.body, author: req.params.id });
  res.status(201).json(await post.populate('author', 'name email'));
});

app.get('/users/:id/posts', async (req, res) => {
  res.json(await Post.find({ author: req.params.id }).populate('author', 'name email'));
});

app.listen(3000, () => console.log('MongoDB :3000'));
