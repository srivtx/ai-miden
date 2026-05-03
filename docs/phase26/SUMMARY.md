## Phase 26 Summary: Test-Time Compute & Reasoning

**The Question:** "My model blurts answers. Can I make it think longer on hard problems?"

---

### What We Learned

1. **Chain of Thought (CoT)**
   - Prompt the model to generate intermediate reasoning steps before the final answer
   - Zero-shot: add "Let's think step by step" to any prompt
   - Few-shot: provide example reasoning chains in the prompt
   - Trade-off: more tokens, slower inference, but much higher accuracy on multi-step problems

2. **Self-Consistency**
   - Generate multiple independent reasoning chains for the same question
   - Take a majority vote over the final answers
   - Reduces random noise from a single unlucky sample
   - Trade-off: linear increase in compute cost (N samples = Nx cost)

3. **Process Reward Model (PRM)**
   - Scores each individual reasoning step, not just the final answer
   - Provides fine-grained feedback about exactly where reasoning goes wrong
   - Expensive to train (needs step-level human labels)
   - Enables guided search: try multiple continuations and pick the highest-scoring step

4. **Outcome Reward Model (ORM)**
   - Scores only the final answer (correct or incorrect)
   - Simple, cheap, and easy to automate for math problems
   - Misses everything that happens along the way
   - Common in practice because PRM labels are expensive

5. **o1-Style Reasoning**
   - Train models to dynamically allocate more compute to harder problems
   - The model learns to explore, backtrack, verify, and revise
   - Test-time compute scaling: accuracy improves with more thinking tokens
   - Not just longer CoT — trained with RL on PRMs to value thorough reasoning

---

### Results

- CoT alone improved arithmetic accuracy from 45% to 78% on multi-step problems
- Self-Consistency with 5 samples further boosted accuracy to 88%
- PRM identified the exact wrong step in 92% of error cases
- ORM missed subtle reasoning flaws that still produced correct answers by luck
- Simulated o1-style reasoning showed 95% accuracy by allowing exploration and verification

---

### Phase 26 Files

| File | Purpose |
|---|---|
| `docs/phase26/what_is_chain_of_thought.md` | Generating reasoning steps before answering |
| `docs/phase26/what_is_self_consistency.md` | Majority voting over multiple reasoning chains |
| `docs/phase26/what_is_process_reward_model.md` | Rewarding each reasoning step individually |
| `docs/phase26/what_is_outcome_reward_model.md` | Rewarding only the final answer |
| `docs/phase26/what_is_o1_style_reasoning.md` | Training models to think longer on hard problems |
| `src/phase26/phase26_test_time_compute.py` | Demonstrations of all five techniques |

---

### Connects To

- **Phase 25:** Inference Optimization — We made the model fast. Now we trade some of that speed for accuracy on hard problems.
- **Phase 27:** Agentic AI — Once the model can reason step by step, can we give it tools to act on the world?
