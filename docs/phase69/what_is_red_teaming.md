# What is Red-Teaming?

## 1. Why it exists (THE PROBLEM)

AI models can generate harmful, biased, or dangerous content even when their developers never intended it. The problem is not malice—it is **emergent failure**. A model trained on internet-scale data has seen toxic, violent, and illicit content. Without deliberate probing, these failure modes stay hidden until a user, journalist, or attacker discovers them in production. Red-teaming exists because **"we hope it is safe" is not a strategy**.

## 2. Definition

**Red-teaming** is the proactive practice of adversarially probing an AI system to discover vulnerabilities, harmful outputs, and policy violations *before* deployment.

## 3. Real-life analogy

Before a new car goes on sale, test drivers intentionally crash it into walls, slam the brakes on ice, and roll it down hills. They are not trying to destroy the car—they are trying to find the breaking point so engineers can fix it before a family drives it home. Red-teaming is the crash-test for AI.

## 4. Tiny numeric example

Imagine a chatbot that answers 10,000 innocent questions perfectly. A red-team sends 100 *adversarial* prompts across 5 harm categories (20 each).

| Category | Probes | Harmful responses caught |
|----------|--------|--------------------------|
| Hate speech | 20 | 3 slip through |
| Self-harm | 20 | 1 slips through |
| Malware | 20 | 7 slip through |
| Misinformation | 20 | 0 slip through |
| Harassment | 20 | 2 slip through |

**Refusal rate = (100 - 13) / 100 = 87%**

Without red-teaming, those 13 harmful responses would have been discovered by real users.

## 5. Common confusion

- **"Red-teaming means the model is evil."** No. Red-teaming is a *defensive* exercise. The red team plays the attacker so the blue team (developers) can patch holes.
- **"If a model passes red-teaming, it is 100% safe."** No. Red-teaming improves safety but cannot prove absence of failure. It is sampling, not exhaustive proof.
- **"Red-teaming is the same as jailbreaking."** No. Jailbreaking is an attack by a malicious user. Red-teaming is an authorized, internal audit.
- **"Only security experts can red-team."** No. Diverse red teams (linguists, ethicists, domain experts) find different failure modes than pure ML engineers.
- **"Red-teaming is a one-time event before launch."** No. Models drift, fine-tuning changes behavior, and new attack strategies emerge. Red-teaming must be continuous.
- **"Red-teaming only tests the model weights."** No. It also tests the deployment pipeline: guardrails, filters, moderation APIs, and system prompts.

## 6. Where it is used in our code

In `src/phase69/phase69_red_teaming.py`, we simulate a red-team probe set across multiple harm categories and measure how many simulated "attacks" succeed versus how many are refused. In `src/phase69/phase69_red_teaming_colab.py`, we run a real red-team evaluation against an open-source model, compute refusal rates per category, and generate a safety report.
