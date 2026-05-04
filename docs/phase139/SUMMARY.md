## Phase 139 Summary: Multi-Agent Training (Collaboration and Competition)

---

### What We Learned

1. **Multi-agent training is harder than single-agent training because the environment is non-stationary.** Every agent's update changes the reward distribution for every other agent. Convergence is not guaranteed, and oscillations are common.

2. **Self-play creates an automatic curriculum.** An agent training against a copy of itself always faces an opponent of equal skill. This scales from random play to superhuman performance without hand-designed difficulty levels.

3. **Reward structure determines whether agents cooperate or compete.** The same network architecture and learning algorithm can produce mutual cooperation (shared rewards) or mutual defection (individual rewards) depending solely on how rewards are assigned.

4. **Emergent game theory appears from repeated interaction.** Tit-for-tat, signaling, and retaliation are not programmed; they are discovered because they are locally optimal in the learned strategy landscape.

5. **Adversarial training produces robust policies by pitting an attacker against a defender.** The defender learns to guarantee a minimum performance level because it has already been exposed to the worst-case attacks a learned adversary could devise.

---

### Results

- In the NumPy prisoner's dilemma simulation, cooperative reward sharing drove cooperate-after-cooperate probabilities from 0.50 to 0.89.
- Competitive individual rewards drove the same metric down to 0.12, confirming that incentives dominate architecture.
- Jointly trained language-model agents achieved lower story perplexity than a single agent or a fixed-first-half baseline, demonstrating that coordination improves with mutual adaptation.

---

### Phase 139 Files

| File | Purpose |
|---|---|
| `docs/phase139/what_is_multi_agent_training.md` | Core concept: simultaneous training of interacting agents |
| `docs/phase139/what_is_emergent_game_theory.md` | Strategies that arise naturally from multi-agent interaction |
| `docs/phase139/what_is_adversarial_training_agents.md` | Zero-sum minimax dynamics for robust policy learning |
| `src/phase139/phase139_multi_agent_concepts.py` | NumPy simulation of IPD with policy-gradient training |
| `src/phase139/phase139_multi_agent_colab.py` | Cooperative story generation with two real Qwen models (Colab T4) |

---

### Connects To

- **Phase 24 (RLHF):** Policy-gradient methods from single-agent RL extend to multi-agent REINFORCE.
- **Phase 67 (Jailbreaks):** Adversarial agent training shares mechanics with red-teaming language models.
- **Phase 128 (Safety):** Multi-agent negotiation and constitutional AI both rely on emergent conventions.
- **Phase 140 (NAS):** Searching over agent architectures is an extension of searching over model architectures.

---

### What You Should Remember

> **Agents do what you reward, not what you want.** If you reward individual victory, agents will betray each other. If you reward team success, agents will discover cooperation. The architecture only determines what is learnable; the reward function determines what is learned.

---

### Navigation

- **Previous:** Phase 138 (see curriculum)
- **Next:** Phase 140: Neural Architecture Search for LLMs

