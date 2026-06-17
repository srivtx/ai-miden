// Newsletter subscription API
const express = require('express');
const app = express();
app.use(express.json());

const newsletters = []; const subscribers = []; const campaigns = []; let cId = 1, sId = 1, campId = 1;

// Manage newsletters
app.post('/newsletters', (req, res) => {
  const { name, description, ownerEmail } = req.body;
  if (!name || !ownerEmail) return res.status(400).json({ error: 'name and ownerEmail required' });
  newsletters.push({ id: cId++, name, description: description || '', ownerEmail, subscriberCount: 0, createdAt: new Date().toISOString() });
  res.status(201).json(newsletters[ newsletters.length - 1]);
});

app.get('/newsletters', (req, res) => res.json(newsletters));

// Public subscribe
app.post('/newsletters/:id/subscribe', (req, res) => {
  const nl = newsletters.find(n => n.id === parseInt(req.params.id));
  if (!nl) return res.status(404).json({ error: 'Newsletter not found' });
  const { email, name, preferences } = req.body;
  if (!email || !email.includes('@')) return res.status(400).json({ error: 'Valid email required' });
  if (subscribers.find(s => s.newsletterId === nl.id && s.email === email)) return res.status(409).json({ error: 'Already subscribed' });
  // Confirmation token pattern (in real app: send email with link)
  const sub = { id: sId++, newsletterId: nl.id, email, name: name || null, preferences: preferences || { weekly: true, monthly: false }, status: 'pending', subscribedAt: new Date().toISOString(), confirmToken: 'tok_' + Date.now() };
  subscribers.push(sub);
  nl.subscriberCount++;
  res.status(201).json({ ...sub, confirmUrl: `/newsletters/${nl.id}/confirm/${sub.confirmToken}` });
});

app.get('/newsletters/:id/confirm/:token', (req, res) => {
  const sub = subscribers.find(s => s.newsletterId === parseInt(req.params.id) && s.confirmToken === req.params.token);
  if (!sub) return res.status(404).json({ error: 'Invalid token' });
  sub.status = 'confirmed'; sub.confirmedAt = new Date().toISOString();
  res.json({ confirmed: true, email: sub.email });
});

app.post('/newsletters/:id/unsubscribe', (req, res) => {
  const sub = subscribers.find(s => s.newsletterId === parseInt(req.params.id) && s.email === req.body.email);
  if (!sub) return res.status(404).json({ error: 'Not found' });
  sub.status = 'unsubscribed';
  res.json({ unsubscribed: true });
});

// Campaigns (sends)
app.post('/campaigns', (req, res) => {
  const { newsletterId, subject, body, scheduledFor } = req.body;
  const nl = newsletters.find(n => n.id === parseInt(newsletterId));
  if (!nl) return res.status(404).json({ error: 'Newsletter not found' });
  const camp = { id: campId++, newsletterId: nl.id, subject, body, status: scheduledFor ? 'scheduled' : 'draft', scheduledFor: scheduledFor || null, sent: 0, opened: 0, createdAt: new Date().toISOString() };
  campaigns.push(camp);
  res.status(201).json(camp);
});

app.post('/campaigns/:id/send', (req, res) => {
  const camp = campaigns.find(c => c.id === parseInt(req.params.id));
  if (!camp) return res.status(404).json({ error: 'Not found' });
  const confirmed = subscribers.filter(s => s.newsletterId === camp.newsletterId && s.status === 'confirmed');
  // In real app: queue email job for each subscriber
  camp.status = 'sent'; camp.sent = confirmed.length; camp.sentAt = new Date().toISOString();
  res.json({ sent: camp.sent, campaign: camp });
});

app.get('/newsletters/:id/stats', (req, res) => {
  const nlSubs = subscribers.filter(s => s.newsletterId === parseInt(req.params.id));
  const nlCamps = campaigns.filter(c => c.newsletterId === parseInt(req.params.id));
  res.json({
    subscribers: { total: nlSubs.length, confirmed: nlSubs.filter(s => s.status === 'confirmed').length, pending: nlSubs.filter(s => s.status === 'pending').length, unsubscribed: nlSubs.filter(s => s.status === 'unsubscribed').length },
    campaigns: nlCamps.length, totalSent: nlCamps.reduce((s, c) => s + c.sent, 0),
  });
});

app.listen(3000, () => console.log('Newsletter :3000'));
module.exports = app;
