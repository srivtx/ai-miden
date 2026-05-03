# What is Audio Feature Extraction?

## 1. Why it exists (THE PROBLEM)
Raw audio is just a list of pressure samples—tens of thousands per second. Feeding every single sample into a model is like trying to recognize a painting by analyzing every molecule of paint. It is too high-dimensional, too noisy, and full of redundant information. We need compact features that capture pitch, timbre, and rhythm while throwing away irrelevant detail.

## 2. Definition
Audio feature extraction transforms a raw waveform into a compressed representation—such as a spectrogram, mel-spectrogram, or MFCC—that highlights the frequencies and energies humans actually perceive when they listen to sound.

## 3. Real-life analogy
A wine tasting note. Instead of listing every chemical compound in the wine, a sommelier writes "fruity, oaky, dry with a long finish." That short description captures what matters for recognition. Audio features are the sommelier notes of sound.

## 4. Tiny numeric example
Raw samples (8 values): `[1.0, 2.0, 3.0, 4.0, 3.0, 2.0, 1.0, 0.0]`

Step 1 — STFT (Short-Time Fourier Transform) with window size 8:
```
FFT magnitudes: [16.0, 2.83, 0.0, 0.77]
```

Step 2 — Mel filterbank (2 triangular filters):
```
Mel energies: [14.2, 1.5]
```

Step 3 — Log compression + DCT (first 2 MFCC coefficients):
```
MFCC: [2.1, -0.4]
```

The original 8 samples became 2 numbers that describe the spectral shape.

## 5. Common confusion
- **"A waveform and a spectrogram are the same thing."** No. A waveform is amplitude vs. time. A spectrogram is frequency vs. time. They contain the same information, but one is much easier for a model to read.
- **"MFCC and mel-spectrogram are identical."** No. A mel-spectrogram is frequency energy on a mel scale. MFCCs take the log of that and apply a DCT, decorrelating the features.
- **"Bigger FFT window is always better."** A big window gives better frequency resolution but worse time resolution. You cannot perfectly have both; this is the uncertainty principle.
- **"More FFT bins means better features."** After a point, extra bins just capture noise. That is why we collapse hundreds of FFT bins into ~20-40 mel bins.
- **"MFCCs are outdated because neural networks are powerful."** Deep models can learn from raw waveforms, but MFCCs are still used in embedded devices because they are tiny and fast.
- **"Log-mel is just mel with a log button."** The log compresses dynamic range and matches human loudness perception (we hear multiplicatively, not additively).
- **"Feature extraction is lossless."** It is deliberately lossy. Phase information is often discarded because human ears are relatively insensitive to phase.

## 6. Where it is used in our code
`src/phase73/phase73_speech_audio.py` generates a synthetic sine-wave signal, computes an STFT spectrogram from scratch with NumPy, builds a mel-filterbank, and extracts MFCC-like coefficients. The script plots all three stages so you can see how 8,000 samples become a compact time-frequency image.
