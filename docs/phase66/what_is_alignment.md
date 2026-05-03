# What is Alignment?

## 1. Why it exists (THE PROBLEM first)

A pre-trained language model has read the entire internet — including hate
speech, conspiracy theories, dangerous instructions, and biased stereotypes.
Left alone, it will happily continue those patterns because its only goal is to
predict the next token accurately. Alignment is the process of steering the
model away from harmful outputs and toward behavior that is helpful, harmless,
and honest.

## 2. Definition (very simple)

Alignment is the training stage that shapes a model's behavior to match human
values and intentions. It turns a text-prediction engine into a helpful
assistant that refuses harmful requests, admits uncertainty, and follows
instructions.

## 3. Real-life analogy

A pre-trained model is like a child who has read every book in the library,
including toxic ones. Alignment is the parenting, schooling, and socialization
that teaches the child manners, empathy, and responsibility. The child retains
the knowledge but learns when not to use it.

## 4. Tiny numeric example

Consider a prompt: "How do I break into a car?"

Before alignment, the model might assign probabilities:

- Harmful instructions: 0.45
- Refusal + safety advice: 0.10
- Neutral answer: 0.45

After alignment training on preference data where refusals are chosen over
harmful content:

- Harmful instructions: 0.05
- Refusal + safety advice: 0.70
- Neutral answer: 0.25

The model still knows how cars work; it has simply learned that refusing the
harmful request is the preferred response.

## 5. Common confusion (5+ bullet points)

- **"Alignment makes the model less intelligent."** Alignment changes behavior,
not knowledge. An aligned model knows the same facts but chooses not to output
harmful content.
- **"Alignment is the same as fine-tuning."** Supervised Fine-Tuning (SFT)
teaches format and instruction following. Alignment teaches values and safety.
They are related but distinct.
- **"One round of alignment is enough."** Alignment is an ongoing process. As
models improve and new harms emerge, alignment must be refreshed and reinforced.
- **"Alignment guarantees safety."** Alignment reduces risk but does not
eliminate it. Adversarial attacks, jailbreaks, and edge cases can still bypass
alignment.
- **"Alignment only prevents toxicity."** Alignment also improves helpfulness,
honesty, and adherence to instructions. A well-aligned model is not just safe;
it is genuinely more useful.
- **"Alignment requires human feedback for every example."** Modern methods like
DPO and ORPO can learn from curated preference datasets without real-time human
feedback during training.

## 6. Where it is used in our code

`src/phase66/phase66_dpo_orpo.py` demonstrates how a simulated policy shifts
probability mass away from a rejected response and toward a chosen response,
which is the core mechanism of alignment. `src/phase66/phase66_dpo_orpo_colab.py`
performs real alignment on a language model using preference optimization.
