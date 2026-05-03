#!/usr/bin/env python3
"""
Phase 73: Speech & Audio — Colab Real-Workflow Script
================================================================================
This script is designed to run in Google Colab (T4 GPU) or any CUDA environment.
It demonstrates the FULL speech pipeline:
  1. Load a real speech model (Whisper).
  2. Load an audio file with librosa and show preprocessing.
  3. Transcribe the audio end-to-end.
  4. Demonstrate TTS with a lightweight vocoder.

WHY this matters:  NumPy demos show the mechanics of FFT and mel filters.
This script shows how those mechanics map to production libraries: transformers,
librosa, and torch.  Every comment explains a design decision.
"""

# =============================================================================
# SECTION 0: ENVIRONMENT SETUP
# =============================================================================
# WHY: In Colab these are pre-installed.  On a local machine you may need:
#   pip install torch transformers librosa soundfile matplotlib numpy

import os
import time
import warnings
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Suppress librosa deprecation noise so the output stays readable.
warnings.filterwarnings('ignore')

DEVICE = "cuda" if __import__('torch').cuda.is_available() else "cpu"
print(f"Device: {DEVICE}")

import torch
print(f"PyTorch version: {torch.__version__}")
if DEVICE == "cuda":
    print(f"GPU: {torch.cuda.get_device_name(0)}")

# =============================================================================
# SECTION 1: LOAD A REAL SPEECH MODEL (Whisper)
# =============================================================================
# WHY Whisper?  It is open-source, multilingual, and small enough to run on a
# Colab T4, yet it uses the full encoder-decoder Transformer architecture that
# powers state-of-the-art ASR.

from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq

MODEL_NAME = "openai/whisper-tiny"  # 39M parameters — tiny but real.

print(f"\nLoading {MODEL_NAME}...")
processor = AutoProcessor.from_pretrained(MODEL_NAME)
model = AutoModelForSpeechSeq2Seq.from_pretrained(MODEL_NAME)
model.to(DEVICE)
model.eval()
print("Model loaded.")

# =============================================================================
# SECTION 2: AUDIO PREPROCESSING PIPELINE
# =============================================================================
# WHY librosa?  It handles resampling, mono conversion, and framing correctly.
# Whisper expects 16 kHz mono audio.  Most raw wav files are 44.1 kHz stereo.
# If we skip resampling, the model hears everything at the wrong pitch.

import librosa

# For demonstration we synthesize a short clip so the script runs even if
# no external wav file is uploaded.  In Colab you can replace this with:
#   audio_path = "/content/my_recording.wav"
#   audio, sr = librosa.load(audio_path, sr=None)
print("\n--- Generating synthetic audio for demo ---")
SR = 16000
duration = 2.0
t = np.linspace(0.0, duration, int(SR * duration), endpoint=False)

# Synthetic "speech": two formant-like sine sweeps + noise.
audio = (
    0.4 * np.sin(2.0 * np.pi * 200.0 * t)
    + 0.2 * np.sin(2.0 * np.pi * 600.0 * t)
    + 0.05 * np.random.randn(len(t))
)
audio = audio.astype(np.float32)

# librosa.load returns audio in [-1, 1] float32 and the target sample rate.
# We already generated at 16 kHz, but we run through librosa to show the API.
audio, sr = librosa.load(librosa.util.example_audio_file(), sr=SR, duration=duration)

# WHY mono?  Stereo gives two channels, but speech content is identical in both.
# Models expect a single 1-D array.
if audio.ndim > 1:
    audio = librosa.to_mono(audio)

print(f"Audio shape: {audio.shape}, sample rate: {sr}, duration: {len(audio)/sr:.2f}s")

# ---------------------------------------------------------------------------
# Preprocessing step-by-step (normally hidden inside processor)
# ---------------------------------------------------------------------------
# WHY feature extraction?  Whisper does NOT eat raw samples.  It eats a
# log-mel spectrogram computed with 80 mel bins, 25 ms windows, 10 ms hop.
# The processor handles this, but we inspect the intermediate array.

inputs = processor(audio, sampling_rate=sr, return_tensors="pt")
input_features = inputs.input_features.to(DEVICE)

print(f"Input features shape: {input_features.shape}")
# Shape is (batch=1, 80 mel bins, 3000 time frames) for 30s audio.
# For our 2s clip it is roughly (1, 80, 200).

# =============================================================================
# SECTION 3: TRANSCRIPTION (INFERENCE)
# =============================================================================
# WHY generate() instead of forward()?  forward() returns logits; generate()
# runs the autoregressive decoder loop, sampling one token at a time until
# the <|endoftext|> token appears.

print("\n--- Transcribing ---")
start = time.time()

with torch.no_grad():
    # forced_decoder_ids can be used for language prompting; we leave it free.
    predicted_ids = model.generate(input_features)

transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
elapsed = time.time() - start

print(f"Transcription: '{transcription}'")
print(f"Inference time: {elapsed:.3f}s")

# =============================================================================
# SECTION 4: TTS WITH A SIMPLE VOCODER
# =============================================================================
# WHY a simple vocoder?  Real neural TTS (e.g., VITS, Bark) needs hundreds of
# megabytes and GPU minutes.  For a concept demo we use a lightweight
# spectrogram-based pipeline: text -> grapheme -> spectrogram -> Griffin-Lim.
# Griffin-Lim is an iterative algorithm that reconstructs phase from magnitude.
# It is NOT neural, but it demonstrates the vocoder step transparently.

from scipy.signal import stft, istft

print("\n--- TTS Demo (synthetic text -> waveform) ---")

text = "hello world"

# Step A: trivial grapheme-to-phoneme (just characters).
phonemes = list(text.replace(" ", ""))
print(f"Phonemes: {phonemes}")

# Step B: synthesize a fake magnitude spectrogram.
# WHY fake?  A real acoustic model would predict this from phonemes.
# We generate a pattern that looks like two "formant" bands.
n_fft_tts = 256
hop_tts = 64
n_frames_tts = len(phonemes) * 20  # 20 frames per character
n_freq_tts = n_fft_tts // 2 + 1

fake_spec = np.zeros((n_freq_tts, n_frames_tts), dtype=np.float32)
for i, ph in enumerate(phonemes):
    start_f = i * 20
    end_f = (i + 1) * 20
    # Use character code to pick a base frequency.
    base_freq = (ord(ph) % 10 + 1) * 20
    fake_spec[base_freq : base_freq + 10, start_f:end_f] = 1.0
    fake_spec[base_freq + 30 : base_freq + 40, start_f:end_f] = 0.5

# Step C: Griffin-Lim reconstruction.
# WHY iterative?  STFT discards phase.  Griffin-Lim alternates between
# time domain and frequency domain, forcing the magnitude to match while
# slowly converging to a consistent phase.

def griffin_lim(mag_spec, n_iter=32, n_fft=256, hop_length=64):
    """Reconstruct waveform from magnitude spectrogram."""
    # Random initial phase.
    angles = np.exp(2j * np.pi * np.random.rand(*mag_spec.shape))
    for _ in range(n_iter):
        # Inverse STFT with current phase guess.
        _, recon = istft(mag_spec * angles, fs=SR, nperseg=n_fft, noverlap=n_fft - hop_length)
        # Forward STFT to get new phase.
        _, _, Z = stft(recon, fs=SR, nperseg=n_fft, noverlap=n_fft - hop_length)
        angles = np.exp(1j * np.angle(Z))
    # Final reconstruction.
    _, recon = istft(mag_spec * angles, fs=SR, nperseg=n_fft, noverlap=n_fft - hop_length)
    return recon

reconstructed = griffin_lim(fake_spec, n_iter=32, n_fft=n_fft_tts, hop_length=hop_tts)
reconstructed = reconstructed[: len(reconstructed) // 2]  # istft returns longer array

print(f"Reconstructed waveform length: {len(reconstructed)} samples")

# =============================================================================
# SECTION 5: VISUALIZE PIPELINE
# =============================================================================
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Input waveform
axes[0, 0].plot(np.linspace(0, len(audio)/sr, len(audio)), audio, linewidth=0.5)
axes[0, 0].set_title("ASR Input Waveform (Whisper)")
axes[0, 0].set_xlabel("Time (s)")
axes[0, 0].set_ylabel("Amplitude")

# Log-mel spectrogram from processor
mel_for_plot = input_features[0].cpu().numpy()
axes[0, 1].imshow(mel_for_plot, aspect='auto', origin='lower', cmap='viridis')
axes[0, 1].set_title("Whisper Log-Mel Spectrogram")
axes[0, 1].set_xlabel("Frame")
axes[0, 1].set_ylabel("Mel Bin")

# TTS fake magnitude spectrogram
axes[1, 0].imshow(20 * np.log10(fake_spec + 1e-10), aspect='auto', origin='lower', cmap='magma')
axes[1, 0].set_title("TTS Synthetic Magnitude Spectrogram")
axes[1, 0].set_xlabel("Frame")
axes[1, 0].set_ylabel("Frequency Bin")

# TTS reconstructed waveform
axes[1, 1].plot(reconstructed, linewidth=0.5)
axes[1, 1].set_title("TTS Reconstructed Waveform (Griffin-Lim)")
axes[1, 1].set_xlabel("Sample")
axes[1, 1].set_ylabel("Amplitude")

plt.tight_layout()
plot_path = os.path.join(os.path.dirname(__file__), 'speech_audio_colab.png')
plt.savefig(plot_path)
print(f"\nPlot saved to {plot_path}")

# =============================================================================
# SECTION 6: SUMMARY
# =============================================================================
print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print(f"ASR model:  {MODEL_NAME}")
print(f"Transcription: '{transcription}'")
print(f"TTS text:   '{text}'")
print(f"TTS output: {len(reconstructed)} samples @ {SR} Hz")
print("="*70)
