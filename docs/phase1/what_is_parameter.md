# What Is a Parameter?

Welcome! If you are completely new to AI and programming, you are in the right place. We are going to explain what a **parameter** is using only basic algebra—no fancy words, no coding knowledge needed.

---

### 1. Definition (Very Simple)

A **parameter** is just a number inside the model that we can adjust or change to make the model fit the data better.

Think of parameters as the **knobs** or **dials** on our model. We turn them until the model works well.

---

### 2. Why It Exists

A model by itself is just an empty template—like a blank coloring book. Parameters fill in the details and bring it to life.

Without adjustable parameters, the model would always give the same answer no matter what data it sees. Parameters let the model adapt to different situations, so it can learn from the information it is given.

---

### 3. Real-Life Analogy

Imagine a **radio**.

- The radio itself is the **model**. It receives signals and plays sound.
- The **tuning knob** and the **volume dial** are the **parameters**.
  - You turn the tuning knob to find your favorite station.
  - You turn the volume dial to hear it properly.

Different settings (different parameters) give you different results, but it is still the same radio (the same model).

---

### 4. Tiny Numeric Example

Let's look at a very simple model:

```
output = input × W + B
```

Here, **W** and **B** are our parameters.

- If **W = 2** and **B = 1**, and our input is **3**:
  - output = 3 × 2 + 1 = **7**
- If **W = 5** and **B = 0**, and our input is still **3**:
  - output = 3 × 5 + 0 = **15**

See what happened? It is the same model, but different parameters gave us a completely different answer. Parameters are the numbers we can twist and turn to change how the model behaves.

---

### 5. Common Confusion

Let's clear up two common mix-ups:

1. **Parameter vs. Settings in a Phone App**
   When you change a setting in a phone app—like switching on Dark Mode—you are flipping a switch. Parameters are not like that. They are numbers that the **computer learns automatically** by looking at data. A human might give the computer a starting guess, but the computer does the heavy lifting of adjusting them.

2. **Parameter vs. Perimeter**
   These words sound similar, but they have nothing to do with each other. "Perimeter" is the distance around a shape (from geometry class). "Parameter" is a number inside a model that we adjust.

---

### 6. Where It Is Used in Our Code

In our **Linear Regression** code, we will have two parameters:

- A **weight** (we will call it **W**)
- A **bias** (we will call it **B**)

The code will start with random guesses for these two parameters. Then, by looking at the data, it will slowly adjust them—turning the knobs—until they fit the data better and make better predictions.

---

**Great job reading this far!** You now understand that a parameter is simply an adjustable number that helps a model learn and adapt. That is a powerful first step.
