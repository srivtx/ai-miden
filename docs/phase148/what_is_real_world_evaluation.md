## What Is Real-World Evaluation?

---

### The Problem

A model achieves a new state-of-the-art score on MMLU. The research team celebrates. Six months later, the product team deploys it and discovers that users abandon it after two interactions. The model gives technically correct but irrelevant answers. It misunderstands context. It is slow. It contradicts itself across sessions. The benchmark score was a mirage.

Lab benchmarks measure capability under controlled conditions. Real-world evaluation measures value under messy, human conditions. The gap between the two is where products live or die.

---

### Definition

**Real-World Evaluation** is the practice of measuring model performance in production environments using metrics that reflect actual user outcomes: task completion rate, user satisfaction, latency, error escalation rates, and business impact. It answers the question "Did this model make the user's life better?" instead of "Did this model get the right answer on a test?"

**How it works:**
```
Deploy model A to 50% of users
Deploy model B to 50% of users
Measure:
  - Did users complete their task?
  - How long did it take?
  - Did they rate the interaction positively?
  - Did they escalate to a human?
  - Did they return the next day?
Choose the model that wins on user outcomes, not lab scores.
```

**Key techniques:**
- **A/B testing:** randomly assigning users to different model versions and comparing outcomes
- **Task completion rate:** measuring whether the user achieved their goal after interacting with the model
- **User satisfaction surveys:** direct feedback on helpfulness, clarity, and trust
- **Escalation rate:** how often users give up and ask for a human
- **Retention and engagement:** whether users come back, and how deeply they interact

**Why this matters:**
- A model with a lower benchmark score can deliver better user outcomes if it is faster, more concise, or better calibrated
- Lab benchmarks do not measure latency, cost, or reliability — all critical in production
- User behavior reveals failure modes that benchmarks miss: overconfidence, tone issues, and context amnesia
- Real-world evaluation is the only way to know if a model is worth its inference cost

---

### Real-Life Analogy

Crash tests versus real accident data.
- **Lab benchmark:** A car scores five stars in a controlled frontal crash test. The test is rigorous, reproducible, and standardized. Every car is tested the same way.
- **Real-world evaluation:** Insurance data shows that the same car has a 40% higher injury rate in real side-impact collisions at intersections, which the frontal test never simulated. Drivers also complain that the seatbelt alarm is so annoying that they disable it, reducing real-world safety.
- **The mismatch:** The crash test measured one thing perfectly but missed the things that actually kill people in practice. The car is safe in the lab and dangerous on the road.
- **The lesson:** Controlled tests are necessary but not sufficient. You must also look at what happens when real humans use the product in real conditions.

---

### Tiny Numeric Example

**Two models deployed to a customer support chatbot:**

```
Model X (benchmark champion):
  MMLU score:           84%
  Average response time: 4.2 seconds
  Task completion rate:  38%
  User satisfaction:     2.9/5
  Escalation to human:   52%
  Weekly retention:      11%

Model Y (practical workhorse):
  MMLU score:           68%
  Average response time: 1.1 seconds
  Task completion rate:  61%
  User satisfaction:     4.1/5
  Escalation to human:   22%
  Weekly retention:      34%
```

**Business outcome after 90 days:**
```
Model X: support costs increased 18% because users escalated to expensive
human agents. Negative reviews mentioned "slow" and "unhelpful."

Model Y: support costs decreased 31%. Users praised speed and clarity.
The lower MMLU score was irrelevant because the support domain was narrow.
```

**Correlation analysis:**
```
Correlation between MMLU and user satisfaction in this deployment: r = 0.12
Correlation between response time and user satisfaction:            r = -0.71

The benchmark that predicted success was not MMLU. It was latency.
```

---

### Common Confusion

1. **"Real-world evaluation is just a user survey."** Surveys are one input. Real-world evaluation also includes behavioral metrics: did the user complete the task, how long did they spend, did they return, did they escalate? Actions speak louder than ratings.

2. **"A/B testing is only for marketing."** A/B testing is the scientific method for production systems. It isolates the effect of the model from confounding variables like seasonality, user demographics, and product changes. Every model deployment should be an experiment.

3. **"If a model wins in the lab, it will win in production."** The correlation is weak. Production introduces latency constraints, context windows, user frustration, ambiguous queries, and integration bugs. A model that needs 10 seconds to think may be brilliant and unusable.

4. **"Real-world evaluation is too slow."** It is slower than running a benchmark, but it is faster than discovering a failure six months after deployment. Quick lab tests filter candidates; real-world tests make the final decision.

5. **"Task completion is easy to measure."** For a calculator, yes. For a therapy chatbot, "completion" is subjective. Defining the success criterion is often the hardest part of real-world evaluation. You need clear, measurable proxies for ambiguous goals.

6. **"One real-world test generalizes to all users."** A model that works for English-speaking power users in the United States may fail for non-native speakers in India. Real-world evaluation must cover your actual user distribution, not a convenient subset.

7. **"Real-world metrics are purely business metrics."** Business metrics (revenue, cost) matter, but user welfare matters too. A model that increases engagement by manipulating users is a bad model, even if the revenue graph looks good. Ethical real-world evaluation includes harm detection.

---

### Where It Is Used in Our Code

`src/phase148/phase148_evaluation_concepts.py` — We simulate a production environment where models are ranked by benchmark score, then re-ranked by real-world task completion and user satisfaction. We show the weak correlation between lab and field performance, and we identify which metrics actually predict user success.

`src/phase148/phase148_evaluation_colab.py` — We compare two real models on both benchmark perplexity and practical metrics like multi-step instruction following and simulated preference. We demonstrate that the model with better perplexity does not always deliver better user-facing outcomes, and we discuss how to weight different metrics for deployment decisions.

(End of file)
