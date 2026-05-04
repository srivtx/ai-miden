## What Is Evolutionary Search?

---

### The Problem

Gradient descent is the engine of deep learning, but it only works when the variables are continuous and differentiable. How do you optimize the *number of layers* in a network? You cannot take the derivative of validation loss with respect to layer count — it is an integer. Grid search is too expensive. Random search is blind. You need an optimization method that handles discrete choices, noisy objectives, and non-convex landscapes without gradients. Nature solved this problem billions of years ago.

---

### Definition

**Evolutionary Search** is a population-based optimization algorithm inspired by natural selection. A population of candidate architectures is maintained. In each generation, the fittest candidates are selected, mutated, and recombined to produce offspring. Over time, the population converges to high-performing regions of the search space.

**How it works:**
```
Initialize:   Create N random architectures (the population)
Evaluate:     Train each architecture for a few steps, measure fitness
Select:       Keep the top K architectures (survival of the fittest)
Mutate:       For each survivor, create offspring by randomly changing
              depth, width, or heads (small random perturbations)
Replace:      The offspring form the next generation
Repeat:       For G generations
```

**Key operators:**
- **Mutation:** Change one attribute of an architecture (e.g., increase layers by 2, decrease width by 64). Mutation strength controls exploration vs. exploitation.
- **Crossover:** Combine two parent architectures (e.g., take depth from parent A and width from parent B). This mixes good building blocks.
- **Selection pressure:** How aggressively you prune the population. High pressure converges fast but may get stuck in local optima. Low pressure explores more but needs more generations.
- **Elitism:** Always keep the single best architecture from the previous generation. This prevents regression.

**Why this matters:**
- Evolutionary search discovered AmoebaNet, which matched the accuracy of hand-designed ResNets on ImageNet.
- It requires no gradients, making it ideal for discrete search spaces like architecture choices.
- It is embarrassingly parallel: each individual in the population can be evaluated on a separate GPU.
- It naturally handles multi-objective optimization (accuracy vs. latency) by maintaining a Pareto frontier as the population.

---

### Real-Life Analogy

Breeding championship racing dogs.
- **Grid search:** You test every purebred dog in the registry. It takes decades and you miss crossbreeds that might be faster.
- **Random search:** You adopt random dogs from shelters and race them. You might get lucky, but you have no way to combine the best traits.
- **Evolutionary search:** You start with 100 mixed-breed dogs. You race them and keep the 20 fastest. You breed them, introducing small random mutations (ear length, muscle density) and occasionally crossing two unrelated fast dogs. After 10 generations, you have a breed that is faster than any purebred, optimized for your specific track surface.
- **Elitism:** The single fastest dog from generation 3 is always allowed to breed in generation 4, so you never accidentally lose a winning bloodline.

---

### Tiny Numeric Example

**Search space:** Layers in {2,4,6,8,10}, Width in {64,128,192,256}
**Fitness:** accuracy = 0.5 + 0.02*layers + 0.001*width - 0.0001*width^2 + noise(0, 0.01)

**Generation 0 (random population of 6):**
```
Arch      Layers    Width    Fitness
A         2         64       0.544
B         8         128      0.644
C         4         256      0.624
D         10        64       0.684
E         6         192      0.651
F         2         128      0.556
```

**Selection (keep top 3):** D (0.684), E (0.651), B (0.644)

**Mutation (offspring):**
- D -> D1: layers=10+2=12 (clipped to 10), width=64 -> 128 -> fitness 0.692
- E -> E1: layers=6, width=192+64=256 -> fitness 0.653
- B -> B1: layers=8-2=6, width=128 -> fitness 0.631

**Generation 1 population:** D, E, B, D1, E1, B1
**Best fitness:** D1 at 0.692

**After 5 generations:** The population clusters around (layers=10, width=128), which is the true optimum in this synthetic landscape.

---

### Common Confusion

1. **"Evolutionary search is just random search with extra steps."** It is not random. Selection and mutation create a directed walk toward high-fitness regions. Random search has no memory; evolutionary search accumulates good building blocks.

2. **"Evolutionary algorithms always find the global optimum."** They do not guarantee global optimality. Like gradient descent, they can get stuck in local optima, especially if mutation strength is too low.

3. **"You need a huge population."** For architecture search, populations of 10-50 are often sufficient because evaluation is expensive. The key is elitism and mutation strength, not population size.

4. **"Crossover is always better than mutation."** In high-dimensional spaces, crossover can disrupt good architectures by mixing incompatible parts. For LLM architecture search, mutation (tweak one hyperparameter) is often more effective than crossover.

5. **"Evolutionary search is slow because it is sequential."** It is highly parallel. Each individual in a generation is independent. A population of 50 can be evaluated on 50 GPUs simultaneously.

6. **"Fitness must be a single scalar."** Multi-objective evolutionary algorithms (NSGA-II) maintain a Pareto frontier of non-dominated solutions across accuracy, latency, and memory simultaneously.

7. **"Evolutionary search is outdated compared to Bayesian optimization."** Bayesian optimization excels on continuous, low-dimensional spaces with expensive evaluations. Evolutionary search excels on discrete, high-dimensional spaces with many local optima — exactly the NAS setting.

---

### Where It Is Used in Our Code

`src/phase140/phase140_nas_concepts.py` — We implement a full evolutionary loop on a synthetic accuracy landscape. We initialize a population of architectures, evaluate them, mutate the best, and track how the population converges toward the global optimum. We compare this to random and grid baselines.

`src/phase140/phase140_nas_colab.py` — After training all 9 real models, we run an evolutionary search *in simulation* using their measured perplexities. Starting from a random subset, we mutate depth and width, select for low perplexity, and show that evolutionary search finds the Pareto-optimal config with fewer evaluations than grid search.
