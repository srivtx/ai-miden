"""
Minimal LoRA (Low-Rank Adaptation).

The idea: When fine-tuning, the weight update DeltaW is low-rank.
Instead of updating all of W, freeze W and train A and B where
DeltaW = A * B. For rank r=4, this is ~0.1% of parameters.

  Standard: h = Wx          (update W: d*k params)
  LoRA:     h = Wx + ABx    (update A: d*r, B: r*k)

At inference, merge: W_new = W + A*B. Zero overhead.
"""

import torch
import torch.nn as nn


class LoRALinear(nn.Module):
    """
    A linear layer augmented with a low-rank adapter.

    During fine-tuning: h = Wx + (alpha/r) * (AB)x
    During inference:   h = W_merged * x  (merge once, zero overhead)
    """

    def __init__(self, in_features, out_features, r=4, alpha=1.0, bias=False):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.r = r

        # Frozen pre-trained weight
        self.weight = nn.Parameter(torch.randn(out_features, in_features) * 0.02)
        self.weight.requires_grad = False

        if bias:
            self.bias = nn.Parameter(torch.zeros(out_features))
        else:
            self.register_parameter("bias", None)

        # LoRA parameters (trainable)
        # A: (out_features, r) — projects down
        # B: (r, in_features) — projects up
        self.lora_A = nn.Parameter(torch.zeros(out_features, r))
        self.lora_B = nn.Parameter(torch.zeros(r, in_features))
        self.reset_lora_parameters()

        self.scaling = alpha / r

        # Whether the adapter is active
        self.merged = False

    def reset_lora_parameters(self):
        """Initialize A with zeros, B with normal(0, sigma^2)."""
        nn.init.zeros_(self.lora_A)
        nn.init.normal_(self.lora_B, std=1.0 / self.r)

    def forward(self, x):
        # Base output
        out = nn.functional.linear(x, self.weight, self.bias)

        if not self.merged:
            # LoRA output: (x @ B^T) @ A^T * scaling
            lora_out = (x @ self.lora_B.T) @ self.lora_A.T * self.scaling
            out = out + lora_out

        return out

    def merge(self):
        """Merge LoRA weights into the base weight. Irreversible."""
        if not self.merged:
            delta = (self.lora_A @ self.lora_B) * self.scaling
            self.weight.data = self.weight.data + delta
            self.merged = True

    def unmerge(self):
        """Separate LoRA weights from the base weight. Reversible."""
        if self.merged:
            delta = (self.lora_A @ self.lora_B) * self.scaling
            self.weight.data = self.weight.data - delta
            self.merged = False


# =============================================================================
# Demo: compare LoRA vs full fine-tune on a toy regression
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("LoRA Demo: toy regression")
    print("=" * 60)

    # Toy data: y = 3*x1 - 2*x2 + noise
    torch.manual_seed(42)
    n_samples = 200
    X = torch.randn(n_samples, 2)
    y = 3 * X[:, 0] - 2 * X[:, 1] + 0.1 * torch.randn(n_samples)

    # Pre-trained model (trained on different data: y = x1 + x2)
    print("\nPre-training on y = x1 + x2...")
    base = nn.Linear(2, 1)
    opt = torch.optim.Adam(base.parameters(), lr=0.01)
    X_pretrain = torch.randn(500, 2)
    y_pretrain = X_pretrain[:, 0] + X_pretrain[:, 1]
    for _ in range(500):
        loss = nn.functional.mse_loss(base(X_pretrain), y_pretrain.unsqueeze(-1))
        opt.zero_grad()
        loss.backward()
        opt.step()
    print(f"  Base weights: {base.weight.data.numpy().ravel()}")

    # Full fine-tune
    print("\nFull fine-tune on y = 3*x1 - 2*x2...")
    model_full = nn.Linear(2, 1)
    model_full.weight.data = base.weight.data.clone()
    opt_full = torch.optim.Adam(model_full.parameters(), lr=0.01)
    for _ in range(200):
        loss = nn.functional.mse_loss(model_full(X), y.unsqueeze(-1))
        opt_full.zero_grad()
        loss.backward()
        opt_full.step()
    print(f"  Fine-tuned weights: {model_full.weight.data.numpy().ravel()}")
    print(f"  Target: [3.0, -2.0]")

    # LoRA fine-tune
    print("\nLoRA fine-tune (r=2, alpha=4, 50% of params)...")
    model_lora = LoRALinear(2, 1, r=2, alpha=4.0)
    model_lora.weight.data = base.weight.data.clone()
    opt_lora = torch.optim.Adam([model_lora.lora_A, model_lora.lora_B], lr=0.01)

    for step in range(200):
        loss = nn.functional.mse_loss(model_lora(X), y.unsqueeze(-1))
        opt_lora.zero_grad()
        loss.backward()
        opt_lora.step()

    model_lora.merge()
    print(f"  Merged weights:     {model_lora.weight.data.numpy().ravel()}")
    print(f"  Target: [3.0, -2.0]")

    # Compare: how many parameters were trained?
    n_full = sum(p.numel() for p in model_full.parameters())
    n_lora = sum(p.numel() for p in [model_lora.lora_A, model_lora.lora_B])
    print(f"\n  Full fine-tune params: {n_full} (100%)")
    print(f"  LoRA params:           {n_lora} ({100*n_lora/n_full:.0f}%)")

    # Show the adapter matrices
    print(f"\n  LoRA A (2x2): {model_lora.lora_A.data}")
    print(f"  LoRA B (1x2): {model_lora.lora_B.data}")
    print(f"  DeltaW = A*B: {(model_lora.lora_A @ model_lora.lora_B).data}")
    print(f"  Scaling:      {model_lora.scaling}")

    print(f"\nKey insight: LoRA trains {n_lora} parameters instead of {n_full}.")
    print(f"The adapter captures the DELTA between the pre-trained weights")
    print(f"and the fine-tuned weights. Most of the change is low-rank.")
