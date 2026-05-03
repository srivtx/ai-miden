## What Is Tool Evaluation?

---

### The Problem

You have trained your model on 500 tool-use examples. The training loss went down smoothly. The model outputs look reasonable when you glance at them. But when you test it on real queries, you discover a cascade of failures. The model picks the right tool 90% of the time but passes the city name "New York" as "New" and "York" as separate parameters. It calls the calculator with "2 + 2 * 3" and gets 8 instead of the expected 8 — wait, that is actually correct. But it calls the calculator for "Who wrote Hamlet?" and gets a syntax error. You need a rigorous evaluation framework that separates different failure modes so you know what to fix. A single accuracy number hides the truth.

---

### Definition

**Tool evaluation** is the systematic measurement of a tool-enabled model across multiple dimensions: tool selection accuracy (did it pick the right tool?), parameter extraction accuracy (did it pass valid parameters?), end-to-end task success (did the user get a correct answer?), and robustness to edge cases (empty inputs, ambiguous queries, tool errors). It replaces a single headline number with a diagnostic breakdown.

**How it works:**
```
Evaluation dimensions:

1. Tool selection accuracy:
   Test queries: 50 calculator, 50 weather, 50 search, 50 direct-answer
   Metric: % of queries where the model's first action matches the gold label
   
2. Parameter extraction accuracy:
   For calculator: is the expression a valid Python/math expression?
   For weather: is the location a non-empty string?
   For search: is the query a non-empty string?
   Metric: % of tool calls with parseable, schema-valid parameters
   
3. End-to-end task success:
   For each test query, execute the model's tool call (or direct answer)
   Compare the final response to a gold answer
   Metric: % of queries with correct final answer
   
4. Error analysis categories:
   - Wrong tool selected
   - Right tool, malformed parameters
   - Right tool, right parameters, but integration failure
   - Direct answer when tool was needed
   - Tool call when direct answer was sufficient
```

**Why this matters:**
- A model with 95% tool selection but 40% parameter extraction is unusable in production
- Error analysis tells you whether to collect more parameter-variation training data or more decision-boundary data
- End-to-end success is the only metric users care about, but it does not tell you why failures happen
- ToolBench and similar benchmarks provide standardized queries across dozens of tools

---

### Real-Life Analogy

Imagine evaluating a new medical diagnostic robot.

- **Tool selection accuracy:** Does the robot order a blood test when it should, or does it order an X-ray? This is like knowing which department to call.
- **Parameter extraction accuracy:** When ordering a blood test, does the robot specify the correct panel (CBC vs. lipid profile)? A wrong panel wastes resources and gives useless results.
- **End-to-end success:** Does the patient receive the correct diagnosis and treatment? This is the only thing that matters to the patient, but it depends on every upstream step being correct.
- **Error analysis:** If 80% of failures are wrong test panels, you know to retrain the robot on panel selection. If 80% are wrong department choices, you retrain on triage. Without separating the metrics, you would randomly collect more training data and hope something helps.

---

### Tiny Numeric Example

**Test set and results for a trained 3B model:**
```
Test set: 200 queries (50 per category)

Tool Selection Accuracy:
  Calculator queries:     48/50 = 96%
  Weather queries:        47/50 = 94%
  Search queries:         45/50 = 90%
  Direct-answer queries:  46/50 = 92%
  Overall selection:      186/200 = 93%

Parameter Extraction Accuracy (among correct tool selections):
  Calculator expressions:
    Valid and parseable:   42/48 = 87.5%
    Common errors:         missing quotes, wrong variable names
  Weather locations:
    Valid string:          46/47 = 97.9%
    Common errors:         empty string, extra punctuation
  Search queries:
    Valid string:          43/45 = 95.6%
    Common errors:         too vague ("the thing"), too long

End-to-End Task Success:
  Calculator:   41/50 = 82%  (some exprs evaluate incorrectly despite valid syntax)
  Weather:      45/50 = 90%  (mock data always returns something)
  Search:       42/50 = 84%  (search results may not contain answer)
  Direct answer: 44/50 = 88%  (base knowledge errors)
  Overall:      172/200 = 86%
```

**Diagnostic insight:**
```
The bottleneck is NOT tool selection (93%).
The bottleneck is parameter extraction for calculator (87.5%)
  and end-to-end integration for calculator (82%).

Root cause: the model sometimes generates expressions like
  "sqrt(1764" (missing parenthesis)
  or "2^3" (uses ^ instead of **)
  
Fix: add 50 more training examples with explicit parentheses
  and operator syntax variations.
```

---

### Common Confusion

1. **"High tool selection accuracy means the model is production-ready."** Not if parameter extraction is poor. A model that picks calculator 96% of the time but generates invalid expressions 30% of the time will frustrate users. All metrics must be high.

2. **"End-to-end success is the only metric that matters."** For users, yes. For developers, no. If end-to-end success is 70%, you need to know whether the problem is tool selection, parameters, or integration. Without per-dimension metrics, you cannot prioritize fixes.

3. **"ToolBench scores translate directly to real-world performance."** ToolBench tests on 16,000+ tools with simulated APIs. Real-world performance depends on API latency, error rates, and schema drift. Benchmark scores set an upper bound; reality is usually 5-15% lower.

4. **"Evaluation requires a live test environment."** For final validation, yes. But during development, you can evaluate tool selection and parameter extraction without live APIs by comparing generated text against gold annotations. Only end-to-end success needs execution.

5. **"A failed tool call is always the model's fault."** Not necessarily. The API might be down, rate-limited, or returning unexpected formats. Robust evaluation includes error-handling tests: what does the model do when the calculator returns "Error: division by zero"?

6. **"You only need to evaluate on in-distribution queries."** Out-of-distribution evaluation reveals brittleness. Test queries like "What is the weather on Mars?" (invalid location), "Calculate infinity minus 7" (edge case), and "Search for ''" (empty query) expose failure modes that in-distribution tests miss.

7. **"Tool evaluation is the same as general LLM evaluation."** General evaluation measures fluency, coherence, and factual accuracy. Tool evaluation adds structural correctness (valid JSON/XML), functional correctness (executable parameters), and decision correctness (tool vs. no tool). The methods overlap but the criteria differ.

---

### Where It Is Used in Our Code

`src/phase126/phase126_tool_concepts.py` — We implement a toy evaluation framework that scores simulated tool-use trajectories on three dimensions: tool selection correctness, parameter validity, and end-to-end answer accuracy. We generate an error breakdown showing which failure mode dominates.

`src/phase126/phase126_tool_colab.py` — We construct a held-out test set of 60 queries (20 per tool + 20 direct-answer) and evaluate the fine-tuned Qwen2.5-3B model. We report tool selection accuracy, parameter extraction accuracy, and per-category end-to-end success. We plot a confusion matrix for tool selection and analyze failure cases.
