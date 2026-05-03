## What Is Method Archaeology?

---

## The Problem

A paper on arXiv claims a new state-of-the-art result on CIFAR-10: 96.8% accuracy. The methods section describes the architecture, the optimizer, and the learning rate. But the result refuses to reproduce. You copy the exact architecture, use the stated optimizer, and achieve only 93.1%. The difference is not random noise; it is a systematic gap of 3.7 percentage points. You suspect the authors omitted something critical, but the paper says nothing about weight decay, warmup schedule, exact data augmentation order, or random seed handling. Without these hidden details, the published result is an unreachable mirage.

---

## Definition

**Method archaeology** is the investigative work of recovering hidden implementation details from released code, author correspondence, community forums, or careful controlled experiments. It treats the full method as an artifact that must be excavated layer by layer, because the published paper is only the visible tip of the iceberg.

**How it works:**
```
Paper claims:          96.8% accuracy
Reproduction (paper only): 93.1% accuracy (-3.7 gap)
Step 1 — inspect official code:    discover weight decay = 0.05    → 94.2%
Step 2 — email authors:            discover cosine warmup = 5 epochs → 95.5%
Step 3 — inspect augmentation:     discover RandAugment, not basic  → 96.1%
Step 4 — match random seed:        discover torch.manual_seed(42)   → 96.7%
```

**Key techniques:**
- **Code excavation:** reading the authors' official repository for defaults not mentioned in the paper.
- **Author correspondence:** asking direct questions about omitted details via email or issue trackers.
- **Controlled probing:** varying one hidden variable at a time to isolate its impact.
- **Community triangulation:** comparing multiple independent reproductions to find consistent missing details.

**Why this matters:**
- A 3.7-point gap can decide whether a method is publishable or obsolete.
- Hidden details like initialization schemes or batch-normalization momentum often dominate the advertised architectural novelty.
- Without archaeology, the scientific record contains unverifiable claims that waste follow-up research.

---

## Real-Life Analogy

Imagine you are restoring a Stradivarius violin from a partial diagram drawn in 1700. The diagram shows the graceful curves of the body and the placement of the f-holes, but it omits the thickness of the wood in the top plate, the recipe for the varnish, the exact angle of the bass bar, and the density of the sound post. These invisible details are what make the instrument sing.

**The archaeological approach:** You visit workshops that own authenticated Stradivarius instruments and measure the wood thickness with calipers. You analyze the varnish with spectroscopy to reverse-engineer the resin mixture. You interview luthiers who have restored similar instruments. Each recovered detail brings your replica closer to the original sound. But some details turn out to be red herrings: the exact tree the wood came from matters less than the graduation pattern. Method archaeology is not just collecting facts; it is weighing which hidden facts matter.

**The trade-off:** Spending three months on archaeology for a single paper might seem excessive. But if that paper is the foundation of your thesis or product, those three months prevent a year of building on sand. Conversely, some omitted details are genuinely irrelevant; the challenge is knowing when to stop digging.

---

## Tiny Numeric Example

**Reproducing a claimed validation loss of 0.234 on a synthetic regression task:**

| Step | Detail Recovered | Validation Loss | Gap from Claim |
|---|---|---|---|
| Paper only | — | 0.341 | +0.107 |
| + hidden label smoothing (0.1) | official repo | 0.251 | +0.017 |
| + cosine decay (not step decay) | author email | 0.236 | +0.002 |
| + exact augmentation seed (42) | community forum | 0.234 | 0.000 |

**Cost of each discovery:**
```
Paper-only reproduction:        2 hours to implement
Code excavation:                +1 hour reading repo
Author correspondence:          +3 days waiting for reply
Controlled probing:             +4 hours running experiments
Community triangulation:        +30 minutes reading issues
Total time to close gap:        ~4 days
```

**The shift:** The model did not change. The loss function did not change. Only the training recipe changed. Method archaeology reveals that the "method" is 30% architecture and 70% implementation details.

---

## Common Confusion

1. **"Method archaeology is the same as reverse engineering."** Reverse engineering aims to clone a black-box system for competitive or interoperable purposes; method archaeology aims to understand and document the scientific details that a paper failed to report.

2. **"If the authors released code, there is nothing left to excavate."** Released code still contains implicit defaults in library versions, environment variables, and hardware-specific behavior that are not obvious.

3. **"A failed reproduction means the paper is fraudulent."** Most gaps come from honest omission, not malice. Space-constrained papers routinely leave out learning-rate warmup and data preprocessing.

4. **"Method archaeology is only for ancient papers."** Even recent papers with code repositories hide critical details in training logs, configuration files, or undocumented hyperparameters.

5. **"Recovering one hidden detail is enough."** Performance gaps are usually caused by the interaction of several omitted details, not a single silver bullet.

6. **"Method archaeology replaces original thinking."** It complements original thinking by ensuring you build on a verified foundation rather than a rumored one.

7. **"All hidden details matter equally."** Some details move the needle by less than 0.01%; others move it by 5%. Good archaeologists prioritize the high-impact omissions.

---

## Where It Is Used in Our Code

`src/phase93/phase93_paper_reading.py` — We simulate a "published" toy algorithm with a known ground-truth training recipe. We then provide only a partial description, challenge the reader to reproduce the result, and gradually reveal hidden initialization details and schedule parameters. We measure the accuracy gap at each revelation and plot the convergence curves so you can see how omitted details dominate final performance.
