# What is a Harm Taxonomy?

## 1. Why it exists (THE PROBLEM)

"This model is harmful" is too vague to act on. A safety engineer needs to know *what kind* of harm, *how severe* it is, and *which users* it affects. Without categories, teams waste time fixing edge cases while missing systemic risks. **Harm taxonomies exist because you cannot fix what you cannot classify.**

## 2. Definition

A **harm taxonomy** is a structured classification system that categorizes AI-generated harmful outputs by type, severity, and target.

## 3. Real-life analogy

A hospital emergency room does not just log "patient is sick." It triages by category: trauma, cardiac, respiratory, neurological. Each category triggers a different protocol, specialist, and urgency level. A harm taxonomy is the ER triage chart for AI safety incidents.

## 4. Tiny numeric example

A red-team evaluation of 500 prompts produces 80 harmful responses. Without a taxonomy, you see "80 failures." With a taxonomy, you see:

| Category | Count | Severity |
|----------|-------|----------|
| Hate speech | 25 | High |
| Self-harm instructions | 5 | Critical |
| Malware generation | 15 | Critical |
| Misinformation | 20 | Medium |
| Harassment | 10 | High |
| Sexual content | 5 | High |

Now you know the top priority is not hate speech—it is the 5 self-harm cases that need an immediate hotfix.

## 5. Common confusion

- **"Harm is subjective, so taxonomies are useless."** No. While edge cases are debatable, core categories (self-harm, child safety, malware) are universally agreed upon and legally regulated.
- **"One taxonomy fits all models."** No. A medical AI has different harm categories (diagnostic error, dosing mistakes) than a general chatbot (toxicity, bias).
- **"Taxonomies are just labels for PR."** No. They drive engineering priorities, bug tracking, and safety investment. "Fix self-harm" is an actionable ticket; "make it safer" is not.
- **"Severity is always obvious."** No. A model giving slightly wrong historical trivia is low severity. A model giving instructions to synthesize a toxin is critical. Taxonomies include severity scoring to prevent alert fatigue.
- **"Taxonomies are static."** No. New failure modes emerge (e.g., prompt injection, model exploitation) and taxonomies must evolve.
- **"If a response does not fit a taxonomy category, it is not harmful."** No. Taxonomies cover known harms. Novel harms need a catch-all category and human review.

## 6. Where it is used in our code

In `src/phase69/phase69_red_teaming.py`, we define a harm taxonomy (Hate speech, Self-harm, Malware, Misinformation, Harassment) and evaluate refusal rates *per category*. In `src/phase69/phase69_red_teaming_colab.py`, we classify red-team prompts by taxonomy category before evaluation and report per-category safety metrics.
