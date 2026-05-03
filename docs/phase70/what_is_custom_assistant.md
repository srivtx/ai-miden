## What Is a Custom Assistant?

---

### The Problem

You have built a general-purpose chatbot. It answers trivia, writes poems, and explains physics. But your hospital needs an assistant that reads radiology reports, flags critical findings, and writes discharge summaries in the hospital's exact format. Your law firm needs an assistant that drafts contracts using your firm's templates, cites the correct jurisdiction's case law, and never hallucinates statutes. Off-the-shelf models cannot do this. They do not know your data, your format, or your constraints. How do you build an assistant that is truly yours?

---

### Definition

A **Custom Assistant** is an AI system built by adapting a base model to a specific organization's needs through a pipeline of data curation, domain adaptation, task-specific fine-tuning, evaluation, and deployment. It is not a single training run — it is an iterative product development cycle.

**The full pipeline:**
```
1. Data Curation     → collect, clean, and format domain data
2. Continual PT      → teach the model domain language
3. Task SFT          → teach the model specific skills
4. Evaluation        → measure accuracy, safety, and hallucinations
5. Deployment        → serve the model with monitoring and feedback loops
```

**Why this is hard:**
- Bad data produces bad models: "garbage in, garbage out" applies tenfold to fine-tuning
- Domain adaptation without evaluation is flying blind
- Deployment without monitoring lets drift and degradation go unnoticed
- Each step depends on the previous one; you cannot skip data curation and hope fine-tuning fixes it

**Why this matters:**
- A custom legal assistant can draft contracts in 30 seconds instead of 3 hours
- A custom medical assistant can triage patients before a human doctor sees them
- A custom coding assistant knows your internal libraries and style guide

---

### Real-Life Analogy

Hiring and training a new employee for a specialized role.
- **Base model:** A recent college graduate who is smart, well-read, and articulate. They can hold a conversation about almost anything.
- **Data curation:** You give them a reading list of your company's best memos, worst failures, and industry standards. You filter out gossip and outdated policies.
- **Continual pre-training:** They spend three months reading nothing but your industry journals and internal documentation. They learn the vocabulary.
- **Task-specific fine-tuning:** You pair them with a senior mentor who reviews their work. "Write a project proposal like this one." "Summarize this meeting like that example."
- **Evaluation:** You give them a test project. You check their output for accuracy, tone, and completeness. You red-team them: "Try to get them to reveal confidential information."
- **Deployment:** You put them on real projects but monitor their work. You collect feedback from colleagues. You send them to additional training if they make mistakes.

A custom assistant is not a product you buy. It is an employee you raise.

---

### Tiny Numeric Example

**Building a coding assistant for a fintech startup:**

**Step 1 — Data curation:**
```
Raw data: 500K StackOverflow posts, 10K internal code reviews, 2K API docs
After filtering (remove low-quality, outdated, unsafe):
  Clean data: 120K posts, 8K reviews, 1.8K docs
  Deduplication removed 40% redundancy
```

**Step 2 — Continual pre-training:**
```
Base model perplexity on fintech code: 18.4
After 2B tokens of curated fintech code: 7.2
```

**Step 3 — Task SFT (code generation from docstrings):**
```
Training examples: 5,000 (docstring, implementation) pairs
Epochs: 3
Base model pass@1 on internal API tasks: 12%
Custom assistant pass@1 on internal API tasks: 61%
```

**Step 4 — Evaluation:**
```
HumanEval-style benchmark (general coding): 42% → 38% (slight drop)
Internal API benchmark (domain coding):     12% → 61% (huge gain)
Safety test (refusing to generate SQL injection): 100% pass
```

**Step 5 — Deployment:**
```
Latency: 850ms per completion
Cost: $0.003 per 1K tokens
User satisfaction: 4.2/5 (collected from 200 developers)
```

**The custom assistant is worse at general coding but 5× better at the company's specific tasks. That is the point.**

---

### Common Confusion

1. **"A custom assistant is just a fine-tuned model."** No. Fine-tuning is one step. A custom assistant includes data pipelines, evaluation suites, safety guardrails, deployment infrastructure, and feedback loops. It is a system, not a checkpoint.

2. **"You only need to train once."** Models degrade. APIs change. New regulations appear. A custom assistant needs continuous retraining, monitoring, and data refresh cycles.

3. **"Custom assistants are only for big companies."** With LoRA and open-source models, a single developer can build a useful custom assistant on a laptop. The barrier has never been lower.

4. **"Evaluation is just running a benchmark."** Benchmarks are necessary but not sufficient. Real evaluation includes human review, adversarial testing, A/B testing with users, and monitoring for drift in production.

5. **"If the base model is good, you do not need domain adaptation."** A strong base model helps, but it will never know your internal APIs, your legal precedents, or your hospital's discharge note format. Domain adaptation is essential for depth.

6. **"Custom assistants do not hallucinate."** They hallucinate less in-domain because they have better training data. But they still hallucinate. You always need verification, especially for medical and legal outputs.

7. **"The pipeline is linear: data → train → deploy."** In practice, it is a loop. Deployment reveals failure cases, which inform new data collection, which triggers retraining, which requires re-evaluation. The first deployment is version 0.1, not 1.0.

---

### Where It Is Used in Our Code

`src/phase70/phase70_domain_adaptation_colab.py` — We build a complete custom coding assistant pipeline: collecting code instruction data, applying chat templates, fine-tuning a small model with LoRA for coding tasks, evaluating on HumanEval-style prompts, and showing before/after code generation quality. This mirrors the full production workflow in a compact Colab script.
