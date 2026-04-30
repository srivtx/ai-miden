# AI from Absolute Zero

> **A complete AI course for absolute beginners.**
> 
> No prior knowledge of AI, machine learning, or advanced math required.
> Basic algebra is all you need.

---

## Welcome

If you have never heard of neural networks, gradients, or backpropagation, you are in the right place.

This project builds an AI system **completely from scratch** while teaching you every concept along the way. We use only Python and NumPy. No shortcuts. No black boxes. Every line of code is explained.

By the end, you will understand:
- What AI actually is (hint: it is not magic)
- How a computer learns from examples
- How to build a neural network by hand
- Why every piece of the puzzle exists

---

## How to Use This Course

This project is organized into **phases**. Each phase builds on the previous one.

**Recommended path:**
1. Read the docs in `docs/phaseX/` in order
2. Run the code in `src/phaseX/` to see it in action
3. Do the dry-run with numbers yourself
4. Move to the next phase only when you feel comfortable

Every technical term has its own documentation file. If you see a word you do not recognize, find it in the docs folder.

---

## Project Structure

```
ai-miden/
├── docs/
│   ├── phase0/          # The absolute basics
│   ├── phase1/          # Our first model
│   ├── phase2/          # How we measure wrongness
│   ├── phase3/          # How the model learns
│   └── phase4/          # Neural networks
├── src/
│   ├── phase0/          # Functions and predictions
│   ├── phase1/          # Linear regression model
│   ├── phase2/          # Error, loss, gradients
│   ├── phase3/          # Gradient descent training
│   └── phase4/          # Neural network from scratch
└── README.md            # This file
```

---

## Phase 0: Absolute Zero

**Goal:** Understand the foundational vocabulary.

### Terms Covered
| File | Term |
|---|---|
| `what_is_ai.md` | AI (Artificial Intelligence) |
| `what_is_prediction.md` | Prediction |
| `what_is_function.md` | Function |
| `what_is_input_output.md` | Input and Output |

### Code
`src/phase0/phase0_basics.py` — Demonstrates functions, input/output, and making predictions from learned patterns.

### Run It
```bash
python src/phase0/phase0_basics.py
```

---

## Phase 1: First Model

**Goal:** Build a Linear Regression model and understand its parts.

### Terms Covered
| File | Term |
|---|---|
| `what_is_model.md` | Model |
| `what_is_parameter.md` | Parameter |
| `what_is_weight.md` | Weight |
| `what_is_bias.md` | Bias |
| `what_is_numpy.md` | NumPy |

### Code
`src/phase1/phase1_linear_regression.py` — A model with weight and bias parameters. Shows how bad parameters give bad predictions, and good parameters give perfect predictions.

### Run It
```bash
python src/phase1/phase1_linear_regression.py
```

---

## Phase 2: The Learning Process

**Goal:** Learn how to measure how wrong our model is.

### Terms Covered
| File | Term |
|---|---|
| `what_is_error.md` | Error |
| `what_is_loss_function.md` | Loss Function (MSE) |
| `what_is_derivative.md` | Derivative |
| `what_is_gradient.md` | Gradient |

### Code
`src/phase2/phase2_learning_process.py` — Computes predictions, errors, loss, and gradients for a bad model. Only measures. Does not learn yet.

### Run It
```bash
python src/phase2/phase2_learning_process.py
```

---

## Phase 3: The Learning Mechanism

**Goal:** Make the model actually learn by adjusting its parameters automatically.

### Terms Covered
| File | Term |
|---|---|
| `what_is_gradient_descent.md` | Gradient Descent |
| `what_is_learning_rate.md` | Learning Rate |
| `what_is_optimization.md` | Optimization |

### Code
`src/phase3/phase3_gradient_descent.py` — A complete training loop. The model starts with random parameters and learns the correct pattern by repeatedly measuring error and taking small steps downhill.

### Run It
```bash
python src/phase3/phase3_gradient_descent.py
```

---

## Phase 4: Neural Networks

**Goal:** Build a neural network from scratch that can learn non-linear (curved) patterns.

### Terms Covered
| File | Term |
|---|---|
| `what_is_neuron.md` | Neuron |
| `what_is_layer.md` | Layer |
| `what_is_neural_network.md` | Neural Network |
| `what_is_activation_function.md` | Activation Function (ReLU) |
| `what_is_non_linearity.md` | Non-Linearity |
| `what_is_forward_pass.md` | Forward Pass |
| `what_is_chain_rule.md` | Chain Rule |
| `what_is_backpropagation.md` | Backpropagation |

### Code
`src/phase4/phase4_neural_network.py` — A complete neural network with one hidden layer, ReLU activation, and manual backpropagation. First shows linear regression failing on a parabola, then shows the neural network succeeding.

### Run It
```bash
python src/phase4/phase4_neural_network.py
```

---

## The Big Picture

Here is how everything connects:

```
PHASE 0: Vocabulary
    AI, Prediction, Function, Input/Output
    ↓
PHASE 1: Structure
    Model, Parameter, Weight, Bias
    We can make predictions, but only with hand-picked parameters
    ↓
PHASE 2: Measurement
    Error, Loss, Derivative, Gradient
    We can measure how wrong we are and which way to improve
    ↓
PHASE 3: Learning
    Gradient Descent, Learning Rate, Optimization
    We automatically adjust parameters to minimize loss
    ↓
PHASE 4: Power
    Neuron, Layer, Activation, Backpropagation
    We build a network of many neurons that can learn curved patterns
```

**The entire journey:** A computer starts knowing nothing, measures its mistakes, figures out which knobs to turn, and slowly becomes good at making predictions. That is learning. That is AI.

---

## Quick Start

Make sure you have Python and NumPy installed:

```bash
pip install numpy
```

Then run any phase:

```bash
# Phase 0: Basics
python src/phase0/phase0_basics.py

# Phase 1: Linear Regression
python src/phase1/phase1_linear_regression.py

# Phase 2: Error and Gradients
python src/phase2/phase2_learning_process.py

# Phase 3: Learning (Gradient Descent)
python src/phase3/phase3_gradient_descent.py

# Phase 4: Neural Network
python src/phase4/phase4_neural_network.py
```

---

## What Makes This Course Different

- **Every term is explained.** No jargon without a definition, analogy, and numeric example.
- **No shortcuts.** We build everything from scratch using only Python and NumPy.
- **No prior knowledge assumed.** If you know basic algebra, you can follow along.
- **Dry runs with real numbers.** Every concept is demonstrated with concrete examples.
- **Code is readable.** Comments explain WHY, not just WHAT.

---

## Course Stats

| Phase | Docs | Code Files | New Terms |
|---|---|---|---|
| Phase 0 | 4 | 1 | 4 |
| Phase 1 | 5 | 1 | 5 |
| Phase 2 | 4 | 1 | 4 |
| Phase 3 | 3 | 1 | 3 |
| Phase 4 | 8 | 1 | 8 |
| **Total** | **24** | **5** | **24** |

---

## Final Message

You just built an AI system from absolute zero.

You started with the question "What is a function?" and ended with a neural network that learns to approximate curves. Every step along the way was explained from first principles.

The fancy words — gradient descent, backpropagation, neural network — are not magic. They are just systematic ways of:
1. Making a guess
2. Measuring how wrong the guess is
3. Figuring out which direction to improve
4. Taking a small step
5. Repeating

That is all AI is. And now you know it from the inside out.

**Keep going. You have everything you need.**
