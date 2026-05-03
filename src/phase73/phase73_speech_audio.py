"""
Phase 73: Speech & Audio — NumPy Concept Demo
------------------------------------------------
This script demonstrates the core signal-processing steps behind modern
speech systems using only NumPy and Matplotlib.  It shows:
  1. How a raw waveform is just a list of pressure samples.
  2. How STFT turns time-domain samples into a time-frequency picture.
  3. How a mel-filterbank compresses frequency bins into perceptual bands.
  4. How MFCCs further compress those bands into decorrelated coefficients.
  5. How CTC alignment collapses repeated frame predictions into text.

 WHY this matters:  Before you plug a wav file into Whisper, someone had to
design every one of these transforms.  Understanding them makes the black box
transparent.
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# 0. PARAMETERS
# ---------------------------------------------------------------------------
# WHY 8 kHz?  Telephone-quality speech is intelligible at 8 kHz, and it keeps
# our arrays small enough to print and inspect.
SR = 8000
DURATION = 1.0
N_SAMPLES = int(SR * DURATION)

# WHY these sizes?  A 256-sample window is ~32 ms at 8 kHz — short enough to
# capture phonemes, long enough to resolve pitch.  Hop of 128 gives 50 % overlap.
N_FFT = 256
HOP_LENGTH = 128
N_MELS = 20
N_MFCC = 13

np.random.seed(73)

# ---------------------------------------------------------------------------
# 1. GENERATE SYNTHETIC AUDIO
# ---------------------------------------------------------------------------
# WHY sine waves?  Real speech is a mixture of harmonics, but a pure tone is
# the simplest building block.  We switch frequency mid-clip to simulate two
# different phonemes.
t = np.linspace(0.0, DURATION, N_SAMPLES, endpoint=False)
signal = np.zeros_like(t)

# First half: 220 Hz (like an "aa" vowel with low pitch)
signal[: N_SAMPLES // 2] = 0.5 * np.sin(2.0 * np.pi * 220.0 * t[: N_SAMPLES // 2])

# Second half: 440 Hz (like an "ee" vowel with higher pitch)
signal[N_SAMPLES // 2 :] = 0.3 * np.sin(2.0 * np.pi * 440.0 * t[N_SAMPLES // 2 :])

# Add tiny noise so the spectrogram isn't artificially clean.
signal += 0.01 * np.random.randn(N_SAMPLES)

# ---------------------------------------------------------------------------
# 2. COMPUTE STFT SPECTROGRAM FROM SCRATCH
# ---------------------------------------------------------------------------
# WHY not just call librosa.stft?  Because we want to see every step.
# The STFT slices the signal into overlapping windows, applies a taper
# (Hann window) to reduce edge artifacts, and runs a Fourier transform.

window = np.hanning(N_FFT)
n_frames = 1 + (N_SAMPLES - N_FFT) // HOP_LENGTH

# Keep only the non-redundant bins from the real FFT.
n_freq = N_FFT // 2 + 1
spec = np.zeros((n_freq, n_frames), dtype=np.float32)

for i in range(n_frames):
    start = i * HOP_LENGTH
    frame = signal[start : start + N_FFT]

    # Zero-pad if we run off the end (shouldn't happen with our math above,
    # but defensive programming is good).
    if len(frame) < N_FFT:
        frame = np.pad(frame, (0, N_FFT - len(frame)))

    # WHY Hann window?  Multiplying by a smooth taper prevents spectral leakage
    # — sharp rectangle edges create fake high frequencies.
    windowed = frame * window

    # WHY rfft?  Real signals have symmetric spectra; we only need the positive
    # frequencies, which cuts memory and computation in half.
    fft = np.fft.rfft(windowed)
    spec[:, i] = np.abs(fft)

# ---------------------------------------------------------------------------
# 3. BUILD MEL-FILTERBANK
# ---------------------------------------------------------------------------
# WHY mel scale?  Humans perceive pitch logarithmically.  Two frequencies
# 100 Hz apart sound very different at low frequencies (100 vs 200 Hz) but
# almost identical at high frequencies (4100 vs 4200 Hz).  The mel scale
# stretches low frequencies and compresses high ones to match human hearing.

def hz_to_mel(hz):
    return 2595.0 * np.log10(1.0 + hz / 700.0)

def mel_to_hz(mel):
    return 700.0 * (10.0 ** (mel / 2595.0) - 1.0)

f_min = 0.0
f_max = SR / 2.0
mel_points = np.linspace(hz_to_mel(f_min), hz_to_mel(f_max), N_MELS + 2)
hz_points = mel_to_hz(mel_points)

# Map Hz to FFT bin indices.
bin_points = np.floor((N_FFT + 1) * hz_points / SR).astype(int)

mel_filters = np.zeros((N_MELS, n_freq), dtype=np.float32)
for m in range(1, N_MELS + 1):
    f_minus = bin_points[m - 1]
    f_center = bin_points[m]
    f_plus = bin_points[m + 1]

    # Rising slope of triangle.
    for k in range(f_minus, f_center):
        mel_filters[m - 1, k] = (k - f_minus) / (f_center - f_minus)

    # Falling slope of triangle.
    for k in range(f_center, f_plus):
        mel_filters[m - 1, k] = (f_plus - k) / (f_plus - f_center)

# Apply filters: each mel bin is a weighted sum of FFT bins.
mel_spec = np.dot(mel_filters, spec)

# ---------------------------------------------------------------------------
# 4. EXTRACT MFCC-LIKE FEATURES
# ---------------------------------------------------------------------------
# WHY log?  Human loudness perception is roughly logarithmic.  A sound with
# 10× the energy does not sound 10× louder.  Taking the log matches the model
# to the ear.
log_mel_spec = np.log(mel_spec + 1e-10)

# WHY DCT?  The mel bins are highly correlated (neighboring frequencies rise
# and fall together).  The Discrete Cosine Transform decorrelates them,
# producing compact coefficients similar to how JPEG compresses images.
mfcc = np.zeros((N_MFCC, n_frames), dtype=np.float32)
for k in range(N_MFCC):
    for n in range(N_MELS):
        mfcc[k, :] += log_mel_spec[n, :] * np.cos(np.pi * k * (n + 0.5) / N_MELS)

# Normalization factor used in type-II DCT.
mfcc *= np.sqrt(2.0 / N_MELS)

# ---------------------------------------------------------------------------
# 5. SIMULATE SIMPLE CTC ALIGNMENT
# ---------------------------------------------------------------------------
# WHY CTC?  In speech, we don't know which frame maps to which character.
# CTC solves this by allowing blank "-" predictions and collapsing repeats.
# We simulate frame-level predictions for the word "CAT".

LABELS = ["-", "C", "A", "T"]  # index 0 is blank
T = 8
L = len(LABELS)

# Random emissions, then boost the correct path so it wins.
emissions = np.random.rand(L, T).astype(np.float32)
emissions[1, 1] += 3.0   # C at t=1
emissions[2, 3] += 3.0   # A at t=3
emissions[3, 5] += 3.0   # T at t=5
emissions[0, [0, 2, 4, 6, 7]] += 2.0  # blanks elsewhere
emissions = emissions / emissions.sum(axis=0, keepdims=True)

# Greedy best-path (simplified Viterbi).
best_path = [LABELS[np.argmax(emissions[:, t])] for t in range(T)]

# CTC collapse: remove blanks, then remove consecutive duplicates.
collapsed = []
prev = None
for token in best_path:
    if token != "-":
        if token != prev:
            collapsed.append(token)
        prev = token
ctc_result = "".join(collapsed)

# ---------------------------------------------------------------------------
# 6. VISUALIZE
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Waveform
axes[0, 0].plot(t, signal, linewidth=0.8)
axes[0, 0].set_title("Synthetic Audio Waveform")
axes[0, 0].set_xlabel("Time (s)")
axes[0, 0].set_ylabel("Amplitude")
axes[0, 0].axvline(x=DURATION / 2, color='r', linestyle='--', alpha=0.5, label='Freq switch')
axes[0, 0].legend()

# Spectrogram (log scale for visibility)
im1 = axes[0, 1].imshow(
    20.0 * np.log10(spec + 1e-10),
    aspect='auto',
    origin='lower',
    cmap='viridis',
    extent=[0, n_frames, 0, SR // 2]
)
axes[0, 1].set_title("STFT Spectrogram (dB)")
axes[0, 1].set_xlabel("Frame")
axes[0, 1].set_ylabel("Frequency (Hz)")

# Mel-spectrogram
im2 = axes[1, 0].imshow(
    20.0 * np.log10(mel_spec + 1e-10),
    aspect='auto',
    origin='lower',
    cmap='magma',
    extent=[0, n_frames, 0, N_MELS]
)
axes[1, 0].set_title("Mel-Spectrogram")
axes[1, 0].set_xlabel("Frame")
axes[1, 0].set_ylabel("Mel Bin")

# CTC alignment
im3 = axes[1, 1].imshow(emissions, aspect='auto', origin='lower', cmap='coolwarm')
axes[1, 1].set_title(f"Simulated CTC Alignment (best path: {' '.join(best_path)} -> '{ctc_result}')")
axes[1, 1].set_xlabel("Time Frame")
axes[1, 1].set_ylabel("Token")
axes[1, 1].set_yticks(range(L))
axes[1, 1].set_yticklabels(LABELS)

plt.tight_layout()
output_path = os.path.join(os.path.dirname(__file__), 'speech_audio.png')
plt.savefig(output_path)
print(f"Plot saved to {output_path}")

# ---------------------------------------------------------------------------
# 7. PRINT VERIFICATION
# ---------------------------------------------------------------------------
print(f"\nAudio samples: {N_SAMPLES}")
print(f"Spectrogram shape: {spec.shape} (freq bins x frames)")
print(f"Mel-spectrogram shape: {mel_spec.shape} (mel bins x frames)")
print(f"MFCC shape: {mfcc.shape} (coefficients x frames)")
print(f"CTC best path: {' '.join(best_path)}")
print(f"CTC collapsed result: '{ctc_result}'")
