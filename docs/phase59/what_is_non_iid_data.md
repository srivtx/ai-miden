## What Is Non-IID Data?

---

### The Problem

In federated learning, each client has its own data. But real-world data is not uniformly distributed. One hospital sees mostly elderly patients. Another sees mostly children. One phone user texts about sports, another about cooking. When data distributions differ across clients, federated averaging breaks down. Why?

---

### Definition

**Non-IID (non-independent and identically distributed)** data means that the distribution of examples across clients is not uniform. Each client's local dataset has a different statistical distribution than the global dataset.

**Types of non-IIDness:**

**1. Label skew:**
```
Client A: 90% cats, 10% dogs
Client B: 90% dogs, 10% cats
Global:   50% cats, 50% dogs
```

**2. Feature skew:**
```
Client A: Photos taken in bright daylight
Client B: Photos taken in dark rooms
Same labels, different feature distributions
```

**3. Quantity skew:**
```
Client A: 100,000 examples
Client B: 100 examples
```

**4. Concept drift:**
```
Client A: Winter clothing (coats, scarves)
Client B: Summer clothing (shorts, t-shirts)
Same label "clothing" but different concepts
```

**Why non-IID is hard:**
- Each client optimizes for its own local distribution
- FedAvg averages models that want to go in different directions
- The global model becomes a mediocre compromise
- Convergence slows or fails entirely

---

### Real-Life Analogy

Five people from different countries trying to write a shared cookbook.
- **Client A (Italy):** Only knows pasta recipes. Their "best cookbook" is 100% pasta.
- **Client B (Japan):** Only knows sushi recipes. Their "best cookbook" is 100% sushi.
- **Client C (India):** Only knows curry recipes.
- **Client D (Mexico):** Only knows taco recipes.
- **Client E (France):** Only knows pastry recipes.

**FedAvg (averaging their cookbooks):** A terrible book with one chapter of each. No one is happy.

**Solutions:**
- **Personalized federated learning:** Each person keeps their specialty but shares common techniques (knife skills, timing).
- **FedProx:** Add a penalty if your local model drifts too far from the global model.
- **Clustered federated learning:** Group similar clients (Italy + France = European cuisine) and train separate models.

---

### Tiny Numeric Example

**True global model:** `y = 2x` (slope = 2)

**Client A (only low x values):** Data near x=1
```
Local optimum: y = 1.5x (learns lower slope from limited range)
```

**Client B (only high x values):** Data near x=10
```
Local optimum: y = 2.5x (learns higher slope from limited range)
```

**FedAvg:**
```
w_global = (1.5 + 2.5) / 2 = 2.0
```

**But gradients during training:**
```
Client A pushes toward 1.5
Client B pushes toward 2.5
They fight each other. Convergence is slow.
```

**With many clients and many rounds:** It eventually reaches 2.0, but takes 10× more rounds than with IID data.

---

### Common Confusion

1. **"Non-IID data is rare."** No. Real-world federated data is almost always non-IID. IID is the unrealistic assumption.

2. **"Non-IID only affects federated learning."** No. Any distributed system with heterogeneous data faces this: multi-task learning, transfer learning, meta-learning.

3. **"You can fix non-IID by shuffling data."** That defeats the purpose of federated learning. The data must stay local.

4. **"Non-IID always hurts performance."** It hurts convergence speed. But the final model can still be good if you train long enough or use specialized algorithms.

5. **"All clients have the same non-IID pattern."** No. Some clients have label skew, others have feature skew, others have concept drift. The problem is multifaceted.

---

### Where It Is Used in Our Code

`src/phase59/phase59_federated_learning.py` — We simulate non-IID data across clients (each client sees a different subset of features), showing how FedAvg converges slower than with IID data and how the global model is pulled in conflicting directions.
