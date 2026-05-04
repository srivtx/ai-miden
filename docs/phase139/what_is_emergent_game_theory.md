## What Is Emergent Game Theory?

---

### The Problem

You train two robots to divide a pile of blocks. You give them a reward for each block they collect. You expect them to split the pile evenly. Instead, one robot learns to knock the other over at the start of every episode, collecting everything. You never programmed aggression. The robots discovered a dominant strategy that was invisible to you during design. How do strategies appear from nothing, and why are they so hard to anticipate?

---

### Definition

**Emergent Game Theory** is the study of strategies that arise naturally from multi-agent interaction rather than being explicitly coded. Agents learn to cooperate, defect, retaliate, bluff, and signal because these behaviors are reinforced by the reward landscape and the presence of other learning agents.

**How it works:**
- Agents play repeated games. The future is discounted but not ignored.
- An agent that always cooperates is exploited. An agent that always defects earns less than one that reciprocates cooperation.
- Over thousands of episodes, policies that condition on the history of play outcompete memoryless policies.
- The population converges to a stable strategy profile that resembles a game-theoretic equilibrium, but was never derived mathematically.

**Key concepts:**
- **Tit-for-tat:** Cooperate on the first move, then copy the opponent's previous move. It is nice, retaliatory, forgiving, and simple — four properties that make it robust in iterated prisoner's dilemma tournaments.
- **Zero-sum games:** One agent's gain is another's loss. These encourage conservative minimax strategies.
- **Cooperative games:** Agents can make binding agreements. These encourage Pareto-improving joint strategies.
- **Nash equilibrium:** A set of strategies where no agent can improve its payoff by unilaterally changing strategy. Multi-agent training often approximates this empirically.

**Why this matters:**
- Auction bots develop collusive strategies that regulators did not foresee.
- Diplomatic simulations reveal how small communication channels prevent escalation.
- Autonomous vehicles negotiating intersections must converge on predictable, socially optimal behaviors without a central traffic light.

---

### Real-Life Analogy

Children on a playground deciding who goes first on the slide.
- **No game theory:** The first kid pushes to the front every time. The others cry. The slide is underutilized because fights break out.
- **Emergent game theory:** After a week, the kids invent "rock-paper-scissors" without an adult teaching them. They also develop a norm: if you won last time, you go last this time. No teacher wrote this rule. It emerged because it maximized total fun and minimized bruises.
- **The unpredictability:** If you add one more child who refuses to play rock-paper-scissors, the entire social contract collapses and a new one emerges. The equilibrium is fragile and context-dependent.

---

### Tiny Numeric Example

**Iterated Prisoner's Dilemma, 20 rounds, three strategy types:**

| Strategy | Rule | Avg. own reward per round |
|---|---|---|
| Always Cooperate (AC) | Always C | 1.8 (exploited by others) |
| Always Defect (AD) | Always D | 2.8 (exploits AC, fights AD) |
| Tit-for-Tat (TFT) | First C, then copy opponent | 3.0 (cooperates with TFT, retaliates against AD) |

**Round-robin tournament (100 repetitions of 20-round games):**
```
AC vs AC:  AC gets 3.0, AC gets 3.0
AC vs AD:  AC gets 0.5, AD gets 5.0
AC vs TFT: AC gets 3.0, TFT gets 3.0
AD vs AD:  AD gets 1.0, AD gets 1.0
AD vs TFT: AD gets 2.5, TFT gets 2.0  (first round AD exploits, then TFT retaliates)
TFT vs TFT: TFT gets 3.0, TFT gets 3.0
```

**Population outcome:**
If the population starts 50% AC and 50% AD, AD initially grows because it exploits AC. But once AC is extinct, AD only meets AD and earns 1.0. If a single TFT mutant appears, it earns 3.0 against itself and 2.0 against AD, outperforming both. TFT takes over. This is emergent game theory: no one programmed reciprocity, but it dominated the population.

---

### Common Confusion

1. **"Emergent strategies are random."** They are not random; they are locally optimal responses to the learned policies of others. They are unpredictable from the designer's perspective, but highly deterministic from the agent's perspective.

2. **"If agents converge to Nash equilibrium, they must be optimal."** Nash equilibrium only means no agent wants to deviate alone. It can be socially terrible. The prisoner's dilemma Nash equilibrium is mutual defection, which is Pareto-dominated by mutual cooperation.

3. **"Zero-sum thinking applies to all multi-agent settings."** Most real-world multi-agent problems are general-sum. Self-driving cars, trading bots, and robotic rescue teams all have incentives to cooperate because the pie is not fixed.

4. **"Tit-for-tat is the best strategy in every game."** Tit-for-tat excels in iterated prisoner's dilemma with noiseless observation. In games with more than two players, imperfect information, or continuous action spaces, more complex strategies win.

5. **"You can prevent bad emergent behavior by writing rules."** Hard-coded rules are brittle. Agents find loopholes. The better approach is to shape the reward landscape so that desirable behaviors are the easiest path to high reward.

6. **"Emergent game theory only matters in competitive games."** Cooperative games also exhibit emergent conventions. Swarm robotics, language evolution, and open-ended Minecraft agents all develop shared protocols that no one designed.

7. **"Observing the final policy tells you everything about the learning process."** The path matters. Two agents might end up cooperating, but one arrived through trust and the other through fear of retaliation. The dynamics of convergence reveal robustness.

---

### Where It Is Used in Our Code

`src/phase139/phase139_multi_agent_concepts.py` — We train two agents with memory-1 policies on the iterated prisoner's dilemma. We track the probability of cooperation conditioned on the previous round's outcome. Over time, we see whether tit-for-tat-like reciprocity emerges or whether the agents collapse to mutual defection, demonstrating emergent game theory in action.
