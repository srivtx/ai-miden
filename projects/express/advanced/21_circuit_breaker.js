// 21_circuit_breaker.js — Prevent cascading failures. Trip when downstream fails.

const states = { CLOSED: 'closed', OPEN: 'open', HALF_OPEN: 'half_open' };

class CircuitBreaker {
  constructor(fn, { failureThreshold = 3, resetTimeout = 10000 } = {}) {
    this.fn = fn;
    this.failureThreshold = failureThreshold;
    this.resetTimeout = resetTimeout;
    this.state = states.CLOSED;
    this.failures = 0;
    this.lastFailure = 0;
  }

  async call(...args) {
    if (this.state === states.OPEN) {
      if (Date.now() - this.lastFailure > this.resetTimeout) {
        this.state = states.HALF_OPEN;
      } else {
        throw new Error('Circuit is OPEN — service unavailable');
      }
    }

    try {
      const result = await this.fn(...args);
      if (this.state === states.HALF_OPEN) { this.state = states.CLOSED; this.failures = 0; }
      return result;
    } catch (err) {
      this.failures++;
      this.lastFailure = Date.now();
      if (this.failures >= this.failureThreshold) this.state = states.OPEN;
      throw err;
    }
  }

  get status() { return { state: this.state, failures: this.failures }; }
}

// ---- Demo ----
const express = require('express');
const app = express();

// Simulated unreliable service (fails 60% of the time)
async function fetchUser(id) {
  if (Math.random() < 0.6) throw new Error(`Failed to fetch user ${id}`);
  return { id, name: 'Zen', email: 'zen@test.com' };
}

const cb = new CircuitBreaker(fetchUser, { failureThreshold: 3, resetTimeout: 8000 });

app.get('/user/:id', async (req, res, next) => {
  try {
    const user = await cb.call(req.params.id);
    res.json({ user, breaker: cb.status });
  } catch (err) {
    res.status(503).json({ error: err.message, breaker: cb.status });
  }
});

app.get('/breaker/status', (req, res) => res.json(cb.status));

app.listen(3000, () => console.log('Circuit breaker :3000'));
