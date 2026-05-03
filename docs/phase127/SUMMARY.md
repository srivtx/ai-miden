# Phase 127 Summary: Vision-Language Fine-tuning (LLaVA-style)

## What We Learned

1. **Vision-language fine-tuning connects a frozen vision encoder to a frozen LLM through a trainable projection layer.** The vision encoder and language model are already excellent at their jobs. The only new component is the bridge.

2. **Multimodal projection is not just dimensionality matching; it is semantic alignment.** A random matrix would map vision features to nonsense language embeddings. The projection layer must learn that "dog" in vision space corresponds to "dog" in text space.

3. **Instruction tuning for vision teaches the model to follow specific visual tasks, not just generate generic captions.** Counting, comparing, locating, and reasoning require the model to attend to specific image regions and emit precise answers.

4. **The trade-off is data cost versus generality.** High-quality multimodal instruction data is expensive to collect, but a small amount of VQA data can shift the model from captioning to grounded question answering.

## Prerequisites

- Phase 25: Attention Mechanisms (how the LLM processes tokens)
- Phase 42: Chain-of-Thought Reasoning (structured reasoning in language)
- Phase 70: Domain Adaptation (fine-tuning concepts, freezing components)

## Recommended Reading Order

1. `what_is_multimodal_projection.md` — The MLP bridge between vision and language, why it is the critical component
2. `what_is_vision_language_fine_tuning.md` — Full pipeline: vision encoder, projection, LLM, and training strategies
3. `what_is_instruction_tuning_vision.md` — How VQA and grounded instruction following differ from captioning
4. `SUMMARY.md` — Phase recap and curriculum connections

## Visual Outputs

- `src/phase127/vl_projection_alignment.png` — Training loss and held-out concept cosine similarity for the NumPy projection simulation.
- `src/phase127/vl_finetuning_results.png` — Training loss curve and VQA accuracy before/after for the real LLaVA model.

## Navigation

- **Previous:** Phase 126 (see curriculum)
- **Next:** Phase 128: Safety RLHF (Rejection Sampling + Safety Rewards)
