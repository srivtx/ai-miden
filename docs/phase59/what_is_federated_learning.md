## What Is Federated Learning?

---

### The Problem

You want to train a medical diagnosis model on patient data from 100 hospitals. But privacy laws (HIPAA, GDPR) make it illegal to centralize that data. Each hospital has its own private dataset that cannot leave its premises. How do you train a single shared model without any hospital ever seeing another hospital's data?

---

### Definition

**Federated learning** is a distributed machine learning approach where models are trained across multiple decentralized devices or servers holding local data samples, without exchanging the raw data itself. Only model updates (gradients or weights) are shared.

**How it works:**
```
1. Server sends the current global model to all clients (hospitals, phones, etc.)
2. Each client trains the model on its local private data
3. Each client sends only its model updates (gradients or new weights) back to the server
4. Server aggregates all updates (e.g., averages them) to produce a new global model
5. Repeat for many rounds
```

**Key properties:**
- **Data never leaves the client.** Only model parameters travel.
- **Heterogeneous data.** Each client has different data (non-IID).
- **Communication efficiency.** Only small model updates are sent, not massive datasets.
- **Privacy-preserving.** Raw data stays local by design.

**Why this matters:**
- Train on smartphones without uploading personal photos/messages
- Train on medical data across hospitals without violating HIPAA
- Train on financial data across banks without exposing transactions
- Train on IoT sensors without sending raw sensor streams to the cloud

---

### Real-Life Analogy

A group of chefs improving a shared recipe without revealing their secret ingredients.
- **Centralized training:** All chefs send their ingredients to a central kitchen. The head chef tastes everything and improves the recipe. But now everyone knows each other's secret ingredients.
- **Federated learning:** Each chef improves the recipe using only their own ingredients at home. They only tell the head chef "I added more salt" or "I reduced cooking time by 2 minutes." The head chef averages all suggestions and updates the master recipe. No one learns what anyone else is cooking.

The recipe gets better, but the secret ingredients stay secret.

---

### Tiny Numeric Example

**Global model:** `y = w*x` where `w = 1.0`

**Client A (hospital A):** Data: [(x=1, y=2), (x=2, y=4)]
```
Local gradient: average of (-2.0, -4.0) = -3.0
Local update: w_A = 1.0 - 0.1*(-3.0) = 1.3
```

**Client B (hospital B):** Data: [(x=1, y=3), (x=2, y=5)]
```
Local gradient: average of (-3.0, -5.0) = -4.0
Local update: w_B = 1.0 - 0.1*(-4.0) = 1.4
```

**Server aggregation (FedAvg):**
```
w_global = (w_A + w_B) / 2 = (1.3 + 1.4) / 2 = 1.35
```

**If data were centralized:**
```
All data: [(1,2), (2,4), (1,3), (2,5)]
True gradient: (-2.5, -4.5) average = -3.5
Centralized update: w = 1.0 - 0.1*(-3.5) = 1.35
```

**Federated averaging matches centralized training exactly** when data is IID (independent and identically distributed) across clients. With non-IID data, the match is approximate.

---

### Common Confusion

1. **"Federated learning is completely private."** No. Model updates can still leak information about training data (membership inference attacks). Differential privacy is needed for strong guarantees.

2. **"Federated learning is just distributed training."** Similar but different. Distributed training (Phase 55) assumes you can access all data. Federated learning explicitly forbids data sharing.

3. **"All clients train on the same data."** No. Each client has its own local, private, often very different data.

4. **"Federated learning is slower than centralized."** Yes. Communication rounds replace data access. But the privacy benefit is worth the cost.

5. **"Federated learning only works for small models."** Modern systems federate billion-parameter models. The challenge is communication bandwidth, not model size.

---

### Where It Is Used in Our Code

`src/phase59/phase59_federated_learning.py` — We simulate 5 clients with local datasets, train models locally, and aggregate updates on a central server using federated averaging, showing convergence without any client seeing another's data.
