# What is Content Moderation?

## 1. Why it exists (THE PROBLEM)

Even a well-aligned model can slip up, and malicious users deliberately try to make it slip. Relying solely on the model's internal "morality" is like leaving a bank vault unlocked because you trust the employees. **Content moderation exists because defense in depth requires a gatekeeper that operates independently of the model itself.**

## 2. Definition

**Content moderation** is the process of filtering, classifying, and managing AI inputs and outputs to enforce safety policies and prevent the distribution of harmful content.

## 3. Real-life analogy

A nightclub has a bouncer at the door (input moderation) who checks IDs and bags, and a manager on the floor (output moderation) who intervenes if a patron gets too aggressive. The bouncer and manager are not the DJ—they are an independent layer of control. Content moderation is the bouncer-manager system for AI.

## 4. Tiny numeric example

A model receives 1,000 prompts in one hour.

| Layer | Action | Count |
|-------|--------|-------|
| Input filter (banned keywords) | Blocked | 50 |
| Input classifier (toxicity score > 0.9) | Blocked | 30 |
| Model generates response | Passed through | 920 |
| Output classifier (harm probability > 0.8) | Blocked | 15 |
| Human review queue | Flagged | 5 |
| Final user-facing responses | Delivered | 900 |

Without moderation, 100 harmful inputs/outputs would have reached users. With moderation, only 5 reached human review and 0 reached users unflagged.

## 5. Common confusion

- **"Content moderation is censorship."** No. Censorship suppresses lawful speech. Moderation enforces safety policies (e.g., no malware instructions) that are legal and ethical obligations.
- **"Moderation only happens on outputs."** No. Input moderation is equally important. Blocking a prompt that tries to jailbreak the model prevents harm before generation even starts.
- **"A single classifier is enough."** No. Classifiers have blind spots. A layered approach (keyword + semantic + human) catches more with fewer false positives.
- **"Moderation makes the model useless."** No. Well-tuned moderation blocks only policy violations. Over-moderation is a tuning problem, not a moderation problem.
- **"Automated moderation is perfect."** No. Classifiers lag behind novel attacks and can be biased. Human review and red-teaming are required to keep them current.
- **"Only big tech needs moderation."** No. Any deployed model—even a small open-source one wrapped in an API—needs moderation because *users* will probe it.

## 6. Where it is used in our code

In `src/phase69/phase69_red_teaming.py`, we simulate both an input filter and an output classifier to show how a layered moderation stack catches attacks that slip through individual layers. In `src/phase69/phase69_red_teaming_colab.py`, we implement a lightweight safety classifier to flag model outputs and demonstrate a real moderation pipeline.
