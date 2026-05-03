# What Are Progressive Networks?

## 1. Why it exists (THE PROBLEM first)

Every continual learning method we've discussed tries to protect old knowledge inside a **single, shared** model. But what if we just... didn't share? What if each new task got its own set of parameters, while still being able to reuse representations from old tasks? Progressive Networks take this idea to the extreme: instead of fighting over weights, they add a whole new "column" of layers for each task. Old columns are frozen forever. New columns can read from old columns but never write to them. Zero forgetting, by architecture.

## 2. Definition

**Progressive Networks** are a neural architecture for continual learning where each new task adds a new column (a stack of layers) to the network. Previously trained columns are frozen. New columns receive lateral connections from all old columns, allowing knowledge reuse, but old columns are never modified. The result is guaranteed zero forgetting at the cost of linearly growing model size.

$$h_i^{(t)} = \sigma(W_i^{(t)} h_{i-1}^{(t)} + \sum_{j < t} U_i^{(t,j)} h_{i-1}^{(j)})$$

Where $t$ is the task index, $i$ is the layer index, $W$ is the main weight, and $U$ are lateral connections from old task $j$.

## 3. Real-life analogy

Imagine a library. For the first book collection (Task A), you build one wing with its own shelves, catalog, and reading room. When you get a second collection (Task B), you don't tear down or reorganize the first wing. You build a **new wing** next to it. Patrons in the new wing can walk into the old wing to reference books, but librarians never move books out of the old wing. The first collection stays exactly as it was. Each new collection = new wing.

## 4. Tiny numeric example

Task A column: 2 layers, 10 weights each = 20 weights. Trained, frozen.
Task B column: 2 layers, 10 weights each + 10 lateral connections from Task A = 30 weights. Trained on Task B.

During Task B inference:
- Input flows through Task A column (frozen, produces features)
- Input also flows through Task B column
- Task B column receives Task A's layer-1 output as extra input via lateral weights
- Task B uses both its own weights and Task A's frozen knowledge

Task A weights: never touched. Task A accuracy: still 95%.

## 5. Common confusion

- **"Progressive Networks share no parameters at all."** They share no **trainable** parameters for old tasks, but new tasks can read from old tasks via lateral connections. There is information flow, just no gradient flow back to old columns.
- **"The model size stays constant."** No. Model size grows **linearly** with the number of tasks. 10 tasks = ~10x the parameters. This is the trade-off: zero forgetting, but unbounded growth.
- **"You can delete old columns to save space."** If you delete them, you lose the ability to solve old tasks. The whole point is keeping them.
- **"Progressive Networks are the same as multi-task learning."** In multi-task learning, all tasks are trained jointly with shared layers. In Progressive Networks, tasks are trained sequentially, old layers are frozen, and only new layers are trained.
- **"Lateral connections are optional."** Without lateral connections, each task column is isolated and can't benefit from previous representations. The lateral connections are what make Progressive Networks powerful—they enable forward transfer.
- **"They only work for small numbers of tasks."** True in practice due to growth, but this is a practical limitation, not a theoretical one. Variants like "Progressive Compressed Networks" address growth by distilling old columns.

## 6. Where it is used in our code

In `src/phase81/phase81_continual_learning_colab.py`, we implement a simplified Progressive Network for split MNIST. After training a base column on digits 0-4, we freeze all its layers. For digits 5-9, we add a new column with the same architecture but include lateral connections from each layer of the old column. The new column's first hidden layer receives concatenated input: the raw image AND the old column's first hidden activation. We show Task A accuracy remains exactly at its peak (zero forgetting) while Task B learns effectively. The architecture growth is visible in the model summary.