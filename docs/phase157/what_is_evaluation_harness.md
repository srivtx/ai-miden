## What Is a Real Evaluation Harness?

**The Problem:**
Your team trained two models. Model A scores 87.3% accuracy. Model B scores 87.1% accuracy. Is A actually better? Or is the 0.2% difference just random noise? If you deploy A and it is not actually better, you wasted engineering time. If B is actually better and you miss it, you left accuracy on the table. How do you know if a difference is real?

**Definition:**
A **real evaluation harness** is a system that runs models on benchmark tasks, computes multiple metrics, and performs statistical significance testing to determine whether observed differences are genuine or due to chance.

**Real-life analogy:**
An evaluation harness is like a clinical trial for new medicines. Two groups of patients take Drug A and Drug B. Their recovery rates are 87.3% and 87.1%. The trial does not stop there. Statisticians run t-tests and bootstrap analyses to ask: "If we ran this trial 1000 times, how often would Drug A win by chance?" If the answer is "less than 5%," the difference is significant. An evaluation harness does the same for models: it measures performance and tests whether the winner is genuinely better.

**Tiny numeric example:**
Model A: 87.3% accuracy on 500 samples
Model B: 87.1% accuracy on 500 samples
Bootstrap test (1000 resamples):
- Observed difference: +0.2%
- p-value: 0.42
- 95% CI: [-1.8%, +2.1%]
Result: NOT significant. The difference is likely noise.

**Common confusion:**
- **"Higher accuracy always means a better model."** Not without significance testing. A 0.1% improvement on 100 samples is meaningless. A 0.1% improvement on 1M samples is significant.
- **"One metric is enough."** Accuracy can be misleading on imbalanced datasets. A good harness reports accuracy, precision, recall, and F1.
- **"Significance testing is only for research papers."** No. Production teams use it to decide whether to deploy a new model. It prevents deploying models that are not actually better.
- **"Bootstrap is too slow."** 1000 bootstrap samples on 1000 data points takes seconds. The cost is negligible compared to training time.
- **"A t-test works on accuracy scores."** A paired t-test works on per-sample correctness, not on aggregate accuracy. Each sample is either correct (1) or wrong (0), and you test whether Model A is correct more often than Model B.
- **"Evaluation is the last step."** It should be continuous. Every checkpoint should be evaluated. The best checkpoint is often not the last one.

**Where it appears in our code:**
`src/phase157/phase157_evaluation_harness.py` — Evaluates two models on SST-2 and MRPC, computes accuracy/F1/precision/recall, runs bootstrap significance testing (1000 samples), paired t-test, and generates a structured report.
