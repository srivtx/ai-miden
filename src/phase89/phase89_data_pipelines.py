import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# WHY: MinHash estimates Jaccard similarity without comparing all pairs.
# This is critical when you have billions of documents.

# WHY: Precompute independent random hashes so each (token, seed) pair is unpredictable.
# This makes the MinHash property hold: Pr(min match) ≈ Jaccard similarity.
HASH_TABLE = np.random.RandomState(42).randint(0, 2**32, size=(200, 200))

def simple_hash(x, seed):
    return HASH_TABLE[seed % 200, x % 200]

def minhash_signature(tokens, num_hashes=100):
    # WHY: The signature is the minimum hash value for each hash function.
    sig = np.zeros(num_hashes, dtype=np.uint32)
    for i in range(num_hashes):
        min_val = 2**32
        for t in tokens:
            h = simple_hash(t, i)
            if h < min_val:
                min_val = h
        sig[i] = min_val
    return sig

def jaccard_estimate(sig1, sig2):
    # WHY: The fraction of matching minima approximates true Jaccard similarity.
    return np.mean(sig1 == sig2)

# Toy documents represented as token integers
doc_a = [1, 2, 3, 4, 5]
doc_b = [1, 2, 3, 6, 7]  # 60% overlap
doc_c = [100, 101, 102]  # no overlap

sig_a = minhash_signature(doc_a, num_hashes=100)
sig_b = minhash_signature(doc_b, num_hashes=100)
sig_c = minhash_signature(doc_c, num_hashes=100)

sim_ab = jaccard_estimate(sig_a, sig_b)
sim_ac = jaccard_estimate(sig_a, sig_c)

print(f"Estimated Jaccard(A,B): {sim_ab:.2f} (expected ~0.43)")
print(f"Estimated Jaccard(A,C): {sim_ac:.2f} (expected ~0.0)")

# WHY: Quality filters remove low-signal text before training.
def quality_score(text_info):
    # text_info: [length, num_unique_words, punctuation_ratio]
    length, unique, punct_ratio = text_info
    if length < 20:
        return 0.0
    if punct_ratio > 0.5:
        return 0.0
    return unique / length

texts = np.array([
    [100, 80, 0.05],  # good
    [10, 8, 0.05],    # too short
    [200, 20, 0.6],   # too much punctuation
    [150, 120, 0.03], # good
])

scores = [quality_score(t) for t in texts]
print("Quality scores:", scores)

# WHY: Visualize similarity matrix to show dedup power.
docs = [doc_a, doc_b, doc_c]
sigs = [minhash_signature(d) for d in docs]
sim_mat = np.zeros((3, 3))
for i in range(3):
    for j in range(3):
        sim_mat[i, j] = jaccard_estimate(sigs[i], sigs[j])

fig, ax = plt.subplots()
im = ax.imshow(sim_mat, cmap='viridis', vmin=0, vmax=1)
ax.set_xticks([0, 1, 2])
ax.set_yticks([0, 1, 2])
ax.set_xticklabels(['A', 'B', 'C'])
ax.set_yticklabels(['A', 'B', 'C'])
for i in range(3):
    for j in range(3):
        ax.text(j, i, f"{sim_mat[i,j]:.2f}", ha="center", va="center", color="w")
ax.set_title("MinHash Similarity Matrix")
fig.colorbar(im, ax=ax)
fig.savefig('/Users/zen/Desktop/building-ai/ai-miden/src/phase89/minhash_similarity.png')
print("Saved plot to minhash_similarity.png")
