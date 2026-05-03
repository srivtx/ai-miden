### 1. Why it exists (THE PROBLEM first)

Before object detection, image classification could only answer: **"What is in this picture?"** It would say "dog" or "cat," but it could not tell you WHERE the dog was, how many dogs there were, or whether a dog and a cat were in the same image. For self-driving cars, robots, or medical imaging, knowing that something exists is useless without knowing its location. A car cannot brake for a pedestrian if it only knows a pedestrian is "somewhere in the scene."

### 2. Definition (very simple)

Object detection is the task of drawing a **bounding box** around every object in an image and labeling each box with a class. It answers two questions simultaneously: **What is it?** and **Where is it?** The output is a list of rectangles, each defined by four numbers (x, y, width, height) plus a class label and a confidence score.

### 3. Real-life analogy

**A security guard scanning a parking lot.** The guard does not just say "there are cars." They point and say: "Silver sedan at coordinates A3, blue truck at B7, motorcycle at C1." Object detection is that pointing. The bounding box is the guard's finger tracing an invisible rectangle around each vehicle.

### 4. Tiny numeric example

Imagine a 10x10 image with one object. A ground-truth box says the object is at:
- Top-left corner: (3, 4)
- Bottom-right corner: (7, 8)

A model predicts:
- Predicted top-left: (2, 3)
- Predicted bottom-right: (8, 9)

Intersection Over Union (IoU):
- Intersection area: width = min(7,8) - max(3,2) = 5 - 3 = 2, height = min(8,9) - max(4,3) = 8 - 4 = 4, area = 2 * 4 = 8
- Union area: area_A + area_B - intersection = 16 + 36 - 8 = 44
- IoU = 8 / 44 = **0.18**

An IoU threshold of 0.5 is common. Since 0.18 < 0.5, this prediction is considered a miss.

### 5. Common confusion

1. **Detection is not classification.** Classification says "dog." Detection says "dog at (x1, y1, x2, y2) with 92% confidence." These are different tasks with different outputs and different loss functions.
2. **Bounding boxes are not pixel-perfect.** A box is a crude rectangle. It often includes background pixels and may cut off parts of the object. Masks (segmentation) fix this, but boxes are faster.
3. **IoU is not accuracy.** A model can have high classification accuracy but terrible IoU if its boxes are in the wrong places. IoU measures spatial overlap, not label correctness.
4. **Anchors are not the final predictions.** Anchors are pre-defined template boxes of various shapes and sizes. The network predicts offsets from these anchors, not raw coordinates. The anchor is the starting guess; the offset is the refinement.
5. **mAP averages over many thresholds.** Mean Average Precision (mAP) does not use one IoU threshold. It computes AP at IoU = 0.50, 0.55, 0.60, ... 0.95 and averages them. A model that is good at 0.50 but bad at 0.95 will have lower mAP.
6. **Non-maximum suppression removes duplicates, not errors.** NMS keeps the best box in a cluster and throws away overlapping boxes of the same class. It does not fix boxes that are simply in the wrong place.
7. **More boxes does not mean better detection.** A model that predicts 1,000 boxes per image will have high recall but terrible precision. Good detection balances finding objects with avoiding false alarms.

### 6. Where it is used in our code

In `src/phase78/phase78_object_detection.py`, we generate a synthetic image with shapes, define ground-truth bounding boxes, simulate predicted boxes from a sliding window and a YOLO-style grid, compute IoU between every prediction and every ground truth, and apply non-maximum suppression to remove duplicate detections. The IoU matrix and NMS result are visualized to show exactly how spatial overlap determines which predictions survive.
