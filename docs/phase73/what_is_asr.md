# What is ASR?

## 1. Why it exists (THE PROBLEM)
Humans communicate by speaking naturally, but computers only understand numbers and text. If you want a machine to take a voice command, transcribe a podcast, or caption a video, there is a massive gap between a sound wave and a string of characters. Typing everything by hand is slow and inaccessible. ASR exists to bridge that gap: turning spoken audio into written text automatically.

## 2. Definition
Automatic Speech Recognition (ASR) is the task of converting a raw audio waveform into a sequence of text tokens (words or characters) that represent what was said.

## 3. Real-life analogy
A courtroom stenographer. A person sits and listens to speech in real time, pressing keys on a special machine to produce a written transcript. They do not understand the legal arguments deeply—they just faithfully convert sound into text. ASR is an automatic stenographer.

## 4. Tiny numeric example
Imagine a 1-second audio clip sampled at 8 kHz. That is 8,000 numbers.

```
Audio samples (first 8): [0.01, 0.03, 0.02, -0.01, -0.03, -0.02, 0.00, 0.01]

After feature extraction -> frame energies: [0.5, 0.8, 0.3, 0.9]

CTC decoder output (with blanks "-"):
  Frame 1: "-"
  Frame 2: "C"
  Frame 3: "C"
  Frame 4: "-"
  Frame 5: "A"
  Frame 6: "-"
  Frame 7: "T"
  Frame 8: "T"

Collapse repeats and remove blanks -> "CAT"
```

## 5. Common confusion
- **"ASR understands what you mean."** No. ASR only transcribes sound into text. Understanding meaning is NLP.
- **"ASR and speaker recognition are the same thing."** No. ASR answers "what was said?" Speaker recognition answers "who said it?"
- **"More data always fixes accent problems."** Not automatically. If the training data lacks certain accents, the model will hallucinate words it has heard more frequently.
- **"CTC, attention, and RNN-T are the same."** No. CTC assumes conditional independence between frames and uses a blank symbol. Attention models learn an explicit alignment. RNN-T combines an encoder and a prediction network jointly.
- **"Whisper is only an ASR model."** Whisper is also a translation model. It can transcribe Spanish audio directly into English text.
- **"ASR quality is measured only by word error rate."** WER is the main metric, but latency, memory usage, and robustness to noise also matter in production.
- **"A larger model always transcribes better."** A 100M-parameter model trained on diverse data often beats a 1B-parameter model trained on clean studio speech alone.

## 6. Where it is used in our code
`src/phase73/phase73_speech_audio.py` simulates a CTC alignment path: synthetic frame-level predictions are collapsed with blanks to show how "CAT" emerges from repeated character emissions. `src/phase73/phase73_speech_audio_colab.py` loads OpenAI Whisper (a real encoder-decoder ASR model) and transcribes a wav file with its full preprocessing pipeline.
