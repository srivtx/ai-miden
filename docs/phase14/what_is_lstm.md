# What is an LSTM?

Welcome! You already know about RNNs and BPTT. You know that RNNs are great for sequences, but they struggle with long-term memory. Now let's meet the LSTM — the RNN's smarter cousin.

---

### 1. Why it exists (THE PROBLEM first)

RNNs have a fatal flaw: they forget the distant past.

Example: "The cat, which was hungry and had not eaten all day because the owner forgot to feed it in the morning, sat on the mat."

To understand "sat," we need to remember "cat" from the beginning. But an RNN's hidden state gets rewritten at every word. By the time we reach "sat," the information about "cat" has been drowned out by "hungry," "eaten," "day," "owner," "forgot," "feed," "morning."

This is the vanishing gradient problem in disguise. Gradients from the distant past are multiplied by small numbers at every step, so they become essentially zero.

We need a mechanism that can:
1. REMEMBER important information for a long time
2. FORGET irrelevant information
3. Only UPDATE memory when necessary

---

### 2. Definition (very simple)

LSTM stands for Long Short-Term Memory. It is a type of RNN that uses a special "cell state" (a protected conveyor belt) and three gates to control information flow.

The cell state runs straight through the entire chain with only minor interactions. It is like a highway where information can travel long distances unchanged.

The three gates are:
- **Forget Gate**: Decides what information to throw away from the cell state
- **Input Gate**: Decides what new information to store in the cell state
- **Output Gate**: Decides what to output based on the cell state

---

### 3. Real-life analogy

**The Airport Baggage Carousel**

Imagine an airport baggage carousel (the cell state). Luggage (information) goes around and around.

**Forget Gate (security checkpoint):**
- Before luggage enters the carousel, security checks each bag.
- Dangerous items (irrelevant information) are removed.
- "That bag has a bomb? Remove it." = forget

**Input Gate (new arrivals):**
- New luggage arrives from incoming flights.
- Security decides which bags are allowed onto the carousel.
- "This bag belongs to a passenger? Add it." = remember

**Output Gate (baggage claim):**
- Passengers stand at the claim area.
- They only take THEIR bag, not every bag.
- "That black bag is mine. I'll take it." = output

The carousel keeps running. Some bags stay on for hours (long-term memory). Some are removed immediately (forgotten). New bags are added. Passengers take what they need.

**Another analogy: A librarian's desk.**
- The desk has a main drawer (cell state) that holds important documents.
- Every morning, the librarian removes old documents (forget gate).
- Every afternoon, the librarian adds new documents (input gate).
- When someone asks a question, the librarian only pulls out relevant documents (output gate).
- Important documents stay in the drawer for years. Unimportant ones are thrown away quickly.

---

### 4. Tiny numeric example

Show a simplified LSTM cell:

At time t:
- Input x_t = [1, 0] (encoding of current word)
- Previous cell state C_{t-1} = [2, 3]
- Previous hidden state h_{t-1} = [0.5, 0.5]

**Forget gate:**
f_t = sigmoid(W_f @ [h_{t-1}, x_t] + b_f)
Let's say f_t = [0.1, 0.9]
- This means: forget 90% of the first cell element, keep 90% of the second.

**Input gate:**
i_t = sigmoid(W_i @ [h_{t-1}, x_t] + b_i)
Let's say i_t = [0.8, 0.2]
- This means: add new info to the first cell element, ignore new info for the second.

**Candidate values:**
C_tilde = tanh(W_C @ [h_{t-1}, x_t] + b_C)
Let's say C_tilde = [1, 0.5]

**New cell state:**
C_t = f_t * C_{t-1} + i_t * C_tilde
C_t = [0.1, 0.9] * [2, 3] + [0.8, 0.2] * [1, 0.5]
C_t = [0.2, 2.7] + [0.8, 0.1] = [1.0, 2.8]

The first element changed a lot (forgotten old, added new).
The second element stayed similar (kept old, ignored new).

**Output gate:**
o_t = sigmoid(W_o @ [h_{t-1}, x_t] + b_o)
Let's say o_t = [0.5, 0.5]

**New hidden state:**
h_t = o_t * tanh(C_t)
h_t = [0.5, 0.5] * tanh([1.0, 2.8])
h_t = [0.5, 0.5] * [0.762, 0.993]
h_t = [0.381, 0.497]

---

### 5. Common confusion

- **"LSTM is NOT a completely different architecture from RNN."** It IS an RNN. It just has a more sophisticated update mechanism.
- **"The cell state and hidden state are DIFFERENT."** Cell state = long-term memory (protected). Hidden state = working memory / output.
- **"Gates use sigmoid because they need to output 0-1."** Sigmoid squashes to [0, 1], perfect for "how much to let through."
- **"Candidate values use tanh because they can be positive or negative."** Tanh squashes to [-1, 1], allowing the network to increase or decrease cell values.
- **"LSTMs were invented in 1997 by Hochreiter and Schmidhuber."** They are old but still widely used.
- **"GRU is a simplified LSTM."** It combines forget and input gates into one "update gate."

---

### 6. Where it is used in our code

In our code, we will implement an LSTM from scratch and test it on a long-range copy task: remembering a bit across 50 time steps. The LSTM will succeed where a vanilla RNN fails.

---

*You've got this! LSTMs sound fancy, but at their core they are just RNNs with a memory drawer and three smart guards. Now let's build one.*
