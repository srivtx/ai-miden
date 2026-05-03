#!/usr/bin/env python3
"""
================================================================================
Phase 21 (Colab T4): Training a Tiny GPT — Character-Level Generation
================================================================================

Copy-paste into Google Colab with T4 GPU.
This trains a real character-level GPT on a text corpus.

For best results, upload a text file (e.g., Shakespeare, Wikipedia excerpt)
and change TEXT_FILE to the path.
"""

import torch
import torch.nn as nn
import torch.optim as optim
import math
import random

print(f"PyTorch: {torch.__version__}")
print(f"CUDA: {torch.cuda.is_available()}")
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


# ==============================================================================
# DATA
# ==============================================================================

def load_data(text_file=None):
    """Load text data. If no file, use a small built-in corpus."""
    if text_file:
        with open(text_file, 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        text = """To be, or not to be, that is the question:
Whether 'tis nobler in the mind to suffer
The slings and arrows of outrageous fortune,
Or to take arms against a sea of troubles
And by opposing end them. To die—to sleep,
No more; and by a sleep to say we end
The heart-ache and the thousand natural shocks
That flesh is heir to: 'tis a consummation
Devoutly to be wish'd. To die, to sleep;
To sleep, perchance to dream—ay, there's the rub:
For in that sleep of death what dreams may come,
When we have shuffled off this mortal coil,
Must give us pause—there's the respect
That makes calamity of so long life.
"""

    chars = sorted(set(text))
    char_to_idx = {c: i for i, c in enumerate(chars)}
    idx_to_char = {i: c for i, c in enumerate(chars)}

    data = [char_to_idx[c] for c in text]
    return data, chars, char_to_idx, idx_to_char, text


def get_batch(data, batch_size, seq_len):
    """Get a random batch of sequences."""
    ix = torch.randint(len(data) - seq_len, (batch_size,))
    x = torch.stack([torch.tensor(data[i:i+seq_len]) for i in ix])
    y = torch.stack([torch.tensor(data[i+1:i+seq_len+1]) for i in ix])
    return x, y


# ==============================================================================
# MODEL
# ==============================================================================

class TinyGPT(nn.Module):
    def __init__(self, vocab_size, d_model=256, nhead=8, num_layers=6, dim_ff=1024, max_len=512, dropout=0.1):
        super().__init__()
        self.d_model = d_model
        self.max_len = max_len

        self.token_emb = nn.Embedding(vocab_size, d_model)
        self.pos_emb = nn.Embedding(max_len, d_model)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=nhead, dim_feedforward=dim_ff,
            dropout=dropout, batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.fc = nn.Linear(d_model, vocab_size)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        B, T = x.shape
        positions = torch.arange(0, T, device=x.device).unsqueeze(0)
        x = self.dropout(self.token_emb(x) + self.pos_emb(positions))

        # Causal mask
        mask = nn.Transformer.generate_square_subsequent_mask(T).to(x.device)
        x = self.transformer(x, mask=mask, is_causal=True)
        return self.fc(x)

    def generate(self, idx, max_new_tokens, temperature=1.0, top_k=None):
        """Generate text from a seed."""
        self.eval()
        for _ in range(max_new_tokens):
            idx_cond = idx[:, -self.max_len:]
            logits = self(idx_cond)
            logits = logits[:, -1, :] / temperature

            if top_k is not None:
                v, _ = torch.topk(logits, min(top_k, logits.size(-1)))
                logits[logits < v[:, [-1]]] = -float('Inf')

            probs = torch.softmax(logits, dim=-1)
            idx_next = torch.multinomial(probs, num_samples=1)
            idx = torch.cat((idx, idx_next), dim=1)

        return idx


# ==============================================================================
# TRAINING
# ==============================================================================

def train(model, data, epochs=5000, batch_size=64, seq_len=128, lr=0.001, eval_interval=500):
    optimizer = optim.AdamW(model.parameters(), lr=lr, betas=(0.9, 0.99))
    criterion = nn.CrossEntropyLoss()

    print(f"\nTraining Tiny GPT on {device}...")
    print(f"Parameters: {sum(p.numel() for p in model.parameters()):,}")
    print(f"Data size: {len(data):,} characters")
    print(f"Epochs: {epochs}, Batch: {batch_size}, Seq: {seq_len}")
    print()

    model.train()
    for epoch in range(epochs):
        x, y = get_batch(data, batch_size, seq_len)
        x, y = x.to(device), y.to(device)

        logits = model(x)
        loss = criterion(logits.view(-1, logits.size(-1)), y.view(-1))

        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()

        if epoch % eval_interval == 0:
            print(f"  Step {epoch:5d}: Loss = {loss.item():.4f}")

    print(f"\nFinal Loss: {loss.item():.4f}")


# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    # Load data
    # Set TEXT_FILE to a .txt file path for larger training
    TEXT_FILE = None
    data, chars, char_to_idx, idx_to_char, text = load_data(TEXT_FILE)

    # Create model
    vocab_size = len(chars)
    model = TinyGPT(
        vocab_size=vocab_size,
        d_model=256,
        nhead=8,
        num_layers=6,
        dim_ff=1024,
        max_len=512
    ).to(device)

    # Train
    train(model, data, epochs=5000, batch_size=64, seq_len=128, lr=0.001)

    # Generate
    print("\n" + "="*60)
    print("GENERATING TEXT")
    print("="*60)

    seeds = ["To be, ", "Whether ", "For in "]

    for seed in seeds:
        seed_idx = torch.tensor([[char_to_idx[c] for c in seed]]).to(device)
        generated = model.generate(seed_idx, max_new_tokens=200, temperature=0.8, top_k=40)
        text_generated = ''.join([idx_to_char[i] for i in generated[0].tolist()])
        print(f"\nSeed: '{seed}'")
        print(f"Generated:\n{text_generated}\n")

    print("Tiny GPT trained and generated text successfully!")
