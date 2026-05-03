#!/usr/bin/env python3
"""
================================================================================
Phase 17 (Colab T4 Version): Attention Mechanism with PyTorch GPU
================================================================================

THIS SCRIPT IS DESIGNED FOR GOOGLE COLAB T4 (FREE GPU).

Copy-paste this into a Colab notebook.
It trains a Seq2Seq model WITH ATTENTION on a character reversal task.
The attention weights are visualized to show which input positions
 the decoder focuses on at each step.
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

def prepare_data(num_samples=10000, max_len=10):
    chars = 'abcdefghijklmnopqrstuvwxyz'
    char_to_idx = {c: i+3 for i, c in enumerate(chars)}
    char_to_idx['<PAD>'] = 0
    char_to_idx['<SOS>'] = 1
    char_to_idx['<EOS>'] = 2
    idx_to_char = {i: c for c, i in char_to_idx.items()}
    vocab_size = len(char_to_idx)

    data = []
    for _ in range(num_samples):
        length = random.randint(3, max_len)
        word = ''.join(random.choices(chars, k=length))
        reversed_word = word[::-1]

        encoder_input = [char_to_idx[c] for c in word]
        decoder_input = [char_to_idx['<SOS>']] + [char_to_idx[c] for c in reversed_word]
        target = [char_to_idx[c] for c in reversed_word] + [char_to_idx['<EOS>']]

        data.append((encoder_input, decoder_input, target))

    return data, char_to_idx, idx_to_char, vocab_size


def pad_sequence(sequences, pad_value=0):
    max_len = max(len(s) for s in sequences)
    padded = []
    for seq in sequences:
        padded.append(seq + [pad_value] * (max_len - len(seq)))
    return torch.LongTensor(padded)


# ==============================================================================
# ATTENTION MODULE
# ==============================================================================

class Attention(nn.Module):
    """Additive attention mechanism."""

    def __init__(self, hidden_size):
        super().__init__()
        self.W_q = nn.Linear(hidden_size, hidden_size)
        self.W_k = nn.Linear(hidden_size, hidden_size)
        self.v = nn.Linear(hidden_size, 1)

    def forward(self, query, keys, mask=None):
        # query: (batch, hidden)
        # keys: (batch, src_len, hidden)

        # Expand query to match keys shape
        # query: (batch, 1, hidden)
        query = query.unsqueeze(1)

        # Compute attention scores
        # score = v * tanh(W_q(query) + W_k(keys))
        scores = self.v(torch.tanh(self.W_q(query) + self.W_k(keys))).squeeze(-1)
        # scores: (batch, src_len)

        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)

        # Softmax over source positions
        attention_weights = torch.softmax(scores, dim=-1)

        # Weighted sum of values (keys are values in this case)
        # attention_weights: (batch, src_len)
        # keys: (batch, src_len, hidden)
        context = torch.bmm(attention_weights.unsqueeze(1), keys).squeeze(1)

        return context, attention_weights


# ==============================================================================
# ENCODER
# ==============================================================================

class Encoder(nn.Module):
    def __init__(self, vocab_size, embed_dim, hidden_size):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.lstm = nn.LSTM(embed_dim, hidden_size, batch_first=True, bidirectional=True)
        self.fc = nn.Linear(hidden_size * 2, hidden_size)

    def forward(self, x):
        embedded = self.embedding(x)
        outputs, (hidden, cell) = self.lstm(embedded)

        # Combine bidirectional hidden states
        hidden = torch.tanh(self.fc(torch.cat((hidden[-2], hidden[-1]), dim=1)))
        cell = torch.tanh(self.fc(torch.cat((cell[-2], cell[-1]), dim=1)))

        return outputs, hidden, cell


# ==============================================================================
# DECODER WITH ATTENTION
# ==============================================================================

class AttentionDecoder(nn.Module):
    def __init__(self, vocab_size, embed_dim, hidden_size, attention):
        super().__init__()
        self.attention = attention
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.lstm = nn.LSTM(embed_dim + hidden_size * 2, hidden_size, batch_first=True)
        self.fc_out = nn.Linear(hidden_size + hidden_size * 2 + embed_dim, vocab_size)

    def forward(self, x, hidden, cell, encoder_outputs, mask=None):
        # x: (batch, 1)
        x = x.unsqueeze(1)
        embedded = self.embedding(x)

        # Attention
        context, attention_weights = self.attention(hidden, encoder_outputs, mask)

        # LSTM input: embedding + context
        lstm_input = torch.cat((embedded, context.unsqueeze(1)), dim=-1)
        output, (hidden, cell) = self.lstm(lstm_input, (hidden.unsqueeze(0), cell.unsqueeze(0)))

        # Prediction
        output = output.squeeze(1)
        prediction = self.fc_out(torch.cat((output, context, embedded.squeeze(1)), dim=-1))

        return prediction, hidden.squeeze(0), cell.squeeze(0), attention_weights


# ==============================================================================
# SEQ2SEQ WITH ATTENTION
# ==============================================================================

class Seq2SeqAttention(nn.Module):
    def __init__(self, encoder, decoder, device):
        super().__init__()
        self.encoder = encoder
        self.decoder = decoder
        self.device = device

    def forward(self, src, trg, teacher_forcing_ratio=0.5):
        batch_size = src.shape[0]
        trg_len = trg.shape[1]
        trg_vocab_size = self.decoder.fc_out.out_features

        outputs = torch.zeros(batch_size, trg_len, trg_vocab_size).to(self.device)
        attentions = torch.zeros(batch_size, trg_len, src.shape[1]).to(self.device)

        encoder_outputs, hidden, cell = self.encoder(src)

        input = trg[:, 0]

        for t in range(1, trg_len):
            output, hidden, cell, attention = self.decoder(input, hidden, cell, encoder_outputs)
            outputs[:, t] = output
            attentions[:, t] = attention

            teacher_force = random.random() < teacher_forcing_ratio
            top1 = output.argmax(1)
            input = trg[:, t] if teacher_force else top1

        return outputs, attentions


# ==============================================================================
# TRAINING
# ==============================================================================

def train(model, data, char_to_idx, epochs=15, batch_size=128, lr=0.001):
    optimizer = optim.Adam(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss(ignore_index=char_to_idx['<PAD>'])

    print(f"\nTraining Seq2Seq + Attention on {device}...")
    print(f"  Training samples: {len(data)}")
    print()

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
            output, _ = model(src, trg)

            output_dim = output.shape[-1]
            output = output[1:].view(-1, output_dim)
            target = target[1:].view(-1)

            loss = criterion(output, target)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

            total_loss += loss.item()
            num_batches += 1

        print(f"  Epoch {epoch+1}/{epochs}: Loss = {total_loss/num_batches:.4f}")


# ==============================================================================
# EVALUATION + VISUALIZATION
# ==============================================================================

def translate_and_visualize(model, word, char_to_idx, idx_to_char, max_len=15):
    model.eval()

    src = torch.LongTensor([[char_to_idx[c] for c in word]]).to(device)

    with torch.no_grad():
        encoder_outputs, hidden, cell = model.encoder(src)

        outputs = []
        attentions = []
        input = torch.LongTensor([char_to_idx['<SOS>']]).to(device)

        for _ in range(max_len):
            output, hidden, cell, attention = model.decoder(input, hidden, cell, encoder_outputs)
            top1 = output.argmax(1)
            input = top1

            if top1.item() == char_to_idx['<EOS>']:
                break

            outputs.append(top1.item())
            attentions.append(attention.cpu().numpy().squeeze())

    result = ''.join([idx_to_char[i] for i in outputs if i in idx_to_char and idx_to_char[i] not in ['<PAD>', '<SOS>', '<EOS>']])

    # Visualize attention
    if attentions:
        fig, ax = plt.subplots(figsize=(10, 6))
        attention_matrix = np.array(attentions)
        im = ax.imshow(attention_matrix, cmap='Blues', aspect='auto')

        input_chars = list(word)
        output_chars = list(result)

        ax.set_xticks(np.arange(len(input_chars)))
        ax.set_yticks(np.arange(len(output_chars)))
        ax.set_xticklabels(input_chars)
        ax.set_yticklabels(output_chars)

        ax.set_xlabel('Input Characters', fontsize=12)
        ax.set_ylabel('Output Characters', fontsize=12)
        ax.set_title(f'Attention Weights: {word} -> {result}', fontsize=14)

        plt.colorbar(im, ax=ax)
        plt.tight_layout()
        plt.savefig(f'attention_{word}.png', dpi=150)
        plt.show()

    return result


# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    data, char_to_idx, idx_to_char, vocab_size = prepare_data(num_samples=20000, max_len=12)

    embed_dim = 32
    hidden_size = 64

    encoder = Encoder(vocab_size, embed_dim, hidden_size)
    attention = Attention(hidden_size)
    decoder = AttentionDecoder(vocab_size, embed_dim, hidden_size, attention)
    model = Seq2SeqAttention(encoder, decoder, device).to(device)

    print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")

    train(model, data, char_to_idx, epochs=15, batch_size=128)

    print("\n" + "="*60)
    print("TESTING WITH ATTENTION VISUALIZATION")
    print("="*60)

    test_words = ['hello', 'python', 'abcdef', 'reverse']
    for word in test_words:
        word = ''.join(c for c in word if c in char_to_idx)
        if word:
            result = translate_and_visualize(model, word, char_to_idx, idx_to_char)
            print(f"  {word} -> {result} (expected: {word[::-1]})")
