# What is the Input Gate?

## 1. Why it exists (THE PROBLEM first)

New information arrives at every time step in the form of the current input $x_t$. If we blindly added all of it to the cell state, the long-term memory would quickly become noisy, overloaded, and filled with irrelevant details. The input gate solves this by filtering which parts of the *new candidate information* are actually worth storing in the cell state.

## 2. Definition (very simple)

The input gate is a sigmoid-activated layer that produces a vector of values between 0 and 1. Each value decides how much of the corresponding element in the *candidate cell state* $\tilde{c}_t$ should be added to the long-term memory.

**Formula:**

$$
i_t = \sigma(W_i \cdot [h_{t-1}, x_t] + b_i)
$$

Where:
- $W_i$ = weight matrix for the input gate
- $[h_{t-1}, x_t]$ = concatenation of previous hidden state and current input
- $b_i$ = bias vector
- $\sigma$ = sigmoid function

The candidate cell state (created by a separate tanh layer) is:

$$
\tilde{c}_t = \tanh(W_c \cdot [h_{t-1}, x_t] + b_c)
$$

And the actual update to the cell state is:

$$
c_t = f_t \odot c_{t-1} + i_t \odot \tilde{c}_t
$$

## 3. Real-life analogy

**Taking notes in class.**

The professor is talking for an hour straight. You don't write down every single word. Instead, you decide in real time: "This definition is important — write it down" (input gate ≈ 0.9). "That anecdote about the professor's cat is trivial — ignore it" (input gate ≈ 0.1). The input gate is your personal relevance filter.

## 4. Tiny numeric example

Suppose the candidate cell state (new information ready to be stored) is:

$$
\tilde{c}_t = [4.0, \; -2.0]
$$

After computing the input gate with made-up weights and inputs, we get:

$$
i_t = [0.8, \; 0.1]
$$

This means:
- **First element (0.8):** Add 80% of the new candidate value to the first element of the cell state.
- **Second element (0.1):** Add only 10% of the new candidate value to the second element — effectively ignoring it.

The contribution to the cell state from new information is:

$$
i_t \odot \tilde{c}_t = [0.8 \times 4.0, \; 0.1 \times -2.0] = [3.2, \; -0.2]
$$

## 5. Common confusion

1. **"The input gate creates the new candidate values"** — No, the input gate only decides *how much* of the candidate values to let through. The candidate values $\tilde{c}_t$ are created by a separate tanh layer.

2. **"Input gate = 1 means block everything"** — Opposite. An input gate value of 1 means "let all of this candidate through." A value of 0 means "block this candidate completely."

3. **"The input gate and forget gate do the same thing"** — They are related but distinct. The forget gate filters *old* memory; the input gate filters *new* memory. Both are needed for a clean update.

4. **"Input gate values can be negative"** — No, because it uses sigmoid activation, all output values are in the range [0, 1].

5. **"The input gate only looks at the current input $x_t$"** — It actually looks at the concatenation of the previous hidden state $h_{t-1}$ and the current input $x_t$, so it can make context-aware decisions.

## 6. Where it is used in our code

In our LSTM implementation, the input gate appears alongside the candidate cell state computation:

```python
i_t = torch.sigmoid(self.W_i(torch.cat([h_prev, x_t], dim=1)) + self.b_i)
c_tilde = torch.tanh(self.W_c(torch.cat([h_prev, x_t], dim=1)) + self.b_c)
```

These two vectors are then combined via element-wise multiplication and added to the forgotten cell state to produce the updated long-term memory.
