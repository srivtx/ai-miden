# What Is the Hidden State?

Welcome! If you just learned about RNNs, you might be wondering: **what exactly is this "hidden state" thing?** Don't worry — by the end of this guide, you'll understand it clearly.

---

## 1. Why it exists (THE PROBLEM first)

Imagine reading a sentence: **"The cat sat on the mat and looked at the mouse."**

To understand **"mouse,"** you need to remember:
- There is a cat (subject)
- The cat is sitting (action)
- The cat is looking (current action)

You cannot understand **"mouse"** by only looking at the word **"mouse."** You need **CONTEXT** from earlier in the sentence.

A standard neural network has no memory. It sees each word in isolation.

**The hidden state solves this by acting as a memory that carries information forward through time.**

---

## 2. Definition (very simple)

The hidden state is a **vector of numbers** that represents the network's memory of everything it has seen so far in the sequence.

At each time step:
- The hidden state is **UPDATED** by combining the current input with the previous hidden state.
- The hidden state is **PASSED** to the next time step.
- The hidden state can be **USED** to make predictions.

Think of it as a **"summary"** or **"compressed memory"** of the sequence up to the current point.

---

## 3. Real-life analogy

### The Notepad While Reading a Book

Imagine reading a mystery novel. You keep a notepad where you jot down key facts.

- **Page 1:** "A man named John entered the room."
  - Notepad: [John, man, entered, room]

- **Page 50:** "John picked up the knife."
  - Notepad: [John, man, entered, room, picked up, knife]

- **Page 200:** "The detective arrested John."
  - Notepad: [John, man, entered, room, picked up, knife, detective, arrested]

At every page, your notepad contains a **SUMMARY** of everything important so far.

In an RNN:
- The **notepad** = the hidden state
- Each **page** = one time step
- **Updating the notepad** = the RNN update equation

### Another Analogy: A Baton in a Relay Race

- The baton carries information from the start to the end.
- Each runner adds their contribution and passes it on.
- Without the baton, each runner is running independently and the race makes no sense.

---

## 4. Tiny numeric example

Let's watch a hidden state evolve through a sequence.

We have a vocabulary of 3 words, encoded as one-hot vectors:
- **"cat"** = `[1, 0, 0]`
- **"sat"** = `[0, 1, 0]`
- **"mat"** = `[0, 0, 1]`

### RNN parameters:
- `W_xh` = `[[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]`  (3 input dims → 2 hidden dims)
- `W_hh` = `[[0.7, 0.8], [0.9, 1.0]]`  (2 hidden dims → 2 hidden dims)
- `b_h` = `[0, 0]`
- **Activation:** `tanh`

### Initial hidden state: `h_0` = `[0, 0]`

---

### Step 1: Input "cat" = `[1, 0, 0]`

```
h_1 = tanh(W_xh @ [1,0,0] + W_hh @ [0,0] + [0,0])
h_1 = tanh([0.1, 0.4] + [0, 0])
h_1 = tanh([0.1, 0.4])
h_1 = [0.100, 0.380]
```

---

### Step 2: Input "sat" = `[0, 1, 0]`

```
h_2 = tanh(W_xh @ [0,1,0] + W_hh @ [0.100, 0.380] + [0,0])
h_2 = tanh([0.2, 0.5] + [0.7*0.100 + 0.8*0.380, 0.9*0.100 + 1.0*0.380])
h_2 = tanh([0.2, 0.5] + [0.374, 0.470])
h_2 = tanh([0.574, 0.970])
h_2 = [0.518, 0.749]
```

---

### Step 3: Input "mat" = `[0, 0, 1]`

```
h_3 = tanh(W_xh @ [0,0,1] + W_hh @ [0.518, 0.749] + [0,0])
h_3 = tanh([0.3, 0.6] + [0.7*0.518 + 0.8*0.749, 0.9*0.518 + 1.0*0.749])
h_3 = tanh([0.3, 0.6] + [0.962, 1.215])
h_3 = tanh([1.262, 1.815])
h_3 = [0.853, 0.948]
```

### Result

The hidden state grew from `[0, 0]` to `[0.853, 0.948]`, **accumulating information about "cat sat mat."**

---

## 5. Common confusion

Let's clear up some common misconceptions:

### ❌ "Hidden state is the same as hidden layer."
**✅ Nope!** A hidden layer is a layer in a feedforward network. A hidden state is a **memory vector** in an RNN. They sound similar but are totally different concepts.

### ❌ "The hidden state is fixed like network weights."
**✅ Nope!** The hidden state **changes at EVERY time step.** It is not fixed like network weights. It is **dynamic memory**.

### ❌ "The hidden state is the output."
**✅ Nope!** The hidden state is **internal memory.** The output might be derived from it, but they are different things. Think of the hidden state as your notepad, and the output as what you say aloud based on your notes.

### ❌ "The hidden state is the same for every sequence."
**✅ Nope!** Different sequences have different hidden states. The hidden state for "cat sat" is completely different from "dog ran."

### ❌ "The hidden state grows with the sequence length."
**✅ Nope!** The hidden state has a **fixed size.** Even if the input sequence is 1000 words long, the hidden state might only be 128 numbers. It is a **COMPRESSED summary** — not a growing list.

---

## 6. Where it is used in our code

In our RNN code, the hidden state starts at zeros and gets updated at every character of the input sequence **"HELLO"**. By the end, it contains a compressed memory of the entire word.

Think about it: after seeing 'H', then 'E', then 'L', then 'L', then 'O', the hidden state has absorbed information from all five characters. If we then ask the network to predict what comes next, it uses this hidden state — this memory — to make an informed guess.

---

## Summary

| Concept | What It Is |
|---------|-----------|
| Hidden State | A vector of numbers (memory) |
| Purpose | Carry context forward through time |
| Analogy | A notepad you update while reading |
| Key Property | Fixed size, dynamic, sequence-dependent |

**You got this!** The hidden state is just memory. And now you know exactly how it works. 🎉
