#!/usr/bin/env python3
"""
================================================================================
Phase 20 (Colab T4): GPT with Causal Masking
================================================================================

Copy-paste into Google Colab with T4 GPU.
Demonstrates GPT-style autoregressive generation.
"""

import torch
import torch.nn as nn
import torch.optim as optim
import math

print(f"CUDA: {torch.cuda.is_available()}")
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


class GPTDecoder(nn.Module):
    def __init__(self, vocab_size, d_model=128, nhead=4, num_layers=4, dim_ff=512, max_len=512):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_encoding = nn.Embedding(max_len, d_model)

        decoder_layer = nn.TransformerDecoderLayer(
            d_model=d_model, nhead=nhead, dim_feedforward=dim_ff,
            batch_first=True, dropout=0.1
        )
        self.transformer = nn.TransformerDecoder(decoder_layer, num_layers=num_layers)
        self.fc = nn.Linear(d_model, vocab_size)

    def forward(self, x):
        positions = torch.arange(0, x.size(1)).unsqueeze(0).to(x.device)
        x = self.embedding(x) + self.pos_encoding(positions)

        # Causal mask
        mask = nn.Transformer.generate_square_subsequent_mask(x.size(1)).to(x.device)
        x = self.transformer(x, x, tgt_mask=mask, tgt_is_causal=True)
        return self.fc(x)


def prepare_data():
    text = "the cat sat on the mat and looked at the mouse the dog ran in the park and chased the ball the bird flew in the sky and sang a song"
    words = text.split()
    vocab = sorted(set(words))
    word_to_idx = {w: i for i, w in enumerate(vocab)}
    idx_to_word = {i: w for i, w in enumerate(vocab)}

    # Create sequences
    seq_len = 8
    data = []
    for i in range(len(words) - seq_len):
        data.append(([word_to_idx[w] for w in words[i:i+seq_len]],
                     [word_to_idx[w] for w in words[i+1:i+seq_len+1]]))

    return data, vocab, word_to_idx, idx_to_word


def train(model, data, epochs=100, lr=0.001, batch_size=32):
    optimizer = optim.Adam(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()

    print(f"Training GPT on {device}...")
    print(f"Training sequences: {len(data)}")

    for epoch in range(epochs):
        import random
        random.shuffle(data)
        total_loss = 0
        count = 0

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
            optimizer.step()

            total_loss += loss.item()
            count += 1

        if epoch % 20 == 0:
            print(f"  Epoch {epoch}: Loss = {total_loss/count:.4f}")


def generate(model, seed_words, word_to_idx, idx_to_word, length=20):
    model.eval()
    generated = [word_to_idx[w] for w in seed_words if w in word_to_idx]

    with torch.no_grad():
        for _ in range(length):
            src = torch.LongTensor([generated[-16:]]).to(device)
            output = model(src)
            next_word = output[0, -1].argmax().item()
            generated.append(next_word)

    return ' '.join([idx_to_word[i] for i in generated])


if __name__ == "__main__":
    data, vocab, word_to_idx, idx_to_word = prepare_data()
    model = GPTDecoder(len(vocab), d_model=64, nhead=4, num_layers=2).to(device)

    train(model, data, epochs=200)

    print("\nGenerating text:")
    for seed in [["the", "cat"], ["the", "dog"], ["a", "bird"]]:
        result = generate(model, seed, word_to_idx, idx_to_word, length=10)
        print(f"  Seed: '{' '.join(seed)}' -> '{result}'")
