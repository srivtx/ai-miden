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
│   ├── [phase0/](/docs/phase0/)          # The absolute basics
│   ├── [phase1/](/docs/phase1/)          # Our first model
│   ├── [phase2/](/docs/phase2/)          # How we measure wrongness
│   ├── [phase3/](/docs/phase3/)          # How the model learns
│   ├── [phase4/](/docs/phase4/)          # Neural networks
│   ├── [phase5/](/docs/phase5/)          # Binary classification
│   ├── [phase6/](/docs/phase6/)          # Multi-class classification
│   ├── [phase7/](/docs/phase7/)          # Deep networks
│   ├── [phase8/](/docs/phase8/)          # L2 regularization
│   ├── [phase9/](/docs/phase9/)          # Dropout
│   ├── [phase10/](/docs/phase10/)         # Batch normalization
│   ├── [phase11/](/docs/phase11/)         # CNNs Part 1
│   ├── [phase12/](/docs/phase12/)         # Residual Networks
│   ├── [phase13/](/docs/phase13/)         # RNNs
│   ├── [phase14/](/docs/phase14/)         # LSTMs
│   ├── [phase15/](/docs/phase15/)         # Word Embeddings
│   ├── [phase16/](/docs/phase16/)         # Seq2Seq
│   ├── [phase17/](/docs/phase17/)         # Attention
│   ├── [phase18/](/docs/phase18/)         # Transformer
│   ├── [phase19/](/docs/phase19/)         # BERT
│   ├── [phase20/](/docs/phase20/)         # GPT Architecture
│   ├── [phase21/](/docs/phase21/)         # Training a Tiny GPT
│   ├── [phase22/](/docs/phase22/)         # Supervised Fine-Tuning
│   ├── [phase23/](/docs/phase23/)         # RLHF
│   ├── [phase24/](/docs/phase24/)         # DPO & GRPO
│   ├── [phase25/](/docs/phase25/)         # Inference Optimization
│   ├── [phase26/](/docs/phase26/)         # Test-Time Compute & Reasoning
│   ├── [phase27/](/docs/phase27/)         # Agentic AI
│   ├── [phase28/](/docs/phase28/)         # Multimodal AI
│   ├── [phase29/](/docs/phase29/)         # Generative Models — VAEs
│   ├── [phase30/](/docs/phase30/)         # Generative Models — GANs
│   ├── [phase31/](/docs/phase31/)         # Generative Models — Diffusion
│   ├── [phase32/](/docs/phase32/)         # Foundation Models & The Future
│   ├── [phase33/](/docs/phase33/)         # Mixture of Experts
│   ├── [phase34/](/docs/phase34/)         # Mamba & State Space Models
│   ├── [phase35/](/docs/phase35/)         # LoRA & Parameter-Efficient Fine-Tuning
│   ├── [phase36/](/docs/phase36/)         # Speculative Decoding
│   ├── [phase37/](/docs/phase37/)         # Retrieval-Augmented Generation
│   ├── [phase38/](/docs/phase38/)         # Scaling Laws & Compute-Optimal Training
│   ├── [phase39/](/docs/phase39/)         # Knowledge Distillation
│   ├── [phase40/](/docs/phase40/)         # Flow Matching & Diffusion Transformers
│   ├── [phase41/](/docs/phase41/)         # Vision-Language Instruction Tuning
│   ├── [phase42/](/docs/phase42/)         # Reasoning with Verifiable Rewards
│   ├── [phase43/](/docs/phase43/)         # Model Merging & Ensembles
│   ├── [phase44/](/docs/phase44/)         # Long Context & Position Interpolation
│   ├── [phase45/](/docs/phase45/)         # Quantization & GGUF
│   ├── [phase46/](/docs/phase46/)         # Mechanistic Interpretability
│   ├── [phase47/](/docs/phase47/)         # Synthetic Data & Self-Improvement
│   ├── [phase48/](/docs/phase48/)         # Test-Time Training
│   ├── [phase49/](/docs/phase49/)         # Advanced Optimizers
│   ├── [phase50/](/docs/phase50/)         # Self-Supervised Learning
│   ├── [phase51/](/docs/phase51/)         # Evaluation Metrics
│   ├── [phase52/](/docs/phase52/)         # Data Augmentation & Tokenization
│   ├── [phase53/](/docs/phase53/)         # Classical Reinforcement Learning
│   ├── [phase54/](/docs/phase54/)         # Graph Neural Networks
│   ├── [phase55/](/docs/phase55/)         # Distributed Training
│   ├── [phase56/](/docs/phase56/)         # Gradient Boosting
│   ├── [phase57/](/docs/phase57/)         # Adversarial Robustness
│   ├── [phase58/](/docs/phase58/)         # Time Series Forecasting
│   ├── [phase59/](/docs/phase59/)         # Federated Learning
│   ├── [phase60/](/docs/phase60/)         # Bayesian Neural Networks
│   ├── [phase61/](/docs/phase61/)         # AutoML & Hyperparameter Search
│   ├── [phase62/](/docs/phase62/)         # Active Learning
│   ├── [phase63/](/docs/phase63/)         # Dataset Curation for Fine-Tuning
│   ├── [phase64/](/docs/phase64/)         # Practical SFT with LoRA
│   ├── [phase65/](/docs/phase65/)         # QLoRA & Memory-Efficient Training
│   ├── [phase66/](/docs/phase66/)         # Preference Alignment (DPO & ORPO)
│   ├── [phase67/](/docs/phase67/)         # Jailbreaking — Basic Attacks
│   ├── [phase68/](/docs/phase68/)         # Jailbreaking — Advanced (GCG & AutoDAN)
│   ├── [phase69/](/docs/phase69/)         # Red-Teaming & Safety Evaluation
│   ├── [phase70/](/docs/phase70/)         # Domain Adaptation — Custom Assistants
│   ├── [phase71/](/docs/phase71/)         # Inference & Deployment
│   ├── [phase72/](/docs/phase72/)         # Real Agents with Tool Use
│   ├── [phase73/](/docs/phase73/)         # Speech & Audio
│   ├── [phase74/](/docs/phase74/)         # Recommendation Systems
│   ├── [phase75/](/docs/phase75/)         # Explainable AI (XAI)
│   ├── [phase76/](/docs/phase76/)         # Fairness & Bias
│   ├── [phase77/](/docs/phase77/)         # Unsupervised Learning
│   ├── [phase78/](/docs/phase78/)         # Object Detection & Segmentation
│   ├── [phase79/](/docs/phase79/)         # Causal Inference
│   ├── [phase80/](/docs/phase80/)         # MLOps
│   ├── [phase81/](/docs/phase81/)         # Continual Learning
│   ├── [phase83/](/docs/phase83/)         # GPU Kernel Optimization
│   ├── [phase84/](/docs/phase84/)         # Memory Engineering
│   ├── [phase85/](/docs/phase85/)         # Multi-Node Training
│   ├── [phase86/](/docs/phase86/)         # JAX & XLA
│   ├── [phase87/](/docs/phase87/)         # Checkpointing & Fault Tolerance
│   ├── [phase88/](/docs/phase88/)         # Docker, Kubernetes & Orchestration
│   ├── [phase89/](/docs/phase89/)         # Data Engineering at Scale
│   ├── [phase90/](/docs/phase90/)         # Inference Serving
│   ├── [phase91/](/docs/phase91/)         # Experiment Tracking & MLOps
│   ├── [phase92/](/docs/phase92/)         # Benchmark Design
│   ├── [phase93/](/docs/phase93/)         # Paper Reading & Reproduction
│   ├── [phase94/](/docs/phase94/)         # Statistical Rigor
│   ├── [phase95/](/docs/phase95/)         # Open Source & Research Communication
│   ├── [phase96/](/docs/phase96/)         # Sparse MoE Training
│   ├── [phase97/](/docs/phase97/)         # Extreme Context Windows
│   ├── [phase98/](/docs/phase98/)         # System-2 Reasoning
│   ├── [phase99/](/docs/phase99/)         # Video & 3D Generation
│   ├── [phase100/](/docs/phase100/)       # Automated Circuit Discovery
│   ├── [phase101/](/docs/phase101/)       # Advanced Alignment
│   ├── [phase102/](/docs/phase102/)       # Synthetic Data Bootstrapping
│   ├── [phase103/](/docs/phase103/)       # Multimodal Data Curation
│   ├── [phase104/](/docs/phase104/)       # Architecture Search
│   ├── [phase105/](/docs/phase105/)       # Tiny ML & Edge Deployment
│   ├── [phase106/](/docs/phase106/)       # AI for Science
│   ├── [phase107/](/docs/phase107/)       # On-Device LLMs
│   ├── [phase108/](/docs/phase108/)       # Multimodal Reasoning
│   ├── [phase109/](/docs/phase109/)       # World Models
│   └── [phase110/](/docs/phase110/)       # Test-Time Compute Scaling
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
# [Phase 0: Basics](docs/phase0/)
python src/phase0/phase0_basics.py

# [Phase 1: Linear Regression](docs/phase1/)
python src/phase1/phase1_linear_regression.py

# [Phase 2: Error and Gradients](docs/phase2/)
python src/phase2/phase2_learning_process.py

# [Phase 3: Learning (Gradient Descent)](docs/phase3/)
python src/phase3/phase3_gradient_descent.py

# [Phase 4: Neural Network](docs/phase4/)
python src/phase4/phase4_neural_network.py

# [Phase 5: Binary Classification](docs/phase5/)
python src/phase5/phase5_binary_classifier.py

# [Phase 6: Multi-Class Classification](docs/phase6/)
python src/phase6/phase6_multiclass_classifier.py

# [Phase 7: Deep Networks](docs/phase7/)
python src/phase7/phase7_deep_network.py

# [Phase 8: L2 Regularization](docs/phase8/)
python src/phase8/phase8_l2_regularization.py

# [Phase 9: Dropout](docs/phase9/)
python src/phase9/phase9_dropout.py

# [Phase 10: Batch Normalization](docs/phase10/)
python src/phase10/phase10_batch_normalization.py

# [Phase 11: CNNs](docs/phase11/)
python src/phase11/phase11_cnn.py

# [Phase 12: ResNets](docs/phase12/)
python src/phase12/phase12_resnet.py

# [Phase 13: RNNs](docs/phase13/)
python src/phase13/phase13_rnn.py

# [Phase 14: LSTMs](docs/phase14/)
python src/phase14/phase14_lstm.py

# [Phase 15: Word Embeddings](docs/phase15/)
python src/phase15/phase15_word2vec.py

# [Phase 16: Seq2Seq](docs/phase16/)
python src/phase16/phase16_seq2seq.py

# [Phase 17: Attention](docs/phase17/)
python src/phase17/phase17_attention.py

# [Phase 18: Transformer](docs/phase18/)
python src/phase18/phase18_transformer.py

# [Phase 19: BERT](docs/phase19/)
python src/phase19/phase19_bert.py

# [Phase 20: GPT Architecture](docs/phase20/)
python src/phase20/phase20_gpt.py

# [Phase 21: Training a Tiny GPT](docs/phase21/)
python src/phase21/phase21_tiny_gpt.py

# [Phase 22: Supervised Fine-Tuning](docs/phase22/)
python src/phase22/phase22_sft.py

# [Phase 23: RLHF](docs/phase23/)
python src/phase23/phase23_rlhf.py

# [Phase 24: DPO & GRPO](docs/phase24/)
python src/phase24/phase24_dpo_grpo.py

# [Phase 25: Inference Optimization](docs/phase25/)
python src/phase25/phase25_inference_optimization.py

# [Phase 26: Test-Time Compute & Reasoning](docs/phase26/)
python src/phase26/phase26_test_time_compute.py

# [Phase 27: Agentic AI](docs/phase27/)
python src/phase27/phase27_agentic_ai.py

# [Phase 28: Multimodal AI](docs/phase28/)
python src/phase28/phase28_multimodal_ai.py

# [Phase 29: Generative Models — VAEs](docs/phase29/)
python src/phase29/phase29_vae.py

# [Phase 30: Generative Models — GANs](docs/phase30/)
python src/phase30/phase30_gan.py

# [Phase 31: Generative Models — Diffusion](docs/phase31/)
python src/phase31/phase31_diffusion.py

# [Phase 32: Foundation Models & The Future](docs/phase32/)
python src/phase32/phase32_foundation_models.py

# [Phase 33: Mixture of Experts](docs/phase33/)
python src/phase33/phase33_moe.py

# [Phase 34: Mamba & State Space Models](docs/phase34/)
python src/phase34/phase34_mamba.py

# [Phase 35: LoRA & Parameter-Efficient Fine-Tuning](docs/phase35/)
python src/phase35/phase35_lora.py

# [Phase 36: Speculative Decoding](docs/phase36/)
python src/phase36/phase36_speculative_decoding.py

# [Phase 37: Retrieval-Augmented Generation](docs/phase37/)
python src/phase37/phase37_rag.py

# [Phase 38: Scaling Laws & Compute-Optimal Training](docs/phase38/)
python src/phase38/phase38_scaling_laws.py

# [Phase 39: Knowledge Distillation](docs/phase39/)
python src/phase39/phase39_knowledge_distillation.py

# [Phase 40: Flow Matching & Diffusion Transformers](docs/phase40/)
python src/phase40/phase40_flow_matching.py

# [Phase 41: Vision-Language Instruction Tuning](docs/phase41/)
python src/phase41/phase41_vlm.py

# [Phase 42: Reasoning with Verifiable Rewards](docs/phase42/)
python src/phase42/phase42_verifiable_rewards.py

# [Phase 43: Model Merging & Ensembles](docs/phase43/)
python src/phase43/phase43_model_merging.py

# [Phase 44: Long Context & Position Interpolation](docs/phase44/)
python src/phase44/phase44_long_context.py

# [Phase 45: Quantization & GGUF](docs/phase45/)
python src/phase45/phase45_quantization.py

# [Phase 46: Mechanistic Interpretability](docs/phase46/)
python src/phase46/phase46_mechanistic_interpretability.py

# [Phase 47: Synthetic Data & Self-Improvement](docs/phase47/)
python src/phase47/phase47_synthetic_data.py

# [Phase 48: Test-Time Training](docs/phase48/)
python src/phase48/phase48_test_time_training.py

# [Phase 49: Advanced Optimizers](docs/phase49/)
python src/phase49/phase49_advanced_optimizers.py

# [Phase 50: Self-Supervised Learning](docs/phase50/)
python src/phase50/phase50_self_supervised_learning.py

# [Phase 51: Evaluation Metrics](docs/phase51/)
python src/phase51/phase51_evaluation_metrics.py

# [Phase 52: Data Augmentation & Tokenization](docs/phase52/)
python src/phase52/phase52_data_augmentation.py

# [Phase 53: Classical Reinforcement Learning](docs/phase53/)
python src/phase53/phase53_classical_rl.py

# [Phase 54: Graph Neural Networks](docs/phase54/)
python src/phase54/phase54_graph_neural_networks.py

# [Phase 55: Distributed Training](docs/phase55/)
python src/phase55/phase55_distributed_training.py

# [Phase 56: Gradient Boosting](docs/phase56/)
python src/phase56/phase56_gradient_boosting.py

# [Phase 57: Adversarial Robustness](docs/phase57/)
python src/phase57/phase57_adversarial_robustness.py

# [Phase 58: Time Series Forecasting](docs/phase58/)
python src/phase58/phase58_time_series_forecasting.py

# [Phase 59: Federated Learning](docs/phase59/)
python src/phase59/phase59_federated_learning.py

# [Phase 60: Bayesian Neural Networks](docs/phase60/)
python src/phase60/phase60_bayesian_neural_networks.py

# [Phase 61: AutoML & Hyperparameter Search](docs/phase61/)
python src/phase61/phase61_automl.py

# [Phase 62: Active Learning](docs/phase62/)
python src/phase62/phase62_active_learning.py

# [Phase 63: Dataset Curation for Fine-Tuning](docs/phase63/)
python src/phase63/phase63_dataset_curation.py

# [Phase 64: Practical SFT with LoRA (Colab)](docs/phase64/)
# Upload src/phase64/phase64_sft_lora_colab.py to Colab T4

# [Phase 65: QLoRA & Memory-Efficient Training (Colab)](docs/phase65/)
# Upload src/phase65/phase65_qlora_colab.py to Colab T4

# [Phase 66: Preference Alignment DPO & ORPO (Colab)](docs/phase66/)
# Upload src/phase66/phase66_dpo_orpo_colab.py to Colab T4

# [Phase 67: Jailbreaking — Basic Attacks](docs/phase67/)
python src/phase67/phase67_jailbreak_basic.py

# [Phase 67: Jailbreaking — Basic Attacks (Colab)](docs/phase67/)
# Upload src/phase67/phase67_jailbreak_basic_colab.py to Colab T4

# [Phase 68: Jailbreaking — Advanced GCG & AutoDAN](docs/phase68/)
python src/phase68/phase68_jailbreak_advanced.py

# [Phase 68: Jailbreaking — Advanced GCG & AutoDAN (Colab)](docs/phase68/)
# Upload src/phase68/phase68_jailbreak_advanced_colab.py to Colab T4

# [Phase 69: Red-Teaming & Safety Evaluation (Colab)](docs/phase69/)
# Upload src/phase69/phase69_red_teaming_colab.py to Colab T4

# [Phase 70: Domain Adaptation — Custom Assistants](docs/phase70/)
python src/phase70/phase70_domain_adaptation.py

# [Phase 70: Domain Adaptation — Custom Assistants (Colab)](docs/phase70/)
# Upload src/phase70/phase70_domain_adaptation_colab.py to Colab T4

# [Phase 71: Inference & Deployment (Colab)](docs/phase71/)
# Upload src/phase71/phase71_inference_deployment_colab.py to Colab T4

# [Phase 72: Real Agents with Tool Use (Colab)](docs/phase72/)
# Upload src/phase72/phase72_real_agents_colab.py to Colab T4

# [Phase 73: Speech & Audio](docs/phase73/)
python src/phase73/phase73_speech_audio.py

# [Phase 73: Speech & Audio (Colab)](docs/phase73/)
# Upload src/phase73/phase73_speech_audio_colab.py to Colab T4

# [Phase 74: Recommendation Systems](docs/phase74/)
python src/phase74/phase74_recommendation_systems.py

# [Phase 74: Recommendation Systems (Colab)](docs/phase74/)
# Upload src/phase74/phase74_recommendation_systems_colab.py to Colab T4

# [Phase 75: Explainable AI (XAI)](docs/phase75/)
python src/phase75/phase75_xai_numpy.py

# [Phase 75: Explainable AI (XAI) (Colab)](docs/phase75/)
# Upload src/phase75/phase75_xai_colab.py to Colab T4

# [Phase 76: Fairness & Bias](docs/phase76/)
python src/phase76/phase76_fairness_bias.py

# [Phase 76: Fairness & Bias (Colab)](docs/phase76/)
# Upload src/phase76/phase76_fairness_bias_colab.py to Colab T4

# [Phase 77: Unsupervised Learning](docs/phase77/)
python src/phase77/phase77_unsupervised_learning.py

# [Phase 77: Unsupervised Learning (Colab)](docs/phase77/)
# Upload src/phase77/phase77_unsupervised_learning_colab.py to Colab T4

# [Phase 78: Object Detection & Segmentation](docs/phase78/)
python src/phase78/phase78_object_detection.py

# [Phase 78: Object Detection & Segmentation (Colab)](docs/phase78/)
# Upload src/phase78/phase78_object_detection_colab.py to Colab T4

# [Phase 79: Causal Inference](docs/phase79/)
python src/phase79/phase79_causal_inference.py

# [Phase 79: Causal Inference (Colab)](docs/phase79/)
# Upload src/phase79/phase79_causal_inference_colab.py to Colab T4

# [Phase 80: MLOps](docs/phase80/)
python src/phase80/phase80_mlops.py

# [Phase 80: MLOps (Colab)](docs/phase80/)
# Upload src/phase80/phase80_mlops_colab.py to Colab T4

# [Phase 81: Continual Learning](docs/phase81/)
python src/phase81/phase81_continual_learning.py

# [Phase 81: Continual Learning (Colab)](docs/phase81/)
# Upload src/phase81/phase81_continual_learning_colab.py to Colab T4
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
| Phase 49 | 4 | 1 | 4 |
| Phase 50 | 4 | 1 | 4 |
| Phase 51 | 4 | 1 | 4 |
| Phase 52 | 4 | 1 | 4 |
| Phase 53 | 4 | 1 | 4 |
| Phase 54 | 4 | 1 | 4 |
| Phase 55 | 4 | 1 | 4 |
| Phase 56 | 4 | 1 | 4 |
| Phase 57 | 4 | 1 | 4 |
| Phase 58 | 4 | 1 | 4 |
| Phase 59 | 4 | 1 | 4 |
| Phase 60 | 4 | 1 | 4 |
| Phase 61 | 4 | 1 | 4 |
| Phase 62 | 4 | 1 | 4 |
| Phase 63 | 4 | 2 | 4 |
| Phase 64 | 4 | 2 | 4 |
| Phase 65 | 4 | 2 | 4 |
| Phase 66 | 4 | 2 | 4 |
| Phase 67 | 4 | 2 | 4 |
| Phase 68 | 4 | 2 | 4 |
| Phase 69 | 4 | 2 | 4 |
| Phase 70 | 4 | 2 | 4 |
| Phase 71 | 4 | 2 | 4 |
| Phase 72 | 4 | 2 | 4 |
| Phase 73 | 4 | 2 | 4 |
| Phase 74 | 4 | 2 | 4 |
| Phase 75 | 4 | 2 | 4 |
| Phase 76 | 4 | 2 | 4 |
| Phase 77 | 4 | 2 | 4 |
| Phase 78 | 4 | 2 | 4 |
| Phase 79 | 4 | 2 | 4 |
| Phase 80 | 4 | 2 | 4 |
| Phase 81 | 4 | 2 | 4 |
| Phase 83 | 4 | 1 | 3 |
| Phase 84 | 4 | 1 | 3 |
| Phase 85 | 4 | 1 | 3 |
| Phase 86 | 4 | 1 | 3 |
| Phase 87 | 4 | 1 | 3 |
| Phase 88 | 4 | 1 | 3 |
| Phase 89 | 4 | 1 | 3 |
| Phase 90 | 4 | 1 | 3 |
| Phase 91 | 4 | 1 | 3 |
| Phase 92 | 4 | 1 | 3 |
| Phase 93 | 4 | 1 | 3 |
| Phase 94 | 4 | 1 | 3 |
| Phase 95 | 4 | 1 | 3 |
| Phase 96 | 4 | 1 | 3 |
| Phase 97 | 4 | 1 | 3 |
| Phase 98 | 4 | 1 | 3 |
| Phase 99 | 4 | 1 | 3 |
| Phase 100 | 4 | 1 | 3 |
| Phase 101 | 4 | 1 | 3 |
| Phase 102 | 4 | 1 | 3 |
| Phase 103 | 4 | 1 | 3 |
| Phase 104 | 4 | 1 | 3 |
| Phase 105 | 4 | 1 | 3 |
| Phase 106 | 4 | 1 | 3 |
| Phase 107 | 4 | 1 | 3 |
| Phase 108 | 4 | 1 | 3 |
| Phase 109 | 4 | 1 | 3 |
| Phase 110 | 4 | 1 | 3 |
| **Total** | **415** | **155** | **387** |

---

## Final Message

You just built an AI system from absolute zero.

You started with the question "What is a function?" and ended with a complete understanding of modern AI. Through one hundred ten phases, you went from simple predictions all the way to building production-ready applied AI systems and understanding frontier research.

---

### What You Learned

**Foundations (Phases 0-10)**
You learned what a model is, how gradient descent finds better parameters, why neural networks need depth, and how regularization, dropout, and batch normalization make deep learning actually work.

**Seeing and Remembering (Phases 11-14)**
You built convolutional networks that see, residual networks that train to arbitrary depth, recurrent networks that remember sequences, and LSTMs that preserve long-term dependencies.

**Understanding Language (Phases 15-24)**
You embedded words into meaning spaces, built sequence-to-sequence translators, discovered attention, constructed the Transformer from scratch, trained BERT to understand context and GPT to generate text. Then you aligned these models with human values through RLHF, DPO, and GRPO.

**Making AI Useful (Phases 25-28)**
You optimized inference with KV caching and Flash Attention, taught models to reason through chain-of-thought, built agents that use tools, and connected vision and language into unified multimodal systems.

**Creating Data (Phases 29-31)**
You built variational autoencoders that learn compressed representations, GANs that compete to generate realistic images, and diffusion models that denoise their way to photorealistic output.

**The Future (Phases 32-46)**
You scaled beyond dense limits with Mixture of Experts, processed infinite sequences in linear time with Mamba, adapted giant models cheaply with LoRA, accelerated generation with speculative decoding, grounded outputs with retrieval-augmented generation, allocated compute optimally with scaling laws, distilled massive teachers into tiny students, replaced diffusion with flow matching, built vision-language conversational agents, trained reasoning models with verifiable rewards, merged specialist models without retraining, extended context windows to entire books, shrank models 4-8× with quantization, and reverse-engineered neural networks to understand what individual neurons compute.

**Data and Training (Phases 47-56)**
You broke the data wall with synthetic generation and self-improvement, adapted models in real time with test-time training, optimized convergence with Adam and learning rate schedules, learned from unlabeled data with self-supervised learning, measured quality with rigorous metrics, prepared training data with augmentation and tokenization, taught agents to learn from rewards with Q-learning and policy gradients, applied deep learning to graphs with GNNs, trained across thousands of GPUs with distributed data and model parallelism, and combined weak models into strong predictors with gradient boosting.

**Robustness and Uncertainty (Phases 57-62)**
You defended models against adversarial attacks with FGSM, PGD, and adversarial training. You forecasted temporal sequences with autoregressive models and exponential smoothing. You trained on decentralized data without centralization through federated learning and differential privacy. You quantified prediction uncertainty with Bayesian neural networks and Monte Carlo dropout. You automated model selection with AutoML and successive halving. And you intelligently selected which data to label when labeling is expensive through active learning.

**Applied AI (Phases 63-78)**
You curated real instruction-following datasets, applied chat templates, and packed sequences for GPU efficiency. You fine-tuned open-source models with LoRA and QLoRA on consumer hardware. You aligned models with human preferences using DPO and ORPO. You executed and defended against jailbreak attacks — from basic roleplay and encoding tricks to automated GCG adversarial suffix optimization. You red-teamed models for safety vulnerabilities across harm taxonomies. You built domain-specific assistants for medicine, law, and coding. You deployed models at scale with vLLM, dynamic batching, and ONNX export. You built real agentic systems with ReAct loops, function calling, and multi-turn tool use. You personalized content at scale with collaborative filtering, matrix factorization, two-tower retrieval, and ranking losses. You closed the sensory loop by teaching machines to hear and speak with ASR, TTS, mel-spectrograms, and Speech Transformers. You discovered hidden structure in unlabeled data with K-means, PCA, t-SNE, and DBSCAN. And you taught machines to see not just what is in an image, but where objects are and what shape they take, using bounding boxes, single-shot detectors, and pixel-perfect segmentation masks.

**Systems & Frontier (Phases 83-110)**
You wrote conceptual GPU kernels and understood SIMT execution, warps, and memory coalescing. You engineered memory for training at scale through activation checkpointing, gradient accumulation, and bandwidth optimization. You synchronized gradients across distributed machines with ring-allreduce and collective communication. You explored functional ML programming with JAX, XLA, and JIT compilation. You built resilient training systems with checkpointing, fault tolerance, and deterministic seeding. You containerized ML workflows and orchestrated them with Kubernetes concepts. You processed web-scale data with MinHash deduplication, quality filtering, and perplexity scoring. You served models efficiently with PagedAttention, continuous batching, and KV cache management. You tracked experiments, designed benchmarks, read papers rigorously, applied statistical significance testing, and contributed to open source. You scaled model capacity with sparse Mixture of Experts and load-balanced routing. You extended context windows to hundreds of thousands of tokens with ring attention and positional extrapolation. You trained models to think step-by-step with process reward models, chain-of-thought, and self-consistency. You generated video and 3D content with spatiotemporal diffusion and Gaussian splatting. You reverse-engineered neural networks with mechanistic interpretability, attribution patching, and sparse autoencoders. You aligned AI beyond RLHF through constitutional AI, debate, and iterated amplification. You bootstrapped training data with rejection sampling and verifier-augmented generation. You curated multimodal datasets with contrastive filtering and CLIP scoring. You designed architectures with inductive bias and scaling law awareness. You compressed models for edge deployment with quantization-aware training and knowledge distillation. You applied AI to science with equivariant networks and molecular diffusion. You ran language models on-device with INT4 quantization and latency-aware design. You reasoned across vision and language with cross-modal attention. You planned in learned world models with model predictive control. And you scaled intelligence at test time through search, refinement loops, and best-of-N sampling.

---

### The Fancy Words

These are not magic. They are systematic ways of doing the same five things:

**Core mechanics:** gradient descent, backpropagation, neural network, weight, bias, activation, loss function, optimizer, learning rate, batch, epoch, overfitting, underfitting, regularization, dropout, batch normalization

**Architectures:** convolution, residual connection, LSTM, GRU, attention, self-attention, multi-head attention, Transformer, encoder, decoder, BERT, GPT, vision transformer, U-Net, diffusion transformer, Mamba, state space model

**Training at scale:** data parallelism, model parallelism, pipeline parallelism, gradient accumulation, all-reduce, distributed SGD, mixed precision, gradient clipping, gradient checkpointing

**Making models useful:** RLHF, DPO, ORPO, GRPO, instruction tuning, SFT, chain of thought, self-consistency, tool use, agent, ReAct, function calling, retrieval-augmented generation, vector database, embedding, prompt engineering

**Efficiency:** LoRA, QLoRA, PEFT, quantization, GPTQ, AWQ, GGUF, pruning, knowledge distillation, speculative decoding, KV cache, Flash Attention, continuous batching

**Creating data:** VAE, GAN, diffusion, flow matching, latent space, forward diffusion, reverse diffusion, noise scheduling, classifier-free guidance

**Understanding internals:** mechanistic interpretability, activation patching, sparse autoencoder, superposition, feature visualization, logit lens

**Safety:** adversarial example, FGSM, PGD, adversarial training, jailbreak, red-teaming, safety benchmark, harm taxonomy, content moderation, differential privacy, constitutional AI

**Specialized domains:** graph neural network, GCN, GAT, message passing, federated learning, federated averaging, non-IID data, Bayesian neural network, Monte Carlo dropout, variational inference, epistemic uncertainty, time series, autoregressive model, exponential smoothing, seasonality decomposition, AutoML, hyperparameter search, neural architecture search, successive halving, active learning, uncertainty sampling, ASR, TTS, spectrogram, mel-filterbank, MFCC, CTC, vocoder, wav2vec, Whisper, object detection, bounding box, IoU, non-maximum suppression, anchor box, YOLO, R-CNN, Faster R-CNN, Region Proposal Network, semantic segmentation, instance segmentation, panoptic segmentation, mask, U-Net, SAM, Segment Anything

**Unsupervised learning:** K-means, PCA, t-SNE, DBSCAN, clustering, centroid, elbow method, eigenvector, eigenvalue, dimensionality reduction, density-based clustering

---

### What AI Actually Is

1. Making a guess
2. Measuring how wrong the guess is
3. Figuring out which direction to improve
4. Taking a small step
5. Repeating

That is all AI is. And now you know it from the inside out.

**Keep going. You have everything you need.**
