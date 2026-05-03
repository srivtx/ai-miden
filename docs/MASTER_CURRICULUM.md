# AI-MIDEN: The Complete Master Curriculum

> **From Absolute Zero to Understanding Modern AI**
> 
> Every concept. Every architecture. Every "why."
> Built from scratch in Python + NumPy.
> No shortcuts. Nothing skipped.

---

## How to Read This Map

Each phase has:
- **The Natural Question** — what the student asks after finishing the previous phase
- **New Concepts** — what is introduced (usually 1-3)
- **Why It Is Needed** — the problem this phase solves
- **What We Build** — the actual code project
- **The Analogy** — how to think about it intuitively
- **Connects To** — which future phases build on this

---

## Phase 0: Absolute Zero (COMPLETED)

**The Question:** "What even is AI?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| AI | Computers learn patterns from examples instead of following explicit rules | Child learning dogs by seeing pictures, not by checklist |
| Prediction | Making educated guesses about unknown values | Weather forecast from current conditions |
| Function | Reliable input-to-output transformation | Blender: fruit in, smoothie out |
| Input/Output | Separating what we know from what we want to find out | Vending machine: button press → chips |

**What We Built:** `phase0_basics.py` — A function that predicts pizza prices from examples.

**Leads To:** "If the computer can learn patterns, how do I build a real model?"

---

## Phase 1: First Model (COMPLETED)

**The Question:** "How do I build a model that learns from data?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Model | A chosen template for the pattern (we pick "straight line") | Cookie cutter: decides the general shape |
| Parameter | Adjustable numbers inside the model | Radio tuning knob and volume dial |
| Weight | Controls how much influence each input has | Recipe: flour matters more than salt |
| Bias | Shifts the output up or down | Phone bill base fee: you pay $20 even with 0 minutes |
| NumPy | Python tool for doing math on groups of numbers | Shopping cart: move 50 items at once instead of one by one |

**What We Built:** `phase1_linear_regression.py` — A model that draws a line through house price data.

**Leads To:** "I can make predictions, but I guessed the parameters by hand. How do I find them automatically?"

---

## Phase 2: The Learning Process (COMPLETED)

**The Question:** "How do I measure how wrong my model is?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Error | Difference between prediction and actual | Arrow distance from bullseye |
| Loss Function | One number summarizing all errors | GPA: one score from six test scores |
| Derivative | How fast output changes when input is nudged | Speedometer: rate of change, not position |
| Gradient | Which way to turn each parameter knob | Mountain climber feeling the slope in fog |

**What We Built:** `phase2_learning_process.py` — Measures predictions, errors, loss, and gradients. Does not learn yet.

**Leads To:** "We know which way to turn the knobs. How do we actually turn them?"

---

## Phase 3: The Learning Mechanism (COMPLETED)

**The Question:** "How do I automatically find the best parameters?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Gradient Descent | Repeated small steps opposite to gradient | Hiker in fog: feel slope, step downhill, repeat |
| Learning Rate | How big each step is | Shower knob: tiny turn = slow, huge crank = chaos |
| Optimization | The process of minimizing loss | Tuning a guitar: pluck, listen, adjust, repeat |

**What We Built:** `phase3_gradient_descent.py` — A training loop. Model starts at weight=0 and learns the correct pattern.

**Leads To:** "This works for straight lines. What about curves?"

---

## Phase 4: Neural Networks (COMPLETED)

**The Question:** "What if the pattern is NOT a straight line?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Neuron | Computing unit that takes inputs, applies weights, adds bias | Committee member weighing opinions before voting |
| Layer | Group of neurons working in parallel | Factory assembly line: each station builds on the previous |
| Neural Network | Many neurons in layers, outputs feed to next layer | Team of detectives: juniors observe, seniors combine, chief concludes |
| Activation Function (ReLU) | Introduces non-linearity so network can bend | Light switch: on if positive, off if negative |
| Non-Linearity | Real-world relationships are curved, not straight | Water filling a bathtub: level rises at changing rate |
| Forward Pass | Sending data through network to get prediction | Assembly line baking: dough → shape → bake → package |
| Chain Rule | Multiplying local effects to find total sensitivity | Domino chain: push first, each knocks next, find total effect on last |
| Backpropagation | Sending error backward to assign blame to each parameter | Group project: teacher gives bad grade, team traces blame backward |

**What We Built:** `phase4_neural_network.py` — Network with hidden layer + ReLU + manual backprop. Learns a parabola. 120× better than linear regression.

**Leads To:** "Our network predicts numbers. But what about YES/NO questions?"

---

## Phase 5: Binary Classification (COMPLETED)

**The Question:** "Can the network tell me YES or NO?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Sigmoid Activation | Squeezes any number into probability 0-1 | Thermostat: maps temperature to "how likely is it hot?" |
| Binary Cross-Entropy | Measures how wrong a probability guess is | Scoring a weather forecaster: 90% rain when it rains = good, 90% rain when sunny = terrible |
| Decision Boundary | The line separating YES from NO | Fence between two properties |

**Why It Is Needed:** The real world is full of YES/NO: spam detection, medical diagnosis, fraud detection.

**What We Build:** A network that classifies 2D points as red or blue. We visualize the decision boundary.

**Connects To:** Phase 6 (what if there are 3 colors?)

---

## Phase 6: Multi-Class Classification (COMPLETED)

**The Question:** "What if there are MORE than two possible answers?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Softmax Activation | Turns scores into valid probability distribution | Voting: 3 candidates, everyone gets a share of 100% |
| Categorical Cross-Entropy | Measures wrongness across multiple classes | Scoring a multiple-choice test |
| One-Hot Encoding | Representing "the answer is class 3" as [0,0,1,0,0] | Light switch panel: exactly one light is on |

**Why It Is Needed:** Most real problems have many options: digits 0-9, animal species, product categories.

**What We Build:** A network that classifies points into 3 spirals. We visualize the softmax probabilities.

**Connects To:** Phase 7 (one layer is not enough for hard problems)

---

## Phase 7: Deep Networks (COMPLETED)

**The Question:** "What if I add MORE hidden layers?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Multiple Hidden Layers | Complex patterns need hierarchical feature learning | Factory: raw materials → parts → assemblies → finished product |
| Xavier/He Initialization | Proper starting weights prevent vanishing/exploding gradients | Tuning guitar strings: too loose = no sound, too tight = snap |
| Depth vs. Width | More layers vs. more neurons per layer | Tall thin building vs. short wide building |

**Why It Is Needed:** One hidden layer can learn curves. But some patterns (like a sine wave) need multiple levels of abstraction.

**What We Build:** A 3-layer network that learns a sine wave. We compare 1-layer vs. 3-layer performance.

**Connects To:** Phase 8 (deep networks memorize training data)

---

## Phase 8: L2 Regularization (Weight Decay) (COMPLETED)

**The Question:** "My network gets 100% on training but fails on new data. How do I stop memorizing?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| L2 Penalty | Penalizes large weights, forcing simpler solutions | Speed limit: prevents driving recklessly fast |
| Bias-Variance Tradeoff | Simple models underfit; complex models overfit | Drawing with a thick marker (too simple) vs. thin pen copying every pixel (too complex) |
| Train/Validation Split | Holding out data to test generalization | Practicing with flashcards, then taking a real exam |

**Why It Is Needed:** Deep networks have enough parameters to memorize noise. Regularization forces them to learn robust patterns.

**What We Build:** Same deep network with L2 penalty added. We plot training vs. validation loss curves.

**Connects To:** Phase 9 (L2 keeps all neurons; what if we randomly disable some?)

---

## Phase 9: Dropout (COMPLETED)

**The Question:** "L2 shrinks weights but keeps every neuron active. Can we randomly 'damage' the network during training?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Dropout Masks | Randomly setting neurons to zero during training | Training basketball with one hand tied: forces using both hands equally |
| Training vs. Inference Behavior | Dropout is ON during training, OFF during testing | Practice with weighted bat; game with normal bat |
| Ensemble Approximation | Dropout approximates training many networks | Jury of 12 vs. one expert: more robust decisions |

**Why It Is Needed:** Prevents neurons from co-adapting too tightly. Forces robust feature learning.

**What We Build:** Deep network with dropout layers. We compare validation accuracy with/without dropout.

**Connects To:** Phase 10 (training is still unstable even with dropout)

---

## Phase 10: Batch Normalization (COMPLETED)

**The Question:** "Training deep nets is unstable — activations explode or vanish. How do I stabilize them?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Batch Normalization | Normalizing activations within each mini-batch | Audio engineer normalizing volume levels before mixing |
| Gamma/Beta Parameters | Learnable scale and shift after normalization | After normalizing, the model can learn to re-scale if needed |
| Internal Covariate Shift | Layer inputs changing distribution during training | Cooking while someone keeps changing the stove temperature |

**Why It Is Needed:** Keeps every layer's inputs in a stable range. Allows higher learning rates. Makes deep networks trainable.

**What We Build:** Deep network with BatchNorm. We visualize how activations stay stable during training.

**Connects To:** Phase 11 (images have 2D structure — fully connected layers waste parameters)

---

## Phase 11: CNNs Part 1 — Convolutions & Pooling (COMPLETED)

**The Question:** "Images have thousands of pixels. How do I process them without millions of weights?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Convolution Operation | Sliding a filter across an image to detect patterns | Flashlight scanning a dark room for objects |
| Filters/Kernels | Small matrices that detect edges, corners, textures | Cookie cutters of different shapes |
| Receptive Field | How much of the image a neuron can "see" | Looking through a straw vs. a wide window |
| Max-Pooling | Downsampling by taking maximum value in a region | Photograph thumbnail: keeps brightest/most important parts |
| Parameter Sharing | Same filter applied everywhere in the image | One detective skill used at every crime scene |

**Why It Is Needed:** Images have spatial locality and translation invariance. A cat in the top-left corner is still a cat. CNNs exploit this structure.

**What We Build:** A simple CNN from scratch on 8×8 synthetic images (X vs O). We visualize learned filters.

**Connects To:** Phase 12 (very deep CNNs get worse with more layers)

---

## Phase 12: CNNs Part 2 — Residual Networks (COMPLETED)

**The Question:** "I added more layers to my CNN and accuracy DROPPED. Why?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Degradation Problem | Deeper networks performing worse than shallow ones | Adding more chefs to a kitchen until they bump into each other |
| Skip Connections | Adding input directly to output, creating a shortcut | Express highway bypassing city traffic |
| Identity Mapping | Learning "do nothing" is easier than learning a transformation | Copy-paste vs. rewriting from scratch |

**Why It Is Needed:** Skip connections allow gradients to flow directly through the network, enabling 50+ layer CNNs.

**What We Build:** A ResNet-style block. We compare "plain" deep CNN vs. ResNet of equal depth.

**Connects To:** Phase 13 (images are 2D grids. What about text where ORDER matters?)

---

## Phase 13: Recurrent Neural Networks (RNNs) (COMPLETED)

**The Question:** "What if my input is a sentence or time series where order matters?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Sequential Data | Data where order cannot be shuffled | A sentence: "dog bites man" ≠ "man bites dog" |
| Hidden State | Memory that carries forward through time | A baton passed from runner to runner in a relay race |
| Backpropagation Through Time (BPTT) | Unrolling the loop and backpropagating through each step | Watching a video frame-by-frame in reverse to find where the mistake happened |

**Why It Is Needed:** Text, audio, and stock prices are sequences. RNNs maintain a "memory" of past inputs.

**What We Build:** A vanilla RNN for character-level prediction. We feed it "HELLO" and watch it predict the next character.

**Connects To:** Phase 14 (RNN forgets the beginning of long sentences)

---

## Phase 14: LSTMs & GRUs (COMPLETED)

**The Question:** "My RNN works for short words but forgets the subject in long sentences. How do I give it longer memory?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Cell State | A protected conveyor belt for long-term information | Airport baggage carousel: luggage stays on until claimed |
| Input Gate | Decides what new information to store | Security checkpoint: what gets into the airport |
| Forget Gate | Decides what old information to discard | Cleaning out fridge: what to keep, what to toss |
| Output Gate | Decides what to output based on current state | Stage curtain: what the audience sees |
| GRU | Simplified LSTM with fewer gates | LSTM is a Swiss watch; GRU is a reliable digital watch |

**Why It Is Needed:** Vanilla RNNs suffer from vanishing gradients. Gates create highways for gradient flow and allow selective memory.

**What We Build:** An LSTM for a long-range copy task. We show it remembers information across 50 steps.

**Connects To:** Phase 15 (LSTM treats "king" and "queen" as unrelated numbers)

---

## Phase 15: Word Embeddings (Word2Vec) (COMPLETED)

**The Question:** "If I have 50,000 words, my input layer is huge. How do I give words MEANING?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Dense Vectors | Small lists of numbers representing each word | GPS coordinates: nearby places have similar coordinates |
| Skip-Gram | Predicting context words from a center word | A friend describing someone by listing their friends |
| CBOW | Predicting center word from context words | Guessing a missing word in a sentence |
| Negative Sampling | Training by contrasting real pairs with fake pairs | Police lineup: pick the real suspect from fakes |
| Semantic Similarity | Similar words cluster in vector space | Map: "king" and "queen" are near each other, far from "apple" |

**Why It Is Needed:** One-hot encoding is wasteful and treats all words as unrelated. Embeddings capture meaning in geometry.

**What We Build:** Skip-gram with negative sampling on a tiny corpus. We visualize word vectors with t-SNE.

**Connects To:** Phase 16 (how do we translate "hello" to "bonjour" when input and output have different lengths?)

---

## Phase 16: Seq2Seq (Encoder-Decoder) (COMPLETED)

**The Question:** "How do I translate a sentence when input and output are different lengths?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Encoder | Compresses input sequence into a "thought vector" | Writer summarizing a book into one paragraph |
| Decoder | Expands thought vector into output sequence | Author writing a new book from a one-page outline |
| Context Vector | Fixed-size summary of the entire input | Cliff Notes: entire book compressed to 5 pages |
| Teacher Forcing | Feeding ground-truth to decoder during training | Piano teacher placing student's fingers on correct keys |

**Why It Is Needed:** Translation, summarization, and speech recognition have variable-length inputs AND outputs.

**What We Build:** LSTM encoder-decoder for character reversal ("hello" → "olleh").

**Connects To:** Phase 17 (one fixed-size vector cannot hold a long sentence)

---

## Phase 17: Attention Mechanism (COMPLETED)

**The Question:** "When translating long sentences, my model loses details. How can it focus on relevant parts?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Query-Key-Value (Q,K,V) | Query asks question, Key labels content, Value provides content | Library: research question, book titles, book contents |
| Attention Scores | How relevant each input position is to current output position | Relevance ranking of search results |
| Context Vector | Weighted sum of encoder states based on attention | Blending multiple expert opinions by importance |
| Alignment | Which input words map to which output words | Bilingual dictionary learned from data |

**Why It Is Needed:** The context vector bottleneck loses information. Attention lets the decoder dynamically focus on relevant input words.

**What We Build:** Seq2Seq with attention. We visualize attention weights as a heatmap.

**Connects To:** Phase 18 (RNNs are slow — can we process all words at once?)

---

## Phase 18: The Transformer Architecture (COMPLETED)

**The Question:** "GPUs have thousands of cores, but my LSTM uses only one at a time. Can I process ALL words in parallel?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Self-Attention | Every token attends to every other token simultaneously | Roundtable meeting: everyone talks to everyone at once |
| Multi-Head Attention | Multiple attention heads capturing different relationship types | Jury of experts: one focuses on motive, another on evidence, another on law |
| Positional Encoding | Injecting order information since attention ignores position | Choir seat numbers: everyone sings same note, but knows their place |
| Residual Connections | Adding input to output for gradient highways | Express lane bypassing toll booths |
| Layer Normalization | Stabilizing layer inputs | Audio engineer normalizing volumes |
| Feed-Forward Network | Processing each token independently after attention | Each choir member practices their solo after the group rehearsal |

**Why It Is Needed:** Self-attention captures global dependencies in one step and is massively parallelizable. No more slow sequential processing.

**What We Build:** A full Transformer (encoder-decoder) from scratch. We inspect individual attention heads.

**Connects To:** Phase 19 (bidirectional reading is great for understanding, but can we also generate text?)

---

## Phase 19: BERT (Bidirectional Encoder) (COMPLETED)

**The Question:** "The Transformer encoder reads the whole sentence in both directions. Can I use ONLY this for understanding tasks?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Masked Language Modeling (MLM) | Predicting hidden words from full context | Mad Libs: filling in blanks using surrounding words |
| [CLS] Token | Special token whose embedding represents the whole sentence | Book spine: one label summarizing the entire book |
| Fine-Tuning | Adapting a pre-trained model to a specific task | Musician who learned piano, now learning jazz improvisations |
| Transfer Learning | Using knowledge from one task to help another | Cooking skills transfer from Italian to French cuisine |

**Why It Is Needed:** BERT proved that deep bidirectional context learned via pre-training can be fine-tuned to shatter benchmarks.

**What We Build:** We demonstrate BERT-style masked prediction and fine-tune on a tiny sentiment task.

**Connects To:** Phase 20 (BERT cannot generate text left-to-right. What does a generative Transformer look like?)

---

## Phase 20: GPT Architecture (COMPLETED)

**The Question:** "BERT is bidirectional, so it cannot write a story word-by-word. What does a purely generative model look like?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Causal / Autoregressive Masking | Token can only see past tokens, not future | Author writing: can re-read what is written, cannot peek at next chapter |
| Decoder-Only Stack | Only the decoder half of the Transformer | One-way street vs. two-way street |
| Next-Token Prediction | Training objective: predict the next word | Completing sentences in a book |
| Prompting | Giving the model instructions through the input | Asking a novelist: "Write a mystery story about a lighthouse" |

**Why It Is Needed:** GPT showed that predicting the next token, at scale, produces reasoning, coding, and creativity.

**What We Build:** A decoder-only transformer that generates text one character at a time.

**Connects To:** Phase 21 (how do we actually TRAIN this to be helpful?)

---

## Phase 21: Training a Tiny GPT (COMPLETED)

**The Question:** "Can I put everything together and train a model that writes coherent sentences?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Character-Level Language Modeling | Predicting next character instead of next word | Learning to spell before learning vocabulary |
| Generation Loop | Sampling tokens one at a time and feeding them back | Improvisational jazz: each note inspires the next |
| Temperature Sampling | Controlling randomness in generation | Chef adding spice: low = consistent recipe, high = experimental |
| Top-k / Top-p Sampling | Limiting which tokens can be chosen | Menu with daily specials vs. full menu |

**Why It Is Needed:** We synthesize everything: embeddings + causal self-attention + feedforward + layer norm. We train on a small corpus and watch it generate.

**What We Build:** A ~100K parameter character-level GPT trained on Shakespeare. It generates coherent Elizabethan-style sentences.

**Connects To:** Phase 22 (pre-training produces a completion engine, not an assistant. How do we make it helpful?)

---

## Phase 22: Supervised Fine-Tuning (SFT) (COMPLETED)

**The Question:** "My GPT completes text, but it does not answer questions helpfully. How do I teach it to be an assistant?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Instruction-Response Pairs | Training data formatted as (question, answer) | Tutoring: student asks, teacher answers |
| Prompt Templates | Structured formatting for instructions | Mad Libs with fixed sections: instruction, context, response |
| System Prompt | Setting the model's behavior and persona | Stage directions: "You are a helpful assistant" |
| Catastrophic Forgetting | Losing pre-trained knowledge during fine-tuning | Student cramming for one exam and forgetting everything else |

**Why It Is Needed:** Pre-training teaches language structure. SFT teaches the FORMAT of being helpful — how to follow instructions and hold conversations.

**What We Build:** We fine-tune our tiny GPT on a tiny instruction dataset. It learns to answer questions instead of just completing text.

**Connects To:** Phase 23 (SFT alone is not enough — models still produce harmful or unhelpful outputs)

---

## Phase 23: RLHF — Reinforcement Learning from Human Feedback (COMPLETED)

**The Question:** "My assistant answers questions, but sometimes it is rude, biased, or unhelpful. How do I align it with human values?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Reward Model | A model that scores how good a response is | Food critic learning to rate dishes |
| PPO (Proximal Policy Optimization) | Stable RL algorithm that prevents drastic changes | Car with speed limiter: turn toward destination but not too sharply |
| KL Penalty | Punishing divergence from the original model | Bungee cord: explore for gold but don't wander too far |
| Reward Hacking | Exploiting loopholes in the reward model | Students stuffing essays with buzzwords to game the grading algorithm |
| Pairwise Comparisons | Humans pick better response from two options | Taste test: which soda do you prefer? |

**Why It Is Needed:** We cannot write a formula for "helpful and harmless." But we can collect human preferences and train a model to approximate them.

**What We Build:** A simplified RLHF pipeline on our tiny GPT. We collect preference data and update the model with PPO.

**Connects To:** Phase 24 (RLHF is complex. Is there a simpler way?)

---

## Phase 24: DPO & GRPO (Simpler Alignment) (COMPLETED)

**The Question:** "RLHF requires three models and is unstable. Is there a simpler way to align models?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| DPO (Direct Preference Optimization) | Skips reward model, optimizes preferences directly | Home cook tasting two dishes and remembering which is better — no critic needed |
| Implicit Reward | Using the model's own probabilities as reward | Student grading their own homework against the answer key |
| GRPO (Group Relative Policy Optimization) | Eliminates critic model by comparing responses within a group | Teacher comparing students' answers to each other instead of using an answer key |
| Relative Rewards | Advantage = response reward − group average | Grading on a curve |

**Why It Is Needed:** RLHF is complex, expensive, and unstable. DPO and GRPO simplify the pipeline while achieving similar results.

**What We Build:** We implement DPO on our tiny model and compare it to our earlier RLHF results.

**Connects To:** Phase 25 (the model is helpful but slow. How do I make it faster?)

---

## Phase 25: Inference Optimization (COMPLETED)

**The Question:** "My model takes forever to generate text. How do I make it fast?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| KV Cache | Reusing past key/value vectors instead of recomputing them | Keeping notes open while writing an essay |
| Flash Attention | Memory-efficient attention by tiling and keeping operations in fast SRAM | Chef keeping ingredients on the counter instead of walking to the pantry |
| Quantization (INT8/INT4) | Reducing weight precision to shrink model size | Converting RAW photo to JPEG: smaller, slightly less detail |
| Grouped Query Attention (GQA) | Sharing key/value across heads to reduce memory | Restaurant with one shared menu instead of copies for every waiter |

**Why It Is Needed:** At scale, memory and speed dominate cost. These techniques make large models deployable.

**What We Build:** We implement KV caching and demonstrate quantized inference on our tiny model.

**Connects To:** Phase 26 (can the model reason step-by-step?)

---

## Phase 26: Test-Time Compute & Reasoning (COMPLETED)

**The Question:** "My model blurts answers. Can I make it think longer on hard problems?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Chain of Thought (CoT) | Generating reasoning steps before answering | Showing work on a math exam |
| Self-Consistency | Sampling multiple answers and taking majority vote | Asking a room of experts and voting |
| Process Reward Models | Rewarding each reasoning step, not just final answer | Coach giving feedback after each drill, not just the final game |
| Outcome Reward Models | Rewarding only the final answer | Grading the final exam only |
| o1-Style Reasoning | Training the model to spend more compute on hard problems | Take-home exam vs. timed quiz: some problems need hours |

**Why It Is Needed:** Complex problems need more computation. Test-time compute trades speed for accuracy.

**What We Build:** We prompt our model with "think step by step" and show improvement on math problems.

**Connects To:** Phase 27 (can the model use tools?)

---

## Phase 27: Agentic AI (COMPLETED)

**The Question:** "My model can talk. Can I give it tools to actually DO things?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| AI Agent | System that perceives, plans, and acts | Consultant given a laptop, phone, budget, and a mandate |
| Tool Use | Calling external APIs (calculator, search, code) | Chef using a thermometer, not just intuition |
| ReAct Pattern | Interleaving reasoning and acting | Detective: think → search → observe → think again |
| Multi-Agent Systems | Multiple specialized agents collaborating | Research team: one researches, one writes, one reviews |
| Computer Use | Controlling GUIs directly | Robot using a mouse and keyboard |

**Why It Is Needed:** Real-world tasks require iteration and interaction, not just text generation.

**What We Build:** A simple agent that uses a calculator tool to solve math problems it cannot do alone.

**Connects To:** Phase 28 (can the model understand images too?)

---

## Phase 28: Multimodal AI (COMPLETED)

**The Question:** "My model only understands text. Can it see images too?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Vision Transformer (ViT) | Applying transformers directly to image patches | Reading a book by looking at paragraphs instead of individual letters |
| CLIP | Learning shared space for text and images | Translator who knows both languages so well that concepts map directly |
| Shared Embedding Space | Images and text mapped to same vectors | Universal translator device |
| DALL-E / Stable Diffusion | Generating images from text descriptions | Architect drawing from a written brief |
| GPT-4o | Unified multimodal reasoning | Person with all five senses intact |

**Why It Is Needed:** The real world is multimodal. Humans see, hear, and read simultaneously.

**What We Build:** A tiny CLIP-like model that learns to match text descriptions with simple shapes.

**Connects To:** Phase 29 (can the model CREATE new data?)

---

## Phase 29: Generative Models — VAEs (COMPLETED)

**The Question:** "My model classifies and generates text. Can it create entirely new images?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Autoencoder | Compresses input to latent space, then reconstructs | ZIP file: compress and decompress |
| Latent Space | Compressed representation where similar items cluster | Map where nearby cities have similar weather |
| VAE (Variational Autoencoder) | Latent space is a smooth probability distribution | Smooth map where you can interpolate between cities |
| Reparameterization Trick | Sampling from a distribution while keeping gradients differentiable | Dice with a dial: you can adjust the odds smoothly |
| KL Divergence | Penalizing deviation from a standard normal distribution | Keeping the map from stretching too far |

**Why It Is Needed:** Before generating images, you need a compressed, structured representation.

**What We Build:** A VAE on MNIST. We interpolate in latent space to morph digits.

**Connects To:** Phase 30 (VAE images are blurry. How do we make them sharp?)

---

## Phase 30: Generative Models — GANs (COMPLETED)

**The Question:** "My VAE produces blurry images. How do I generate sharp, realistic ones?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Generator | Creates fake data from noise | Art forger creating paintings |
| Discriminator | Detects real vs. fake data | Art inspector spotting forgeries |
| Minimax Game | Two networks competing | Counterfeiter vs. police: both get better |
| Mode Collapse | Generator producing limited variety of outputs | Forger who only paints one painting over and over |

**Why It Is Needed:** Adversarial training produces remarkably sharp images without explicit density estimation.

**What We Build:** A GAN that generates MNIST digits. We watch generator and discriminator losses duel.

**Connects To:** Phase 31 (GANs are unstable. Is there a more reliable way to generate images?)

---

## Phase 31: Generative Models — Diffusion (COMPLETED)

**The Question:** "GANs are hard to train and sometimes collapse. Is there a more stable way to generate images?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Forward Diffusion | Gradually adding noise to an image until it is pure static | Photo fading in the sun until it is white |
| Reverse Diffusion | Learning to denoise step by step | Restorer carefully removing dust from an old photo layer by layer |
| U-Net Architecture | Network shaped like an hourglass for image-to-image tasks | Funnel that compresses then expands |
| Timestep Conditioning | The network knows "how noisy" the current image is | Restorer knows the photo is 50% damaged vs. 90% damaged |

**Why It Is Needed:** Diffusion models are stable to train, cover all data modes, and currently produce the highest-quality images.

**What We Build:** A simplified diffusion model on MNIST. We visualize progressive denoising from static to clear digit.

**Connects To:** Phase 32 (how do we connect text transformers to image generators?)

---

## Phase 32: Foundation Models & The Future (COMPLETED)

**The Question:** "Having seen the entire landscape, where is AI going next?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Foundation Models | Large models pre-trained on broad data, adaptable to many tasks | Swiss Army knife: one tool, many uses |
| Contrastive Learning (CLIP-style) | Learning by comparing positive and negative pairs | Learning flavors by tasting similar vs. different foods |
| RLHF at Scale | Training on human preferences for safety | Teaching ethics by example, not by rules |
| Test-Time Training | Adapting the model during inference | Student who learns during the exam |
| World Models | Models that learn physics and causality | Virtual reality engine that understands gravity |

**Why It Is Needed:** This is the culmination. We have seen the entire evolution from linear regression to multimodal foundation models.

**What We Build:** A reflective project where the student uses their tiny GPT to explain what they have learned.

**Connects To:** Phase 33 (foundation models are huge. How do we scale capacity without scaling compute?)

---

## Phase 33: Mixture of Experts (COMPLETED)

**The Question:** "Bigger models are smarter, but training a dense trillion-parameter model is prohibitively expensive. How do you get massive capacity without massive compute?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Mixture of Experts (MoE) | Replacing dense FFNs with sparse expert subsets | Hospital with 100 specialists where each patient sees only 2 |
| Router Gating | Learnable assignment of tokens to experts | Restaurant host routing parties to specific chefs |
| Load Balancing | Preventing router collapse to a few easy experts | School principal redirecting overflow students to other classes |
| Expert Capacity | Hard limit on tokens per expert per batch | Toll booth that can only process 50 cars per hour |

**Why It Is Needed:** MoE decouples total parameter count from active compute. GPT-4, Mixtral, and DeepSeek-V3 all use MoE to achieve huge capacity without proportional cost.

**What We Build:** A tiny MoE layer with 4 experts and top-2 routing. We visualize routing specialization, load balancing, and capacity dropping. We compare parameter counts (total vs. active) against a dense baseline.

**Connects To:** Phase 34 (MoE scales model width. How do we scale sequence length efficiently?)

---

## Phase 34: Mamba & State Space Models (COMPLETED)

**The Question:** "Transformers use O(N²) attention. For long sequences, this is impossibly expensive. Is there a way to process sequences in linear time while maintaining Transformer-quality results?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| State Space Model (SSM) | Compressed state summary updated linearly per step | Note-taker maintaining a running summary instead of transcribing every word |
| Selectivity | Input-dependent gating for content-aware filtering | Security guard who sizes people up and writes detailed notes only for important visitors |
| Parallel Scan | Parallelizing sequential recurrences via tree reduction | Team of accountants computing running totals in log(N) parallel steps |
| Mamba | Selective SSM with hardware-aware parallel training | Elite executive assistant who maintains a concise, high-quality summary of every meeting |

**Why It Is Needed:** Mamba is the first sub-quadratic architecture to genuinely compete with Transformers on language. It removes the KV cache entirely, enabling million-token contexts with constant memory.

**What We Build:** A simplified selective SSM that learns to filter important impulses from noise. We compare training loss, memory usage, and scaling against a non-selective baseline and Transformer attention.

**Connects To:** Phase 35 (Mamba scales sequence length. How do we fine-tune huge models without full retraining?)

---

## Phase 35: LoRA & Parameter-Efficient Fine-Tuning (COMPLETED)

**The Question:** "Fine-tuning a 70B model requires a terabyte of GPU memory. How do you adapt giant models without updating billions of parameters?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| LoRA (Low-Rank Adaptation) | Low-rank matrices for cheap model adaptation | Interchangeable drill bits on a universal power drill |
| PEFT | Family of techniques for minimal-parameter adaptation | One motor, many cheap attachments |
| QLoRA | 4-bit base model + high-precision adapters | Architect using compressed blueprints with full-resolution edits |
| Adapter Merging | Combining BA into W for zero inference overhead | Printing a new permanent menu that includes popular daily specials |

**Why It Is Needed:** Full fine-tuning is inaccessible for most practitioners. PEFT democratizes customization by training only 0.1–2% of parameters while achieving comparable quality.

**What We Build:** A frozen base model and a tiny LoRA adapter (rank=2) that learns a low-rank adaptation. We compare parameter counts, show merging produces identical outputs, and demonstrate 80% parameter reduction.

**Connects To:** Phase 36 (we can adapt models cheaply. How do we make them generate faster?)

---

## Phase 36: Speculative Decoding (COMPLETED)

**The Question:** "Autoregressive generation produces one token per forward pass. For a 1000-token response, you need 1000 sequential passes. How do you generate multiple tokens without sacrificing quality?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Speculative Decoding | Using a fast draft model to predict multiple tokens verified by a slow target | Student taking practice exam, teacher grading all answers in one pass |
| Draft Model | Small approximate model for generating candidate tokens | Junior editor suggesting changes for senior editor review |
| Acceptance Sampling | Statistical guarantee that output matches target distribution exactly | Quality inspector using calibrated acceptance rules |
| Medusa Decoding | Multiple prediction heads on the target model itself | Chess player thinking several moves ahead and evaluating the line |

**Why It Is Needed:** LLM inference latency is dominated by the serial nature of autoregressive generation. Speculative decoding achieves 2–3× speedup with zero quality loss.

**What We Build:** A simulated draft model and target model over a small vocabulary. We implement the acceptance/rejection algorithm, measure speedup, and verify that the output distribution matches pure autoregressive sampling.

**Connects To:** Phase 37 (we can generate fast. How do we ground generation in external knowledge?)

---

## Phase 37: Retrieval-Augmented Generation (COMPLETED)

**The Question:** "LLMs only know their training data. They cannot access your private documents, today's news, or real-time information. How do you ground their answers in external knowledge without retraining?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| RAG | Augmenting LLM prompts with retrieved documents | Lawyer researching case law with a paralegal |
| Vector Database | Storing document embeddings for fast similarity search | Library organized by topic similarity instead of alphabet |
| Embedding Retrieval | Finding documents by semantic meaning instead of keywords | Perfume shop organizing scents by similarity in scent space |
| Context Injection | Inserting retrieved documents into the LLM prompt | Teacher placing relevant pages on a student's desk for an open-book exam |

**Why It Is Needed:** LLMs have knowledge cutoffs and hallucinate when uncertain. RAG grounds answers in real, up-to-date, and private documents without changing the model.

**What We Build:** A toy RAG system with 10 documents, bag-of-words embeddings, cosine similarity retrieval, and a tiny linear model. We compare answering with and without retrieved context.

**Connects To:** Phase 38 (we can scale models, adapt them, speed them up, and ground them. But how much data and compute do we actually need?)

---

## Phase 38: Scaling Laws & Compute-Optimal Training (COMPLETED)

**The Question:** "Training large models costs millions. For a fixed budget, should you build a bigger model or train longer? The field got this wrong for years — what is the right answer?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Scaling Laws | Empirical power laws predicting loss from model size and data | Predicting how fast a car goes based on engine size and fuel |
| Compute-Optimal Training | Balancing model size and data for fixed budgets | Building a library sized exactly for your book collection |
| Chinchilla Rule | Practical guideline: D ≈ 20N for optimal training | Training athletes with both good genetics AND proper conditioning |
| Data Wall | Finite high-quality training data limiting further scaling | Running out of textbooks to study from |

**Why It Is Needed:** Every training run at frontier labs uses Chinchilla-optimal or over-trained schedules. Understanding scaling laws is essential for making cost-effective training decisions.

**What We Build:** Simulated scaling law curves that show loss as a function of model size and data size. We compare Kaplan vs. Chinchilla frontiers, analyze real models (GPT-3, Gopher, Llama 3), and visualize the data wall.

**Connects To:** This is the culmination of the scaling thread — we now understand how to build, adapt, speed up, ground, and efficiently train modern AI systems.

---

## Phase 39: Knowledge Distillation (COMPLETED)

**The Question:** "You have a huge model that works great but is too slow for phones and too expensive for APIs. How do you transfer its intelligence into a tiny model without starting from scratch?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Knowledge Distillation | Transferring a large model's behavior to a small model | Master chef teaching an apprentice through tasting, not just recipes |
| Teacher Model | Large frozen model that generates soft training targets | University professor explaining nuanced reasoning |
| Soft Labels | Probability distributions encoding class similarities | Grading with partial credit based on answer similarity |
| Temperature Scaling | Controlling distribution sharpness to reveal more information | Professor explaining rejected alternatives in detail |

**Why It Is Needed:** Edge devices and cost-sensitive APIs need tiny models. Distillation produces 10-100× smaller models that retain most of the teacher's capability.

**What We Build:** A large teacher MLP and a small student MLP on a 3-class synthetic task. The student trained on the teacher's soft labels (T=4) matches the teacher's accuracy (78.7%), while the baseline student on hard labels alone lags behind (76.2%).

**Connects To:** Phase 40 (we can make models smaller through distillation. What other modern techniques reshape generative models?)

---

## Phase 40: Flow Matching & Diffusion Transformers (COMPLETED)

**The Question:** "DDPM diffusion works but trains indirectly (predict noise) and needs 1000 sampling steps. Is there a more direct, faster way to generate data?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Flow Matching | Direct velocity prediction for noise-to-data transformation | Sculptor using a motorized tool on an optimal carving path |
| Rectified Flow | Straight-line optimal transport paths | Flying the direct great-circle route instead of meandering |
| Diffusion Transformer | Transformer backbone replacing U-Net in generative models | Painter planning the entire mural globally instead of section by section |
| ODE Solver | Numerical integration of the velocity field | River navigator adjusting check frequency based on current turbulence |

**Why It Is Needed:** Flow matching is simpler to train and 10–50× faster to sample than DDPM. DiT scales better than U-Nets. Together they power SD3, Flux, and Sora.

**What We Build:** A velocity MLP that learns rectified flow on a 2D swirl dataset. We sample with Euler and midpoint ODE solvers, visualizing flow trajectories from noise to data.

**Connects To:** Phase 41 (we can generate images fast. How do we make models understand both images AND language in conversation?)

---

## Phase 41: Vision-Language Instruction Tuning (COMPLETED)

**The Question:** "You have a model that sees images and a model that writes text. How do you connect them so a user can ask 'What color is the cat in this image?' and get a real answer?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Vision-Language Instruction Tuning | Connecting vision encoders to language models for conversation | Translator at an art museum enabling the tour guide to describe paintings |
| Vision Encoder | Converting images into patch embeddings | Security camera noting visual features of a painting |
| Projection Layer | Mapping vision embeddings to language model space | Translator converting camera notes into words the tour guide understands |
| Multimodal Instruction Tuning | Training on visual Q&A conversations | Teaching a sighted person to actually look before answering |

**Why It Is Needed:** GPT-4V, Claude 3, and Gemini are all multimodal. VLMs power OCR, chart understanding, document QA, and robotics.

**What We Build:** A toy VLM on synthetic 4×4 images. With visual context: 95.6% accuracy. Without visual context: 20.6% accuracy (blind guessing). The architecture mirrors real VLMs: encoder → projection → classifier.

**Connects To:** Phase 42 (we can see and talk. How do we train models to reason deeply through self-play?)

---

## Phase 42: Reasoning with Verifiable Rewards (COMPLETED)

**The Question:** "You have a model that can answer questions, but getting human feedback for every answer is expensive and slow. How do you train it to reason when you can automatically check if the answer is correct?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Verifiable Reward | Automatic training signal from ground-truth checkers | Math answer key: instant, exact, free |
| GRPO | Eliminates critic by comparing outputs within a group | Teacher grading on a curve instead of using an answer key |
| Emergent Reasoning | Problem-solving behaviors arising from RL without explicit teaching | Child inventing puzzle strategies to earn more cookies |
| DeepSeek-R1 Reasoning Chain | Intermediate reasoning steps generated before final answer | Showing work on a math exam to catch mistakes |

**Why It Is Needed:** For math, code, and logic, we can check answers automatically. DeepSeek-R1-Zero trained a 671B model using ONLY verifiable math rewards — no human labels, no SFT — and the model spontaneously developed self-verification and backtracking.

**What We Build:** A tiny position-wise policy trained with GRPO on simple arithmetic. Correct answers get +1, wrong get 0. The model improves from 0% to 70% accuracy using only the answer checker as a teacher.

**Connects To:** Phase 43 (we can train models to reason. How do we combine multiple specialized models?)

---

## Phase 43: Model Merging & Ensembles (COMPLETED)

**The Question:** "You have three specialist models — one for coding, one for medical, one for legal. Each is great at its task but terrible at the others. How do you combine them into a single generalist without retraining?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Model Merging | Combining fine-tuned models by averaging weights in parameter space | Three chefs combining their specialty menus into one super-menu |
| Task Arithmetic | Adding task-specific deltas back to the base model | Keeping the standard recipe book and adding each chef's unique innovations as notes |
| SLERP | Spherical interpolation preserving weight vector norms | Flying the great-circle route instead of tunneling through the Earth |
| TIES-Merging | Trimming noise, electing majority sign, merging only agreed changes | Senior architect ignoring tiny changes and resolving conflicts by majority vote |

**Why It Is Needed:** Open-source communities create hundreds of fine-tuned models. Merging them in seconds on a CPU produces powerful multi-task models without any training cost. Many LLM leaderboard winners are merged models.

**What We Build:** A base linear model fine-tuned on three different synthetic tasks. We merge the three specialists using simple averaging, task arithmetic, SLERP, and TIES-Merging, then evaluate multi-task performance.

**Connects To:** Phase 44 (we can combine models. How do we handle inputs longer than the training sequence length?)

---

## Phase 44: Long Context & Position Interpolation (COMPLETED)

**The Question:** "Your model was trained on 4K-token sequences, but users want to process entire books and codebases. Re-training on 128K sequences costs millions. How do you extend the context window without retraining from scratch?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Position Interpolation | Scaling position indices to fit the training range | Shrinking a 32-octave piano into 4 octaves the musician already knows |
| RoPE | Encoding position through rotation angles that preserve relative distances | Clock face where angles naturally wrap around |
| YaRN | Frequency-aware interpolation preserving local precision | Keeping foreground details sharp while compressing the sky in a panorama |
| NTK-Aware Scaling | Increasing RoPE base to stretch the frequency spectrum | Changing map projection to preserve local detail while expanding global coverage |

**Why It Is Needed:** GPT-4, Claude 3, and Gemini support 100K+ to 1M+ token contexts. Position interpolation is the key technique enabling this without retraining from scratch.

**What We Build:** A RoPE visualization showing how rotation angles scale with position. We compare basic interpolation, YaRN frequency-aware scaling, and NTK-aware base scaling. We verify that attention scores remain coherent after interpolation.

**Connects To:** Phase 45 (we can extend context and merge models. How do we run these massive models on consumer hardware?)

---

## Phase 45: Quantization & GGUF (COMPLETED)

**The Question:** "A 70B parameter model needs 140 GB in FP16. The best consumer GPU has 24 GB. How do you run these models at all?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Quantization | Reducing weight precision from FP16 to INT8/INT4 | Converting a RAW photo to JPEG: smaller, slightly less detail |
| GPTQ | Layer-wise quantization with Hessian-based error compensation | Team carrying a sculpture: each adjustment is compensated by the others |
| AWQ | Protecting the most important weights based on activation magnitudes | Orchestra keeping solo parts complex while simplifying background |
| GGUF | Universal binary format for quantized models | PDF for documents: one file works everywhere |

**Why It Is Needed:** Quantization is what makes large language models accessible. Llama-3-70B in INT4 fits on a single 24GB GPU. Without quantization, only data centers could run frontier models.

**What We Build:** A small neural network quantized to INT8 and INT4. We compare uniform quantization, per-channel scaling, GPTQ-style error compensation, and AWQ-style activation-aware protection. We visualize the memory vs. accuracy trade-off.

**Connects To:** Phase 46 (we can run models efficiently. But what are they actually doing inside?)

---

## Phase 46: Mechanistic Interpretability (COMPLETED)

**The Question:** "Neural networks work, but nobody knows exactly how. A GPT-4 has 1.8 trillion parameters. Which ones handle arithmetic? Which ones know Paris is in France? How do we open the black box?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Mechanistic Interpretability | Reverse-engineering neural networks to find specific computations | Building a repair manual for a car engine with billions of parts |
| Activation Patching | Causal intervention proving which activations cause behavior | Swapping one car battery at a time to find what makes the engine stall |
| Sparse Autoencoder | Decomposing dense activations into sparse, interpretable features | A 4096-page book decomposed into 5 relevant index cards |
| Superposition | Representing more features than neurons by overlapping directions | 88 piano keys producing millions of sounds through combination |

**Why It Is Needed:** Without interpretability, AI is a black box we cannot debug, trust, or safely deploy. Understanding internals is essential for alignment, safety, and model compression.

**What We Build:** A tiny model with 2 hidden neurons representing 4 patterns. We visualize activations, patch neurons causally, train a sparse autoencoder (93.8% sparsity), and demonstrate superposition.

**Connects To:** Phase 47 (we can understand models. How do we make them improve themselves?)

---

## Phase 47: Synthetic Data & Self-Improvement (COMPLETED)

**The Question:** "High-quality human data is finite and expensive. We have scraped the entire internet. How do we keep improving models when we have run out of human-generated training data?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Synthetic Data | AI-generated training examples | A chess grandmaster playing against themselves to discover new strategies |
| Rejection Sampling | Filtering generated outputs with automatic verifiers | A pearl farm keeping only gem-quality pearls |
| Constitutional AI | Models critiquing their own outputs against written principles | A company writing a code of ethics that employees self-apply |
| Iterative Self-Improvement | Training on a model's own best outputs in a loop | A writer revising their novel using only their best chapters as references |

**Why It Is Needed:** This breaks the data bottleneck. AlphaGo surpassed human Go players by training on its own games. Modern LLMs use synthetic reasoning chains, code solutions, and Q&A pairs to scale beyond human-labeled datasets.

**What We Build:** A model that generates synthetic arithmetic solutions, filters them with an exact verifier, and iteratively trains on the verified correct answers. We show that each self-improvement iteration produces higher-quality synthetic data.

**Connects To:** Phase 48 (models can improve themselves with infinite synthetic data. Can they also adapt at test time on a single new example?)

---

## Phase 48: Test-Time Training (COMPLETED)

**The Question:** "The world changes. Your model was trained on 2023 data and now faces 2024 inputs. How do you adapt to a single new example in real-time without labels, datasets, or retraining from scratch?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Meta-Learning | Learning an initialization that adapts to new tasks in few steps | Learning to ride bicycles so motorcycles take hours instead of months |
| Test-Time Training | Adapting model parameters during inference on the test input | A doctor reading case studies on the spot before diagnosing a rare disease |
| Unsupervised Adaptation | Adjusting to new distributions using only unlabeled data | A chef inferring Japanese cuisine principles by walking through markets |
| Online Learning | Continuously updating the model as new data arrives | A stock trader updating strategy after every trade |

**Why It Is Needed:** Real-world data shifts constantly. Models that can adapt at test time handle new domains, rare inputs, and distribution drift without expensive retraining. This is essential for robust deployment.

**What We Build:** A meta-learned linear classifier that adapts to new tasks with 5 examples. We demonstrate test-time training improving accuracy on shifted data from 60% to 70% without labels, and online learning adapting to a distribution shift in real-time.

**Connects To:** Phase 49 (we can adapt models at test time. But how do we train them efficiently in the first place?)

---

## Phase 49: Advanced Optimizers (COMPLETED)

**The Question:** "Vanilla SGD uses the same step size for every parameter and forgets past gradients. How do modern optimizers like Adam adapt per-parameter learning rates and use momentum to converge faster?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Adam | Adaptive per-parameter learning rates with momentum | A hiker with a GPS that personalizes stride length for every direction |
| AdamW | Decoupled weight decay that treats all parameters uniformly | Two budget envelopes: one for adaptive spending, one for flat wealth tax |
| Learning Rate Schedule | Changing LR over training for better convergence | A driver smoothly decelerating as they approach their destination |
| Warmup | Starting at zero LR to prevent early divergence | Warming up a car engine before accelerating |

**Why It Is Needed:** Adam and AdamW train virtually all modern deep learning models. Learning rate schedules and warmup are essential for stable, fast convergence. Without them, large models diverge or plateau.

**What We Build:** A Rosenbrock function optimization comparing SGD, Momentum, RMSprop, Adam, and AdamW. We visualize trajectories and loss curves. We also compare constant LR vs. cosine annealing vs. warmup+cosine.

**Connects To:** Phase 50 (we can optimize efficiently. How do we learn without any labels at all?)

---

## Phase 50: Self-Supervised Learning (COMPLETED)

**The Question:** "Labeled data is expensive and finite. The internet has billions of unlabeled images. How do you learn useful representations without any human-provided labels?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Self-Supervised Learning | Creating supervision signals from data structure itself | A child learning object permanence by predicting what happens next |
| Contrastive Learning | Pulling augmented views together, pushing different images apart | A police witness learning to identify the same person from different angles |
| Masked Autoencoding | Reconstructing hidden patches from visible context | A restorer reconstructing a damaged painting from surviving fragments |
| Pretext Task | An artificial task designed to teach real skills | Learning vocabulary by solving crossword puzzles |

**Why It Is Needed:** Self-supervised learning breaks the label bottleneck. BERT, CLIP, SimCLR, and MAE all use SSL to learn from unlabeled data. This is how modern models are pre-trained before fine-tuning.

**What We Build:** Contrastive learning on 2D point clusters, masked autoencoding on tiny images, and rotation prediction as a pretext task. We show the encoder learns useful features without labels.

**Connects To:** Phase 51 (we can learn without labels. But how do we measure if the model is actually good?)

---

## The Visual Dependency Graph

```
PHASE 0-4: FOUNDATION
  ├─ Linear Regression → Single-Layer NN → Gradients → GD → Multi-Layer NN
  │
PHASE 5-6: CLASSIFICATION
  ├─ Binary (Sigmoid) → Multi-Class (Softmax)
  │
PHASE 7-10: MAKING IT WORK
  ├─ Deep Networks → L2 Regularization → Dropout → Batch Normalization
  │
PHASE 11-12: SEEING (CNNs)
  ├─ Convolutions → Residual Networks
  │
PHASE 13-14: REMEMBERING (RNNs)
  ├─ Vanilla RNN → LSTM/GRU
  │
PHASE 15-16: MEANING & TRANSLATION
  ├─ Word Embeddings → Seq2Seq
  │
PHASE 17-18: THE BREAKTHROUGH
  ├─ Attention → Transformer
  │
PHASE 19-20: UNDERSTANDING & GENERATION
  ├─ BERT (Encoder) → GPT (Decoder)
  │
PHASE 21: BUILDING GPT
  ├─ Tiny GPT (character-level)
  │
PHASE 22-24: ALIGNMENT
  ├─ SFT → RLHF → DPO/GRPO
  │
PHASE 25-26: OPTIMIZATION & REASONING
  ├─ KV Cache/Flash Attention/Quantization → Test-Time Compute
  │
PHASE 27-28: AGENTS & MULTIMODAL
  ├─ Tool Use/ReAct → Vision/CLIP
  │
PHASE 29-31: CREATING DATA
  ├─ VAEs → GANs → Diffusion
  │
PHASE 32-50: THE FUTURE & SCALING
  ├─ Foundation Models, World Models
  ├─ Mixture of Experts (Sparse Activation)
  ├─ Mamba & State Space Models (Linear Time)
  ├─ LoRA & PEFT (Cheap Adaptation)
  ├─ Speculative Decoding (Fast Generation)
  ├─ RAG (Grounded Knowledge)
  ├─ Scaling Laws (Efficient Training)
  ├─ Knowledge Distillation (Tiny Deployment)
  ├─ Flow Matching & DiT (Fast Generation)
  ├─ VLM Instruction Tuning (Multimodal Conversation)
  ├─ Verifiable Rewards & GRPO (Self-Play Reasoning)
  ├─ Model Merging & Ensembles (Multi-Task Combination)
  ├─ Long Context & Position Interpolation (Context Extension)
  ├─ Quantization & GGUF (Consumer GPU Deployment)
  ├─ Mechanistic Interpretability (Understanding Internals)
  ├─ Synthetic Data & Self-Improvement (Breaking the Data Wall)
  ├─ Test-Time Training (Real-Time Adaptation)
  ├─ Advanced Optimizers (Efficient Training)
  └─ Self-Supervised Learning (Learning Without Labels)
```

---

## Stats

| Metric | Count |
|---|---|
| Total Phases | 51 (0-50) |
| Concepts Covered | 192+ |
| Code Projects | 47 (Phases 5-50, plus 0-4 done) |
| Research Documents | 4 deep-dive research files |
| Estimated Lines of Documentation | 28,500+ |
| Estimated Lines of Code | 12,100+ |

---

## The Promise

By the end of Phase 50, the student will:
- Understand EVERY major AI architecture from first principles
- Have built EVERY architecture from scratch in NumPy
- Know WHY each invention was necessary
- Be able to read any AI research paper and understand the "why"
- Be ready to specialize in any subfield of AI

**This is not a race to GPT. This is a complete education in artificial intelligence.**

---

*Ready for Phase 5?*
