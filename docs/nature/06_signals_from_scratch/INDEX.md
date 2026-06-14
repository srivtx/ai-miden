# Part 6: Signals from Scratch

> The brain is not a neural network. It is a *chemical* signal-processing system. Every concept in Parts 1-5 (synapse, plasticity, learning) is implemented by *specific molecules* that interact in specific ways. This part goes deep into the chemistry — from Ca²⁺ to BDNF to gene expression.

---

## The five files in this part

| File | One-line summary |
|---|---|
| `what_is_calcium_signaling.md` | The universal 2nd messenger. Ca²⁺ entry into a spine triggers LTP/LTD, vesicle release, gene expression, and cell death. |
| `what_is_cAMP_PKA.md` | The cAMP/PKA cascade. The cellular amplifier that turns a small signal (a hormone or neuromodulator) into a big cellular response. |
| `what_is_BDNF.md` | Brain-derived neurotrophic factor. The growth factor that turns *activity* into *growth* — new synapses, new dendrites, new neurons. |
| `what_is_gene_expression_in_neurons.md` | How neural activity changes which genes are expressed. The cAMP response element binding protein (CREB) is the master switch. |
| `what_is_molecular_cascade.md` | The full signal flow: ion → 2nd messenger → kinase → transcription factor → gene → protein → new synapse. |

## Reading order

1. **`what_is_calcium_signaling.md`** — Ca²⁺ is the master 2nd messenger. Everything else cascades from Ca²⁺ entry.
2. **`what_is_cAMP_PKA.md`** — The cAMP/PKA system is the amplifier. It is downstream of G-protein coupled receptors and gates plasticity.
3. **`what_is_BDNF.md`** — BDNF is the *executor*. It is released by activity, acts on TrkB receptors, and changes synapses.
4. **`what_is_gene_expression_in_neurons.md`** — Long-term plasticity requires new proteins. CREB turns activity into gene expression.
5. **`what_is_molecular_cascade.md`** — Tying it all together: the full molecular flow from spike to gene to synapse.

## The synthesis

The brain's "learning" is not a single event. It is a *cascade* of molecular events, taking place over milliseconds to days:

- **ms:** Spike → Ca²⁺ entry into spine
- **100ms - 1s:** Ca²⁺ activates CaMKII → AMPA receptor phosphorylation → more AMPA receptors on the membrane → LTP
- **seconds:** Ca²⁺ + cAMP activate PKA → phosphorylation of substrates → early-phase LTP
- **minutes:** PKA enters nucleus → phosphorylates CREB → CREB binds DNA → gene transcription begins
- **hours:** New mRNA exits nucleus → new proteins synthesized (Arc, BDNF, AMPA receptor subunits) → late-phase LTP, structural plasticity
- **days:** New synapses grow, dendrites remodel, memory consolidates

This is the *physical basis* of memory. Every time you remember something, you are re-activating this molecular cascade. Every time you forget, some part of the cascade failed. The brain is a *chemical computer* running on this molecular substrate.

## Why this matters for AI

Modern AI has none of this. Backprop is a single, synchronous, digital computation. The brain's "backprop" is a *cascade of molecular events* taking days, with multiple feedback loops, neuromodulator gating, and homeostatic regulation. The brain is *much* more robust and adaptive because of this. To build brain-like AI, you may need to incorporate some of this multi-timescale, multi-modal, neuromodulated chemistry.

## Where this leads

After Part 6, you understand the *bottom* of the brain. The next parts go up:
- Part 7: When this chemistry breaks (Alzheimer's, Parkinson's, etc.)
- Part 8: How we measure it (EEG, fMRI, patch clamp, optogenetics)
- Part 9: What this chemistry produces (consciousness, mind, self)
- Part 10: How to use this to build AI
