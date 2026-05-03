#!/usr/bin/env python3
"""
================================================================================
Phase 18 (Colab T4 Version): Transformer with PyTorch GPU
================================================================================

THIS SCRIPT IS DESIGNED FOR GOOGLE COLAB T4 (FREE GPU).

Copy-paste this into a Colab notebook.
It trains a small Transformer on a character-level language modeling task.
This proves the Transformer architecture works end-to-end.
"""

# ==============================================================================
# SETUP
# ==============================================================================

# !pip install torch matplotlib --quiet

import torch
import torch.nn as nn
import torch.optim as optim
import math
import numpy as np
import matplotlib.pyplot as plt

print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")


# ==============================================================================
# POSITIONAL ENCODING
# ==============================================================================

class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=5000):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe.unsqueeze(0))

    def forward(self, x):
        return x + self.pe[:, :x.size(1)]


# ==============================================================================
# TRANSFORMER MODEL
# ==============================================================================

class TinyTransformer(nn.Module):
    def __init__(self, vocab_size, d_model=64, nhead=4, num_layers=2, dim_feedforward=256, max_len=128):
        super().__init__()
        self.d_model = d_model
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_encoder = PositionalEncoding(d_model, max_len)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)

        self.fc_out = nn.Linear(d_model, vocab_size)

    def forward(self, x):
        # x: (batch, seq_len)
        x = self.embedding(x) * math.sqrt(self.d_model)
        x = self.pos_encoder(x)

        # Create causal mask (prevent looking at future tokens)
        mask = nn.Transformer.generate_square_subsequent_mask(x.size(1)).to(x.device)

        x = self.transformer(x, mask=mask, is_causal=True)
        x = self.fc_out(x)
        return x


# ==============================================================================
# DATA
# ==============================================================================

def prepare_data(text, seq_len=32):
    """Prepare character-level data."""
    chars = sorted(set(text))
    char_to_idx = {c: i for i, c in enumerate(chars)}
    idx_to_char = {i: c for i, c in enumerate(chars)}

    data = [char_to_idx[c] for c in text]

    # Create sequences
    sequences = []
    for i in range(0, len(data) - seq_len - 1, seq_len):
        sequences.append((data[i:i+seq_len], data[i+1:i+seq_len+1]))

    return sequences, char_to_idx, idx_to_char


# ==============================================================================
# TRAINING
# ==============================================================================

def train(model, data, epochs=20, batch_size=64, lr=0.001):
    optimizer = optim.Adam(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()

    print(f"\nTraining Transformer on {device}...")
    print(f"  Training sequences: {len(data)}")
    print(f"  Parameters: {sum(p.numel() for p in model.parameters()):,}")
    print()

    model.train()
    for epoch in range(epochs):
        total_loss = 0
        num_batches = 0

        # Shuffle and batch
        import random
        random.shuffle(data)

        for i in range(0, len(data), batch_size):
            batch = data[i:i+batch_size]
            if len(batch) < batch_size:
                continue

            src = torch.LongTensor([x[0] for x in batch]).to(device)
            tgt = torch.LongTensor([x[1] for x in batch]).to(device)

            optimizer.zero_grad()
            output = model(src)

            loss = criterion(output.view(-1, output.size(-1)), tgt.view(-1))
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

            total_loss += loss.item()
            num_batches += 1

        print(f"  Epoch {epoch+1}/{epochs}: Loss = {total_loss/num_batches:.4f}")


# ==============================================================================
# GENERATION
# ==============================================================================

def generate(model, seed_text, char_to_idx, idx_to_char, length=100, temperature=1.0):
    """Generate text from a seed."""
    model.eval()

    input_seq = [char_to_idx[c] for c in seed_text]
    input_tensor = torch.LongTensor([input_seq]).to(device)

    generated = list(seed_text)

    with torch.no_grad():
        for _ in range(length):
            output = model(input_tensor)
            logits = output[0, -1] / temperature
            probs = torch.softmax(logits, dim=-1)
            next_char_idx = torch.multinomial(probs, 1).item()

            generated.append(idx_to_char[next_char_idx])
            input_seq = input_seq[1:] + [next_char_idx]
            input_tensor = torch.LongTensor([input_seq]).to(device)

    return ''.join(generated)


# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    # Small example text (use a larger corpus for better results)
    text = """the cat sat on the mat and looked at the mouse
the dog ran in the park and chased the ball
the bird flew in the sky and sang a song
the fish swam in the water and ate some food
a cat and a dog played together in the garden
the sun shone brightly on a beautiful day
children laughed and played in the park"""

    seq_len = 32
    data, char_to_idx, idx_to_char = prepare_data(text, seq_len)
    vocab_size = len(char_to_idx)

    model = TinyTransformer(vocab_size, d_model=64, nhead=4, num_layers=2).to(device)

    train(model, data, epochs=50, batch_size=8, lr=0.005)

    print("\n" + "="*60)
    print("GENERATING TEXT")
    print("="*60)

    for seed in ["the cat", "the dog", "a bird"]:
        generated = generate(model, seed, char_to_idx, idx_to_char, length=50)
        print(f"\n  Seed: '{seed}'")
        print(f"  Generated: '{generated}'")

    print("\nTransformer trained successfully!")
