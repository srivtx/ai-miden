# What Is Information?

**The Problem:** A signal varies. How do you say *how much* it varies in a meaningful way? How do you measure the "amount" of information in a signal? The brain has a precise answer — and it is the same answer Claude Shannon formalized in 1948.

**Definition:** *Information* (in the Shannon sense) is the reduction of uncertainty. It is measured in *bits*. A signal that reduces uncertainty by half (from 4 to 2 possibilities) carries 1 bit. A signal that reduces it from 8 to 1 carries 3 bits. *Entropy* is the *expected* information: the average uncertainty of a signal before you observe it.

**How It Works (Step-by-Step):**

1. **Probabilities first.** Information theory is built on probabilities. Every signal has a *distribution* over possible values. If a neuron's firing rate is uniform between 0 and 100 Hz, every rate is equally likely. If it is peaked around 5 Hz, the low rates are more likely.
2. **Entropy.** The entropy H(X) of a random variable X is the expected number of bits needed to encode a sample from X. H(X) = -Σ p(x) log₂ p(x). Maximum entropy = uniform distribution.
3. **Information = reduction of uncertainty.** When you observe a signal value x, your uncertainty drops. The amount it drops is the *information content* of that observation: I(x) = -log₂ p(x). Rare events carry more information than common ones.
4. **Conditional information (mutual information).** Two signals A and B have *mutual information* I(A;B) = H(A) - H(A|B). It measures how much knowing B reduces uncertainty about A. If A and B are independent, I(A;B) = 0.
5. **Channel capacity.** The maximum mutual information between input and output of a channel. An axon's channel capacity is ~100-300 bits/s (firing rate) or more if temporal coding is used. A chemical synapse: ~1-3 bits/release.
6. **Coding efficiency.** The actual information rate divided by the channel capacity. A neuron firing at 10 Hz carries ~3.3 bits/spike (log₂(50/1)) if rates are distributed log-normally.
7. **Bottleneck principle.** The brain has many fast channels (axons) and many slow channels (gene expression). The *bottleneck* is the slow channels — they limit how much information can be stored long-term.

**Real-life analogy:** Information is like surprise. A common event (sun rises) carries little information. A rare event (solar eclipse) carries a lot. A *bit* is "yes or no" — the smallest possible surprise. The world around you is constantly surprising you; the brain's job is to *predict* the surprise and *update* when the surprise exceeds the prediction.

**Tiny numeric example:** The English alphabet has 26 letters. If each is equally likely, each letter carries log₂(26) = 4.7 bits. But in English, "E" is much more common than "Z," so the entropy of English is closer to 1.5 bits per letter (after compression, near the Shannon limit). The brain compresses sensory input similarly: it represents natural stimuli with far fewer bits than the raw stimulus. Visual cortex, for example, receives ~10⁷ bits/s from the optic nerve but only *transmits* ~10⁴ bits/s down the ventral stream to higher areas (the "information bottleneck"). The brain's representations are *efficient codes* — they capture the structure of the world with minimum bits.

**Common confusion:**

- No. "Information = meaning." No. Shannon information is *syntactic* — it does not know what the bits mean. The brain adds *semantic* information on top of Shannon information, via predictive models, priors, and embodiment.
- No. "More bits = better." No. *Relevant* bits = better. The brain spends most of its energy *filtering out* irrelevant information (via attention, predictive coding, thalamic gating).
- No. "Entropy = disorder." In Shannon's sense, entropy is *uncertainty* — the *opposite* of information. High entropy = high uncertainty = low information. It is not the same as thermodynamic entropy (which is more about microstates).
- No. "The brain computes information." The brain *uses* information to do work. The work itself is physical. Information is a useful abstraction, not a fundamental physical quantity.
- No. "Compressed representations lose information." Yes and no. Lossless compression preserves all of it. Lossy compression throws away the irrelevant parts. The brain does *lossy* compression — it throws away the noise.
- No. "Entropy always increases." In closed systems, yes. In open systems (like the brain, which eats and breathes), local entropy can decrease — but only at the cost of increasing entropy elsewhere (the second law is preserved). This is the *dissipative structure* concept (Prigogine).

**Key properties:**

- **Quantifiable:** Information is a *number* — the reduction of uncertainty in bits.
- **Universal:** Shannon's theory applies to *any* signal — neural, electronic, genetic, social.
- **Composable:** Information from independent sources *adds*: I(A,B) = I(A) + I(B) (for independent A, B).
- **Bounded:** The channel capacity bounds how much information can flow through any medium.
- **Lossy in biology:** The brain's representations are *lossy compressions* of the world.

**Where it appears in technology:**

- **Compression:** MP3, JPEG, video codecs — all exploit Shannon's source coding theorem.
- **Channel coding:** Error-correcting codes approach the Shannon limit.
- **Machine learning:** The *information bottleneck* (Tishby) frames learning as information compression: keep only the information in the input that is relevant to the output.
- **Neural network training:** The *cross-entropy loss* is the negative log-likelihood — directly measuring "surprise" in bits.
- **LLMs:** The next-token prediction is essentially predicting the *information content* of the next token.
- **Predictive coding in the brain:** The brain minimizes the *surprise* (information content) of its sensory input. See `04_systems/what_is_predictive_coding.md`.

**Connection to next file:** Information is *what* you measure. The next concept is *how you use it to learn* — the gradient.
