## What Is Federated Averaging?

---

### The Problem

In federated learning, each client trains on local data and sends updates to the server. But clients have different amounts of data. Should a client with 10,000 examples have the same influence as a client with 10 examples? How do you combine updates fairly?

---

### Definition

**Federated Averaging (FedAvg)** is the standard aggregation algorithm for federated learning. It computes a weighted average of client model updates, where each client's weight is proportional to the amount of data it trained on.

**The FedAvg formula:**
```
w_global^{t+1} = Σ_k (n_k / n) * w_k^{t+1}
```

Where:
- `w_global^{t+1}` = new global model
- `w_k^{t+1}` = model from client k after local training
- `n_k` = number of examples client k trained on
- `n` = total number of examples across all clients

**Simplified (equal data):**
```
w_global = average of all client models
```

**Why weight by data size:**
- A client with more data has seen more of the overall distribution
- Its model is likely more accurate
- Weighting prevents small, noisy clients from dominating

**Communication efficiency:**
- Instead of sending full models, clients can send only the difference (delta)
- `delta_k = w_k^{local} - w_global^{current}`
- Server: `w_global^{new} = w_global^{current} + average(delta_k)`

---

### Real-Life Analogy

A book club writing a shared novel.
- **Without weighting:** Each member writes one chapter. A member who read 100 books gets one vote. A member who read 2 books also gets one vote. The novel reflects inexperienced voices equally.
- **With FedAvg:** Each member's vote is weighted by how many books they have read. The experienced reader's suggestions carry more weight. The novel reflects expertise proportionally.
- **The delta:** Instead of sending their entire draft, each member only sends "I changed Chapter 3, paragraphs 2-5." The editor merges only the changes.

---

### Tiny Numeric Example

**Global model weight:** `w = 1.0`

**Client A:** 100 examples, local update: `w_A = 1.2`
**Client B:** 50 examples, local update: `w_B = 0.9`
**Client C:** 50 examples, local update: `w_C = 1.1`

**FedAvg (weighted by data size):**
```
w_global = (100/200)*1.2 + (50/200)*0.9 + (50/200)*1.1
         = 0.5*1.2 + 0.25*0.9 + 0.25*1.1
         = 0.6 + 0.225 + 0.275
         = 1.1
```

**Simple average (unweighted):**
```
w_global = (1.2 + 0.9 + 1.1) / 3 = 3.2 / 3 = 1.067
```

**FedAvg favors Client A** because it has more data and its update is more reliable.

---

### Common Confusion

1. **"FedAvg is just taking the mean of models."** Only when all clients have equal data. In practice, data sizes differ, so weighting matters.

2. **"FedAvg requires all clients to participate every round."** No. Modern variants (FedProx, SCAFFOLD) handle partial client participation.

3. **"FedAvg works perfectly with non-IID data."** No. Non-IID data causes "client drift" where local models diverge. FedProx adds a regularization term to fix this.

4. **"FedAvg is the only aggregation method."** No. Alternatives include median aggregation (robust to outliers), trimmed mean (removes extreme updates), and personalized layers (keep some layers local).

5. **"FedAvg preserves privacy by itself."** No. It keeps data local, but the averaged model can still leak information. DP is needed for formal guarantees.

---

### Where It Is Used in Our Code

`src/phase59/phase59_federated_learning.py` — We implement FedAvg with data-size weighting across 5 simulated clients, showing how the global model converges by averaging local updates.
