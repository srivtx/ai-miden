# What is a Safety Benchmark?

## 1. Why it exists (THE PROBLEM)

Without standardized measurement, safety is just a feeling. One team says their model is "safe" because it refused 50 toxic prompts they tried. Another team says theirs is "safer" because it refused 500. But what exactly were those prompts? How severe was the harm? Were they adversarial or obvious? **Safety benchmarks exist because "we tested it" means nothing without a shared, reproducible ruler.**

## 2. Definition

A **safety benchmark** is a standardized dataset and evaluation protocol used to measure how well an AI model resists generating harmful, biased, or policy-violating outputs.

## 3. Real-life analogy

A car manufacturer claims their vehicle is "fuel efficient." Without the EPA test cycle—a standardized route, speed profile, and measurement protocol—that claim is meaningless marketing. Safety benchmarks are the EPA mileage test for AI safety.

## 4. Tiny numeric example

Consider a model tested on two benchmarks:

| Benchmark | Prompts | Harmful outputs | Score |
|-----------|---------|-----------------|-------|
| MHJ (Manual Harmful Jailbreaks) | 100 | 15 | **85% safe** |
| AdvBench (Adversarial) | 200 | 60 | **70% safe** |

If you only reported the MHJ score, the model looks great. If you only reported AdvBench, it looks risky. Benchmarks force you to report *both*.

## 5. Common confusion

- **"A high benchmark score means the model is completely safe."** No. Benchmarks are samples. A model can score 99% on a benchmark and still fail on a novel real-world prompt.
- **"All safety benchmarks measure the same thing."** No. MHJ tests manual jailbreaks, AdvBench tests adversarial suffixes, HarmBench tests diverse automated attacks, and LLM Guardrails tests moderation API coverage. They probe different holes.
- **"Benchmarks are just datasets."** No. They include evaluation protocols: how you prompt the model, how you judge harm (human labeler? classifier?), and what refusal counts as success.
- **"Open-source benchmarks help attackers."** No. The attack strategies are already public knowledge. Keeping benchmarks secret hurts defenders more than it hurts attackers.
- **"If a model beats the current SOTA on a safety benchmark, it is the safest model."** No. Benchmarks can be gamed. A model might over-refuse (become useless) to score high.
- **"Benchmarks replace red-teaming."** No. Benchmarks are the *ruler*; red-teaming is the *craft*. You need both: standardized measurement and creative adversarial thinking.

## 6. Where it is used in our code

In `src/phase69/phase69_red_teaming.py`, we construct a synthetic benchmark (probe sets across categories) and compute a standardized refusal-rate score. In `src/phase69/phase69_red_teaming_colab.py`, we evaluate against real harm-category prompts and report per-benchmark-category metrics.
