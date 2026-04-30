# What Is Bias?

Welcome! If you are new to AI, this page is for you. We will explain one small but important idea: **bias**.

---

### 1. Definition (very simple)

In AI, **bias** is a parameter that shifts the output up or down. It is like the starting point or baseline value when the input is zero.

Think of it this way: a **parameter** is just a number the model uses to make decisions. A **model** is the math formula that turns an input into an output.

Bias allows the model to say: *"Even if the input is zero, the output should still be something."*

---

### 2. Why it exists

Sometimes the relationship between input and output is not perfectly proportional. Even with zero input, you might want a non-zero output.

Bias lets the line move up and down so it doesn't have to pass through the origin (0,0).

Without a bias, every model would be forced to say "zero input means zero output." But in the real world, that is often not true.

---

### 3. Real-life analogy

Imagine your **monthly phone bill**.

Your bill has a **base fee of $20** (this is the bias) plus **$0.10 per minute** of talk time (this is the input multiplied by a weight).

Even if you talk for **0 minutes** (input = 0), you still pay **$20**.

That **$20** is the bias. It shifts the total up.

> **Formula:** total bill = (minutes × $0.10) + $20

The $20 is always there, no matter how many minutes you use.

---

### 4. Tiny numeric example

Let's compare a model **without bias** and a model **with bias**.

#### Model without bias:
```
output = input × 2
```

| Input | Output |
|-------|--------|
| 0     | 0      |
| 3     | 6      |

When the input is 0, the output is forced to be 0.

#### Model with bias:
```
output = (input × 2) + 5
```

| Input | Output |
|-------|--------|
| 0     | 5      |
| 3     | 11     |

Notice what happened:
- When input was 0, the output was **5** (the bias!).
- When input was 3, the output was 11 instead of 6.

The **bias of 5** shifted every output up by 5. That is all it does!

---

### 5. Common confusion

The word **"bias"** can be confusing because it is used in everyday language too.

In AI, bias is **just a number**. It is **NOT** the same as human prejudice (like favoring one group over another). Although the word looks the same, the meaning here is purely mathematical.

In AI, bias simply means **"an additive constant"** or **"a shift."**

It is nothing more than a number you add to the result.

---

### 6. Where it is used in our code

In our Linear Regression code, we will have a bias (often called **'b'**). It will be added after the input is multiplied by the weight.

For example:
```
prediction = (input × weight) + bias
```

The code will adjust this bias during learning to move the line up or down to fit the data. Just like finding the right base fee for your phone bill, the model learns the right bias to make the best predictions.

---

You now understand bias! It is simply a number that shifts results up or down. Easy, right? Let's keep going.
