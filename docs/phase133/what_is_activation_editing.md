## What Is Activation Editing?

---

### The Problem

You have a model that mostly works, but it has one persistent flaw: it drags every answer into an overly formal register, or it hallucinates dates in history questions, or it becomes verbose when you need brevity. Fine-tuning would cost hundreds of dollars and might break other behaviors. Prompt engineering helps, but a cleverly crafted jailbreak bypasses your instructions in seconds. You need a way to reach inside the running model and fix the problem at the source, without retraining and without relying on the input text.

---

### Definition

**Activation Editing** is the modification of intermediate neuron activations during the forward pass of inference. Instead of changing the model's weights, you alter the hidden states that flow between layers. This can take the form of clamping a neuron to a fixed value, shifting an entire activation vector by a steering direction, or replacing a corrupted activation with a clean one.

**How it works:**
```
Standard forward pass:
  x -> Layer 1 -> h1 -> Layer 2 -> h2 -> Layer 3 -> output

Edited forward pass:
  x -> Layer 1 -> h1 -> (edit h1) -> Layer 2 -> h2 -> (edit h2) -> Layer 3 -> output
```

**Key techniques:**
- **Clamp:** force a specific neuron or subspace to a fixed value (e.g., zero out a hallucination direction)
- **Shift:** add a steering vector to an activation (e.g., make output more positive)
- **Replace:** swap an activation from a corrupted run with one from a clean run (causal tracing)

**Why this is safer than fine-tuning:**
- Reversible: remove the edit and the model is exactly as it was before
- Local: only the targeted activation changes; the rest of the network is untouched
- Interpretable: you know exactly which layer and which direction you modified
- Fast: no gradient computation, no weight updates, no training data curation

**Comparison with prompt engineering:**
- Prompt engineering changes the input. Its effect is limited by context length, tokenization artifacts, and the model's ability to follow instructions. It fails against adversarial suffixes.
- Activation editing changes the internal state. It bypasses the input entirely and operates in continuous space. It cannot be undone by prompt manipulation because the prompt has already been encoded.

---

### Real-Life Analogy

Subtitles on a foreign film.
- **Base model:** The film itself. The actors, the camera angles, and the editing are fixed (the weights).
- **Prompt engineering:** Shouting instructions from the audience ("Look happier!"). The actors cannot hear you, and even if they could, they are following a script.
- **Activation editing:** Adding subtitles at the bottom of the screen. The film does not change, but the viewer's understanding changes completely. If you want the audience to think the character is sarcastic, you add ironic subtitles. If you want them to take the scene seriously, you use literal translation. You can swap subtitle tracks instantly without reshooting the movie.
- **The limit:** If the actor never filmed a close-up of their face, no subtitle can make the audience feel the emotion. Editing cannot create knowledge that the model does not possess; it can only nudge how existing knowledge is expressed.

---

### Tiny Numeric Example

**A 3-layer network has hidden state h2 (dimension 3) before the output layer:**
```
Output logits = W_out @ h2 + b_out

Clean forward pass:
  h2_clean = [0.5, -0.2, 1.0]
  logits_clean = [0.3, 0.1, 0.8, -0.4]
  probabilities: "cat"=0.42, "dog"=0.31, "bird"=0.19, "fish"=0.08

Corrupted forward pass (adversarial input):
  h2_corrupt = [0.1, 1.5, -0.3]
  logits_corrupt = [-0.5, 1.2, 0.2, 0.1]
  probabilities: "cat"=0.12, "dog"=0.55, "bird"=0.18, "fish"=0.15
```

**Activation editing: replace h2_corrupt with h2_clean at layer 2:**
```
  h2_edited = h2_clean = [0.5, -0.2, 1.0]
  logits_edited = [0.3, 0.1, 0.8, -0.4]
  probabilities: "cat"=0.42, "dog"=0.31, "bird"=0.19, "fish"=0.08
```

**Shift editing: add steering vector v = [0.2, 0.0, -0.5] to h2_clean:**
```
  h2_shifted = [0.7, -0.2, 0.5]
  logits_shifted = [0.1, 0.2, 0.5, -0.1]
  probabilities: "cat"=0.35, "dog"=0.33, "bird"=0.25, "fish"=0.07
```

**The shift:** Replacing the activation fully recovered the clean output. Shifting it nudged the distribution without collapsing it. Both edits took microseconds and required no retraining.

---

### Common Confusion

1. **"Activation editing changes the model's weights."** No. It intercepts the forward pass and modifies the tensor that flows between layers. The `.pt` or `.safetensors` files on disk remain unchanged. The edit exists only in RAM during inference.

2. **"Activation editing is only for debugging."** While it is heavily used in mechanistic interpretability for causal tracing, it is increasingly deployed in production systems as a lightweight control mechanism. Several inference engines now support activation hooks for real-time steering.

3. **"You need to edit every layer to see an effect."** Often a single well-chosen layer is sufficient. Editing too many layers simultaneously can compound errors and degrade output quality. Start with one middle layer and expand only if needed.

4. **"Clamping a neuron to zero always removes the behavior it encodes."** Neurons are not cleanly disentangled. A single neuron might participate in multiple concepts. Zeroing it out could have unintended side effects on unrelated behaviors. Steering vectors are usually safer than single-neuron clamps.

5. **"Activation editing is slower than normal inference."** The overhead is negligible. A PyTorch forward hook adds a single tensor addition or assignment. The cost is dwarfed by the matrix multiplications in the transformer layers.

6. **"You cannot batch edits across multiple sequences."** You can. Hooks receive the full batch tensor. You can apply different steering vectors to different sequences in the same batch by indexing the batch dimension.

7. **"Activation editing fixes hallucinations by adding truth vectors."** It can reduce certain types of hallucinations if the hallucination has a detectable activation signature. However, it cannot inject facts the model never learned. If the model does not know the capital of Burkina Faso, no activation edit will make it know.

---

### Where It Is Used in Our Code

`src/phase133/phase133_steering_concepts.py` — We implement clamp, shift, and replace edits on a toy MLP in NumPy. We compare the output distributions after each edit type and plot the effect of editing activations at different layers.

`src/phase133/phase133_steering_colab.py` — We register PyTorch forward hooks on a real Llama model to add steering vectors to layer-15 activations during text generation. We show that this real-time activation editing changes sentiment and formality predictably.
