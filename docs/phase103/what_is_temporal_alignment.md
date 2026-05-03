## What Is Temporal Alignment?

---

## The Problem

A video dataset contains millions of clips paired with transcribed audio. In one clip, a chef says "now chop the onions" at the 5-second mark, but the caption is attached to the entire 60-second file. If a model trains on this pairing, it learns to associate chopping instructions with frying scenes, washing scenes, and plating scenes. The signal is smeared across time. How do you ensure that events in one modality line up with the correct moment in another?

---

## Definition

**Temporal Alignment** is the process of ensuring that events in one time-based modality (video frames, audio waveforms, subtitle text) correspond to the correct time window in another modality. It creates frame-level or segment-level correspondence rather than file-level pairing.

**How it works:**
```
Raw dataset:    video_file_A.mp4  +  transcript_A.txt (no timestamps)
Aligned dataset: video_file_A.mp4  +  transcript_A.txt with [00:05.200 - 00:08.400] per sentence
Result:         "chop the onions" is locked to the 5-second window where the knife moves
```

**Key techniques:**
- **Forced alignment:** using speech recognition models to map transcript words to audio timestamps
- **Dynamic time warping (DTW):** finding the optimal non-linear mapping between two time series
- **Cross-modal attention:** learning soft alignment between video frames and text tokens

**Why this matters:**
- A misaligned video-text dataset teaches a model that visual motion is unrelated to spoken words
- Correct alignment increases downstream retrieval accuracy by 20-40 percentage points
- Event-level understanding requires sub-second precision, not file-level pairing

---

## Real-Life Analogy

Dubbing a foreign film is the classic analogy for temporal alignment. A voice actor records dialogue in a studio, and an editor must match every syllable to the actor's lip movements on screen. If the audio drifts by even 300 milliseconds, the viewer immediately notices the disconnect. The immersion breaks because the sensory channels are out of sync. The editor does not just pair the right script with the right film; they lock every line to the exact frame where the mouth opens.

But real temporal alignment is harder than film dubbing because the "editor" is an algorithm working at scale. In a dataset of 100,000 cooking videos, there is no human watching every clip. The algorithm must listen for the word "chop," detect knife motion in the video, and verify that both occur in the same 3-second window. Sometimes the audio is clear but the camera is focused on the chef's face, not the cutting board. Sometimes the video shows the action but background music drowns out the speech. The alignment algorithm must score confidence and discard low-confidence pairs rather than force a false match.

The trade-off is between precision and coverage. Aggressive alignment keeps only the most certain pairs, producing a small, clean dataset. Loose alignment keeps more data but introduces noise. Choosing the threshold is a domain-specific decision: medical procedures demand near-perfect alignment, while casual vlogging tolerates more slop.

---

## Tiny Numeric Example

**A video has 20 time windows and a transcript mentions "chop" at the true event time of window 10:**

**Alignment scores by window (higher = better match):**
```
Window:   5     6     7     8     9    10    11    12    13    14
Score:   0.05  0.10  0.20  0.40  0.70  1.00  0.70  0.40  0.20  0.10
```

**Before alignment (file-level pairing):**
```
The entire transcript is treated as describing the entire video.
Effective training signal: 1 correct match / 20 possible windows = 5% precision
```

**After temporal alignment (window-level pairing):**
```
The caption "chop the onions" is paired only with window 10.
Effective training signal: 1 correct match / 1 paired window = 100% precision
```

**Downstream retrieval task (find video clip given text query):**
```
File-level pairing:    34% top-1 accuracy
Window-aligned pairing: 71% top-1 accuracy
```

**The shift:** Aligning at the window level more than doubled retrieval accuracy by eliminating cross-time contamination.

---

## Common Confusion

1. **"Temporal alignment is the same as general data cleaning."** Data cleaning removes duplicates and fixes formatting. Temporal alignment is specifically about time synchronization. A file can be perfectly clean yet have captions shifted by 10 seconds.

2. **"If two modalities are in the same file, they are already aligned."** File-level pairing does not guarantee event-level alignment. A podcast transcript attached to a 45-minute episode contains hundreds of events that need individual timestamps.

3. **"Temporal alignment requires perfect transcripts."** Forced alignment algorithms can work with imperfect transcripts because they match phoneme sequences rather than exact word boundaries. The alignment itself often improves the transcript.

4. **"Alignment is only needed for video and audio."** Any time-based pairing benefits from alignment: sensor logs with event annotations, EEG data with stimulus markers, or stock prices with news headlines.

5. **"Dynamic time warping always finds the correct alignment."** DTW finds the optimal warping path, but if one modality is missing the event entirely, DTW will force a false match to the nearest available point.

6. **"Once aligned, the dataset is forever clean."** Temporal drift can reappear during data augmentation. Speed perturbations on audio and frame subsampling on video must be applied jointly to preserve alignment.

7. **"Alignment is too expensive for web-scale datasets."** Modern forced alignment runs at 100x real-time on GPU. The cost of alignment is negligible compared to the cost of training on misaligned data.

---

## Where It Is Used in Our Code

`src/phase103/phase103_multimodal_data.py` — We simulate temporal alignment using time-window scoring. A Gaussian scoring function measures how alignment quality drops as the temporal shift between modalities increases, and we plot the score curve against the true event time.
