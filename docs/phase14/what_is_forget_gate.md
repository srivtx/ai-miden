# What is the Forget Gate?

## 1. Why it exists (THE PROBLEM first)

The cell state is LSTM's long-term memory. At every time step, new information gets added to it. If we never remove anything, the cell state becomes a cluttered warehouse full of outdated, irrelevant, and conflicting information. The network would drown in its own history and lose the ability to focus on what actually matters for the current prediction. The forget gate solves this by deciding which pieces of the old memory should be discarded.

## 2. Definition (very simple)

The forget gate is a sigmoid-activated layer that produces a vector of values between 0 and 1. Each value acts as a "keep" or "discard" mask for the corresponding element in the previous cell state.

**Formula:**

$$
f_t = \sigma(W_f \cdot [h_{t-1}, x_t] + b_f)
$$

Where:
- $W_f$ = weight matrix for the forget gate
- $[h_{t-1}, x_t]$ = concatenation of previous hidden state and current input
- $b_f$ = bias vector
- $\sigma$ = sigmoid function

## 3. Real-life analogy

**Cleaning out your closet.**

You open your closet and look at every item. That jacket you haven't worn in 2 years? Throw it away (forget = 0.0). Your favorite pair of jeans you wear every week? Keep them (forget = 0.9). The forget gate is that ruthless but necessary voice that says, "This is irrelevant now — let it go."

## 4. Tiny numeric example

Suppose we have a 2-dimensional cell state. The previous cell state is:

$$
c_{t-1} = [5.0, \; 3.0]
$$

After computing the forget gate with made-up weights and inputs, we get:

$$
f_t = [0.0, \; 0.9]
$$

This means:
- **First element (0.0):** Completely forget the first memory element. It gets multiplied by 0 and vanishes.
- **Second element (0.9):** Keep 90% of the second memory element. It survives mostly intact.

The updated cell state after forgetting becomes:

$$
c_t^{\text{(after forget)}} = f_t \odot c_{t-1} = [0.0 \times 5.0, \; 0.9 \times 3.0] = [0.0, \; 2.7]
$$

## 5. Common confusion

1. **"Forget = 1 means forget everything"** — Actually, the opposite is true. A value of 1 means "keep everything" because we multiply the cell state by this number. A value of 0 means "forget everything."

2. **"The forget gate deletes information permanently from the model"** — No, it only zeros out elements for the current time step's cell state. The weights that produced the gate are still learnable, and on the next step the gate can open again.

3. **"A high forget value is always bad"** — Not at all. If the information is still relevant (like a subject pronoun in a long sentence), a high forget value is exactly what you want.

4. **"The forget gate decides what new information to add"** — No, that's the input gate's job. The forget gate only decides what *old* information to remove.

5. **"All LSTM variants use the same forget gate"** — Most do, but some variants (like Gated Recurrent Units) merge the forget and input decisions into a single "update gate."

## 6. Where it is used in our code

In our LSTM implementation, the forget gate appears as a linear layer followed by a sigmoid activation:

```python
f_t = torch.sigmoid(self.W_f(torch.cat([h_prev, x_t], dim=1)) + self.b_f)
```

It is computed at every forward step and applied to the previous cell state via element-wise multiplication before new candidate values are added.
