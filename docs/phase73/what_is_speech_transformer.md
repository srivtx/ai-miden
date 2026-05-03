# What is a Speech Transformer?

## 1. Why it exists (THE PROBLEM)
RNNs process audio one frame at a time. By the time they reach the end of a long sentence, they have forgotten the beginning. CNNs can look at local patches of a spectrogram, but they struggle to relate the first word to the last word across thousands of time steps. We need an architecture that can attend to every part of the audio at once, in parallel, just like Transformers did for text.

## 2. Definition
A Speech Transformer applies the self-attention mechanism to audio inputs—either raw waveforms or spectrogram patches—so that every time step can directly influence every other time step, enabling parallel processing of long audio sequences.

## 3. Real-life analogy
A conductor leading an orchestra. Instead of walking to each musician one by one (RNN) or only listening to small groups at a time (CNN), the conductor sees every musician simultaneously and adjusts the whole orchestra in parallel. A Speech Transformer is that conductor for audio features.

## 4. Tiny numeric example
Audio features after preprocessing (4 time steps, 3 dimensions):
```
Frame 0: [0.2, 0.1, 0.3]
Frame 1: [0.5, 0.4, 0.6]
Frame 2: [0.1, 0.2, 0.1]
Frame 3: [0.4, 0.3, 0.5]
```

Self-attention computes Query, Key, and Value for each frame. The attention weight matrix (simplified, one head) might look like:
```
        Frame0  Frame1  Frame2  Frame3
Frame0   0.40    0.30    0.15    0.15
Frame1   0.25    0.35    0.20    0.20
Frame2   0.20    0.25    0.30    0.25
Frame3   0.20    0.30    0.20    0.30
```

Each output frame is a weighted sum of all input frames using these scores. Frame 1 pays the most attention to itself and its neighbors, but it still receives information from Frame 0 and Frame 3 directly.

## 5. Common confusion
- **"A Speech Transformer is just a text Transformer with audio file names."** No. Audio requires different positional encodings, patch sizes, and sometimes strided convolutions to reduce sequence length before attention.
- **"wav2vec 2.0 and wav2vec 1.0 are the same."** No. wav2vec 1.0 used contrastive predictive coding on raw waveforms. wav2vec 2.0 added a Transformer and masked prediction, similar to BERT.
- **"Self-supervised pretraining on audio is the same as supervised training."** No. wav2vec 2.0 is trained by masking parts of the audio and asking the model to predict the correct latent representation, without any text labels.
- **"Whisper and wav2vec 2.0 have the same architecture."** No. Whisper is an encoder-decoder Transformer (like T5). wav2vec 2.0 is encoder-only (like BERT) and usually needs a CTC or seq2seq head added later.
- **"Positional encoding for audio works exactly like text."** Not always. Audio uses relative positional biases or sinusoidal encodings scaled to time steps, and sometimes 2D encodings when using spectrogram patches.
- **"A CTC head and a decoder head are interchangeable."** No. CTC heads predict characters independently and rely on a post-processing collapse step. Decoder heads predict tokens autoregressively, conditioned on all previous outputs.
- **"Speech Transformers need less compute than RNNs."** Per step, yes—parallel attention is fast on GPUs. But the quadratic cost of attention over long audio (minutes) is huge, which is why Whisper uses strided convolutions to shrink the sequence first.

## 6. Where it is used in our code
`src/phase73/phase73_speech_audio_colab.py` loads Whisper, a real encoder-decoder Speech Transformer. The script shows how the encoder processes a mel-spectrogram with self-attention, while the decoder generates text tokens autoregressively, attending to both previous text tokens and the encoder audio representation.
