## What Is Model Parallelism?

---

### The Problem

Your model is too large to fit on a single GPU. GPT-4 has trillions of parameters — no single GPU has enough memory to hold the entire model, let alone its activations and gradients. How do you train a model that is bigger than your hardware?

---

### Definition

**Model parallelism** is the technique of splitting a model across multiple devices, where each device holds and computes only a portion of the model's layers or parameters.

**Types of model parallelism:**

**Layer-wise (pipeline) parallelism:**
```
GPU 1: Layers 1-10
GPU 2: Layers 11-20
GPU 3: Layers 21-30
GPU 4: Layers 31-40
```
Data flows sequentially through GPUs like an assembly line.

**Tensor parallelism:**
```
Each linear layer's weight matrix is split across GPUs:
GPU 1: first half of each weight matrix
GPU 2: second half of each weight matrix
```
Both GPUs process the same input but compute different output channels.

**Key insight:**
- Data parallelism duplicates the model. Model parallelism splits it.
- Model parallelism is necessary when the model exceeds GPU memory.
- Pipeline parallelism has "bubble" overhead (GPUs idle waiting for data).

---

### Real-Life Analogy

Building a car on an assembly line.
- **Single worker:** One person builds the entire car. They need a huge workspace and it takes forever.
- **Pipeline parallelism:** Station 1 installs the engine. Station 2 adds the wheels. Station 3 paints the body. Station 4 installs the interior. Each worker only needs tools for their step, and cars move down the line.
- **Tensor parallelism:** Two workers install wheels simultaneously — one does the left side, the other does the right side. They both work on the same car at the same time, but on different parts.

The trade-off: assembly lines have idle time when the first car is at Station 4 and Stations 1-3 are waiting. This is the "pipeline bubble."

---

### Tiny Numeric Example

**Model:** 2-layer MLP
```
Layer 1: y1 = ReLU(W1 @ x + b1)  # W1 is 4×2
Layer 2: y2 = W2 @ y1 + b2        # W2 is 1×4
```

**GPU 1 holds Layer 1:**
```
W1 = [[1, 0],
      [0, 1],
      [1, 1],
      [0, 0]]
b1 = [0, 0, 0, 0]
```

**GPU 2 holds Layer 2:**
```
W2 = [[1, -1, 0.5, 0]]
b2 = [0]
```

**Forward pass on input x = [2, 3]:**
```
GPU 1 computes:
  z1 = W1 @ x + b1 = [2, 3, 5, 0]
  y1 = ReLU(z1) = [2, 3, 5, 0]
  Sends y1 to GPU 2

GPU 2 computes:
  y2 = W2 @ y1 + b2 = 1×2 + (-1)×3 + 0.5×5 + 0×0 = 2 - 3 + 2.5 = 1.5
```

**Backward pass:**
```
GPU 2 computes grad_W2 and sends grad_y1 back to GPU 1
GPU 1 computes grad_W1 from grad_y1
```

Neither GPU holds the full model. They communicate intermediate activations and gradients.

---

### Common Confusion

1. **"Model parallelism is faster than data parallelism."** Usually slower. Communication of activations between layers adds overhead. It is a memory solution, not a speed solution.

2. **"You must choose data OR model parallelism."** Modern training uses both. Data parallelism across nodes, model parallelism within nodes. This is called 3D parallelism.

3. **"Pipeline parallelism has no overhead."** It has pipeline bubbles — GPUs at the start wait while GPUs at the finish work. Techniques like micro-batching reduce this.

4. **"Tensor parallelism is the same as data parallelism."** No. In tensor parallelism, all GPUs process the same data but different parts of each layer. In data parallelism, each GPU processes different data with the same full layer.

5. **"Any model can use model parallelism."** It works best for models with many layers (Transformers, ResNets). Small models gain nothing from the overhead.

---

### Where It Is Used in Our Code

`src/phase55/phase55_distributed_training.py` — We simulate a 2-layer network split across two "workers," showing how activations and gradients must pass between devices during forward and backward passes.
