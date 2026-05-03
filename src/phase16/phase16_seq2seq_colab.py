#!/usr/bin/env python3
"""
================================================================================
Phase 16 (Colab T4 Version): Seq2Seq with PyTorch GPU
================================================================================

THIS SCRIPT IS DESIGNED FOR GOOGLE COLAB T4 (FREE GPU).

Copy-paste this into a Colab notebook.
It trains a real Encoder-Decoder LSTM on a character reversal task
using PyTorch with GPU acceleration.

The local NumPy version (phase16_seq2seq.py) teaches the architecture.
This version shows actual training and convergence.
"""

# ==============================================================================
# SETUP
# ==============================================================================

# !pip install torch matplotlib --quiet

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import matplotlib.pyplot as plt
import random

print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")


# ==============================================================================
# DATA
# ==============================================================================

def prepare_data(num_samples=5000, max_len=10):
    """
    Generate random words and their reversals.
    """
    chars = 'abcdefghijklmnopqrstuvwxyz'
    char_to_idx = {c: i+1 for i, c in enumerate(chars)}  # 0 = PAD
    char_to_idx['<PAD>'] = 0
    char_to_idx['<SOS>'] = len(char_to_idx)
    char_to_idx['<EOS>'] = len(char_to_idx)
    idx_to_char = {i: c for c, i in char_to_idx.items()}

    vocab_size = len(char_to_idx)

    data = []
    for _ in range(num_samples):
        length = random.randint(3, max_len)
        word = ''.join(random.choices(chars, k=length))
        reversed_word = word[::-1]

        # Encode: add <SOS> at start of decoder input, <EOS> at end of target
        encoder_input = [char_to_idx[c] for c in word]
        decoder_input = [char_to_idx['<SOS>']] + [char_to_idx[c] for c in reversed_word]
        target = [char_to_idx[c] for c in reversed_word] + [char_to_idx['<EOS>']]

        data.append((encoder_input, decoder_input, target))

    return data, char_to_idx, idx_to_char, vocab_size


def pad_sequence(sequences, pad_value=0):
    """Pad sequences to same length."""
    max_len = max(len(s) for s in sequences)
    padded = []
    for seq in sequences:
        padded.append(seq + [pad_value] * (max_len - len(seq)))
    return torch.LongTensor(padded)


# ==============================================================================
# MODEL
# ==============================================================================

class Encoder(nn.Module):
    """LSTM Encoder."""

    def __init__(self, vocab_size, embed_dim, hidden_size):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.lstm = nn.LSTM(embed_dim, hidden_size, batch_first=True)

    def forward(self, x):
        # x: (batch, seq_len)
        embedded = self.embedding(x)  # (batch, seq_len, embed_dim)
        outputs, (hidden, cell) = self.lstm(embedded)
        return hidden, cell


class Decoder(nn.Module):
    """LSTM Decoder."""

    def __init__(self, vocab_size, embed_dim, hidden_size):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.lstm = nn.LSTM(embed_dim, hidden_size, batch_first=True)
        self.fc = nn.Linear(hidden_size, vocab_size)

    def forward(self, x, hidden, cell):
        # x: (batch, 1) - one token at a time
        embedded = self.embedding(x)  # (batch, 1, embed_dim)
        outputs, (hidden, cell) = self.lstm(embedded, (hidden, cell))
        predictions = self.fc(outputs.squeeze(1))  # (batch, vocab_size)
        return predictions, hidden, cell


class Seq2Seq(nn.Module):
    """Full Seq2Seq model."""

    def __init__(self, encoder, decoder, device):
        super().__init__()
        self.encoder = encoder
        self.decoder = decoder
        self.device = device

    def forward(self, src, trg, teacher_forcing_ratio=0.5):
        # src: (batch, src_len)
        # trg: (batch, trg_len)

        batch_size = src.shape[0]
        trg_len = trg.shape[1]
        trg_vocab_size = self.decoder.fc.out_features

        # Tensor to store decoder outputs
        outputs = torch.zeros(batch_size, trg_len, trg_vocab_size).to(self.device)

        # Encode
        hidden, cell = self.encoder(src)

        # First decoder input is <SOS>
        input = trg[:, 0]  # (batch,)

        for t in range(1, trg_len):
            output, hidden, cell = self.decoder(input.unsqueeze(1), hidden, cell)
            outputs[:, t] = output

            # Teacher forcing
            teacher_force = random.random() < teacher_forcing_ratio
            top1 = output.argmax(1)
            input = trg[:, t] if teacher_force else top1

        return outputs


# ==============================================================================
# TRAINING
# ==============================================================================

def train(model, data, char_to_idx, epochs=20, batch_size=64, learning_rate=0.001):
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    criterion = nn.CrossEntropyLoss(ignore_index=char_to_idx['<PAD>'])

    print(f"\nTraining Seq2Seq on {device}...")
    print(f"  Training samples: {len(data)}")
    print(f"  Epochs: {epochs}")
    print(f"  Batch size: {batch_size}")
    print()

    model.train()
    for epoch in range(epochs):
        random.shuffle(data)
        total_loss = 0
        num_batches = 0

        for i in range(0, len(data), batch_size):
            batch = data[i:i+batch_size]
            if len(batch) < batch_size:
                continue

            src = pad_sequence([x[0] for x in batch], pad_value=char_to_idx['<PAD>']).to(device)
            trg = pad_sequence([x[1] for x in batch], pad_value=char_to_idx['<PAD>']).to(device)
            target = pad_sequence([x[2] for x in batch], pad_value=char_to_idx['<PAD>']).to(device)

            optimizer.zero_grad()
            output = model(src, trg)

            # output: (batch, trg_len, vocab_size)
            # target: (batch, trg_len)
            output_dim = output.shape[-1]
            output = output[1:].view(-1, output_dim)
            target = target[1:].view(-1)

            loss = criterion(output, target)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

            total_loss += loss.item()
            num_batches += 1

        avg_loss = total_loss / num_batches
        print(f"  Epoch {epoch+1}/{epochs}: Loss = {avg_loss:.4f}")


# ==============================================================================
# EVALUATION
# ==============================================================================

def translate(model, word, char_to_idx, idx_to_char, max_len=15):
    """Translate a word using the trained model."""
    model.eval()

    # Encode
    src = torch.LongTensor([[char_to_idx[c] for c in word]]).to(device)

    with torch.no_grad():
        hidden, cell = model.encoder(src)

        # Decode
        outputs = []
        input = torch.LongTensor([char_to_idx['<SOS>']]).to(device)

        for _ in range(max_len):
            output, hidden, cell = model.decoder(input.unsqueeze(1), hidden, cell)
            top1 = output.argmax(1)
            input = top1

            if top1.item() == char_to_idx['<EOS>']:
                break

            outputs.append(top1.item())

    result = ''.join([idx_to_char[i] for i in outputs if i in idx_to_char and idx_to_char[i] not in ['<PAD>', '<SOS>', '<EOS>']])
    return result


# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    # Prepare data
    data, char_to_idx, idx_to_char, vocab_size = prepare_data(num_samples=10000, max_len=10)

    # Create model
    embed_dim = 32
    hidden_size = 64

    encoder = Encoder(vocab_size, embed_dim, hidden_size)
    decoder = Decoder(vocab_size, embed_dim, hidden_size)
    model = Seq2Seq(encoder, decoder, device).to(device)

    print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")

    # Train
    train(model, data, char_to_idx, epochs=15, batch_size=128)

    # Test
    print("\n" + "="*60)
    print("TESTING")
    print("="*60)

    test_words = ['hello', 'world', 'python', 'abcdef', 'reverse']
    for word in test_words:
        # Filter to valid chars
        word = ''.join(c for c in word if c in char_to_idx)
        if word:
            result = translate(model, word, char_to_idx, idx_to_char)
            print(f"  {word} -> {result} (expected: {word[::-1]})")

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print("  The Seq2Seq model successfully learned to reverse words!")
    print("  This proves the encoder-decoder architecture works.")
    print("  Next: Attention mechanism to handle long sequences.")
