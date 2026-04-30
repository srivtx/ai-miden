# What Is a Forward Pass?

Welcome! If you have never heard of neural networks before, you are in the right place. We are going to explain the "forward pass" using nothing more than basic algebra and a little imagination.

---

## 1. Definition (very simple)

A **forward pass** is the process of sending data through the neural network from the input layer all the way to the output layer to get a prediction.

It is called "forward" because the data moves forward — from left to right, from input to output. Nothing is learned during the forward pass. It is just the network making a guess.

Think of it like a calculator: you punch in numbers, hit a few buttons, and an answer pops out. The calculator did not "learn" anything — it just followed steps.

---

## 2. Why it exists

Before we can measure how wrong we are, we need to **make** a prediction. The forward pass is how we get that prediction.

It is the "thinking" step (although we know networks don't actually think — it is just math). You give the network some input, it runs the forward pass, and it gives you an output. Then you can compare that output to the correct answer and see how far off you were.

---

## 3. Real-life analogy

Imagine a cookie factory with three stations:

- **Station 1: Mix ingredients** (input layer receives dough)
- **Station 2: Shape the cookies** (hidden layer transforms the dough)
- **Station 3: Bake and package** (output layer produces finished cookies)

The dough moves forward through each station. At each station, it gets transformed. By the end, you have cookies.

The forward pass is exactly this: data moves through each layer, getting transformed, until a final result comes out. The dough never goes backward during this step — it only goes forward. That is the forward pass.

---

## 4. Tiny numeric example

Let us walk through a complete forward pass for a tiny network.

**Network:**
- **Input:** `x = 2`
- **Hidden layer:** 1 neuron with `weight = 3`, `bias = 1`, and **ReLU activation**
- **Output layer:** 1 neuron with `weight = 2`, `bias = 0`

> **Quick vocab check:**
> - A **neuron** is just a little math box that multiplies, adds, and maybe squishes a number.
> - A **layer** is a group of neurons working together.
> - A **weight** is a number the network uses to scale (multiply) the input. It is like a volume knob.
> - A **bias** is a number added after scaling. It is like shifting the starting point.
> - An **activation function** (like ReLU) decides whether the neuron "fires" or stays quiet. ReLU is super simple: if the number is negative, it becomes 0. Otherwise, it stays the same.

---

**Step 1 (Input):**
```
x = 2
```

**Step 2 (Hidden layer):**
```
z = (x * weight) + bias
z = (2 * 3) + 1 = 7

a = ReLU(7) = 7
```
*(ReLU leaves positive numbers alone, so 7 stays 7.)*

**Step 3 (Output layer):**
```
prediction = (a * weight) + bias
prediction = (7 * 2) + 0 = 14
```

**Forward pass complete.** The network predicts **14** for input **2**.

---

### Slightly bigger example

Let us try a negative input to see what ReLU does.

- **Input:** `x = -1`
- **Hidden layer:** `z = (-1 * 3) + 1 = -2`, then `a = ReLU(-2) = 0`
- **Output layer:** `prediction = (0 * 2) + 0 = 0`

Notice how ReLU **"turned off"** the hidden neuron when the input was negative, causing the final prediction to be **0**. This is the power of activation functions — they let the network decide which paths to use and which to ignore.

---

## 5. Common confusion

Let us clear up a few things that trip people up:

- **"Forward pass does NOT learn anything."**  
  It only makes predictions. Learning happens later (in the backward pass).

- **"Forward pass happens for EVERY example."**  
  If you have 100 examples, you do 100 forward passes (or batch them together).

- **"The forward pass is just multiplication and addition."**  
  It looks scary in code because of matrix math, but it is fundamentally simple.

- **"Every layer in the forward pass depends on the previous layer."**  
  You cannot skip layers. The output of one layer becomes the input to the next.

---

## 6. Where it is used in our code

In our neural network code, we will write a `forward` method that takes the input data and passes it through the hidden layer (applying weights, biases, and ReLU) and then through the output layer (applying weights and biases).

This method will return the final predictions, which we will then compare to the true answers to measure error.

So every time you see `forward()` in the code, remember: it is just the cookie assembly line moving dough from station to station until cookies come out the other side.

---

**You did it!** You now understand what a forward pass is. It is not magic — it is just math moving in one direction. 🍪
