"""
Minimal ONNX export + inference demo.

ONNX (Open Neural Network Exchange) is a standard format for ML models.
Instead of running PyTorch: model(input) -> output, you:
  1. Export: torch.onnx.export(model, sample_input, "model.onnx")
  2. Load:    onnx.load("model.onnx")
  3. Run:     session.run([output_name], {input_name: data})

Benefits:
  - No PyTorch dependency at inference (lighter, ~50MB vs ~2GB)
  - Vendor-optimized runtimes (ONNX Runtime, TensorRT for Nvidia)
  - Cross-platform (Python, C++, Java, JS, mobile)
  - 2-5x faster inference (operator fusion, graph optimization)
"""

import torch
import torch.nn as nn


def build_toy_model():
    """A simple model that predicts the next token (just for demo)."""
    model = nn.Sequential(
        nn.Linear(64, 32),
        nn.ReLU(),
        nn.Linear(32, 16),
        nn.ReLU(),
        nn.Linear(16, 8),
    )
    model.eval()
    return model


def export_to_onnx(model, sample_input, path="model.onnx"):
    """
    Export a PyTorch model to ONNX format.

    Requirements:
      - model must be in eval() mode
      - sample_input must have the same shape as real input
      - dynamic_axes allows variable batch/sequence lengths
    """
    torch.onnx.export(
        model,
        sample_input,
        path,
        input_names=["input"],
        output_names=["output"],
        dynamic_axes={
            "input": {0: "batch", 1: "sequence"},
            "output": {0: "batch", 1: "sequence"},
        },
        opset_version=14,
    )
    return path


def run_onnx_inference(onnx_path, input_data):
    """Run inference using ONNX Runtime."""
    try:
        import onnxruntime as ort
    except ImportError:
        print("  (onnxruntime not installed — pip install onnxruntime)")
        return None

    session = ort.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])
    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name
    return session.run([output_name], {input_name: input_data.numpy()})[0]


# =============================================================================
# Demo
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("ONNX Export + Inference Demo")
    print("=" * 60)

    model = build_toy_model()
    sample_input = torch.randn(1, 8, 64)  # (batch=1, seq=8, dim=64)

    # PyTorch inference
    with torch.no_grad():
        out_pt = model(sample_input)
    print(f"\n  PyTorch output: {out_pt.sum().item():.4f}")

    # Export to ONNX
    path = export_to_onnx(model, sample_input, "toy_model.onnx")
    print(f"\n  Exported to {path}")
    print(f"  File size: {__import__('os').path.getsize(path):,} bytes")

    # Run with ONNX
    out_onnx = run_onnx_inference(path, sample_input)
    if out_onnx is not None:
        diff = abs(out_pt.sum().item() - out_onnx.sum())
        print(f"\n  ONNX output (approximate): {out_onnx.sum():.4f}")
        print(f"  Difference: {diff:.8f} (should be ~1e-6 or less)")

    print(f"\n{'=' * 60}")
    print("What ONNX does for deployment:")
    print(f"  1. PyTorch -> ONNX (export once)")
    print(f"  2. ONNX -> ONNX Runtime (no PyTorch needed)")
    print(f"  3. ONNX -> TensorRT (Nvidia GPU, 2-5x faster)")
    print(f"  4. ONNX -> ONNX.js (run in browser)")
    print(f"  5. ONNX -> CoreML (run on iPhone)")
    print(f"\nKey insight: ONNX decouples training (PyTorch) from deployment.")
    print(f"Train anywhere. Deploy anywhere. No PyTorch at inference.")
