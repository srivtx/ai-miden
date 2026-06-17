// Stripe Payments — One-time checkout + subscriptions + webhook handling.
const express = require('express');
const app = express();

// In production: npm install stripe, use process.env.STRIPE_SECRET_KEY
// const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
const stripe = { // Mock for demo (replace with real Stripe SDK)
  paymentIntents: { create: async (params) => ({ id: 'pi_' + Date.now(), ...params, status: 'succeeded', client_secret: 'cs_' + Date.now() }) },
  customers: { create: async (params) => ({ id: 'cus_' + Date.now(), ...params }) },
  subscriptions: { create: async (params) => ({ id: 'sub_' + Date.now(), ...params, status: 'active' }) },
  webhooks: { constructEvent: (body, sig, secret) => JSON.parse(body) },
};
const WEBHOOK_SECRET = 'whsec_test';

const customers = {}; // userId -> stripeCustomerId
const orders = [];

app.use(express.json());

// ---- ONE-TIME PAYMENT ----
app.post('/create-payment', async (req, res) => {
  const { amount, currency, userId } = req.body; // amount in smallest unit (cents)
  if (!amount || amount <= 0) return res.status(400).json({ error: 'Valid amount required' });
  try {
    const paymentIntent = await stripe.paymentIntents.create({ amount, currency: currency || 'usd', metadata: { userId } });
    res.json({ clientSecret: paymentIntent.client_secret, paymentId: paymentIntent.id });
    // In real app: client uses clientSecret with Stripe.js to confirm payment in browser
  } catch (e) { res.status(500).json({ error: e.message }); }
});

// ---- CREATE CUSTOMER (for subscriptions) ----
app.post('/customers', async (req, res) => {
  const { userId, email, name } = req.body;
  try {
    const customer = await stripe.customers.create({ email, name, metadata: { userId } });
    customers[userId] = customer.id;
    res.json({ customerId: customer.id });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

// ---- CREATE SUBSCRIPTION ----
app.post('/subscriptions', async (req, res) => {
  const { userId, priceId } = req.body;
  const customerId = customers[userId];
  if (!customerId) return res.status(400).json({ error: 'Create customer first' });
  try {
    const subscription = await stripe.subscriptions.create({ customer: customerId, items: [{ price: priceId }] });
    res.json({ subscriptionId: subscription.id, status: subscription.status });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

// ---- WEBHOOK (STRIPE → YOUR SERVER) ----
app.post('/webhooks/stripe', express.raw({ type: 'application/json' }), (req, res) => {
  const sig = req.headers['stripe-signature'];
  let event;
  try {
    event = stripe.webhooks.constructEvent(req.body, sig, WEBHOOK_SECRET);
  } catch (err) { return res.status(400).send(`Webhook Error: ${err.message}`); }

  switch (event.type) {
    case 'payment_intent.succeeded': {
      const pi = event.data.object;
      console.log(`Payment succeeded: $${pi.amount / 100} from ${pi.metadata.userId}`);
      orders.push({ paymentId: pi.id, userId: pi.metadata.userId, amount: pi.amount, status: 'paid', time: new Date().toISOString() });
      // FULFILL ORDER: grant access, send email, update DB
      break;
    }
    case 'payment_intent.payment_failed':
      console.log('Payment failed:', event.data.object.id);
      break;
    case 'customer.subscription.deleted':
      console.log('Subscription canceled:', event.data.object.customer);
      break;
  }
  res.json({ received: true });
});

app.get('/orders', (req, res) => res.json(orders));

app.listen(3000, () => console.log('Stripe demo :3000'));
module.exports = app;
