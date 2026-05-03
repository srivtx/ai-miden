# What is TTS?

## 1. Why it exists (THE PROBLEM)
Computers output text, but humans prefer to listen. Reading long articles, navigation directions, or accessibility prompts is tiring, impossible for the visually impaired, and dangerous while driving. We need a way to turn written text into natural-sounding speech automatically.

## 2. Definition
Text-to-Speech (TTS) is the task of converting a sequence of text tokens into a synthetic audio waveform that a human can understand and that sounds as natural as possible.

## 3. Real-life analogy
An audiobook narrator. You hand them a printed book, and they read it aloud with proper intonation, pauses, and emotion. TTS is an automatic narrator that never gets tired, but historically sounded robotic. Modern neural TTS sounds almost human.

## 4. Tiny numeric example
Text: "hi"

Step 1 — Grapheme-to-phoneme: "hi" -> /h/ /ay/

Step 2 — Acoustic model predicts a spectrogram (simplified, 3 time steps, 4 frequency bins):
```
Time 0: [0.1, 0.5, 0.2, 0.0]
Time 1: [0.2, 0.6, 0.3, 0.1]
Time 2: [0.1, 0.4, 0.2, 0.0]
```

Step 3 — Vocoder (e.g., Griffin-Lim or neural vocoder) converts spectrogram back to waveform samples:
```
Waveform (first 8 samples): [0.02, -0.05, 0.03, 0.01, -0.04, 0.06, -0.02, 0.01]
```

## 5. Common confusion
- **"TTS just plays prerecorded words like a speak-and-spell."** No. Concatenative TTS did that, but modern neural TTS generates entirely new waveforms from scratch.
- **"The spectrogram IS the audio."** No. A spectrogram is a picture of frequency content over time. You still need a vocoder to turn it back into pressure waves (audio).
- **"Vocoder and acoustic model are the same thing."** No. The acoustic model predicts how the speech should look in frequency space. The vocoder synthesizes the actual sound.
- **"More layers always mean more natural speech."** Not if the training data is small or monotone. Prosody (rhythm and intonation) is harder to learn than phoneme accuracy.
- **"TTS quality is objective."** It is mostly subjective. Researchers use Mean Opinion Score (MOS) where humans rate naturalness from 1 to 5.
- **"End-to-end TTS is always better than pipeline TTS."** End-to-end is simpler, but pipeline systems (text -> phoneme -> spectrogram -> waveform) are easier to debug and control.
- **"TTS works the same in every language."** Tonal languages (Mandarin, Thai) require pitch information. Agglutinative languages (Turkish, Finnish) have very long words that stress the grapheme-to-phoneme module.

## 6. Where it is used in our code
`src/phase73/phase73_speech_audio_colab.py` demonstrates a simple TTS pipeline: text is converted to a mel-spectrogram with a lightweight acoustic model, then a Griffin-Lim-like vocoder reconstructs the waveform. The script plays the result and shows why the vocoder step is necessary.
