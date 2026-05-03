#!/usr/bin/env python3
"""
================================================================================
Phase 78 (Colab): Object Detection & Segmentation — Real Models
================================================================================

Copy-paste into Google Colab with T4 GPU.

This script demonstrates real object detection and segmentation using
pre-trained PyTorch models. We do not train anything. We LOAD weights
that took millions of GPU-hours to learn, then USE them.

WHY: You cannot build a detector from scratch in NumPy and expect it
to work on real photos. The architecture is simple; the weights are magic.
This script shows what the "magic" looks like in practice.

Sections:
  1. Create or load sample images
  2. Load a pre-trained object detection model (Faster R-CNN / DETR-style)
  3. Run inference, decode outputs, draw boxes and labels
  4. Load a pre-trained semantic segmentation model (FCN / DeepLabV3)
  5. Run inference, produce per-pixel class map, visualize overlay
================================================================================
"""

import torch
import torchvision
from torchvision import transforms
from torchvision.models.detection import fasterrcnn_resnet50_fpn
from torchvision.models.segmentation import fcn_resnet50

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

print(f"PyTorch: {torch.__version__}")
print(f"CUDA: {torch.cuda.is_available()}")
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


# ==============================================================================
# SECTION 1: SAMPLE IMAGES
# ==============================================================================

def create_sample_images():
    """
    Generate synthetic sample images so the script runs without uploads.

    WHY: Colab users may not have images handy. Synthetic images let us
    test the pipeline instantly. In practice, you would load real photos.
    """
    images = []

    # --- Image 1: Simple shapes ---
    img1 = Image.new('RGB', (256, 256), color=(240, 240, 240))
    draw1 = ImageDraw.Draw(img1)
    # Red rectangle
    draw1.rectangle([40, 40, 100, 100], fill=(200, 60, 60), outline=(0, 0, 0), width=2)
    # Blue ellipse
    draw1.ellipse([150, 50, 210, 110], fill=(60, 60, 200), outline=(0, 0, 0), width=2)
    # Green rectangle
    draw1.rectangle([80, 160, 160, 220], fill=(60, 180, 60), outline=(0, 0, 0), width=2)
    images.append(('shapes', img1))

    # --- Image 2: Street scene simulation ---
    img2 = Image.new('RGB', (320, 240), color=(135, 206, 235))  # Sky
    draw2 = ImageDraw.Draw(img2)
    # Road
    draw2.rectangle([0, 160, 320, 240], fill=(80, 80, 80))
    # Building
    draw2.rectangle([20, 40, 120, 180], fill=(180, 150, 120), outline=(60, 40, 30), width=2)
    # Car
    draw2.rectangle([180, 170, 260, 200], fill=(200, 50, 50), outline=(0, 0, 0), width=2)
    draw2.ellipse([190, 195, 210, 215], fill=(30, 30, 30))
    draw2.ellipse([230, 195, 250, 215], fill=(30, 30, 30))
    # Person
    draw2.ellipse([140, 140, 160, 160], fill=(255, 220, 180))  # head
    draw2.rectangle([145, 160, 155, 200], fill=(40, 40, 120))  # body
    images.append(('street_sim', img2))

    return images


# ==============================================================================
# SECTION 2: OBJECT DETECTION MODEL
# ==============================================================================

def load_detection_model():
    """
    Load a pre-trained Faster R-CNN with ResNet-50 FPN backbone.

    WHY: We use a model already trained on COCO (330K images, 80 classes).
    Training this from scratch would cost thousands of dollars in GPU time.
    Loading pre-trained weights is the standard way to do detection in practice.

    NOTE: YOLO and DETR follow the same pattern:
      - Load architecture + weights
      - Forward pass the image
      - Decode boxes, scores, and labels
      - Filter by confidence threshold
    The difference is internal architecture, not the usage pattern.
    """
    print("Loading pre-trained Faster R-CNN...")
    model = fasterrcnn_resnet50_fpn(weights='DEFAULT')
    model.to(device)
    model.eval()
    print("Model loaded. Classes: COCO (person, car, dog, etc.)")
    return model


# COCO class names (first 21 shown; model has 91 with background)
COCO_INSTANCE_CATEGORY_NAMES = [
    '__background__', 'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus',
    'train', 'truck', 'boat', 'traffic light', 'fire hydrant', 'N/A', 'stop sign',
    'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow',
    'elephant', 'bear', 'zebra', 'giraffe', 'N/A', 'backpack', 'umbrella', 'N/A', 'N/A',
    'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
    'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket',
    'bottle', 'N/A', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl',
    'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza',
    'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed', 'N/A', 'dining table',
    'N/A', 'N/A', 'toilet', 'N/A', 'tv', 'laptop', 'mouse', 'remote', 'keyboard',
    'cell phone', 'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'N/A',
    'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush'
]


def detect_objects(model, image_pil, score_threshold=0.5):
    """
    Run object detection on a PIL image.

    WHY: The model expects a normalized torch tensor. We convert the PIL
    image, batch it, run inference, then decode the outputs back into
    human-readable boxes, labels, and confidence scores.
    """
    # Convert PIL to tensor and normalize
    # These are the standard ImageNet normalization values
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225])
    ])
    image_tensor = transform(image_pil).to(device)

    # The model expects a list of images (batched)
    with torch.no_grad():
        predictions = model([image_tensor])

    # predictions[0] is a dict with 'boxes', 'labels', 'scores'
    pred = predictions[0]
    boxes = pred['boxes'].cpu().numpy()
    labels = pred['labels'].cpu().numpy()
    scores = pred['scores'].cpu().numpy()

    # Filter by confidence threshold
    # WHY: The model outputs EVERYTHING it thinks might be an object.
    # Most of those guesses are garbage. Thresholding keeps only the confident ones.
    keep = scores >= score_threshold
    boxes = boxes[keep]
    labels = labels[keep]
    scores = scores[keep]

    results = []
    for box, label, score in zip(boxes, labels, scores):
        name = COCO_INSTANCE_CATEGORY_NAMES[label] if label < len(COCO_INSTANCE_CATEGORY_NAMES) else 'N/A'
        results.append({
            'box': [float(b) for b in box],  # [x1, y1, x2, y2]
            'label': name,
            'score': float(score)
        })

    return results


def visualize_detections(image_pil, detections, title="Detections"):
    """
    Draw bounding boxes and labels on the image.

    WHY: Raw tensors are meaningless. Visualization proves the model
    actually found something and lets us judge whether the boxes make sense.
    """
    fig, ax = plt.subplots(1, figsize=(8, 6))
    ax.imshow(image_pil)

    for det in detections:
        x1, y1, x2, y2 = det['box']
        label = det['label']
        score = det['score']

        # Draw rectangle
        rect = plt.Rectangle((x1, y1), x2 - x1, y2 - y1,
                             fill=False, edgecolor='lime', linewidth=2)
        ax.add_patch(rect)

        # Draw label
        ax.text(x1, y1 - 5, f"{label} {score:.2f}",
                color='white', fontsize=10,
                bbox=dict(facecolor='lime', alpha=0.7, edgecolor='none', pad=1))

    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.axis('off')
    return fig


# ==============================================================================
# SECTION 3: SEMANTIC SEGMENTATION MODEL
# ==============================================================================

def load_segmentation_model():
    """
    Load a pre-trained FCN-ResNet50 for semantic segmentation.

    WHY: FCN (Fully Convolutional Network) replaces the final classification
    layers of a classifier with upsampling layers, producing a dense prediction
    for every pixel instead of one label for the whole image.
    """
    print("Loading pre-trained FCN-ResNet50 segmentation model...")
    model = fcn_resnet50(weights='DEFAULT')
    model.to(device)
    model.eval()
    print("Segmentation model loaded. 21 classes (Pascal VOC).")
    return model


PASCAL_VOC_CLASSES = [
    'background', 'aeroplane', 'bicycle', 'bird', 'boat', 'bottle', 'bus',
    'car', 'cat', 'chair', 'cow', 'diningtable', 'dog', 'horse', 'motorbike',
    'person', 'pottedplant', 'sheep', 'sofa', 'train', 'tvmonitor'
]

# Color map for visualization (RGB tuples)
PASCAL_VOC_COLORS = [
    (0, 0, 0), (128, 0, 0), (0, 128, 0), (128, 128, 0), (0, 0, 128),
    (128, 0, 128), (0, 128, 128), (128, 128, 128), (64, 0, 0), (192, 0, 0),
    (64, 128, 0), (192, 128, 0), (64, 0, 128), (192, 0, 128), (64, 128, 128),
    (192, 128, 128), (0, 64, 0), (128, 64, 0), (0, 192, 0), (128, 192, 0),
    (0, 64, 128)
]


def segment_image(model, image_pil):
    """
    Run semantic segmentation on a PIL image.

    WHY: The model outputs a score for every class at every pixel.
    We take the argmax to get the winning class per pixel.
    """
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225])
    ])
    image_tensor = transform(image_pil).to(device)

    with torch.no_grad():
        output = model(image_tensor.unsqueeze(0))['out']

    # output shape: (1, num_classes, H, W)
    # argmax over class dimension gives the predicted class for each pixel
    seg_map = torch.argmax(output.squeeze(), dim=0).cpu().numpy()
    return seg_map


def visualize_segmentation(image_pil, seg_map, title="Segmentation"):
    """
    Overlay the segmentation mask on the original image.

    WHY: Raw class IDs are just numbers. A colored overlay shows WHICH
    pixels belong to WHICH class in a way humans understand instantly.
    """
    h, w = seg_map.shape
    color_mask = np.zeros((h, w, 3), dtype=np.uint8)

    for cls_id in range(len(PASCAL_VOC_COLORS)):
        color_mask[seg_map == cls_id] = PASCAL_VOC_COLORS[cls_id]

    # Resize color mask to original image size if needed
    if color_mask.shape[0] != image_pil.height or color_mask.shape[1] != image_pil.width:
        color_mask = np.array(Image.fromarray(color_mask).resize((image_pil.width, image_pil.height), Image.NEAREST))

    image_np = np.array(image_pil)

    # Blend original and mask
    alpha = 0.5
    blended = (image_np * (1 - alpha) + color_mask * alpha).astype(np.uint8)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    axes[0].imshow(image_np)
    axes[0].set_title("Original Image", fontsize=11, fontweight='bold')
    axes[0].axis('off')

    axes[1].imshow(color_mask)
    axes[1].set_title("Segmentation Mask", fontsize=11, fontweight='bold')
    axes[1].axis('off')

    axes[2].imshow(blended)
    axes[2].set_title("Overlay", fontsize=11, fontweight='bold')
    axes[2].axis('off')

    fig.suptitle(title, fontsize=13, fontweight='bold')
    plt.tight_layout()
    return fig


# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":

    print("=" * 60)
    print("PHASE 78 Colab: Real Detection & Segmentation")
    print("=" * 60)
    print()

    # --------------------------------------------------------------------------
    # Create sample images
    # --------------------------------------------------------------------------
    print("Step 1: Creating sample images...")
    sample_images = create_sample_images()
    for name, img in sample_images:
        print(f"  - {name}: {img.size}")
    print()

    # --------------------------------------------------------------------------
    # Load detection model
    # --------------------------------------------------------------------------
    print("Step 2: Loading detection model...")
    det_model = load_detection_model()
    print()

    # --------------------------------------------------------------------------
    # Run detection
    # --------------------------------------------------------------------------
    print("Step 3: Running object detection...")
    all_det_figs = []
    for name, img in sample_images:
        dets = detect_objects(det_model, img, score_threshold=0.3)
        print(f"  {name}: {len(dets)} detections")
        for d in dets:
            print(f"    - {d['label']:15s} | score={d['score']:.3f} | box={d['box']}")
        fig = visualize_detections(img, dets, title=f"Detections: {name}")
        all_det_figs.append((name, fig))
    print()

    # --------------------------------------------------------------------------
    # Load segmentation model
    # --------------------------------------------------------------------------
    print("Step 4: Loading segmentation model...")
    seg_model = load_segmentation_model()
    print()

    # --------------------------------------------------------------------------
    # Run segmentation
    # --------------------------------------------------------------------------
    print("Step 5: Running semantic segmentation...")
    all_seg_figs = []
    for name, img in sample_images:
        seg_map = segment_image(seg_model, img)
        print(f"  {name}: segmentation map shape {seg_map.shape}")
        unique_classes = np.unique(seg_map)
        class_names = [PASCAL_VOC_CLASSES[i] for i in unique_classes if i < len(PASCAL_VOC_CLASSES)]
        print(f"    Classes found: {', '.join(class_names)}")
        fig = visualize_segmentation(img, seg_map, title=f"Segmentation: {name}")
        all_seg_figs.append((name, fig))
    print()

    # --------------------------------------------------------------------------
    # Save visualizations
    # --------------------------------------------------------------------------
    print("Step 6: Saving visualizations...")
    for name, fig in all_det_figs:
        path = f"/content/phase78_detection_{name}.png"
        fig.savefig(path, dpi=150, bbox_inches='tight')
        print(f"  Saved: {path}")
        plt.close(fig)

    for name, fig in all_seg_figs:
        path = f"/content/phase78_segmentation_{name}.png"
        fig.savefig(path, dpi=150, bbox_inches='tight')
        print(f"  Saved: {path}")
        plt.close(fig)

    # --------------------------------------------------------------------------
    # Summary
    # --------------------------------------------------------------------------
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print()
    print("  WHAT WE DID:")
    print("    - Generated synthetic sample images")
    print("    - Loaded a pre-trained Faster R-CNN detector")
    print("    - Ran inference, filtered by confidence, drew boxes/labels")
    print("    - Loaded a pre-trained FCN-ResNet50 segmentation model")
    print("    - Produced per-pixel class maps and overlay visualizations")
    print()
    print("  KEY INSIGHT:")
    print("    Detection gives you WHERE + WHAT (boxes).")
    print("    Segmentation gives you WHICH PIXEL + WHAT (masks).")
    print("    Both use the same backbone idea:")
    print("      - Extract features with a deep CNN")
    print("      - Add a task-specific head (detector head or upsampling head)")
    print()
    print("  WHY THIS MATTERS:")
    print("    - Pre-trained models let you solve vision tasks in minutes,")
    print("      not months of GPU training.")
    print("    - Thresholding and NMS turn raw network outputs into")
    print("      actionable predictions.")
    print("    - Segmentation is essential for medical imaging, autonomous")
    print("      driving, and any task where pixel boundaries matter.")
    print()
    print("  NEXT QUESTION:")
    print("    'These models are huge and slow. How do we run them")
    print("     on a phone or edge device in real time?'")
    print("    The answer: quantization, pruning, and mobile-optimized")
    print("    architectures like MobileNet-SSD.")
    print("=" * 60)
