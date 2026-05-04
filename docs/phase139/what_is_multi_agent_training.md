## What Is Multi-Agent Training?

---

### The Problem

A single-agent reinforcement learner plays chess against a static board. It learns opening moves that exploit the environment's predictable responses. But as soon as it faces a human opponent who adapts, its policy crumbles. The real world is not a single player against nature — it is many players reacting to each other. A self-driving car must predict how other cars will react to its lane change. A trading bot must anticipate how rival bots will move prices. A negotiation AI must model what the human on the other side of the table wants. Training one agent in isolation ignores the fact that every other agent is also learning, creating a constantly shifting target.

---

### Definition

**Multi-Agent Training** is the simultaneous training of two or more agents whose policies, actions, and rewards are coupled. Each agent's optimal behavior depends on what the other agents do, and because all agents are learning, the environment is non-stationary from any single agent's perspective.

**How it works:**
```
Single-agent loop:   Agent -> Action -> Environment -> Reward -> Agent updates
Multi-agent loop:    Agent A -> Action A
                     Agent B -> Action B
                     Environment -> State' -> Reward A, Reward B
                     Agent A updates using Reward A
                     Agent B updates using Reward B
```

**Key techniques:**
- **Self-play:** An agent trains against copies of itself. Used by AlphaGo and AlphaZero. The opponent is always at the same skill level, creating a curriculum that automatically increases in difficulty.
- **Population-based training (PBT):** A population of diverse agents is maintained. Weak agents are replaced by mutated copies of strong agents. This explores many strategies in parallel.
- **Adversarial training:** One agent attacks, another defends. Both improve by exploiting each other's weaknesses.
- **Centralized training with decentralized execution (CTDE):** During training, agents can access each other's hidden states and rewards. During execution, they act using only local observations.

**Why this matters:**
- OpenAI Five mastered Dota 2 by training five agents as a team with millions of years of simulated self-play.
- Multi-agent negotiation bots learn to lie, signal, and compromise in ways never explicitly programmed.
- Robotic swarms use emergent coordination to search disaster zones without a central controller.

---

### Real-Life Analogy

Two jazz musicians improvising on stage.
- **Single-agent training:** A pianist practicing alone with a metronome. They learn tempo and scales, but they have no idea how to respond when a saxophonist suddenly changes key.
- **Multi-agent training:** The pianist and saxophonist rehearsing together for months. The pianist learns to listen for the saxophonist's breathing before a solo. The saxophonist learns to avoid clashing with the pianist's left-hand chords. Neither musician was taught these rules explicitly; they emerge from mutual adaptation.
- **The non-stationarity:** If the saxophonist takes a year off and returns with a new style, the pianist must adapt again. The target is always moving.

---

### Tiny Numeric Example

**Iterated Prisoner's Dilemma with two learning agents:**

Reward matrix per round:
```
              Agent B: Cooperate    Agent B: Defect
Agent A: C        (3, 3)              (0, 5)
Agent A: D        (5, 0)              (1, 1)
```

**Episode length:** 10 rounds.

**Scenario 1 — Shared reward (cooperation):**
Both agents receive the sum of both rewards. After 2,000 episodes of policy-gradient training:
```
Agent A cooperate probability (after mutual C): 0.91
Agent B cooperate probability (after mutual C): 0.89
Average total reward per episode: 58.2  (close to the theoretical max of 60)
```

**Scenario 2 — Individual reward (competition):**
Each agent receives only its own reward. After 2,000 episodes:
```
Agent A cooperate probability (after mutual C): 0.12
Agent B cooperate probability (after mutual C): 0.14
Average total reward per episode: 22.1  (both settle on defection, the Nash equilibrium)
```

**The shift:** The same learning algorithm, the same network size, and the same environment produced opposite behaviors because the reward structure changed. Cooperation is not a property of the algorithm; it is a property of the incentives.

---

### Common Confusion

1. **"Multi-agent training is just single-agent training repeated N times."** No. In single-agent training, the environment is stationary. In multi-agent training, every agent's update changes the environment for every other agent. This creates feedback loops, oscillations, and convergence to equilibria that no individual agent intended.

2. **"Self-play always produces superhuman agents."** Only if the game is symmetric and the state space is small enough to explore. In highly asymmetric games or real-world robotics, self-play can get stuck in loops where both agents exploit the same trivial strategy.

3. **"Cooperation emerges naturally if agents are smart enough."** Intelligence does not imply cooperation. In the prisoner's dilemma, rational agents defect. Cooperation requires either shared rewards, repeated interaction, communication channels, or explicit alignment training.

4. **"Centralized training means you train one giant network that controls all agents."** CTDE uses separate policy networks for each agent. The "centralized" part refers to the critic or training data, not the actor architecture.

5. **"Adversarial multi-agent training is the same as GANs."** GANs are a specific two-player zero-sum game in the space of distributions. Adversarial agents can have richer action spaces, partial observability, and non-zero-sum payoffs.

6. **"Emergent behaviors can be predicted from the reward function."** Usually not. Small changes in learning rate, network initialization, or exploration noise can tip a population from cooperation to defection. Emergence is inherently hard to forecast.

7. **"You need massive compute for multi-agent training."** While AlphaStar used thousands of GPUs, toy multi-agent environments with small neural networks can demonstrate the core concepts on a laptop. The physics of interaction is what matters, not parameter count.

---

### Where It Is Used in Our Code

`src/phase139/phase139_multi_agent_concepts.py` — We simulate two agents playing iterated prisoner's dilemma with memory-1 policies. We train them with REINFORCE under shared and individual reward structures, showing how cooperation or defection emerges from incentives. We plot strategy evolution and reward curves.

`src/phase139/phase139_multi_agent_colab.py` — We load two copies of a real instruction-tuned language model and train them as a cooperative storytelling team. Agent A writes the first half, Agent B writes the second half, and a pretrained evaluator scores coherence. Joint training improves coordination compared to a single agent or a fixed first half.

