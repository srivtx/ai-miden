#!/usr/bin/env python3
"""
================================================================================
Phase 78: Object Detection & Segmentation — Seeing WHERE Things Are
================================================================================

This script is for a COMPLETE BEGINNER.

In earlier phases, our networks answered: "What is in this picture?"
Now we ask: "WHERE is it?" and "WHAT SHAPE is it?"

Object detection draws boxes. Segmentation paints pixels.
This script demonstrates the core ideas using ONLY NumPy:
  - Drawing shapes on an image
  - Sliding a window across the image (the brute-force approach)
  - Computing IoU (how much does a predicted box overlap the truth?)
  - Non-Maximum Suppression (removing duplicate boxes)
  - YOLO-style grid prediction (one look, all boxes)

Every line has a comment. Read it like a story.
"""

# ==============================================================================
# IMPORTS
# ==============================================================================

import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


# ==============================================================================
# STEP 1: BUILD A SYNTHETIC IMAGE WITH SHAPES
# ==============================================================================

def create_synthetic_image(size=64):
    """
    Create a blank image and draw simple shapes on it.

    WHY: Real photos are complex. Shapes let us see exactly whether
         our detector found the RIGHT pixels.
    """
    # Start with a gray background
    image = np.ones((size, size, 3), dtype=np.float32) * 0.9

    # Ground-truth objects: list of dicts with box and class
    # Box format: [x1, y1, x2, y2] (top-left, bottom-right)
    ground_truth = []

    # --- Object 1: red square ---
    x1, y1, x2, y2 = 10, 10, 26, 26
    image[y1:y2, x1:x2, 0] = 0.9   # Red channel
    image[y1:y2, x1:x2, 1] = 0.2   # Green channel
    image[y1:y2, x1:x2, 2] = 0.2   # Blue channel
    ground_truth.append({
        'box': [x1, y1, x2, y2],
        'class': 'square',
        'color': 'red'
    })

    # --- Object 2: blue circle ---
    cx, cy, r = 44, 18, 8
    yy, xx = np.ogrid[:size, :size]
    mask = (xx - cx)**2 + (yy - cy)**2 <= r**2
    image[mask, 0] = 0.2
    image[mask, 1] = 0.2
    image[mask, 2] = 0.9
    # Tight bounding box around the circle
    ground_truth.append({
        'box': [cx - r, cy - r, cx + r, cy + r],
        'class': 'circle',
        'color': 'blue'
    })

    # --- Object 3: green square ---
    x1, y1, x2, y2 = 20, 40, 40, 56
    image[y1:y2, x1:x2, 0] = 0.2
    image[y1:y2, x1:x2, 1] = 0.9
    image[y1:y2, x1:x2, 2] = 0.2
    ground_truth.append({
        'box': [x1, y1, x2, y2],
        'class': 'square',
        'color': 'green'
    })

    return image, ground_truth


# ==============================================================================
# STEP 2: SLIDING WINDOW DETECTOR (conceptual)
# ==============================================================================

def sliding_window_predictions(image, window_size=16, stride=8):
    """
    Slide a square window across the image and generate candidate boxes.

    WHY: Before deep learning, this was the only way. It is slow but
         easy to understand: check every location, keep the promising ones.
    """
    h, w = image.shape[:2]
    predictions = []

    # Slide the window from top-left to bottom-right
    for y in range(0, h - window_size + 1, stride):
        for x in range(0, w - window_size + 1, stride):
            # Extract the patch
            patch = image[y:y+window_size, x:x+window_size]

            # Heuristic: if the patch is not uniform gray, pretend we "detected"
            # something. In reality a CNN would score this patch.
            # We measure color variance as a fake "objectness" score.
            score = float(np.std(patch))

            # Keep patches with noticeable color variation
            if score > 0.15:
                predictions.append({
                    'box': [x, y, x + window_size, y + window_size],
                    'score': score
                })

    return predictions


# ==============================================================================
# STEP 3: INTERSECTION OVER UNION (IoU)
# ==============================================================================

def compute_iou(box_a, box_b):
    """
    Compute Intersection over Union between two bounding boxes.

    WHY: A model can predict a box NEAR the truth and still be wrong.
         IoU gives us a NUMBER for "how much overlap is enough?"
         1.0 = perfect overlap. 0.0 = no overlap.
    """
    # Unpack coordinates
    x1_a, y1_a, x2_a, y2_a = box_a
    x1_b, y1_b, x2_b, y2_b = box_b

    # Intersection rectangle
    xi1 = max(x1_a, x1_b)
    yi1 = max(y1_a, y1_b)
    xi2 = min(x2_a, x2_b)
    yi2 = min(y2_a, y2_b)

    # If boxes do not overlap, intersection area is 0
    inter_width = max(0, xi2 - xi1)
    inter_height = max(0, yi2 - yi1)
    inter_area = inter_width * inter_height

    # Areas of each box
    area_a = (x2_a - x1_a) * (y2_a - y1_a)
    area_b = (x2_b - x1_b) * (y2_b - y1_b)

    # Union = both areas added, minus the double-counted intersection
    union_area = area_a + area_b - inter_area

    # Guard against division by zero
    if union_area == 0:
        return 0.0

    return inter_area / union_area


def compute_iou_matrix(predictions, ground_truth):
    """
    Build a matrix of IoU between every prediction and every ground-truth box.

    WHY: During training and evaluation, we need to match predictions to truths.
         This matrix is the matching table.
    """
    n_pred = len(predictions)
    n_gt = len(ground_truth)
    iou_matrix = np.zeros((n_pred, n_gt))

    for i, pred in enumerate(predictions):
        for j, gt in enumerate(ground_truth):
            iou_matrix[i, j] = compute_iou(pred['box'], gt['box'])

    return iou_matrix


# ==============================================================================
# STEP 4: NON-MAXIMUM SUPPRESSION (NMS)
# ==============================================================================

def non_maximum_suppression(predictions, iou_threshold=0.5):
    """
    Remove duplicate detections that overlap too much.

    WHY: A detector often fires multiple boxes around the same object.
         NMS keeps the highest-scoring box and deletes its neighbors.
         Without NMS, a single cat might produce 20 boxes.
    """
    if len(predictions) == 0:
        return []

    # Sort predictions by score, highest first
    sorted_preds = sorted(predictions, key=lambda p: p['score'], reverse=True)

    keep = []

    while len(sorted_preds) > 0:
        # Take the best remaining prediction
        best = sorted_preds.pop(0)
        keep.append(best)

        # Remove anything that overlaps too much with this best box
        survivors = []
        for pred in sorted_preds:
            iou = compute_iou(best['box'], pred['box'])
            # If overlap is low, the box might be a different object; keep it
            if iou < iou_threshold:
                survivors.append(pred)

        sorted_preds = survivors

    return keep


# ==============================================================================
# STEP 5: YOLO-STYLE GRID PREDICTION (simulated)
# ==============================================================================

def yolo_grid_prediction(image, grid_size=4):
    """
    Simulate a YOLO-style single-shot grid prediction.

    WHY: Sliding windows are slow because they check every pixel.
         YOLO divides the image into a coarse grid and predicts
         one or two boxes per cell. One forward pass, all boxes.
    """
    h, w = image.shape[:2]
    cell_h = h / grid_size
    cell_w = w / grid_size

    predictions = []

    for row in range(grid_size):
        for col in range(grid_size):
            # Define the cell boundaries
            cx_start = int(col * cell_w)
            cy_start = int(row * cell_h)
            cx_end = int((col + 1) * cell_w)
            cy_end = int((row + 1) * cell_h)

            # Extract cell patch
            patch = image[cy_start:cy_end, cx_start:cx_end]

            # Fake objectness: standard deviation of the patch
            obj_score = float(np.std(patch))

            # If the cell is interesting, predict a box relative to the cell
            if obj_score > 0.12:
                # Predict center offset within the cell (0-1 range)
                offset_x = 0.5  # Simplified: always center
                offset_y = 0.5

                # Predict box size relative to cell size
                width = cell_w * (0.6 + np.random.rand() * 0.4)
                height = cell_h * (0.6 + np.random.rand() * 0.4)

                # Convert to absolute image coordinates
                abs_cx = cx_start + offset_x * cell_w
                abs_cy = cy_start + offset_y * cell_h
                abs_x1 = int(abs_cx - width / 2)
                abs_y1 = int(abs_cy - height / 2)
                abs_x2 = int(abs_cx + width / 2)
                abs_y2 = int(abs_cy + height / 2)

                # Clip to image boundaries
                abs_x1 = max(0, abs_x1)
                abs_y1 = max(0, abs_y1)
                abs_x2 = min(w, abs_x2)
                abs_y2 = min(h, abs_y2)

                predictions.append({
                    'box': [abs_x1, abs_y1, abs_x2, abs_y2],
                    'score': obj_score,
                    'grid_cell': (row, col)
                })

    return predictions


# ==============================================================================
# STEP 6: VISUALIZATION
# ==============================================================================

def draw_boxes_on_image(ax, image, boxes, color='red', linewidth=2, label=None):
    """Draw bounding boxes on a matplotlib axis."""
    ax.imshow(image)
    ax.set_xlim(0, image.shape[1])
    ax.set_ylim(image.shape[0], 0)
    for b in boxes:
        x1, y1, x2, y2 = b['box']
        rect = Rectangle((x1, y1), x2 - x1, y2 - y1,
                         linewidth=linewidth, edgecolor=color,
                         facecolor='none')
        ax.add_patch(rect)
        if label and label in b:
            ax.text(x1, y1 - 2, b[label], color=color, fontsize=8,
                    verticalalignment='bottom')
    ax.axis('off')


def visualize_all(image, ground_truth, sliding_preds, yolo_preds, iou_matrix):
    """
    Create a comprehensive four-panel visualization.

    Panels:
      1. Ground-truth boxes (what the answer should be)
      2. Sliding-window predictions before NMS (noisy, many duplicates)
      3. IoU matrix (how well predictions match truths)
      4. YOLO predictions after NMS (clean, one look)
    """
    fig, axes = plt.subplots(2, 2, figsize=(12, 12))

    # --------------------------------------------------------------------------
    # Panel 1: Ground truth
    # --------------------------------------------------------------------------
    ax = axes[0, 0]
    ax.imshow(image)
    ax.set_title('Ground Truth Boxes', fontsize=12, fontweight='bold')
    for gt in ground_truth:
        x1, y1, x2, y2 = gt['box']
        rect = Rectangle((x1, y1), x2 - x1, y2 - y1,
                         linewidth=2, edgecolor='lime', facecolor='none')
        ax.add_patch(rect)
        ax.text(x1, y1 - 2, gt['class'], color='lime', fontsize=10)
    ax.set_xlim(0, image.shape[1])
    ax.set_ylim(image.shape[0], 0)
    ax.axis('off')

    # --------------------------------------------------------------------------
    # Panel 2: Sliding-window predictions BEFORE NMS
    # --------------------------------------------------------------------------
    ax = axes[0, 1]
    ax.imshow(image)
    ax.set_title('Sliding-Window Predictions (Before NMS)', fontsize=12, fontweight='bold')
    # Color by score: higher score = redder
    for pred in sliding_preds:
        x1, y1, x2, y2 = pred['box']
        alpha = min(1.0, pred['score'] * 2.0)
        rect = Rectangle((x1, y1), x2 - x1, y2 - y1,
                         linewidth=1.5, edgecolor='red',
                         facecolor='none', alpha=alpha)
        ax.add_patch(rect)
    ax.set_xlim(0, image.shape[1])
    ax.set_ylim(image.shape[0], 0)
    ax.axis('off')

    # --------------------------------------------------------------------------
    # Panel 3: IoU Matrix (sliding window vs ground truth)
    # --------------------------------------------------------------------------
    ax = axes[1, 0]
    im = ax.imshow(iou_matrix, cmap='YlOrRd', aspect='auto', vmin=0, vmax=1)
    ax.set_title('IoU Matrix: Predictions vs Ground Truth', fontsize=12, fontweight='bold')
    ax.set_xlabel('Ground Truth Objects')
    ax.set_ylabel('Predicted Boxes')
    ax.set_xticks(np.arange(len(ground_truth)))
    ax.set_xticklabels([gt['class'] for gt in ground_truth])
    ax.set_yticks(np.arange(0, iou_matrix.shape[0], max(1, iou_matrix.shape[0] // 10)))

    # Add colorbar
    plt.colorbar(im, ax=ax, label='IoU')

    # Annotate max IoU per ground-truth column
    for j in range(len(ground_truth)):
        best_i = np.argmax(iou_matrix[:, j])
        ax.text(j, best_i, f'{iou_matrix[best_i, j]:.2f}',
                ha='center', va='center', color='black', fontsize=9)

    # --------------------------------------------------------------------------
    # Panel 4: YOLO predictions AFTER NMS
    # --------------------------------------------------------------------------
    ax = axes[1, 1]
    ax.imshow(image)
    ax.set_title('YOLO-Style Grid + NMS', fontsize=12, fontweight='bold')

    # Run NMS on YOLO predictions
    nms_preds = non_maximum_suppression(yolo_preds, iou_threshold=0.3)

    for pred in nms_preds:
        x1, y1, x2, y2 = pred['box']
        rect = Rectangle((x1, y1), x2 - x1, y2 - y1,
                         linewidth=2, edgecolor='cyan', facecolor='none')
        ax.add_patch(rect)
        ax.text(x1, y1 - 2, f"{pred['score']:.2f}", color='cyan', fontsize=9)

    ax.set_xlim(0, image.shape[1])
    ax.set_ylim(image.shape[0], 0)
    ax.axis('off')

    plt.tight_layout()
    save_path = '/Users/zen/Desktop/building-ai/ai-miden/src/phase78/object_detection.png'
    plt.savefig(save_path, dpi=150)
    print(f"Plot saved to: {save_path}")
    plt.close()


# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":

    print("=" * 60)
    print("PHASE 78: Object Detection & Segmentation")
    print("=" * 60)
    print()

    # --------------------------------------------------------------------------
    # Create synthetic image
    # --------------------------------------------------------------------------
    print("Step 1: Creating synthetic image with shapes...")
    image, ground_truth = create_synthetic_image(size=64)
    print(f"  Image shape: {image.shape}")
    print(f"  Ground-truth objects: {len(ground_truth)}")
    for gt in ground_truth:
        print(f"    {gt['class']:10s} | box={gt['box']}")
    print()

    # --------------------------------------------------------------------------
    # Sliding window
    # --------------------------------------------------------------------------
    print("Step 2: Running sliding-window detector...")
    sliding_preds = sliding_window_predictions(image, window_size=16, stride=8)
    print(f"  Windows generated: {len(sliding_preds)}")
    if sliding_preds:
        print(f"  Top score: {max(p['score'] for p in sliding_preds):.3f}")
    print()

    # --------------------------------------------------------------------------
    # IoU computation
    # --------------------------------------------------------------------------
    print("Step 3: Computing IoU matrix...")
    iou_matrix = compute_iou_matrix(sliding_preds, ground_truth)
    print(f"  Matrix shape: {iou_matrix.shape}")
    for j, gt in enumerate(ground_truth):
        best_iou = np.max(iou_matrix[:, j]) if iou_matrix.shape[0] > 0 else 0.0
        print(f"    Best IoU for {gt['class']:10s}: {best_iou:.3f}")
    print()

    # --------------------------------------------------------------------------
    # NMS demonstration
    # --------------------------------------------------------------------------
    print("Step 4: Applying Non-Maximum Suppression...")
    nms_preds = non_maximum_suppression(sliding_preds, iou_threshold=0.3)
    print(f"  Before NMS: {len(sliding_preds)} boxes")
    print(f"  After NMS:  {len(nms_preds)} boxes")
    print()

    # --------------------------------------------------------------------------
    # YOLO-style grid
    # --------------------------------------------------------------------------
    print("Step 5: Simulating YOLO-style grid prediction...")
    yolo_preds = yolo_grid_prediction(image, grid_size=4)
    print(f"  Grid cells with detections: {len(yolo_preds)}")
    yolo_nms = non_maximum_suppression(yolo_preds, iou_threshold=0.3)
    print(f"  After NMS: {len(yolo_nms)} boxes")
    print()

    # --------------------------------------------------------------------------
    # Visualization
    # --------------------------------------------------------------------------
    print("Step 6: Creating visualization...")
    visualize_all(image, ground_truth, sliding_preds, yolo_preds, iou_matrix)

    # --------------------------------------------------------------------------
    # Summary
    # --------------------------------------------------------------------------
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print()
    print("  WHAT WE BUILT:")
    print("    - Synthetic image with circles and squares")
    print("    - Sliding-window detector (conceptual)")
    print("    - IoU computation for box overlap")
    print("    - Non-Maximum Suppression to remove duplicates")
    print("    - YOLO-style grid prediction (simulated)")
    print("    - Four-panel visualization")
    print()
    print("  KEY INSIGHT:")
    print("    Detection is two problems at once:")
    print("      1. WHERE is the object? (regression)")
    print("      2. WHAT is the object? (classification)")
    print("    IoU turns 'WHERE' into a number we can optimize.")
    print("    NMS turns noisy network outputs into clean predictions.")
    print()
    print("  WHY THIS IS POWERFUL:")
    print("    - Self-driving cars need boxes around pedestrians.")
    print("    - Medical imaging needs boxes around tumors.")
    print("    - Robotics needs to know WHERE to grasp.")
    print()
    print("  NEXT QUESTION:")
    print("    'Boxes are coarse. Can we label every pixel?'")
    print("    The answer: Segmentation.")
    print("=" * 60)
