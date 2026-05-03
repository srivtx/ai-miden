← [Previous: Phase 72: Real Agents with Tool Use](docs/phase72/SUMMARY.md) | [Next: Phase 74: Recommendation Systems](docs/phase74/SUMMARY.md) →

---

# Phase 73: Speech & Audio — Summary

Phase 73 closes the sensory gap: computers can now hear and speak.  Students learn that audio is not magic—it is just a high-frequency sequence that must be transformed into compact features before a neural network can understand it.

1. **Audio Feature Extraction** — Raw waveforms are too large and noisy.  STFT, mel-filterbanks, and MFCCs compress sound into perceptual representations.
2. **ASR** — Automatic Speech Recognition converts those features into text.  CTC provides a way to align variable-length audio to variable-length text without forced segmentation.
3. **TTS** — Text-to-Speech runs the pipeline in reverse: text -> phonemes -> spectrogram -> vocoder -> waveform.
4. **Speech Transformer** — Self-attention applied to audio (wav2vec, Whisper) enables parallel processing of long utterances, replacing slow recurrent loops.

The NumPy demo (`src/phase73/phase73_speech_audio.py`) builds every transform from scratch—sine wave generation, Hann-windowed STFT, triangular mel filters, DCT-based MFCCs, and a greedy CTC collapse—so the mechanics are transparent.  The Colab script (`src/phase73/phase73_speech_audio_colab.py`) maps those same stages to real libraries: librosa for loading, Whisper for transcription, and Griffin-Lim for vocoder reconstruction.

Key takeaway: Speech is a sequence problem, just like text.  The same attention mechanisms work once you convert pressure waves into feature vectors.

---

← [Previous: Phase 72: Real Agents with Tool Use](docs/phase72/SUMMARY.md) | [Next: Phase 74: Recommendation Systems](docs/phase74/SUMMARY.md) →
