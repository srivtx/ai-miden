← [Previous: Phase 77: Unsupervised Learning](docs/phase77/SUMMARY.md) | [Next: Phase 79: Causal Inference](docs/phase79/SUMMARY.md) →

---

# Phase 78 Summary: Object Detection & Segmentation

## What This Phase Taught

Neural networks can see. But seeing is not just naming what is in a picture. It is knowing WHERE things are, drawing boxes around them, and even tracing every pixel of their outline. This phase covers the full spectrum of visual localization: from sliding windows to single-shot detectors, from two-stage precision to pixel-perfect masks.

## Key Concepts

- **Object Detection:** Finding objects in an image and drawing bounding boxes around them. Combines localization (where?) with classification (what?).
- **IoU (Intersection Over Union):** The standard metric for measuring how much a predicted box overlaps with the true box. Thresholds like 0.5 decide whether a prediction counts as correct.
- **Non-Maximum Suppression (NMS):** Removing duplicate detections. When a model fires multiple overlapping boxes for the same object, NMS keeps the best one and discards the rest.
- **YOLO (You Only Look Once):** A single-shot detector that divides the image into a grid and predicts all boxes and classes in one forward pass. Fast but slightly less precise on small objects.
- **R-CNN / Faster R-CNN:** Two-stage detectors. Stage 1 proposes likely regions with an RPN; Stage 2 classifies and refines them. Slower but more accurate, especially for crowded scenes.
- **Semantic Segmentation:** Labeling every pixel with a class. All cars are the same color in the output mask.
- **Instance Segmentation:** Labeling every pixel AND separating individual objects. Car 1, Car 2, and Car 3 each get their own mask.
- **SAM (Segment Anything Model):** A promptable segmentation model that produces a mask for any object given a point, box, or text prompt, without needing class labels.

## The Code

**Local (NumPy):** `src/phase78/phase78_object_detection.py` — Generates a synthetic image with circles and squares. Demonstrates sliding window proposals, IoU computation, non-maximum suppression, and YOLO-style grid prediction. Visualizes ground-truth boxes, predicted boxes, the full IoU matrix, and the cleaned NMS result.

**Colab (PyTorch GPU):** `src/phase78/phase78_object_detection_colab.py` — Loads a pre-trained YOLO or DETR model for real object detection on sample images. Also demonstrates semantic segmentation with a pre-trained model, visualizing bounding boxes, labels, and per-pixel class masks.

## Results

**Local:** The script produces a four-panel visualization: (1) the synthetic image with ground-truth boxes, (2) the image with noisy predicted boxes before NMS, (3) the IoU matrix between predictions and ground truth, and (4) the final cleaned boxes after NMS. This shows exactly how overlap metrics and deduplication turn raw network outputs into usable detections.

**Colab:** The pre-trained detector draws accurate bounding boxes and class labels on real images. The segmentation model produces a dense per-pixel class map, demonstrating the jump from coarse rectangles to exact boundaries.

## The Analogy

Detection is like a security guard pointing at every person in a room and naming them. Segmentation is like painting a portrait where every person is colored in down to their fingertips. YOLO is the guard who glances once and points everywhere instantly. R-CNN is the guard who first notes suspicious spots and then inspects each one carefully. SAM is an artist who can outline any object you tap with your finger, even if they have never seen that object before.

## Connection to Previous Phase

Phase 77 explored unlabeled data through clustering and dimensionality reduction. Phase 78 adds the critical missing skill: localizing objects spatially. We move from "what is in the image?" to "where exactly is it?" and "what is its exact shape?"}

## Connection to Next Phase

Phase 79 will ask: "We can detect and segment objects. But what if the objects are moving through time? How do we track the same car across 30 frames of video?" The answer: object tracking and multi-object tracking (MOT).

---

← [Previous: Phase 77: Unsupervised Learning](docs/phase77/SUMMARY.md) | [Next: Phase 79: Causal Inference](docs/phase79/SUMMARY.md) →
