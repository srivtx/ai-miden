# What is Temporal Alignment?

## Problem

In video-audio or video-text datasets, the modalities are not just paired; they are synchronized over time. A caption describing a scene at 10 seconds should not be aligned with audio from 30 seconds. Mismatched timing creates noisy training signals.

## Definition

Temporal Alignment is the process of ensuring that events in one time-based modality (e.g., video frames) correspond to the correct time window in another modality (e.g., audio or subtitles). This can involve forced alignment, timestamp matching, or learning dynamic time warping.

## Analogy

Dubbing a foreign film requires lip-sync: the voice actor's words must align with the character's mouth movements. If the audio is even one second off, the scene is jarring and the viewer loses immersion. Temporal alignment keeps the soundtrack locked to the action.

## Example

A dataset of cooking videos has transcribed speech. Temporal alignment ensures that the caption "now chop the onions" is paired with the 5-second window where the chef is actually chopping onions, not with a later scene where the onions are frying.

## Confusion

Temporal alignment is not the same as general data cleaning. It is specifically about time synchronization. Two modalities can be correctly paired at the file level but misaligned at the frame level.

## Code Location

See `src/phase103/phase103_multimodal_data.py` for a NumPy simulation of temporal alignment using time-window scoring.
