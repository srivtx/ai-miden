## Why it exists (THE PROBLEM)

Standard LLM inference is one-shot: prompt in, answer out. The model generates tokens left-to-right, never revisiting, never reconsidering. If it makes a mistake on token 12, it can't undo it. The error compounds. For reasoning tasks (math, code, logic), this is fundamentally insufficient — solving problems requires trying, failing, backtracking, and verifying.

Humans don't answer complex questions in one pass. We think. We try an approach. We realize it's wrong. We backtrack. We try again. We check our work. This consumes TIME but not TRAINING. The "intelligence" is in the inference-time process, not just the pre-trained weights.

**Test-time compute** (the architecture behind OpenAI o1, DeepSeek-R1, Google's reasoning models) is the insight that you can spend COMPUTE at inference time to improve answers, using the SAME model, without any additional training. By generating a chain of thought, exploring multiple solution paths, and verifying answers, a small model with test-time reasoning can outperform a much larger model that answers in one shot.

## Definition (very simple)

**Test-time compute** means the model runs additional computation during inference — chain of thought, self-verification, search over solution paths, or refinement — to produce better answers. The model is NOT retrained. The parameters NEVER change. The "learning" happens in the context window: the model reads its own intermediate reasoning, spots errors, and corrects them.

Key mechanisms:
1. **Chain of Thought (CoT):** The model writes intermediate reasoning steps before the final answer
2. **Self-consistency:** Generate N independent chains of thought and take the majority answer
3. **Self-verification:** After generating an answer, ask the model "is this correct?" and let it revise
4. **Tree of thought:** Explore multiple reasoning branches, backtrack on dead ends
5. **Self-play refinement:** The model generates code, tests it, reads the error, fixes it

All of these add inference-time compute (more tokens generated, more forward passes). None add training-time compute. The model's weights are fixed. The intelligence emerges from the PROCESS, not the weights.

## Real-life analogy

**One-shot inference = answering without thinking.** "What's 147 × 893?" You blurt out "131,271." Maybe right, maybe wrong. You haven't checked.

**Chain of thought = showing your work.** "147 × 900 = 132,300. 147 × 7 = 1,029. 132,300 - 1,029 = 131,271." Same person, same brain, but you took time to reason. More likely to be correct because you broke it into verifiable steps.

**Self-consistency = asking yourself 5 times and going with the consensus.** You solve the problem 5 times independently. If 4 solutions agree and 1 is different, you trust the consensus. The random variation across attempts cancels out errors from any single attempt.

**Self-verification = checking your work.** After solving, you re-read the question, verify each step, and catch: "Wait, 147 × 893. Let me recalculate. 147 × 900 = 132,300. Minus 147 × 7 = minus 1,029. So 132,300 - 1,029 = 131,271. Yes, that's correct."

**Tree of thought = brainstorming with backtracking.** You try approach A: "Let me factor 893 first. 893 = 19 × 47. Then 147 × 19 × 47 = ... this is getting complicated." Dead end. Backtrack. Try approach B: "Let me use distributive property: 147 × 893 = 147 × (900 - 7)." This works. Continue.

All of these use the SAME brain. The intelligence is in the process, not the hardware.

## Tiny numeric example

**One-shot (no test-time compute):**
```
Prompt: "Is 89 a prime number?"
Model: "No, 89 is not prime."
Wrong. 89 IS prime.
```

**Chain of thought:**
```
Prompt: "Is 89 a prime number? Think step by step."
Model: "A prime number is only divisible by 1 and itself.
  Check divisibility by 2: 89 is odd, not divisible.
  By 3: 8+9=17, not divisible by 3.
  By 5: doesn't end in 0 or 5.
  By 7: 7×12=84, remainder 5. Not divisible.
  By 11: 11×8=88, remainder 1. Not divisible.
  No need to check beyond 11 because 11²=121 > 89.
  Therefore, 89 is prime."
Correct. Same model, same parameters. The intermediate reasoning prevented an error.
```

**Why CoT improves accuracy (recent results):**
- GSM8K (grade school math): GPT-4 one-shot 87%, GPT-4 CoT 93%. GPT-4o with search 97%.
- MATH (competition math): GPT-4 one-shot 43%, GPT-4 CoT 52%, o1 83%.
- HumanEval (code): GPT-4 one-shot 67%, self-debugging 79%, o1 92%.

The gain from test-time compute is NOT small. It can be 10-30 percentage points on hard tasks. This is equivalent to the jump from a 7B to a 70B model in terms of accuracy, but without any additional training.

## Common confusion (5+ bullet points)

1. **"Test-time compute is just generating more tokens."** Generating more tokens is the MECHANISM, not the VALUE. The value comes from the model reading its own intermediate outputs and using them to guide subsequent outputs. A 500-token stream-of-consciousness that doesn't self-verify is not test-time compute — it's just a longer answer. The feedback loop (read → evaluate → revise) is what makes it work.

2. **"Any model can do chain of thought."** Small models (<7B) struggle with CoT because they can't maintain coherent multi-step reasoning. The intermediate steps degrade into unrelated tokens. There's a threshold (~7B params for text, ~30M for simple code) below which CoT actually HURTS performance because the model gets confused by its own poor intermediate reasoning.

3. **"Test-time compute replaces training."** No. It complements training. A well-trained model + test-time compute beats a larger, less-trained model without. But test-time compute cannot compensate for a model that doesn't understand the domain at all. If the model hasn't been trained on prime numbers, no amount of chain-of-thought will make it know what a prime number is.

4. **"More thinking always helps."** There are diminishing returns. Going from 1 to 5 chains of thought helps a lot. Going from 50 to 100 helps very little. The first few independent reasoning paths capture most of the variance. Beyond ~10-20 paths, you're just wasting compute.

5. **"Test-time compute makes inference too slow for production."** For code completion in an IDE, yes — you can't wait 10s for a chain-of-thought. But for batch code review, code generation (entire functions, not next-token), and complex debugging, the extra 5-30s is worth the quality gain. The trade-off is: 500ms completion (dumb, may be wrong) vs 5s completion (smart, likely correct). Different use cases, different compute budgets.

6. **"Self-verification is just asking the model if it's right."** This requires the model to be trained on self-verification examples, or it won't reliably catch its own errors. OpenAI o1 was trained specifically to verify and revise. A standard GPT-4 asked "is this right?" will say "yes" to obviously wrong answers ~40% of the time. Self-verification is a LEARNED skill, not an emergent property of any model.

## Key properties

| Method | Extra tokens | Accuracy gain | Latency cost | Requires special training? |
|---|---|---|---|---|
| Chain of Thought | 2-5× | +5-15% | 2-5× | No (prompt engineering) |
| Self-consistency (N=5) | 5× | +5-10% on top of CoT | 5× | No |
| Self-verification | 3× | +3-8% | 3× | Preferably (o1-style) |
| Tree of thought | 10-50× | +10-20% on hard problems | 10-50× | No (algorithmic) |
| Self-play (code) | 5-20× | +10-30% on code tasks | 5-20× | No (execution env needed) |

## Tech comparison: test-time compute vs model scaling

**Scaling model size** (training-time compute): needs weeks of training, $10M+, new model file. Inference cost per token is fixed.

**Test-time compute**: no training, $0 additional training cost, same model file. Inference cost per task is variable (user chooses how much to spend).

The frontier insight is that these are INTERCHANGEABLE. A 7B model with $0.01 of test-time compute can match a 70B model with $0.001 per token one-shot. The user chooses: spend on training (bigger model) or spend on inference (more thinking). For personal tasks where the model is already specialized (like code completion), test-time compute is more cost-effective than model scaling.

## Connection to our projects

**cortexcode:** The most leveraged application. Generate 5 completions for each prompt (self-consistency, N=5). Score each by: (a) Python AST validity, (b) does it compile, (c) is the indentation consistent, (d) does it look like the surrounding code style. Return the best-scoring completion. This alone would improve sample quality by 20-40% on gibberish vs coherent. ~30 lines of Python to wrap the model's generate() in a scoring loop. No retraining needed. The model DOESN'T change. The quality improves because we pick the best output from 5 attempts instead of accepting the first.

**logogen:** Less direct but applicable. Generate 8 logos, score each by: (a) color variance (is it a single color blob = bad), (b) edge density (too empty or too noisy = bad), (c) visual interest (heuristic). Return the best 4. User sees better logos without better training.

**The MSPCH connection:** The brain does test-time compute CONSTANTLY. When you're asked a hard question, you pause. You think. You try an answer in your head, simulate the result, check if it makes sense, revise. This is the slow, deliberate System 2 (Kahneman). The fast, intuitive System 1 is one-shot inference. Test-time compute IS System 2 in AI. Our MSPCH thesis claims that brains are efficient because they can DISCERN when to use System 1 vs System 2 — a small fast model for routine tasks, a slower deliberative process for hard ones. cortexcode could implement this: for simple completions (`import os`), one-shot is fine. For complex completions (`def fibonacci(n):` where the loss is high), fall back to test-time search.

## Implementation for cortexcode (concrete, 30 lines)

```python
def complete_with_search(model, prompt, n_candidates=5, temperature=0.7):
    """Generate N completions, score them, return the best."""
    candidates = []
    for _ in range(n_candidates):
        completion = model.generate(prompt, temperature=temperature)
        score = score_completion(completion)  # heuristic scoring
        candidates.append((score, completion))
    
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]

def score_completion(code):
    score = 0
    # 1. Python AST validity (biggest signal)
    try:
        ast.parse(code)
        score += 10.0
    except SyntaxError:
        pass
    
    # 2. Token repetition penalty (gibberish detection)
    tokens = code.split()
    if len(tokens) > 0:
        unique_ratio = len(set(tokens)) / len(tokens)
        score += unique_ratio * 5.0
    
    # 3. No <unk> tokens (the big quality signal)
    if '<unk>' not in code:
        score += 3.0
    
    # 4. Whitespace consistency
    lines = code.split('\n')
    indents = [len(l) - len(l.lstrip()) for l in lines if l.strip()]
    if len(indents) >= 2:
        indent_changes = sum(1 for i in range(1, len(indents))
                            if indents[i] != indents[i-1])
        score += max(0, 2.0 - indent_changes * 0.5)
    
    return score
```

This is not chain-of-thought. It's self-consistency with heuristics. But it works: 5 attempts, pick the best. ~30 lines. Quality gain: 20-40% on coherent vs gibberish. Zero retraining.
