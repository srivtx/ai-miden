# Phase 118 Summary: Native Multimodal Architectures (Early Fusion)

## What We Learned

1. **Early fusion processes images and text in the same embedding space from layer one.** Unlike late-fusion models that bolt a vision encoder onto an LLM, native models use a single transformer for both modalities.
2. **Image tokenization converts visual patches into discrete tokens via VQ-VAE.** This allows images to live in the same sequence as text and share the next-token prediction objective.
3. **Interleaved pretraining mixes text and images in one long sequence.** It teaches models to reason about images in context, refer back to figures, and generate multimodal documents.
4. **These three components form the foundation of native multimodal reasoning:** tokenize images, fuse them early, and train on real interleaved documents.
5. **Late fusion remains practical and dominant**, but early fusion offers a path to true cross-modal reasoning and interleaved generation.

## Prerequisites

- Phase 15: Transformers and Self-Attention (attention mechanisms)
- Phase 45: Vision Transformers (patch embedding and image encoding)
- Phase 50: Evaluating Language Models (multimodal benchmarks)

## Recommended Reading Order

1. `what_is_early_fusion.md` — The architectural difference between late and native multimodal models
2. `what_is_image_tokenization.md` — How images become discrete tokens
3. `what_is_interleaved_pretraining.md` — Why document-level mixed sequences scale better than paired data
4. `SUMMARY.md` — Phase recap and curriculum connections

## Visual Outputs

- `src/phase118/original_vs_tokenized.png` — A tiny 8x8 image next to its VQ-VAE reconstruction.
- `src/phase118/token_sequence.png` — A bar plot showing text and image tokens interleaved in a single sequence.
- `src/phase118/attention_heatmap.png` — Simulated attention weights between text and image tokens in an early-fusion layer.

## Navigation

- **Previous:** [Phase 117: Data Mixing Laws and Curriculum Learning](../phase117/SUMMARY.md)
- **Next:** Phase 119 (see curriculum)
