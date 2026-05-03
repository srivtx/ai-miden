### 1. Why it exists (THE PROBLEM first)
Supervised learning requires labeled data, which is expensive and scarce. For images, labeling millions of photos with captions costs millions of dollars. But the internet has billions of image-text pairs that are already "labeled" by humans (captions, alt text, comments). Contrastive learning asks: can we learn from these naturally occurring pairs by simply teaching the model "this image and this caption go together, but this image and that random caption do not"?

### 2. Definition (very simple)
Contrastive Learning is a training paradigm where the model learns by comparing positive pairs (matching examples) against negative pairs (non-matching examples). The model is trained to pull positive pairs close together in embedding space while pushing negative pairs far apart. No explicit labels like "cat" or "dog" are needed — just the structure of what belongs together.

### 3. Real-life analogy
Learning wine tasting without a textbook. You are handed two glasses and told: "These two are from the same vineyard." Then another two glasses: "These are from different vineyards." After hundreds of comparisons, you learn to identify subtle similarities and differences — fruity notes, acidity, tannins — without anyone ever defining those words for you. CLIP learns vision and language the same way: by comparison, not by dictionary definitions.

### 4. Tiny numeric example
Batch of 3 image-text pairs:
- Pair 1: Image A + Text A ("a dog")
- Pair 2: Image B + Text B ("a cat")
- Pair 3: Image C + Text C ("a car")

Similarity matrix (image rows, text columns):

|       | Text A | Text B | Text C |
|-------|--------|--------|--------|
| Img A |  0.9   |  0.1   |  0.05  |
| Img B |  0.15  |  0.85  |  0.08  |
| Img C |  0.05  |  0.1   |  0.92  |

The contrastive loss:
- For Image A, we want similarity with Text A (0.9) to be much higher than with Text B (0.1) and Text C (0.05).
- Loss = -log( exp(0.9) / (exp(0.9) + exp(0.1) + exp(0.05)) )
- Loss = -log( 2.46 / (2.46 + 1.11 + 1.05) ) = -log(0.53) = 0.63

After training, the diagonal values increase and off-diagonals decrease.

### 5. Common confusion
- **Contrastive learning is not just for images and text.** It is used for self-supervised learning in vision (SimCLR, MoCo), for sentence embeddings (Sentence-BERT), and even for protein folding (AlphaFold uses contrastive-like structure alignment).
- **The negative samples matter.** If negatives are too easy (completely unrelated), the model learns nothing. If negatives are too hard (almost identical), training is unstable. Hard negative mining — deliberately picking challenging non-matching pairs — improves learning.
- **It is not the same as triplet loss.** Triplet loss uses one anchor, one positive, and one negative. Contrastive loss uses a full batch of positives and negatives at once (infoNCE).
- **Temperature scaling is crucial.** The similarity scores are divided by a temperature parameter (usually 0.07). Lower temperature makes the distribution sharper, forcing the model to be more confident. Too low and it becomes brittle; too high and it becomes lazy.
- **CLIP is the most famous example, but not the only one.** ALIGN (Google), FLAVA (Meta), and many others use the same contrastive pre-training approach across modalities.

### 6. Where it is used in our code
`src/phase32/phase32_foundation_models.py` demonstrates a tiny contrastive learning setup where matching vector pairs are pulled together and non-matching pairs are pushed apart.
