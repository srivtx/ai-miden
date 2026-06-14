# Part 0: First Principles

> Before diving into neurons, you need four foundational concepts: **signals, information, gradients, energy**. These are the *language* the brain speaks. Every file in the rest of the curriculum uses them.

---

## The four files in this part

| File | One-line summary |
|---|---|
| `what_is_a_signal.md` | A signal is a physical quantity that varies in space and time and carries information about something else. |
| `what_is_information.md` | Information is the reduction of uncertainty. Shannon formalized it; the brain exploits it. |
| `what_is_a_gradient.md` | A gradient is the direction of steepest change. The brain does gradient descent on prediction error. |
| `what_is_thermodynamics_of_brain.md` | The brain is a hot, dissipative system. Energy and entropy are not metaphors — they are the budget. |

## Reading order

1. **Start with `what_is_a_signal.md`.** The brain is a *signal-processing* system. Every concept after this is a specific signal.
2. **Then `what_is_information.md`.** Information theory is the math of surprise. The brain minimizes surprise.
3. **Then `what_is_a_gradient.md`.** The brain implements learning as gradient descent on prediction error.
4. **Then `what_is_thermodynamics_of_brain.md`.** All this signal-processing is expensive. The brain uses 20% of your body's energy to do it.

## The synthesis

The brain is a **signal-processing, information-maximizing, gradient-following, thermodynamically-constrained** physical system. Every other concept in this curriculum is a specific instance of these four.

- Ion channels are *signals* in chemistry
- Action potentials are *digital* signals
- Synapses are *graded* signals modulated by neuromodulators
- LTP is *gradient descent* on a loss function defined by prediction error
- Sleep is *offline* information processing
- The whole brain is a *dissipative structure* (Prigogine) — it maintains its order by burning energy

## Where this leads

After Part 0, you have the *language* to read Parts 1-10. Go to Part 1.
