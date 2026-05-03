### 1. Why it exists (THE PROBLEM first)
Convolutional Neural Networks (CNNs) dominated computer vision for years, but they use hand-designed inductive biases like translation invariance and local connectivity. Transformers proved incredibly powerful for text. Researchers wondered: can we apply the same Transformer architecture to images without convolutions at all? The challenge is that an image has too many pixels to treat each as a token — a 224x224 image has 50,176 pixels, which is far more than a typical sentence.

### 2. Definition (very simple)
A Vision Transformer (ViT) splits an image into fixed-size patches (like cutting a photo into squares), flattens each patch into a vector, adds positional embeddings, and feeds the sequence into a standard Transformer encoder. It treats image patches exactly like word tokens in BERT.

### 3. Real-life analogy
Reading a book word-by-word is slow. Reading it paragraph-by-paragraph is faster and captures broader context. ViT does the same with images: instead of processing individual pixels (words), it processes 16x16 pixel patches (paragraphs). Each patch contains enough local detail to be meaningful, and the Transformer learns which patches relate to each other.

### 4. Tiny numeric example
Image: 32x32 pixels, RGB (3 channels).

CNN approach:
- Apply 3x3 filters sliding across the image
- Each filter sees only 9 pixels at a time
- Many layers needed to see the whole image

ViT approach:
- Patch size = 8x8 pixels
- Number of patches = (32/8) x (32/8) = 4 x 4 = 16 patches
- Each patch = 8 x 8 x 3 = 192 numbers → flattened to a 192-dim vector
- Add 16 positional embeddings (one per patch position)
- Feed 16 tokens of dimension 192 into a Transformer encoder
- Output: classification token predicts "cat" or "dog"

### 5. Common confusion
- **ViT does not use convolutions at all.** The patch embedding is a simple linear projection (matrix multiply), not a convolutional filter. This is the whole point — pure Transformer.
- **ViTs need more data than CNNs.** Because CNNs have built-in assumptions about images (nearby pixels matter), they learn faster with small datasets. ViTs have no such biases and need large datasets (like ImageNet-21k or JFT-300M) to learn these patterns from scratch.
- **Positional embeddings are crucial.** Unlike text, image patches have no natural order. A patch in the top-left is different from the same patch in the bottom-right. Positional embeddings encode spatial location.
- **The CLS token works like BERT.** A special classification token is prepended to the patch sequence. Its final hidden state is used for the image label, just like BERT's CLS token is used for sentence classification.
- **ViTs are not always better than CNNs.** On small datasets, a ResNet often beats a ViT. At scale (millions of images), ViTs catch up and can surpass CNNs.

### 6. Where it is used in our code
`src/phase28/phase28_multimodal_ai.py` implements a tiny ViT that splits 8x8 images into 2x2 patches and processes them with a Transformer encoder to classify simple shapes.
