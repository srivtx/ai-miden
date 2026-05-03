### 1. Why it exists (THE PROBLEM first)

Sliding a classifier across every possible window in an image is brutally inefficient. A 1,000x1,000 image has millions of possible rectangles. Running a deep network on each one would take hours per image. R-CNN asked: **"Can we propose a small set of likely regions first, then only run the expensive classifier on those?"** The problem was computational cost. The solution was to separate region proposal from classification.

### 2. Definition (very simple)

R-CNN (Region-based Convolutional Neural Network) is a **two-stage detector.** Stage 1 proposes a few thousand candidate regions that might contain objects. Stage 2 classifies each proposed region and refines its bounding box. Faster R-CNN made this faster by teaching the network to propose its own regions using a **Region Proposal Network (RPN),** so the entire pipeline becomes one unified neural network.

### 3. Real-life analogy

**A detective investigating a crime scene.** Instead of dusting every square inch for fingerprints (sliding window), the detective first scans the room and says: "The doorknob, the windowsill, and the coffee cup are the only places worth checking." Then they carefully analyze only those three items. Stage 1 is the scan; Stage 2 is the careful analysis.

### 4. Tiny numeric example

An image passes through a convolutional backbone and produces a feature map of size 16x16 with 512 channels.

Stage 1 — RPN:
- An RPN slides a 3x3 window over the 16x16 feature map.
- At each position, it considers 9 anchor boxes (3 scales x 3 aspect ratios).
- Total anchors: 16 * 16 * 9 = **2,304**
- The RPN predicts, for each anchor: objectness score + 4 box-refinement offsets.
- After filtering by objectness threshold and NMS, maybe **200 regions** survive.

Stage 2 — Classifier:
- Each of the 200 regions is cropped from the feature map and resized.
- A classifier head predicts: class probabilities (dog, cat, background) + refined box coordinates.
- Final output after another NMS: **3 detected objects.**

The network looked at 2,304 candidates but only ran the heavy classifier on 200.

### 5. Common confusion

1. **R-CNN is not one model; it is a family.** Original R-CNN used Selective Search (an external algorithm) for proposals. Fast R-CNN reused convolutional features. Faster R-CNN replaced Selective Search with a learned RPN. Each version fixed the speed problem of the previous one.
2. **The Region Proposal Network is not a separate script.** In Faster R-CNN, the RPN shares the convolutional backbone with the classifier. It is an extra head attached to the same feature map, not a pre-processing step running on the CPU.
3. **Two-stage does not mean two separate forward passes.** In Faster R-CNN, the image goes through the backbone once. The RPN and classifier both consume the same feature map. It is two logical stages, not two complete network evaluations.
4. **Anchor boxes in the RPN are not the final boxes.** The RPN predicts whether an anchor contains an object and how to shift/resize that anchor. The final box comes after both RPN refinement AND classifier refinement.
5. **R-CNN is slower than YOLO because it does more work per region.** The classifier head is often a heavy fully connected network applied to each region independently. This per-region cost is why R-CNN trails YOLO in frames per second.
6. **Background is a class in the classifier.** If the RPN proposes a region that contains nothing useful, the classifier should label it "background." This is how false-positive proposals are discarded.
7. **RoI pooling is not the same as regular pooling.** Region of Interest pooling crops and resizes irregular feature-map regions into fixed-size tensors so the classifier head can process them. Without it, different-sized regions could not feed into a fixed-size network.

### 6. Where it is used in our code

In `src/phase78/phase78_object_detection.py`, we demonstrate the two-stage concept by first generating candidate windows with a sliding window (analogous to the RPN proposing regions) and then scoring those windows against ground-truth objects (analogous to the classifier stage). This shows why separating proposal from classification reduces the number of expensive evaluations needed.
