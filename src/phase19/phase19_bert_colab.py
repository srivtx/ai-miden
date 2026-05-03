#!/usr/bin/env python3
"""
================================================================================
Phase 19 (Colab T4): BERT-style Masked Language Modeling
================================================================================

Copy-paste into Google Colab with T4 GPU.
Trains a small BERT-style model on masked word prediction.
"""

import torch
import torch.nn as nn
import torch.optim as optim
import math
import numpy as np

print(f"CUDA: {torch.cuda.is_available()}")
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=512):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe.unsqueeze(0))

    def forward(self, x):
        return x + self.pe[:, :x.size(1)]


class BERTEncoder(nn.Module):
    def __init__(self, vocab_size, d_model=128, nhead=4, num_layers=4, dim_ff=512):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_encoder = PositionalEncoding(d_model)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=nhead, dim_feedforward=dim_ff,
            batch_first=True, dropout=0.1
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.fc = nn.Linear(d_model, vocab_size)

    def forward(self, x):
        x = self.embedding(x) * math.sqrt(self.embedding.embedding_dim)
        x = self.pos_encoder(x)
        x = self.transformer(x)
        return self.fc(x)


def prepare_data():
    sentences = [
        "the cat sat on the mat",
        "the dog ran in the park",
        "the bird flew in the sky",
        "a fish swam in the water",
        "the sun shone brightly",
        "children played in the garden",
        "the chef cooked delicious food",
        "a student read a book",
    ] * 100  # Repeat for more data

    words = set()
    for s in sentences:
        words.update(s.split())
    words = sorted(words)
    word_to_idx = {w: i for i, w in enumerate(words)}
    word_to_idx['<MASK>'] = len(word_to_idx)
    vocab_size = len(word_to_idx)

    # Create masked data
    data = []
    for sent in sentences:
        tokens = sent.split()
        for i in range(len(tokens)):
            masked = tokens.copy()
            original = masked[i]
            masked[i] = '<MASK>'
            data.append((masked, original, i))

    return data, word_to_idx, words, vocab_size


def train(model, data, word_to_idx, epochs=50, lr=0.001):
    optimizer = optim.Adam(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()

    print(f"Training BERT on {device}...")
    print(f"Vocab size: {len(word_to_idx)}")

    for epoch in range(epochs):
        total_loss = 0
        correct = 0
        total = 0

        import random
        random.shuffle(data)

        for masked_tokens, target_word, mask_pos in data:
            input_ids = torch.LongTensor([word_to_idx.get(w, 0) for w in masked_tokens]).unsqueeze(0).to(device)
            target = torch.LongTensor([word_to_idx[target_word]]).to(device)

            optimizer.zero_grad()
            output = model(input_ids)

            # Get prediction at mask position
            pred = output[0, mask_pos].unsqueeze(0)
            loss = criterion(pred, target)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()
            if pred.argmax() == target:
                correct += 1
            total += 1

        if epoch % 10 == 0:
            print(f"  Epoch {epoch}: Loss = {total_loss/total:.4f}, Acc = {correct/total*100:.1f}%")


if __name__ == "__main__":
    data, word_to_idx, words, vocab_size = prepare_data()
    model = BERTEncoder(vocab_size, d_model=128, nhead=4, num_layers=4).to(device)

    train(model, data, word_to_idx, epochs=100)

    # Test
    print("\nTesting masked predictions:")
    test_sentences = [
        ["the", "<MASK>", "sat", "on", "the", "mat"],
        ["the", "dog", "<MASK>", "in", "the", "park"],
    ]

    model.eval()
    with torch.no_grad():
        for tokens in test_sentences:
            input_ids = torch.LongTensor([word_to_idx.get(w, 0) for w in tokens]).unsqueeze(0).to(device)
            output = model(input_ids)
            mask_pos = tokens.index('<MASK>')
            pred_idx = output[0, mask_pos].argmax().item()
            pred_word = words[pred_idx] if pred_idx < len(words) else '<MASK>'
            print(f"  '{' '.join(tokens)}' -> Predicted: '{pred_word}'")
