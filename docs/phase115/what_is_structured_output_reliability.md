## What Is Structured Output Reliability?

---

### The Problem

A payment processor routes LLM-generated SQL directly into a read-only analytics database. On 99.9% of queries the model returns valid SQL, but on 0.1% it hallucinates a syntax error or an unauthorized DROP statement. At 10,000 queries per hour, that 0.1% means ten failures, three of which corrupt the pipeline. A 99.9% success rate is not enough for production infrastructure. How do you reach 99.99% or higher?

---

### Definition

**Structured Output Reliability** is the engineering discipline of ensuring that LLM-generated structured data (JSON, SQL, function calls) is syntactically and schematically correct with extremely high probability. It combines constrained decoding, temperature control, batch validation, and defensive parsing to minimize failure rates.

**How it works:**
```
Target: 99.99% valid JSON rate
Method 1: constrained decoding → eliminates syntax errors
Method 2: temperature = 0 for structured paths → reduces randomness
Method 3: batch constrained decoding → amortize mask overhead
Method 4: fallback parser + retry on failure → catch residual edge cases
Result: failure rate drops from 0.1% to less than 0.01%
```

**Key techniques:**
- Constrained decoding for syntax guarantees
- Temperature = 0 (greedy) or very low for structural tokens
- Higher temperature allowed only inside string values if creativity is needed
- Batch processing with shared FSM masks
- Fallback validation layer and automatic retry with stricter constraints

**Why this matters:**
- Financial and medical systems cannot tolerate malformed payloads
- SQL generation must be valid before execution
- SLA agreements often require 99.99% uptime, which includes downstream LLM calls
- Debugging a 0.01% failure is harder than preventing it

---

### Real-Life Analogy

Air traffic control vs. self-driving cars.
- **Unreliable structured output:** A self-driving car that correctly stops at 99.9% of red lights. At 1,000 intersections per day, it runs one red light per day. That is unacceptable for public roads. You cannot patch the car after each crash; the system must be designed to never run a red light.
- **Reliable structured output:** Air traffic control uses rigid protocols, redundant checklists, and automated collision-avoidance systems that physically prevent two planes from occupying the same airspace. The system is engineered for six-nines reliability because failure is catastrophic.
- **The trade-off:** Engineering six-nines reliability costs more in design, testing, and compute. Constrained decoding adds latency. Batch processing requires queueing. The trade-off is infrastructure cost for the certainty that a malformed response will never reach a critical system.

---

### Tiny Numeric Example

**Generation of 10,000 JSON objects:**

```
Without constraints:
  Valid JSON:    9,870 (98.70%)
  Invalid JSON:    130 (1.30%)

With constrained decoding only:
  Valid JSON:    9,998 (99.98%)
  Invalid JSON:      2 (0.02%)  ← edge cases in tokenizer

With constrained decoding + temperature=0 + batch validation:
  Valid JSON:   10,000 (100.00%)
  Invalid JSON:      0 (0.00%)
```

**Latency comparison per request (ms):**
```
Unconstrained greedy:     45 ms
Constrained (serial):     62 ms  (+38% overhead)
Constrained (batch):      48 ms  (+7% overhead)
```

---

### Common Confusion

1. **"99.9% is good enough for most use cases."** For low-volume prototypes, yes. For high-throughput production systems, 0.1% failure creates thousands of errors per day.

2. **"Temperature = 0 makes the output deterministic but still invalid without constraints."** Greedy decoding alone does not prevent invalid tokens. It only removes sampling randomness.

3. **"Batch decoding removes the need for constraints."** Batch processing improves throughput but does not change per-sample validity. Constraints are still required.

4. **"Reliability is only about syntax."** Schematic reliability also matters: correct field names, required keys, and correct types. Grammar-based generation covers both.

5. **"You can achieve reliability by fine-tuning on valid examples."** Fine-tuning improves the probability of validity but cannot guarantee it. The model can still generalize to invalid patterns.

6. **"Performance overhead makes constrained decoding impractical at scale."** Modern engines like XGrammar reduce overhead to under 10% in batch mode. The cost of a downstream failure usually exceeds the compute cost.

7. **"Validation after generation is cheaper than constrained decoding."** Post-hoc validation requires parsing, error handling, and retry loops. Constrained decoding pays a small upfront cost to avoid retries entirely.

---

### Where It Is Used in Our Code

`src/phase115/phase115_constrained_colab.py` — We generate 50 outputs with and without constrained decoding, parse them with Python's json module, and compare valid JSON rates. We also measure generation speed to show that constrained decoding overhead is modest compared to the cost of invalid outputs.
