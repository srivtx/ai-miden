## What Is LLM Evaluation?

---

### The Problem

A model scores 90% on a reading comprehension benchmark. Users say it is useless. A model tops the leaderboard on a coding challenge. Engineers find it breaks on simple real-world scripts. A model gets a perfect grade on a medical exam. Doctors catch it prescribing dangerous drug interactions. What is going wrong?

The problem is that benchmarks measure what is easy to score, not what is important to users. Accuracy on multiple-choice questions does not measure whether the model is helpful, harmless, honest, or fluent. It does not measure whether a user trusts the output, whether a developer can debug it, or whether a patient should act on it. We are optimizing for the wrong target.

---

### Definition

**LLM Evaluation** is the science of measuring what language models actually do when deployed, not just what they score on standardized tests. It encompasses automated metrics, human judgments, task-completion rates, safety audits, and real-world A/B experiments. Good evaluation asks: "Is this model useful, safe, and reliable for the people who use it?"

**How it works:**
```
Lab benchmarks     →  quick, cheap, but narrow
Human evaluation   →  slow, expensive, but grounded
Task completion    →  did the user finish their goal?
Production metrics →  engagement, error rates, escalation to humans
Safety red-teaming →  adversarial probing for failure modes
```

**Key techniques:**
- **Perplexity:** measures how well the model predicts held-out text (fluency, not usefulness)
- **Human preference ratings:** humans compare two outputs and pick the better one (the gold standard for helpfulness)
- **Task-completion rate:** can the model follow a multi-step instruction to the end?
- **Harmlessness audits:** testing for toxic, biased, or dangerous outputs across demographic groups
- **Honesty checks:** measuring whether the model says "I don't know" when it should

**Why this matters:**
- A model with a lower benchmark score can be preferred by users if it is more helpful
- Benchmarks are gamed: models are trained on test data, prompts are leaked, and leaders are not always the best in production
- Real-world evaluation prevents deployment of models that are technically impressive but practically harmful
- Without good evaluation, you are flying blind

---

### Real-Life Analogy

Hiring a software engineer.
- **Benchmark score:** The candidate scores 99th percentile on a multiple-choice algorithms test. Impressive on paper.
- **Real evaluation:** You give them a real ticket: "Fix this bug where the checkout page crashes for users in Japan." They spend three hours, introduce two new bugs, and the original issue is still there.
- **The mismatch:** The algorithm test measured memory of concepts. The real task measured debugging skill, attention to detail, communication, and understanding of production constraints. The candidate was good at tests, not at the job.
- **The lesson:** A hiring process that only uses tests will hire brilliant test-takers who cannot ship software. Model evaluation that only uses benchmarks will deploy models that cannot help users.

---

### Tiny Numeric Example

**Two models evaluated on three dimensions:**

```
Model A (optimized for benchmarks):
  MMLU accuracy:        82%   ← excellent
  Human helpfulness:    3.2/5 ← mediocre
  Task completion rate: 44%   ← poor
  Harmless score:       2.8/5 ← concerning

Model B (optimized for human feedback):
  MMLU accuracy:        71%   ← good, not great
  Human helpfulness:    4.5/5 ← excellent
  Task completion rate: 78%   ← strong
  Harmless score:       4.6/5 ← safe
```

**Which model do you deploy?**
```
If you only read MMLU: Model A wins by 11 points.
If you care about users: Model B completes 34% more tasks and is rated
significantly more helpful and safe.

Real-world outcome: Model B reduces customer support tickets by 40%.
Model A increases them by 15% because users get confused by its
overconfident but unhelpful answers.
```

---

### Common Confusion

1. **"High accuracy means the model is good."** Accuracy measures correctness on a specific dataset. It does not measure whether the model is helpful, kind, honest, or reliable in open-ended conversation. A model that always answers "I don't know" has low accuracy but high trustworthiness.

2. **"Perplexity is a good proxy for intelligence."** Perplexity measures how surprised the model is by text. A model memorizing the training set has low perplexity but zero generalization. A creative model may have higher perplexity because it generates novel outputs.

3. **"Human evaluation is too subjective to be useful."** Human judgments are noisy, but they are the only ground truth for what users want. The solution is not to abandon human evaluation but to aggregate many judgments, use clear rubrics, and measure inter-annotator agreement.

4. **"Automated metrics are worthless."** They are not worthless; they are incomplete. BLEU and ROUGE correlate weakly with human quality for open-ended generation, but they are useful for machine translation. Perplexity is useful for detecting training issues. The art is knowing which metric fits which task.

5. **"One benchmark can rank all models."** No single benchmark captures all capabilities. MMLU tests knowledge. HumanEval tests coding. MT-Bench tests conversation. A model that tops one may flop another. Rankings should be multi-dimensional, not a single number.

6. **"Evaluation is a one-time step before deployment."** Evaluation is continuous. Models drift as data distributions shift. User expectations evolve. New failure modes emerge. You need ongoing monitoring, not a pre-flight check.

7. **"If a model passes safety tests, it is safe."** Safety tests probe known failure modes. Adversarial users invent new ones. Passing a red-team exercise is necessary but not sufficient. Safety is a process, not a checkbox.

---

### Where It Is Used in Our Code

`src/phase148/phase148_evaluation_concepts.py` — We simulate a model that scores well on a benchmark but performs poorly on real-world tasks. We show how different evaluation dimensions (benchmark score, task completion, user preference) produce different model rankings, and we visualize the weak correlation between lab metrics and practical utility.

`src/phase148/phase148_evaluation_colab.py` — We compare two real 3B instruction-tuned models across multiple metrics: perplexity on WikiText-2, simulated human preference, and multi-step task completion. We show that the model with lower perplexity does not always win on user-facing metrics, and we implement a contamination check that reveals when benchmark scores are inflated by training data leakage.

(End of file)
