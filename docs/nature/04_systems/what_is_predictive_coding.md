# What Is Predictive Coding?

**The Problem:** Neuroscience has identified many mechanisms — sensory hierarchies, attention, reward, sleep, plasticity rules. Is there a *unifying principle* that ties them all together? In 1999, Rajesh Rao and Dana Ballard published a paper that has become one of the most influential ideas in computational neuroscience: the brain is a *prediction machine*, and most of its activity is the generation, comparison, and refinement of predictions. This idea, called *predictive coding*, has now expanded into a general theory of brain function (Karl Friston) and inspired new AI architectures.

**Definition:** *Predictive coding* is a theory of brain function in which the brain is constantly generating top-down predictions about incoming sensory input, and processing the *difference* between predictions and reality (the *prediction error*). Higher cortical areas send predictions down; lower areas send errors up. The goal is to minimize prediction error — to better predict the world.

**How It Works (Step-by-Step):**

1. **The original insight (Helmholtz, 1860).** Hermann von Helmholtz proposed that perception is *unconscious inference* — the brain uses prior knowledge to interpret ambiguous sensory data. When you see a room, you don't see "raw pixels." You see *objects*, *depth*, *lighting*, *people* — all inferred from incomplete data.

2. **Rao & Ballard (1999).** They modeled V1 as a hierarchical predictive coding network:
   - Each level of the hierarchy predicts the level below.
   - The difference between the prediction and the actual input is the *prediction error*.
   - Errors propagate *up* the hierarchy.
   - Predictions propagate *down* the hierarchy.
   - The network minimizes prediction error by adjusting predictions.
   - They showed this model reproduces known V1 receptive fields (orientation selectivity, end-stopping, extra-classical receptive field effects).

3. **The Free Energy Principle (Friston, 2005, 2010).** Karl Friston proposed a more general mathematical framework: the brain minimizes *variational free energy*, a quantity that bounds the surprise of sensory input. Minimizing free energy = minimizing prediction error = satisfying prior expectations about the world. This is mathematically related to variational Bayesian inference.

4. **Active inference.** A corollary: the brain doesn't just *perceive* — it *acts* to fulfill its predictions. If you predict "I will be holding a cup," your motor system acts to fulfill that prediction. Behavior is a way of *making the world conform to predictions* rather than just passively perceiving it. This is *active inference* (Friston et al., 2010).

5. **The cortical microcircuit as predictive coding.** Bastos et al. (2012) proposed a canonical microcircuit:
   - **Superficial layers (L2/3):** Contain *error neurons* (sparse, respond to unexpected inputs).
   - **Deep layers (L5/6):** Contain *prediction neurons* (dense, send predictions down).
   - **Precision neurons** (interneurons) modulate the gain of error neurons.
   - This microcircuit, repeated across cortex, implements a hierarchical predictive coding network.

6. **Predictive coding explains many findings:**
   - **Mismatch negativity (MMN):** A specific brain response to unexpected sounds, peaking at ~100-250 ms. Predictive coding says this is the prediction error signal.
   - **Repetition suppression:** Neurons respond less to repeated stimuli. Predictive coding says: the prediction is now accurate, so the error is small, so the response is reduced.
   - **Illusory contours:** V2 neurons respond to illusory (subjective) contours. Predictive coding says: the brain "completes" contours based on prior expectations.
   - **End-stopping:** V1 neurons stop responding when a bar extends beyond the receptive field. Predictive coding says: the brain predicts the extension; the actual input matches, so the error is small.
   - **Binocular rivalry:** When different images are presented to each eye, perception alternates. Predictive coding says: the brain commits to one interpretation; the other eye's input is "explained away" as prediction error.

7. **Attention as precision.** In predictive coding, attention is not a separate process — it is the *precision* (inverse variance) of prediction errors for the attended input. When you attend to a stimulus, the brain "trusts" the prediction error more, weighting it more strongly in updating. This is mathematically a gain modulation.

8. **Hierarchical message passing.** Predictive coding is fundamentally about *passing messages* between levels:
   - **Top-down (predictions):** From higher cortex to lower. Predictions about what should be there.
   - **Bottom-up (errors):** From lower to higher cortex. Surprises that need to be explained.
   - Both messages can be implemented by the *same kind of neuron* (a "prediction unit" and an "error unit" that share connections).
   - Modern implementations (Whittington & Bogacz, 2019; Millidge, Salvatori et al., 2022) show this can be implemented with biologically-plausible, *local* learning rules.

9. **Predictive coding as a learning rule.** Predictive coding networks can be trained by a *local* Hebbian-like rule:
   - Δw = η · error · prediction
   - This is *exactly* the Hebbian rule (pre × post), but with "pre" being the prediction and "post" being the error.
   - This means predictive coding can be implemented by *the same kind of local plasticity* the brain already uses — no need for backprop.

10. **Predictive coding vs. backprop.** Backprop requires:
    - Symmetric weight matrices (used in forward and backward pass)
    - A global error signal (the loss)
    - Sequential backward updates (not parallel)
    - All biologically implausible.
    Predictive coding replaces these with:
    - Separate forward and backward weights (more biologically plausible)
    - Local error signals at each level (no global loss)
    - Parallel updates (more brain-like)
    - Modern work (Millidge, Salvatori et al., 2022) shows predictive coding networks can match backprop on MNIST, CIFAR, and other benchmarks.

11. **Predictive coding and other brain systems.**
    - **Sleep:** During sleep, the brain may "replay" predictions to consolidate them.
    - **Reward:** The dopamine system may be one of several "precision weighting" signals. High dopamine = high precision on the prediction error.
    - **Attention:** Attention *is* precision in predictive coding.
    - **Action:** Active inference — actions are chosen to fulfill predictions.
    - **Memory:** Hippocampal replay may be the brain "training" its predictive models on past experience.

**Real-life analogy:** A weather forecaster. The forecaster (cortex) generates predictions about tomorrow's weather (top-down predictions). The actual weather (sensory input) is compared to the prediction. The *difference* (prediction error) is the *surprise* — the cases where the forecast was wrong. The forecaster updates her model to reduce future errors. Some predictions are more confident (high precision) — e.g., "it will be warm in summer." Others are less confident — "it might rain next week." The brain is a forecaster, not a passive receiver.

**Tiny numeric example:** In a predictive coding model of V1:
- L1 (input) sends 32×32 pixel image to L2.
- L2 generates a prediction of the input based on its current internal state.
- L1 error units compute the difference between prediction and actual input.
- Errors propagate up to L2.
- L2 updates its prediction to minimize errors.
- L2's prediction propagates back down to L1.
- This continues for several iterations (~10-50) until errors are small.
- The process is *iterative* — not a single forward pass like a CNN.
- In humans, the iterative process takes ~150-300 ms — the time it takes to perceive a complex visual scene.

**Common confusion:**

- No. "Predictive coding is just backprop with extra steps." No. Predictive coding is a *biologically plausible* alternative to backprop. They share mathematical structure but differ in implementation.
- No. "Predictive coding requires a 'world model'." Yes, the brain learns a world model through predictive coding. But the model is implicit — distributed across the weights of the network.
- No. "Predictive coding is only about perception." It generalizes to action, attention, memory, and reward. Friston's "free energy principle" applies to *all* brain function.
- No. "Predictions are conscious." No. Predictions are largely unconscious. You are not aware of the predicted sensory input — you only become aware when there is a large prediction error.
- No. "Predictive coding is a complete theory of the brain." It is an influential *framework*, not a complete theory. Many details are still debated, and not all brain regions fit cleanly into the predictive coding mold.
- No. "Predictive coding makes testable predictions." It does (e.g., mismatch negativity, repetition suppression, end-stopping). But alternative theories can also explain these. The debate is ongoing.

**Key properties:**

- **Hierarchical:** Predictions and errors flow up and down a hierarchy.
- **Bidirectional:** Top-down predictions + bottom-up errors.
- **Local learning:** Updates depend on local signals only.
- **Precision-weighted:** Attention and neuromodulators set the gain of errors.
- **Active:** The brain can act to fulfill predictions (active inference).
- **Generative:** The brain has an internal model of the world.
- **Unifying:** Connects perception, action, attention, reward, memory.

**Where it appears in technology:**

- **Generative AI** (GANs, VAEs, diffusion models, JEPA) all implement some form of "internal model" that predicts (or generates) data.
- **JEPA (Joint Embedding Predictive Architecture)** (LeCun, 2022) is Meta's attempt at a predictive architecture that learns by predicting embeddings rather than pixels — much more efficient than generative models.
- **World Models** (Ha & Schmidhuber, 2018) train a generative model of the environment, then use it for planning. Direct descendant of predictive coding.
- **Dreamer** (Hafner et al., 2020) — model-based RL with a learned world model. Plans in the world model's "latent space."
- **Predictive coding networks** (Rao & Ballard 1999; Whittington & Bogacz 2019; Millidge et al. 2022) are biologically-plausible neural networks trained by a local Hebbian-like rule. They can match backprop on standard benchmarks.
- **Energy-based models** (LeCun et al., 2006) are a related framework where the network learns an energy function; predictions are the lowest-energy states.
- **Contrastive predictive coding** (van den Oord et al., 2018) is a self-supervised learning method that predicts future embeddings from past ones.

**Why this matters for AI:** Predictive coding is a *unifying* theory that explains how perception, action, attention, and learning fit together. It is also the most biologically-plausible alternative to backprop. As AI moves toward more *agentic*, *sample-efficient*, and *continual* learning, predictive-coding-inspired architectures are likely to become more important. The next generation of AI may not look like a deep feedforward network. It may look like a hierarchical, recurrent, predictive, embodied system — much closer to the brain.

**Connection to next file:** We've covered the major brain systems: vision, attention, sleep, reward, predictive coding. The final part (`05_comparison/`) brings it all together: a deep, first-principles comparison of the brain and modern AI. What is each good at? Where does each fail? What can we learn from biology that we have not yet applied to technology?
