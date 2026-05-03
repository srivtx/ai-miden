## What Is Code Review?

---

## The Problem

A researcher spends three months training a large language model. The final result is remarkable: the model outperforms every baseline on the benchmark. The team submits to a top conference. During the camera-ready phase, a colleague casually reads the training script and notices that the validation loss is computed using the training set because of a variable reuse bug: `val_loss = compute_loss(train_loader)` instead of `val_loss = compute_loss(val_loader)`. The entire paper is based on an illusion. The model was overfitting all along. One hour of careful code review could have prevented a retraction, months of wasted work, and public embarrassment.

---

## Definition

**Code review** is a systematic examination of source code by peers. Reviewers check for correctness, readability, test coverage, and alignment with project standards. It is a social process that uses multiple human perspectives to catch errors that compilers, linters, and unit tests miss.

**How it works:**
```
Author:        writes a feature or fix, opens a pull request
Reviewer:      reads the diff, asks questions, points out issues
Discussion:    author and reviewer debate trade-offs, propose alternatives
Revision:      author addresses feedback, pushes updates
Approval:      reviewer accepts the change, code is merged
```

**Key techniques:**
- **Line-by-line review:** reading every changed line, not just the summary.
- **Scenario testing:** mentally simulating edge cases like empty inputs, division by zero, or off-by-one errors.
- **Standard enforcement:** checking naming conventions, docstring completeness, and type hint consistency.
- **Architectural review:** questioning whether the change fits the overall design or introduces unnecessary coupling.

**Why this matters:**
- A single off-by-one error in a data loader can invalidate an entire research project.
- Reviews spread knowledge: the reviewer learns the codebase, and the author learns better patterns.
- Reviews enforce consistency, making the codebase maintainable long after the original author has moved on.

---

## Real-Life Analogy

Code review is like the pre-flight checklist used by airline pilots before every takeoff. The captain knows the aircraft intimately; they have flown this route a hundred times. But the co-pilot reads the checklist aloud anyway: flaps set, fuel checked, weather reviewed, altimeter calibrated. The captain confirms each item. This ritual seems redundant to an outsider, but it catches anomalies like a fuel cap left open by the ground crew or a navigation system set to the wrong coordinate system.

**The trade-off:** The checklist adds ten minutes to every departure. Over a year, that is hundreds of hours of lost time. But one caught anomaly prevents a crash that costs lives and hundreds of millions of dollars. In research code, the stakes are rarely life-and-death, but the principle is identical: a small time investment in review prevents catastrophic errors in publication, deployment, and reputation. The cost of review is linear; the cost of a missed bug is exponential.

**The nuance:** A checklist is only as good as the person reading it. A bored co-pilot who mumbles "check" without looking will miss the open fuel cap. Similarly, a reviewer who approves a 5,000-line pull request in thirty seconds is performing theater, not review. Effective review requires focus, domain knowledge, and the psychological safety to say "I do not understand this line."

---

## Tiny Numeric Example

**Bug detection rates before and after instituting mandatory code review:**

| Stage | Bugs per 100 Lines | Detection Rate | Cost to Fix |
|---|---|---|---|
| No review | 3.2 | 40% (by tests) | $50 (production) |
| Casual review | 1.8 | 65% | $30 |
| Structured review | 0.4 | 92% | $5 (pre-merge) |

**Time investment:**
```
Average PR size:          150 lines of code
Review time per PR:       45 minutes
Author revision time:     20 minutes
Total overhead per PR:    65 minutes
Bugs caught per 10 PRs:   ~4.8
Time saved per bug caught early:  ~4 hours
Net time saved per 10 PRs:  4.8 × 4h - 10 × 1.08h = 8.4 hours
```

**Research-specific example:**
```
Before review:  validation accuracy reported as 94.2%
After review:   reviewer notices train/val split bug
Corrected validation accuracy: 89.7%
Impact:         paper conclusion changes from "state of the art" to "modest improvement"
```

**The shift:** Code review moves quality assurance from the end of the pipeline to the middle. Bugs cost 10x less to fix when caught in review than when caught in production or peer review.

---

## Common Confusion

1. **"Code review is a substitute for automated testing."** Tests verify behavior against specifications; reviews verify that the human-readable code makes sense, is maintainable, and contains no obvious logic errors. They are complementary, not interchangeable.

2. **"The senior developer should review everything."** Junior reviewers catch different bugs because they are not blinded by familiarity. A senior developer might skip over a dense regular expression they have seen a hundred times; a junior reviewer will ask what it does and expose a bug.

3. **"Code review is about finding style violations."** Style is the shallowest layer of review. The deepest value comes from catching logical errors, design flaws, and missing test cases.

4. **"A approved review guarantees correctness."** Reviewers are human. They miss things. Approval means "I have done my due diligence," not "this code is provably bug-free."

5. **"Review should focus only on the changed lines."** A change in one function might break an invariant in a distant module. Good reviewers read the surrounding context, not just the diff.

6. **"Code review slows down the team too much."** In the short term, yes. In the long term, review reduces rework, prevents outages, and trains junior developers, increasing overall velocity.

7. **"Research code does not need review because it is throwaway."** Most "throwaway" research code becomes the foundation of a paper, a product, or a thesis. The cost of reviewing it is negligible compared to the cost of retracting a paper or debugging a production model.

---

## Where It Is Used in Our Code

`src/phase95/phase95_research_communication.py` — We present a deliberately buggy training script with poor variable naming and a hidden train/validation split error. We then simulate a peer-review refactor that renames variables, adds docstrings, and fixes the bug. We compare the before and after readability scores and plot the bug-detection rate across review rounds so you can see how structured review improves both correctness and maintainability.
