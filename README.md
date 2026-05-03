# AI from Absolute Zero

> **A complete AI course for absolute beginners.**
>
> No prior knowledge of AI, machine learning, or advanced math required.
> Basic algebra is all you need.

---

## Welcome

If you have never heard of neural networks, gradients, or backpropagation, you are in the right place.

This project builds an AI system **completely from scratch** while teaching you every concept along the way. We use only Python and NumPy. No shortcuts. No black boxes. Every line of code is explained.

By the end, you will understand:
- What AI actually is (hint: it is not magic)
- How a computer learns from examples
- How to build a neural network by hand
- Why every piece of the puzzle exists

---

## How to Use This Course

This project is organized into **phases**. Each phase builds on the previous one.

**Recommended path:**
1. Read the docs in `docs/phaseX/` in order
2. Run the code in `src/phaseX/` to see it in action
3. Do the dry-run with numbers yourself
4. Move to the next phase only when you feel comfortable

Every technical term has its own documentation file. If you see a word you do not recognize, find it in the docs folder.

---

## Project Structure

```
ai-miden/
├── docs/
│   ├── phase0/          # The absolute basics
│   ├── phase1/          # Our first model
│   ├── phase2/          # How we measure wrongness
│   ├── phase3/          # How the model learns
│   ├── phase4/          # Neural networks
│   ├── phase5/          # Binary classification
│   ├── phase6/          # Multi-class classification
│   ├── phase7/          # Deep networks
│   ├── phase8/          # L2 regularization
│   ├── phase9/          # Dropout
│   ├── phase10/         # Batch normalization
│   ├── phase11/         # CNNs Part 1
│   ├── phase12/         # Residual Networks
│   ├── phase13/         # RNNs
│   ├── phase14/         # LSTMs
│   ├── phase15/         # Word Embeddings
│   ├── phase16/         # Seq2Seq
│   ├── phase17/         # Attention
│   ├── phase18/         # Transformer
│   ├── phase19/         # BERT
│   ├── phase20/         # GPT Architecture
│   ├── phase21/         # Training a Tiny GPT
│   ├── phase22/         # Supervised Fine-Tuning
│   ├── phase23/         # RLHF
│   ├── phase24/         # DPO & GRPO
│   ├── phase25/         # Inference Optimization
│   ├── phase26/         # Test-Time Compute & Reasoning
│   ├── phase27/         # Agentic AI
│   ├── phase28/         # Multimodal AI
│   ├── phase29/         # Generative Models — VAEs
│   ├── phase30/         # Generative Models — GANs
│   ├── phase31/         # Generative Models — Diffusion
│   ├── phase32/         # Foundation Models & The Future
│   ├── phase33/         # Mixture of Experts
│   ├── phase34/         # Mamba & State Space Models
│   ├── phase35/         # LoRA & Parameter-Efficient Fine-Tuning
│   ├── phase36/         # Speculative Decoding
│   ├── phase37/         # Retrieval-Augmented Generation
│   ├── phase38/         # Scaling Laws & Compute-Optimal Training
│   ├── phase39/         # Knowledge Distillation
│   ├── phase40/         # Flow Matching & Diffusion Transformers
│   ├── phase41/         # Vision-Language Instruction Tuning
│   ├── phase42/         # Reasoning with Verifiable Rewards
│   ├── phase43/         # Model Merging & Ensembles
│   ├── phase44/         # Long Context & Position Interpolation
│   ├── phase45/         # Quantization & GGUF
│   ├── phase46/         # Mechanistic Interpretability
│   ├── phase47/         # Synthetic Data & Self-Improvement
│   └── phase48/         # Test-Time Training
└── README.md            # This file
```

---

## Phase 0: Absolute Zero

**Goal:** Understand the foundational vocabulary.

### Terms Covered
| File | Term |
|---|---|
| `what_is_ai.md` | AI (Artificial Intelligence) |
| `what_is_prediction.md` | Prediction |
| `what_is_function.md` | Function |
| `what_is_input_output.md` | Input and Output |

### Code
`src/phase0/phase0_basics.py` — Demonstrates functions, input/output, and making predictions from learned patterns.

### Run It
```bash
python src/phase0/phase0_basics.py
```

---

## Phase 1: First Model

**Goal:** Build a Linear Regression model and understand its parts.

### Terms Covered
| File | Term |
|---|---|
| `what_is_model.md` | Model |
| `what_is_parameter.md` | Parameter |
| `what_is_weight.md` | Weight |
| `what_is_bias.md` | Bias |
| `what_is_numpy.md` | NumPy |

### Code
`src/phase1/phase1_linear_regression.py` — A model with weight and bias parameters. Shows how bad parameters give bad predictions, and good parameters give perfect predictions.

### Run It
```bash
python src/phase1/phase1_linear_regression.py
```

---

## Phase 2: The Learning Process

**Goal:** Learn how to measure how wrong our model is.

### Terms Covered
| File | Term |
|---|---|
| `what_is_error.md` | Error |
| `what_is_loss_function.md` | Loss Function (MSE) |
| `what_is_derivative.md` | Derivative |
| `what_is_gradient.md` | Gradient |

### Code
`src/phase2/phase2_learning_process.py` — Computes predictions, errors, loss, and gradients for a bad model. Only measures. Does not learn yet.

### Run It
```bash
python src/phase2/phase2_learning_process.py
```

---

## Phase 3: The Learning Mechanism

**Goal:** Make the model actually learn by adjusting its parameters automatically.

### Terms Covered
| File | Term |
|---|---|
| `what_is_gradient_descent.md` | Gradient Descent |
| `what_is_learning_rate.md` | Learning Rate |
| `what_is_optimization.md` | Optimization |

### Code
`src/phase3/phase3_gradient_descent.py` — A complete training loop. The model starts with random parameters and learns the correct pattern by repeatedly measuring error and taking small steps downhill.

### Run It
```bash
python src/phase3/phase3_gradient_descent.py
```

---

## Phase 4: Neural Networks

**Goal:** Build a neural network from scratch that can learn non-linear (curved) patterns.

### Terms Covered
| File | Term |
|---|---|
| `what_is_neuron.md` | Neuron |
| `what_is_layer.md` | Layer |
| `what_is_neural_network.md` | Neural Network |
| `what_is_activation_function.md` | Activation Function (ReLU) |
| `what_is_non_linearity.md` | Non-Linearity |
| `what_is_forward_pass.md` | Forward Pass |
| `what_is_chain_rule.md` | Chain Rule |
| `what_is_backpropagation.md` | Backpropagation |

### Code
`src/phase4/phase4_neural_network.py` — A complete neural network with one hidden layer, ReLU activation, and manual backpropagation. First shows linear regression failing on a parabola, then shows the neural network succeeding.

### Run It
```bash
python src/phase4/phase4_neural_network.py
```

---

## Phase 5: Binary Classification

**Goal:** Use a neural network to answer YES/NO questions.

### Terms Covered
| File | Term |
|---|---|
| `what_is_sigmoid.md` | Sigmoid |
| `what_is_binary_cross_entropy.md` | Binary Cross-Entropy |
| `what_is_decision_boundary.md` | Decision Boundary |

### Code
`src/phase5/phase5_binary_classifier.py` — A neural network that classifies points into two groups. Uses sigmoid output and binary cross-entropy loss, then plots the learned decision boundary.

### Run It
```bash
python src/phase5/phase5_binary_classifier.py
```

---

## Phase 6: Multi-Class Classification

**Goal:** Classify data into three or more categories.

### Terms Covered
| File | Term |
|---|---|
| `what_is_softmax.md` | Softmax |
| `what_is_categorical_cross_entropy.md` | Categorical Cross-Entropy |
| `what_is_one_hot_encoding.md` | One-Hot Encoding |

### Code
`src/phase6/phase6_multiclass_classifier.py` — A neural network that sorts points into three colored groups. Uses softmax probabilities, one-hot targets, and categorical cross-entropy loss.

### Run It
```bash
python src/phase6/phase6_multiclass_classifier.py
```

---

## Phase 7: Deep Networks

**Goal:** Understand why stacking more hidden layers unlocks harder patterns.

### Terms Covered
| File | Term |
|---|---|
| `what_is_deep_network.md` | Deep Network |
| `what_is_xavier_initialization.md` | Xavier / He Initialization |

### Code
`src/phase7/phase7_deep_network.py` — Compares a shallow network (1 hidden layer) against a deep network (3 hidden layers) on a sine wave. Shows that depth enables hierarchical feature learning.

### Run It
```bash
python src/phase7/phase7_deep_network.py
```

---

## Phase 8: L2 Regularization

**Goal:** Prevent overfitting by keeping weights small and simple.

### Terms Covered
| File | Term |
|---|---|
| `what_is_overfitting.md` | Overfitting |
| `what_is_l2_regularization.md` | L2 Regularization |
| `what_is_bias_variance_tradeoff.md` | Bias-Variance Tradeoff |

### Code
`src/phase8/phase8_l2_regularization.py` — Demonstrates overfitting by memorizing noisy data, then shows how adding an L2 penalty forces the model to learn a smoother, more general pattern.

### Run It
```bash
python src/phase8/phase8_l2_regularization.py
```

---

## Phase 9: Dropout

**Goal:** Break neuron co-adaptation by randomly turning neurons off during training.

### Terms Covered
| File | Term |
|---|---|
| `what_is_dropout.md` | Dropout |

### Code
`src/phase9/phase9_dropout.py` — Adds dropout masks during training to force every neuron to learn independently. Shows improved generalization compared to training without dropout.

### Run It
```bash
python src/phase9/phase9_dropout.py
```

---

## Phase 10: Batch Normalization

**Goal:** Stabilize training by normalizing the inputs to every layer.

### Terms Covered
| File | Term |
|---|---|
| `what_is_batch_normalization.md` | Batch Normalization |

### Code
`src/phase10/phase10_batch_normalization.py` — Implements BatchNorm from scratch inside a deep network. Trains faster and more stably, even with a higher learning rate.

### Run It
```bash
python src/phase10/phase10_batch_normalization.py
```

---

## Phase 11: CNNs Part 1

**Goal:** Learn how Convolutional Neural Networks see images using local filters and parameter sharing.

### Terms Covered
| File | Term |
|---|---|
| `what_is_convolution.md` | Convolution |
| `what_is_filter.md` | Filter (Kernel) |
| `what_is_pooling.md` | Pooling |
| `what_is_parameter_sharing.md` | Parameter Sharing |

### Code
`src/phase11/phase11_cnn.py` — A simple CNN that learns to tell X from O in tiny 8x8 images. Implements 2D convolution, max pooling, and backpropagation through convolutional layers from scratch.

### Run It
```bash
python src/phase11/phase11_cnn.py
```

---

## Phase 12: Residual Networks

**Goal:** Build very deep networks that learn reliably using skip connections.

### Terms Covered
| File | Term |
|---|---|
| `what_is_residual_network.md` | Residual Network (ResNet) |
| `what_is_degradation_problem.md` | Degradation Problem |

### Code
`src/phase12/phase12_resnet.py` — Implements residual blocks with skip connections from scratch. Shows how adding shortcuts lets a deep network keep improving instead of degrading.

### Run It
```bash
python src/phase12/phase12_resnet.py
```

---

## Phase 13: RNNs

**Goal:** Process sequences by keeping memory of past inputs.

### Terms Covered
| File | Term |
|---|---|
| `what_is_recurrent_neural_network.md` | Recurrent Neural Network (RNN) |
| `what_is_hidden_state.md` | Hidden State |
| `what_is_backpropagation_through_time.md` | Backpropagation Through Time (BPTT) |

### Code
`src/phase13/phase13_rnn.py` — A vanilla RNN that learns a simple sequence pattern from scratch. Implements forward propagation through time and backpropagation through time manually.

### Run It
```bash
python src/phase13/phase13_rnn.py
```

---

## Phase 14: LSTMs

**Goal:** Control memory flow so the network remembers what matters and forgets what does not.

### Terms Covered
| File | Term |
|---|---|
| `what_is_lstm.md` | LSTM (Long Short-Term Memory) |
| `what_is_cell_state.md` | Cell State |
| `what_is_forget_gate.md` | Forget Gate |
| `what_is_input_gate.md` | Input Gate |
| `what_is_output_gate.md` | Output Gate |

### Code
`src/phase14/phase14_lstm.py` — An LSTM that learns long-range dependencies in a sequence. Implements the cell state and all three gates from scratch, showing how controlled memory solves the vanishing gradient problem.

### Run It
```bash
python src/phase14/phase14_lstm.py
```

---

## Phase 15: Word Embeddings

**Goal:** Give words meaning by learning dense vectors from raw text.

### Terms Covered
| File | Term |
|---|---|
| `what_is_word_embedding.md` | Word Embedding |
| `what_is_skip_gram.md` | Skip-Gram |
| `what_is_negative_sampling.md` | Negative Sampling |

### Code
`src/phase15/phase15_word2vec.py` — Word2Vec with Skip-gram and negative sampling from scratch. Trains on a tiny corpus to show how similar words get similar vectors.

`src/phase15/phase15_word2vec_colab.py` — PyTorch GPU version for Colab T4. Trains on 100M words and shows real analogies like `king - man + woman ≈ queen`.

### Run It
```bash
python src/phase15/phase15_word2vec.py
```

---

## Phase 16: Seq2Seq

**Goal:** Translate sequences when input and output have different lengths.

### Terms Covered
| File | Term |
|---|---|
| `what_is_seq2seq.md` | Seq2Seq |
| `what_is_encoder_decoder.md` | Encoder-Decoder |

### Code
`src/phase16/phase16_seq2seq.py` — Encoder-decoder architecture with LSTM. Shows the forward pass and architecture diagram.

`src/phase16/phase16_seq2seq_colab.py` — PyTorch GPU version for Colab T4. Trains on character reversal with teacher forcing.

### Run It
```bash
python src/phase16/phase16_seq2seq.py
```

---

## Phase 17: Attention Mechanism

**Goal:** Let the decoder dynamically focus on relevant input words.

### Terms Covered
| File | Term |
|---|---|
| `what_is_attention.md` | Attention |
| `what_is_query_key_value.md` | Query / Key / Value |

### Code
`src/phase17/phase17_attention.py` — Dot-product attention with Query/Key/Value from scratch. Demonstrates translation with synthetic attention weights.

`src/phase17/phase17_attention_colab.py` — PyTorch GPU version for Colab T4. Full Seq2Seq with attention. Visualizes attention heatmaps.

### Run It
```bash
python src/phase17/phase17_attention.py
```

---

## Phase 18: Transformer Architecture

**Goal:** Remove RNNs entirely. Use only attention, massively parallelizable.

### Terms Covered
| File | Term |
|---|---|
| `what_is_transformer.md` | Transformer |
| `what_is_self_attention.md` | Self-Attention |
| `what_is_multi_head_attention.md` | Multi-Head Attention |
| `what_is_positional_encoding.md` | Positional Encoding |

### Code
`src/phase18/phase18_transformer.py` — Positional encoding, self-attention, multi-head attention, and Transformer block — all from scratch in NumPy.

`src/phase18/phase18_transformer_colab.py` — PyTorch GPU version for Colab T4. Full Transformer encoder with causal masking for character-level generation.

### Run It
```bash
python src/phase18/phase18_transformer.py
```

---

## Phase 19: BERT

**Goal:** Use only the Transformer encoder for deep bidirectional understanding.

### Terms Covered
| File | Term |
|---|---|
| `what_is_bert.md` | BERT |
| `what_is_masked_language_modeling.md` | Masked Language Modeling (MLM) |

### Code
`src/phase19/phase19_bert.py` — Bidirectional encoder block, masked language modeling demonstration, BERT vs GPT comparison.

`src/phase19/phase19_bert_colab.py` — PyTorch GPU version for Colab T4. Full BERT encoder trained on masked word prediction.

### Run It
```bash
python src/phase19/phase19_bert.py
```

---

## Phase 20: GPT Architecture

**Goal:** Use only the Transformer decoder for left-to-right text generation.

### Terms Covered
| File | Term |
|---|---|
| `what_is_gpt.md` | GPT (Generative Pre-trained Transformer) |
| `what_is_causal_masking.md` | Causal Masking |

### Code
`src/phase20/phase20_gpt.py` — Causal mask, causal self-attention, text generation demonstration, BERT vs GPT architecture comparison.

`src/phase20/phase20_gpt_colab.py` — PyTorch GPU version for Colab T4. Full GPT decoder trained on next-token prediction.

### Run It
```bash
python src/phase20/phase20_gpt.py
```

---

## Phase 21: Training a Tiny GPT

**Goal:** Put everything together and train a model that generates text.

### Code
`src/phase21/phase21_tiny_gpt.py` — Complete Tiny GPT with embeddings, positional encoding, causal self-attention, Transformer blocks, training loop, and generation.

`src/phase21/phase21_tiny_gpt_colab.py` — PyTorch GPU version for Colab T4. Real character-level GPT with 256-dim embeddings, 6 layers, 8 heads. Trains on text and generates coherent output.

### Run It
```bash
python src/phase21/phase21_tiny_gpt.py
```

---

## The Big Picture

Here is how everything connects:

```
PHASE 0: Vocabulary
    AI, Prediction, Function, Input/Output
    ↓
PHASE 1: Structure
    Model, Parameter, Weight, Bias
    We can make predictions, but only with hand-picked parameters
    ↓
PHASE 2: Measurement
    Error, Loss, Derivative, Gradient
    We can measure how wrong we are and which way to improve
    ↓
PHASE 3: Learning
    Gradient Descent, Learning Rate, Optimization
    We automatically adjust parameters to minimize loss
    ↓
PHASE 4: Power
    Neuron, Layer, Activation, Backpropagation
    We build a network of many neurons that can learn curved patterns
    ↓
PHASE 5: Binary Classification
    Sigmoid, Binary Cross-Entropy, Decision Boundary
    We answer YES/NO questions and visualize the boundary
    ↓
PHASE 6: Multi-Class Classification
    Softmax, One-Hot Encoding, Categorical Cross-Entropy
    We sort data into three or more categories
    ↓
PHASE 7: Deep Networks
    Deep Network, Xavier/He Initialization
    We stack layers to learn hierarchical features
    ↓
PHASE 8: Regularization
    Overfitting, L2, Bias-Variance Tradeoff
    We keep weights small so the model generalizes
    ↓
PHASE 9: Dropout
    Dropout
    We randomly disable neurons to break co-adaptation
    ↓
PHASE 10: Batch Normalization
    Batch Normalization
    We normalize layer inputs for fast, stable training
    ↓
PHASE 11: CNNs
    Convolution, Filter, Pooling, Parameter Sharing
    We see images with sliding windows instead of flattening everything
    ↓
PHASE 12: Residual Networks
    ResNet, Degradation Problem
    We skip connections so deep networks can keep learning
    ↓
PHASE 13: RNNs
    RNN, Hidden State, BPTT
    We process sequences by keeping memory of what came before
    ↓
PHASE 14: LSTMs
    LSTM, Cell State, Forget/Input/Output Gates
    We control memory flow to remember important things and forget the rest
    ↓
PHASE 15: Word Embeddings
    Word2Vec, Skip-Gram, Negative Sampling
    We give words meaning by learning dense vectors
    ↓
PHASE 16: Seq2Seq
    Encoder, Decoder, Teacher Forcing
    We translate sequences of different lengths
    ↓
PHASE 17: Attention
    Query/Key/Value, Attention Weights
    The decoder focuses on relevant input words
    ↓
PHASE 18: Transformer
    Self-Attention, Multi-Head Attention, Positional Encoding
    We remove RNNs entirely and use pure attention
    ↓
PHASE 19: BERT
    Bidirectional Encoder, Masked Language Modeling
    We understand text by reading both directions
    ↓
PHASE 20: GPT Architecture
    Causal Masking, Autoregressive Generation
    We generate text left-to-right
    ↓
PHASE 21: Training a Tiny GPT
    Embeddings + Attention + Training Loop + Generation
    We put everything together and create text
    ↓
PHASE 22: Supervised Fine-Tuning
    Instruction-Response Pairs, System Prompt, Catastrophic Forgetting
    We teach the model to answer questions helpfully
    ↓
PHASE 23: RLHF
    Reward Model, PPO, KL Penalty, Pairwise Comparisons
    We align the model with human values
    ↓
PHASE 24: DPO & GRPO
    Direct Preference Optimization, Group Relative Policy Optimization
    We simplify alignment without losing quality
    ↓
PHASE 25: Inference Optimization
    KV Cache, Quantization, Flash Attention, Grouped Query Attention
    We make the model fast and small enough to deploy
    ↓
PHASE 26: Test-Time Compute & Reasoning
    Chain of Thought, Self-Consistency, PRM, ORM, o1-Style Reasoning
    We make the model think longer for better answers
    ↓
PHASE 27: Agentic AI
    AI Agent, Tool Use, ReAct, Multi-Agent, Computer Use
    We give the model tools so it can actually DO things
    ↓
PHASE 28: Multimodal AI
    ViT, CLIP, Shared Embedding Space, Diffusion, Unified Multimodal
    We make the model see images and understand multiple modalities
    ↓
PHASE 29: Generative Models — VAEs
    Autoencoder, Latent Space, VAE, Reparameterization, KL Divergence
    We create new data by learning smooth latent spaces
    ↓
PHASE 30: Generative Models — GANs
    Generator, Discriminator, Minimax Game, Mode Collapse
    We generate sharp, realistic data through adversarial training
    ↓
PHASE 31: Generative Models — Diffusion
    Forward Diffusion, Reverse Diffusion, U-Net, Timestep Conditioning
    We generate stable, high-quality data by gradually refining noise
    ↓
PHASE 32: Foundation Models & The Future
    Foundation Models, Contrastive Learning, RLHF at Scale, TTT, World Models
    We reflect on the complete landscape and where AI is going next
    ↓
PHASE 33: Mixture of Experts
    Router Gating, Load Balancing, Expert Capacity, Sparse Activation
    We decouple model capacity from compute cost by activating only a subset of experts per token
    ↓
PHASE 34: Mamba & State Space Models
    State Space Model, Selectivity, Parallel Scan, Linear Complexity
    We process long sequences in linear time with constant memory using selective state spaces
    ↓
PHASE 35: LoRA & Parameter-Efficient Fine-Tuning
    Low-Rank Adaptation, PEFT, QLoRA, Adapter Merging
    We adapt giant models by training only tiny adapter matrices
    ↓
PHASE 36: Speculative Decoding
    Draft Model, Acceptance Sampling, Medusa Decoding
    We generate multiple tokens per forward pass with zero quality loss
    ↓
PHASE 37: Retrieval-Augmented Generation
    Vector Database, Embedding Retrieval, Context Injection
    We ground LLM answers in external knowledge without retraining
    ↓
PHASE 38: Scaling Laws & Compute-Optimal Training
    Power Laws, Chinchilla Rule, Data Wall, Compute-Optimal Frontier
    We learn how to allocate our training budget between model size and data
    ↓
PHASE 39: Knowledge Distillation
    Teacher Model, Soft Labels, Temperature Scaling, Dark Knowledge
    We transfer a large model's intelligence into a tiny student with matching accuracy
    ↓
PHASE 40: Flow Matching & Diffusion Transformers
    Velocity Field, Rectified Flow, DiT, ODE Solvers
    We replace noise prediction with direct velocity regression for faster generation
    ↓
PHASE 41: Vision-Language Instruction Tuning
    Vision Encoder, Projection Layer, Multimodal Instruction Tuning
    We connect image understanding to language generation for visual conversation
    ↓
PHASE 42: Reasoning with Verifiable Rewards
    Verifiable Reward, GRPO, Emergent Reasoning, DeepSeek-R1 Reasoning Chain
    We train models to reason through self-play with automatic answer checking
    ↓
PHASE 43: Model Merging & Ensembles
    Model Merging, Task Arithmetic, SLERP, TIES-Merging
    We combine specialist models into a single multi-task model without retraining
    ↓
PHASE 44: Long Context & Position Interpolation
    RoPE, Position Interpolation, YaRN, NTK-Aware Scaling
    We extend context windows by scaling position encodings without retraining
    ↓
PHASE 45: Quantization & GGUF
    Quantization, GPTQ, AWQ, GGUF
    We shrink models by 4-8× with minimal quality loss through precision reduction
    ↓
PHASE 46: Mechanistic Interpretability
    Activation Patching, Sparse Autoencoders, Superposition
    We reverse-engineer neural networks to understand what individual neurons compute
    ↓
PHASE 47: Synthetic Data & Self-Improvement
    Synthetic Data, Rejection Sampling, Constitutional AI, Iterative Self-Improvement
    We generate unlimited training data and bootstrap models beyond human-labeled datasets
    ↓
PHASE 48: Test-Time Training
    Meta-Learning, Unsupervised Adaptation, Online Learning
    We adapt models at inference time without labels, datasets, or retraining
```

**The entire journey:** A computer starts knowing nothing, measures its mistakes, figures out which knobs to turn, learns to classify data, goes deeper, stays simple, stays stable, learns to see, skips ahead through deep paths, remembers sequences, gives words meaning, translates languages, focuses attention, removes RNNs entirely, understands bidirectionally, generates autoregressively, and finally writes its own text. That is learning. That is AI.

---

## Quick Start

Make sure you have Python and NumPy installed:

```bash
pip install numpy
```

Then run any phase:

```bash
# Phase 0: Basics
python src/phase0/phase0_basics.py

# Phase 1: Linear Regression
python src/phase1/phase1_linear_regression.py

# Phase 2: Error and Gradients
python src/phase2/phase2_learning_process.py

# Phase 3: Learning (Gradient Descent)
python src/phase3/phase3_gradient_descent.py

# Phase 4: Neural Network
python src/phase4/phase4_neural_network.py

# Phase 5: Binary Classification
python src/phase5/phase5_binary_classifier.py

# Phase 6: Multi-Class Classification
python src/phase6/phase6_multiclass_classifier.py

# Phase 7: Deep Networks
python src/phase7/phase7_deep_network.py

# Phase 8: L2 Regularization
python src/phase8/phase8_l2_regularization.py

# Phase 9: Dropout
python src/phase9/phase9_dropout.py

# Phase 10: Batch Normalization
python src/phase10/phase10_batch_normalization.py

# Phase 11: CNNs
python src/phase11/phase11_cnn.py

# Phase 12: ResNets
python src/phase12/phase12_resnet.py

# Phase 13: RNNs
python src/phase13/phase13_rnn.py

# Phase 14: LSTMs
python src/phase14/phase14_lstm.py

# Phase 15: Word Embeddings
python src/phase15/phase15_word2vec.py

# Phase 16: Seq2Seq
python src/phase16/phase16_seq2seq.py

# Phase 17: Attention
python src/phase17/phase17_attention.py

# Phase 18: Transformer
python src/phase18/phase18_transformer.py

# Phase 19: BERT
python src/phase19/phase19_bert.py

# Phase 20: GPT Architecture
python src/phase20/phase20_gpt.py

# Phase 21: Training a Tiny GPT
python src/phase21/phase21_tiny_gpt.py

# Phase 22: Supervised Fine-Tuning
python src/phase22/phase22_sft.py

# Phase 23: RLHF
python src/phase23/phase23_rlhf.py

# Phase 24: DPO & GRPO
python src/phase24/phase24_dpo_grpo.py

# Phase 25: Inference Optimization
python src/phase25/phase25_inference_optimization.py

# Phase 26: Test-Time Compute & Reasoning
python src/phase26/phase26_test_time_compute.py

# Phase 27: Agentic AI
python src/phase27/phase27_agentic_ai.py

# Phase 28: Multimodal AI
python src/phase28/phase28_multimodal_ai.py

# Phase 29: Generative Models — VAEs
python src/phase29/phase29_vae.py

# Phase 30: Generative Models — GANs
python src/phase30/phase30_gan.py

# Phase 31: Generative Models — Diffusion
python src/phase31/phase31_diffusion.py

# Phase 32: Foundation Models & The Future
python src/phase32/phase32_foundation_models.py

# Phase 33: Mixture of Experts
python src/phase33/phase33_moe.py

# Phase 34: Mamba & State Space Models
python src/phase34/phase34_mamba.py

# Phase 35: LoRA & Parameter-Efficient Fine-Tuning
python src/phase35/phase35_lora.py

# Phase 36: Speculative Decoding
python src/phase36/phase36_speculative_decoding.py

# Phase 37: Retrieval-Augmented Generation
python src/phase37/phase37_rag.py

# Phase 38: Scaling Laws & Compute-Optimal Training
python src/phase38/phase38_scaling_laws.py

# Phase 39: Knowledge Distillation
python src/phase39/phase39_knowledge_distillation.py

# Phase 40: Flow Matching & Diffusion Transformers
python src/phase40/phase40_flow_matching.py

# Phase 41: Vision-Language Instruction Tuning
python src/phase41/phase41_vlm.py

# Phase 42: Reasoning with Verifiable Rewards
python src/phase42/phase42_verifiable_rewards.py

# Phase 43: Model Merging & Ensembles
python src/phase43/phase43_model_merging.py

# Phase 44: Long Context & Position Interpolation
python src/phase44/phase44_long_context.py

# Phase 45: Quantization & GGUF
python src/phase45/phase45_quantization.py

# Phase 46: Mechanistic Interpretability
python src/phase46/phase46_mechanistic_interpretability.py

# Phase 47: Synthetic Data & Self-Improvement
python src/phase47/phase47_synthetic_data.py

# Phase 48: Test-Time Training
python src/phase48/phase48_test_time_training.py
```

---

## What Makes This Course Different

- **Every term is explained.** No jargon without a definition, analogy, and numeric example.
- **No shortcuts.** We build everything from scratch using only Python and NumPy.
- **No prior knowledge assumed.** If you know basic algebra, you can follow along.
- **Dry runs with real numbers.** Every concept is demonstrated with concrete examples.
- **Code is readable.** Comments explain WHY, not just WHAT.

---

## Course Stats

| Phase | Docs | Code Files | New Terms |
|---|---|---|---|
| Phase 0 | 4 | 1 | 4 |
| Phase 1 | 5 | 1 | 5 |
| Phase 2 | 4 | 1 | 4 |
| Phase 3 | 3 | 1 | 3 |
| Phase 4 | 8 | 1 | 8 |
| Phase 5 | 3 | 1 | 3 |
| Phase 6 | 3 | 1 | 3 |
| Phase 7 | 2 | 1 | 2 |
| Phase 8 | 3 | 1 | 3 |
| Phase 9 | 1 | 1 | 1 |
| Phase 10 | 1 | 1 | 1 |
| Phase 11 | 4 | 1 | 4 |
| Phase 12 | 2 | 1 | 2 |
| Phase 13 | 3 | 1 | 3 |
| Phase 14 | 5 | 1 | 5 |
| Phase 15 | 3 | 2 | 3 |
| Phase 16 | 2 | 2 | 2 |
| Phase 17 | 2 | 2 | 2 |
| Phase 18 | 4 | 2 | 4 |
| Phase 19 | 2 | 2 | 2 |
| Phase 20 | 2 | 2 | 2 |
| Phase 21 | 0 | 2 | 0 |
| Phase 22 | 2 | 1 | 2 |
| Phase 23 | 2 | 1 | 2 |
| Phase 24 | 2 | 1 | 2 |
| Phase 25 | 4 | 1 | 4 |
| Phase 26 | 5 | 1 | 5 |
| Phase 27 | 5 | 1 | 5 |
| Phase 28 | 5 | 1 | 5 |
| Phase 29 | 5 | 2 | 5 |
| Phase 30 | 4 | 2 | 4 |
| Phase 31 | 4 | 2 | 4 |
| Phase 32 | 5 | 1 | 5 |
| Phase 33 | 4 | 2 | 4 |
| Phase 34 | 4 | 2 | 4 |
| Phase 35 | 4 | 2 | 4 |
| Phase 36 | 4 | 2 | 4 |
| Phase 37 | 4 | 2 | 4 |
| Phase 38 | 4 | 2 | 4 |
| Phase 39 | 4 | 2 | 4 |
| Phase 40 | 4 | 2 | 4 |
| Phase 41 | 4 | 2 | 4 |
| Phase 42 | 4 | 2 | 4 |
| Phase 43 | 4 | 2 | 4 |
| Phase 44 | 4 | 2 | 4 |
| Phase 45 | 4 | 2 | 4 |
| Phase 46 | 4 | 2 | 4 |
| Phase 47 | 4 | 2 | 4 |
| Phase 48 | 4 | 2 | 4 |
| **Total** | **173** | **77** | **173** |

---

## Final Message

You just built an AI system from absolute zero.

You started with the question "What is a function?" and ended with a complete understanding of modern AI — from foundations to foundation models. Through forty-eight phases, you went from simple predictions all the way to understanding how modern AI systems are trained, aligned, optimized, made to reason, given tools to act, taught to see, enabled to create, sharpened through competition, refined through gradual denoising, connected to the future of the field, scaled beyond dense limits through sparse expert activation, processed infinitely long sequences in linear time with constant memory, adapted giant models with tiny parameter-efficient adapters, accelerated inference by generating multiple tokens per forward pass with zero quality loss, grounded generation in external knowledge through retrieval-augmented pipelines, learned how to wisely allocate training budgets between model size and data using empirical scaling laws, transferred massive models into tiny deployable versions while preserving their intelligence through knowledge distillation, replaced slow noise-prediction diffusion with fast direct-velocity flow matching powered by Transformer backbones, connected vision and language into unified multimodal conversational agents, trained models to reason through self-play with automatically verifiable rewards using group-relative policy optimization, combined specialist models into unified multi-task agents through weight-space merging without any retraining, extended context windows to process entire books and codebases by scaling position encodings through interpolation and NTK-aware frequency scaling, shrank massive models by 4-8× through precision reduction using quantization, GPTQ error compensation, and AWQ activation-aware protection to run on consumer GPUs, reverse-engineered neural networks through activation patching, sparse autoencoders, and superposition analysis to understand what individual neurons and circuits compute inside the black box, broke through the human data bottleneck by generating unlimited synthetic training data and bootstrapping models to improve themselves iteratively beyond the limits of human-labeled datasets, and adapted models in real-time at inference through meta-learning, test-time training, and online learning to handle distribution shifts and rare inputs without any retraining or labeled test data. Every step along the way was explained from first principles.

The fancy words — gradient descent, backpropagation, neural network, regularization, batch normalization, convolution, residual connection, hidden state, LSTM, attention, Transformer, BERT, GPT, RLHF, DPO, quantization, chain of thought, self-consistency, agent, tool use, CLIP, diffusion, VAE, latent space, GAN, generator, discriminator, forward diffusion, reverse diffusion, U-Net, foundation model, world model, mixture of experts, router gating, load balancing, expert capacity, sparse activation, state space model, selectivity, parallel scan, Mamba, LoRA, PEFT, QLoRA, adapter merging, speculative decoding, draft model, acceptance sampling, Medusa, retrieval-augmented generation, vector database, embedding retrieval, context injection, scaling law, Chinchilla rule, compute-optimal training, data wall, knowledge distillation, teacher model, soft labels, temperature scaling, dark knowledge, flow matching, rectified flow, velocity field, diffusion transformer, ODE solver, vision encoder, projection layer, multimodal instruction tuning, vision-language model, verifiable reward, GRPO, emergent reasoning, reasoning chain, model merging, task arithmetic, SLERP, TIES-Merging, position interpolation, RoPE, YaRN, NTK-aware scaling, quantization, GPTQ, AWQ, GGUF, INT4, INT8, per-channel scaling, mechanistic interpretability, activation patching, sparse autoencoder, superposition, synthetic data, rejection sampling, constitutional AI, self-improvement, meta-learning, test-time training, unsupervised adaptation, online learning — are not magic. They are just systematic ways of:
1. Making a guess
2. Measuring how wrong the guess is
3. Figuring out which direction to improve
4. Taking a small step
5. Repeating

That is all AI is. And now you know it from the inside out.

**Keep going. You have everything you need.**
