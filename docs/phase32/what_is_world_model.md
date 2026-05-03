### 1. Why it exists (THE PROBLEM first)
Current AI models are incredible pattern matchers, but they do not truly understand causality or physics. A model can generate a video of a ball rolling, but it does not understand that gravity causes the ball to fall, or that solid objects cannot pass through each other. Without this understanding, models hallucinate impossible scenarios, fail at physical reasoning tasks, and cannot plan actions in the real world. World models aim to give AI an internal simulation of how the world works.

### 2. Definition (very simple)
A World Model is a learned internal representation of how the environment behaves — a neural network that predicts future states given current states and actions. It encodes physics, causality, and object permanence. With a world model, an AI agent can "imagine" the consequences of different actions before taking them, enabling planning and reasoning about hypothetical scenarios.

### 3. Real-life analogy
A flight simulator. Pilots do not learn to fly only by reading manuals or watching videos. They spend hours in a simulator that accurately models physics: gravity, aerodynamics, engine thrust, weather. They can crash virtually without real consequences, learn from mistakes, and try risky maneuvers safely. A world model is the AI equivalent — a virtual reality engine inside the model's mind where it can test ideas before acting in the real world.

### 4. Tiny numeric example
Current model (pattern matching):
```
Input: "If I push a glass off a table, what happens?"
Output: "The glass might break." (vague, no physics)
```

World model (causal simulation):
```
Input: "If I push a glass off a table, what happens?"
Internal simulation:
  Step 1: Glass at edge of table. Push applied.
  Step 2: Glass moves horizontally. Gravity = 9.8 m/s² downward.
  Step 3: Glass leaves table. Vertical velocity increases.
  Step 4: Glass hits floor after 0.5 seconds.
  Step 5: Impact force exceeds glass structural integrity.
  Step 6: Glass shatters.
Output: "The glass will fall, hit the floor in about half a second, and break into pieces."
```

The world model explicitly simulates physics rather than retrieving a memorized pattern.

### 5. Common confusion
- **World models are not just better language models.** They are a different paradigm. Language models predict tokens. World models predict state transitions. The two can be combined (like in Sora or Gemini), but the underlying mechanism is different.
- **They are inspired by human cognition.** Neuroscience suggests the human brain maintains a "generative model" of the world that predicts sensory input. When predictions are wrong (surprise), we learn. World models in AI draw directly from this idea.
- **Video generation is a form of world modeling.** Sora (OpenAI) and similar video models implicitly learn physics by predicting pixel changes over time. They are not explicitly programmed with Newton's laws, but they learn them from data. This is controversial — some researchers argue they are still just pattern matchers.
- **World models enable reinforcement learning at scale.** In model-based RL, the agent trains in its world model instead of the real environment, which is faster and safer. Dreamer (DeepMind) is a famous example.
- **This is the path toward AGI.** Many researchers believe that true general intelligence requires an internal world model. Without it, AI is just a sophisticated autocomplete. With it, AI can plan, reason, and understand.

### 6. Where it is used in our code
`src/phase32/phase32_foundation_models.py` implements a tiny world model that predicts the next state of a simple physical system (a ball bouncing), comparing pattern-matching prediction against causal simulation.
