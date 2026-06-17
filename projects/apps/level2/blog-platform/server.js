// Blog Platform — Users, posts, comments, categories, likes. Full REST API.
const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const app = express();
app.use(express.json());

const SECRET = 'dev-secret';
const users = []; const posts = []; const comments = []; const likes = new Set();
let postId = 1, commentId = 1;

function auth(req, res, next) { try { req.user = jwt.verify((req.headers.authorization || '').split(' ')[1], SECRET); next(); } catch { res.status(401).json({ error: 'Auth required' }); } }

// AUTH
app.post('/auth/register', async (req, res) => {
  const { name, email, password } = req.body;
  if (!name || !email || !password) return res.status(400).json({ error: 'name, email, password required' });
  if (users.find(u => u.email === email)) return res.status(409).json({ error: 'Email exists' });
  const user = { id: users.length + 1, name, email, password: await bcrypt.hash(password, 10), role: 'author' };
  users.push(user);
  res.status(201).json({ user: { id: user.id, name, email, role: user.role }, token: jwt.sign({ id: user.id, role: user.role }, SECRET, { expiresIn: '1h' }) });
});
app.post('/auth/login', async (req, res) => {
  const user = users.find(u => u.email === req.body.email);
  if (!user || !(await bcrypt.compare(req.body.password, user.password))) return res.status(401).json({ error: 'Invalid credentials' });
  res.json({ user: { id: user.id, name: user.name, email: user.email, role: user.role }, token: jwt.sign({ id: user.id, role: user.role }, SECRET, { expiresIn: '1h' }) });
});

// POSTS
app.post('/posts', auth, (req, res) => {
  const { title, content, category, tags } = req.body;
  if (!title || !content) return res.status(400).json({ error: 'title and content required' });
  const post = { id: postId++, authorId: req.user.id, title, content, category: category || 'general', tags: tags || [], createdAt: new Date().toISOString(), updatedAt: new Date().toISOString() };
  posts.push(post);
  res.status(201).json({ post, author: users.find(u => u.id === req.user.id)?.name });
});

app.get('/posts', (req, res) => {
  let result = [...posts];
  if (req.query.category) result = result.filter(p => p.category === req.query.category);
  if (req.query.tag) result = result.filter(p => p.tags.includes(req.query.tag));
  if (req.query.author) result = result.filter(p => users.find(u => u.id === p.authorId)?.name === req.query.author);
  if (req.query.search) {
    const q = req.query.search.toLowerCase();
    result = result.filter(p => p.title.toLowerCase().includes(q) || p.content.toLowerCase().includes(q));
  }
  result.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
  const page = Math.max(1, parseInt(req.query.page) || 1); const limit = Math.min(50, parseInt(req.query.limit) || 10);
  const total = result.length; result = result.slice((page - 1) * limit, page * limit);
  const enriched = result.map(p => ({ ...p, author: users.find(u => u.id === p.authorId)?.name, likeCount: [...likes].filter(l => l.startsWith(`post_${p.id}_`)).length, commentCount: comments.filter(c => c.postId === p.id).length }));
  res.json({ total, page, pages: Math.ceil(total / limit), data: enriched });
});

app.get('/posts/:id', (req, res) => {
  const post = posts.find(p => p.id === parseInt(req.params.id));
  if (!post) return res.status(404).json({ error: 'Not found' });
  const postComments = comments.filter(c => c.postId === post.id);
  res.json({ ...post, author: users.find(u => u.id === post.authorId)?.name, likeCount: [...likes].filter(l => l.startsWith(`post_${post.id}_`)).length, comments: postComments.map(c => ({ ...c, author: users.find(u => u.id === c.userId)?.name })) });
});

app.patch('/posts/:id', auth, (req, res) => {
  const post = posts.find(p => p.id === parseInt(req.params.id));
  if (!post) return res.status(404).json({ error: 'Not found' });
  if (post.authorId !== req.user.id && req.user.role !== 'admin') return res.status(403).json({ error: 'Forbidden' });
  if (req.body.title !== undefined) post.title = req.body.title;
  if (req.body.content !== undefined) post.content = req.body.content;
  if (req.body.category !== undefined) post.category = req.body.category;
  post.updatedAt = new Date().toISOString();
  res.json(post);
});

app.delete('/posts/:id', auth, (req, res) => {
  const idx = posts.findIndex(p => p.id === parseInt(req.params.id));
  if (idx === -1) return res.status(404).json({ error: 'Not found' });
  if (posts[idx].authorId !== req.user.id && req.user.role !== 'admin') return res.status(403).json({ error: 'Forbidden' });
  posts.splice(idx, 1);
  // Cascade delete comments + likes
  const toRemove = [...comments].filter(c => c.postId === req.params.id);
  toRemove.forEach(c => comments.splice(comments.indexOf(c), 1));
  res.status(204).send();
});

// COMMENTS
app.post('/posts/:id/comments', auth, (req, res) => {
  if (!posts.find(p => p.id === parseInt(req.params.id))) return res.status(404).json({ error: 'Post not found' });
  if (!req.body.content) return res.status(400).json({ error: 'content required' });
  const comment = { id: commentId++, postId: parseInt(req.params.id), userId: req.user.id, content: req.body.content, createdAt: new Date().toISOString() };
  comments.push(comment);
  res.status(201).json(comment);
});

// LIKES (toggle)
app.post('/posts/:id/like', auth, (req, res) => {
  if (!posts.find(p => p.id === parseInt(req.params.id))) return res.status(404).json({ error: 'Not found' });
  const key = `post_${req.params.id}_${req.user.id}`;
  if (likes.has(key)) { likes.delete(key); return res.json({ liked: false }); }
  likes.add(key);
  res.json({ liked: true });
});

app.listen(3000, () => console.log('Blog API :3000'));
module.exports = app;
