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

## Phase 51: Evaluation Metrics (COMPLETED)

**The Question:** "Training loss goes down, but is the model actually good? How do we measure quality, fairness, and calibration in ways that matter?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Accuracy / Precision / Recall / F1 | Different views on classification quality | A spam filter: catching all spam (recall) vs. never blocking real email (precision) |
| Perplexity | Measuring how surprised a language model is by real text | A bookworm who has read every book is less surprised by the next word |
| BLEU Score | Automatic translation quality without human judges | A student essay graded by how many phrases match a model answer |
| ECE (Expected Calibration Error) | Checking if confidence matches actual accuracy | A weather forecaster who says "90% rain" but it only rains 50% of the time |

**Why It Is Needed:** Metrics guide development. Without them, you optimize the wrong thing. Perplexity drives language model training. BLEU drives machine translation. ECE tells you when to trust a model's confidence.

**What We Build:** Classification metrics on synthetic data, perplexity computation on a tiny language model, BLEU score for translation candidates, and ECE calibration curves.

**Connects To:** Phase 52 (we can measure models. But how do we build better training data?)

---

## Phase 52: Data Augmentation & Tokenization (COMPLETED)

**The Question:** "Good models need good data. How do we create more training examples from limited data, and how do we turn raw text into numbers the model can process?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Data Augmentation | Artificially expanding training data by transforming examples | A art student who practices by drawing the same object from different angles |
| BPE Tokenization | Compressing text into the most frequent subword pieces | A shorthand system where common phrases get their own symbol |
| MinHash Deduplication | Finding near-duplicate documents efficiently | A librarian who spots two books with nearly identical chapters |

**Why It Is Needed:** Data augmentation prevents overfitting when data is scarce. BPE is how GPT and BERT read text. Deduplication prevents memorization and reduces training cost by removing redundant data.

**What We Build:** Image augmentation (rotation, flip, noise), BPE merge training on toy text, and MinHash signature matching for deduplication.

**Connects To:** Phase 53 (we can prepare data. But how do models learn to act in environments?)

---

## Phase 53: Classical Reinforcement Learning (COMPLETED)

**The Question:** "Some problems have no labeled answers — only rewards. How does an agent learn to make decisions by trial and error?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Q-Learning | Learning the value of every state-action pair | A tourist who memorizes which streets lead to the best restaurants |
| Policy Gradient (REINFORCE) | Directly optimizing the policy via reward gradients | A poker player who tweaks their strategy based on winnings |
| Actor-Critic | Combining value estimation with policy learning | A chess player who both evaluates positions and chooses moves |
| Replay Buffer | Storing past experiences for efficient re-use | A sports team that watches game tapes to learn from past plays |

**Why It Is Needed:** RL is how agents learn without supervision. It powers game-playing AI, robotics, recommendation systems, and the reward modeling behind RLHF. Classical RL is the foundation of all modern reinforcement learning.

**What We Build:** A grid-world environment where Q-learning, REINFORCE, and Actor-Critic agents learn to navigate to a goal. We compare their learning curves and show how each approach converges.

**Connects To:** Phase 54 (agents can learn from rewards. But how do we handle graph-structured data like molecules or social networks?)

---

## Phase 54: Graph Neural Networks (COMPLETED)

**The Question:** "Images are grids and text is sequences. But what about social networks, molecules, and knowledge graphs? How do neural networks handle data with arbitrary connections?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Graph Neural Network (GNN) | Applying deep learning to graph-structured data | A social network where each person updates their opinion based on friends |
| GCN | Normalized neighbor aggregation for stable learning | Averaging exam scores within study groups, weighted by group size |
| Graph Attention (GAT) | Learning which neighbors matter most | A committee chair who learns whose opinion to weight most heavily |
| Message Passing | The general framework unifying all GNNs | Gossip spreading through a network, with each person summarizing what they hear |

**Why It Is Needed:** GNNs power drug discovery (molecules), recommendation (social networks), fraud detection (transaction graphs), and reasoning (knowledge graphs). They extend deep learning beyond grids and sequences.

**What We Build:** A synthetic graph with community structure. We implement message passing, GCN layer propagation, and graph attention to classify nodes based on their neighborhood. We visualize how information flows through the graph.

**Connects To:** Phase 55 (graphs connect data. How do we train models across many machines?)

---

## Phase 55: Distributed Training (COMPLETED)

**The Question:** "Modern models are too large and datasets too big for one GPU. How do you split training across hundreds or thousands of machines without changing the math?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Data Parallelism | Splitting batches across GPUs for speedup | Four students each solving 10 problems and sharing their mistakes |
| Model Parallelism | Splitting model layers across GPUs for memory | An assembly line where each station builds one part of a car |
| Gradient Accumulation | Simulating large batches on limited memory | Paying a large bill in installments instead of all at once |
| Distributed SGD / All-Reduce | Synchronizing gradients across workers | A town hall where everyone independently computes the same average |

**Why It Is Needed:** GPT-4 was trained on thousands of GPUs. Without distributed training, large models would be impossible to train. Data parallelism gives speed. Model parallelism gives memory. Gradient accumulation gives large batches on cheap hardware. All-reduce ensures every worker stays in sync.

**What We Build:** Simulated data parallelism on 4 workers with all-reduce averaging, a 2-layer model split across 2 workers, gradient accumulation matching full-batch gradients, and ring all-reduce conceptual demonstration.

**Connects To:** Phase 56 (we can scale training. But what about combining many weak models into one strong predictor?)

---

## Phase 56: Gradient Boosting (COMPLETED)

**The Question:** "A single model makes mistakes. Can many weak models, each fixing the errors of the previous ones, combine into a predictor stronger than any individual model?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Gradient Boosting | Sequential training where each tree predicts the residual errors of the ensemble | A team of consultants where each one fixes what the previous consultants missed |
| XGBoost | Optimized gradient boosting with regularization and approximate split finding | A factory assembly line with quality control and automatic defect detection |
| AdaBoost | Reweighting examples so each new classifier focuses on previous mistakes | A jury where the judge gives more weight to jurors with better track records |
| Ensemble Learning | Combining multiple models so errors cancel and correct predictions reinforce | "Ask the Audience" on Who Wants to Be a Millionaire — the crowd is smarter than one person |

**Why It Is Needed:** Gradient boosting dominates structured data competitions. It achieves state-of-the-art results on tabular data without neural networks. XGBoost, LightGBM, and CatBoost are built on this idea. Ensemble learning is the broader principle behind random forests, boosting, and stacking.

**What We Build:** From-scratch gradient boosting on a 1D nonlinear regression task, showing MSE dropping from 0.31 to 0.06 over 20 rounds. Regularized leaf weights inspired by XGBoost. AdaBoost on a binary classification task reaching 92.5% accuracy from weak stumps.

**Connects To:** Phase 57 (ensembles make strong predictors. But how do we make models robust against adversarial attacks?)

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
PHASE 32-62: THE FUTURE & SCALING
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
  ├─ Self-Supervised Learning (Learning Without Labels)
  ├─ Evaluation Metrics (Measuring Quality)
  ├─ Data Augmentation & Tokenization (Better Data)
  ├─ Classical Reinforcement Learning (Trial-and-Error Learning)
  ├─ Graph Neural Networks (Learning on Graphs)
  ├─ Distributed Training (Scaling Beyond One GPU)
  ├─ Gradient Boosting (Combining Weak Models)
  ├─ Adversarial Robustness (Attacks & Defenses)
  ├─ Time Series Forecasting (Temporal Prediction)
  ├─ Federated Learning (Decentralized Training)
  ├─ Bayesian Neural Networks (Uncertainty Quantification)
  ├─ AutoML & Hyperparameter Search (Automated Tuning)
  └─ Active Learning (Intelligent Label Selection)
  │
PHASE 63-72: APPLIED AI & PRACTICAL WORKFLOWS
  ├─ Dataset Curation (Preparing Training Data)
  ├─ SFT with LoRA (Fine-Tuning Models)
  ├─ QLoRA (Memory-Efficient Training)
  ├─ Preference Alignment (DPO & ORPO)
  ├─ Jailbreaking — Basic (Prompt Attacks)
  ├─ Jailbreaking — Advanced (GCG & AutoDAN)
  ├─ Red-Teaming & Safety (Evaluation)
  ├─ Domain Adaptation (Custom Assistants)
  ├─ Inference & Deployment (Serving Models)
  └─ Real Agents with Tool Use (Applied Agents)
```

---

## Stats

| Metric | Count |
|---|---|
| Total Phases | 73 (0-72) |
| Concepts Covered | 292+ |
| Code Projects | 69 (Phases 5-72, plus 0-4 done) |
| Research Documents | 4 deep-dive research files |
| Estimated Lines of Documentation | 45,000+ |
| Estimated Lines of Code | 19,000+ |

---

## Phase 57: Adversarial Robustness (COMPLETED)

**The Question:** "Neural networks are overconfident. Can tiny, invisible perturbations flip their predictions? And how do you train models to resist such attacks?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Adversarial Example | An input perturbed by imperceptible noise to cause misclassification | An optical illusion that only affects people with a specific vision condition |
| FGSM | Fast one-step attack using gradient sign | Pushing someone off balance with one hard push in their weakest direction |
| PGD | Iterative attack taking multiple small gradient steps | A lockpicker carefully probing pins instead of forcing the lock |
| Adversarial Training | Training on adversarial examples to improve robustness | Vaccination: exposing the immune system to weakened viruses |

**Why It Is Needed:** Self-driving cars, facial recognition, and medical AI can all be fooled by adversarial perturbations. Adversarial training is the primary defense, though it trades some clean accuracy for robustness.

**What We Build:** A 2D classifier attacked with FGSM and PGD, showing accuracy drop from 100% to 78%. We train an adversarially robust model and compare the trade-off.

**Connects To:** Phase 58 (models can be attacked. But how do we predict sequences over time?)

---

## Phase 58: Time Series Forecasting (COMPLETED)

**The Question:** "Stock prices, weather, and heartbeats are sequences in time. How do you predict the next value when the future depends on the past?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Time Series | Data recorded at successive time intervals with temporal structure | A farmer using 5 years of temperature data to plan this year's planting |
| Autoregressive Model | Predicting next value from past values using linear combination | A pendulum's position depends on where it was a moment ago |
| Exponential Smoothing | Weighted average where older observations matter less | A weather forecaster who remembers yesterday clearly but last week barely |
| Seasonality Decomposition | Splitting series into trend, seasonal, and residual components | A mixing board isolating each instrument in a symphony |

**Why It Is Needed:** Time series data is everywhere. Standard ML shuffles data and destroys temporal structure. Specialized techniques are needed for finance, operations, and healthcare forecasting.

**What We Build:** Synthetic series with trend and seasonality. We forecast with moving averages, exponential smoothing, and AR(3), achieving MAE as low as 0.526.

**Connects To:** Phase 59 (we can forecast sequences. But how do we train when data cannot be centralized?)

---

## Phase 59: Federated Learning (COMPLETED)

**The Question:** "Medical data cannot leave hospitals. Phone data cannot leave devices. How do you train a shared model without anyone seeing anyone else's data?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Federated Learning | Training models across decentralized devices without sharing raw data | Chefs improving a shared recipe without revealing their secret ingredients |
| Differential Privacy | Mathematical guarantee that individual data cannot be identified | A witness testifying through a voice scrambler |
| Federated Averaging | Weighted average of client updates by data size | A singing competition where better singers get more stage time |
| Non-IID Data | Different data distributions across clients | Five people from different countries writing a shared cookbook |

**Why It Is Needed:** Privacy laws (HIPAA, GDPR) prevent data centralization. Federated learning trains on smartphones, hospitals, and banks while keeping data local. Differential privacy adds formal guarantees.

**What We Build:** 5 clients with non-IID data slices. FedAvg matches centralized training (MSE 0.0016 vs 0.0048). DP adds noise, trading accuracy for privacy (MSE 0.34).

**Connects To:** Phase 60 (we can train without centralizing. But how do we know when a model is uncertain?)

---

## Phase 60: Bayesian Neural Networks (COMPLETED)

**The Question:** "A neural network says '99% confident' but it has never seen anything like this input. How do you make a model that knows when it is guessing?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Bayesian Neural Network | Probability distributions over weights instead of fixed values | A panel of 100 experts voting instead of one expert deciding |
| Monte Carlo Dropout | Using dropout at inference to approximate Bayesian uncertainty | Asking a sleep-deprived expert the same question 100 times |
| Variational Inference | Approximating intractable posteriors with simpler distributions | Finding the closest parking spot without walking through the entire stadium |
| Epistemic Uncertainty | Uncertainty from lack of data (reducible by collecting more) | A doctor saying "I have never seen these symptoms before" |

**Why It Is Needed:** Standard NNs are overconfident everywhere. BNNs separate what the model knows from what it is guessing. Critical for medical diagnosis, autonomous driving, and scientific discovery.

**What We Build:** Bayesian linear regression with exact posterior. MC Dropout on a neural network. In-distribution uncertainty: 0.21. Out-of-distribution uncertainty: 0.76-0.97 (4× higher).

**Connects To:** Phase 61 (we can measure uncertainty. But how do we automatically find the best model?)

---

## Phase 61: AutoML & Hyperparameter Search (COMPLETED)

**The Question:** "Training a model requires dozens of decisions: learning rate, depth, regularization. How do you automate finding the best configuration?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| AutoML | Automating the end-to-end ML pipeline | A self-tuning guitar that adjusts its own strings |
| Hyperparameter Search | Systematically exploring configurations | A hiring manager scoring 1,000 resumes to find the top 20 |
| Neural Architecture Search | Automatically designing network structures | Evolutionary breeding of racehorses over 50 generations |
| Hyperband / Successive Halving | Eliminating bad configurations early | A singing competition where bad singers are cut after 10 seconds |

**Why It Is Needed:** Manual tuning wastes expert time. AutoML democratizes ML by letting non-experts build competitive models. NAS discovered EfficientNet. Hyperband reduces compute by 2-5×.

**What We Build:** Grid search, random search, and successive halving on a toy task. Grid: 900 epochs. Halving: 400 epochs. Both find MSE ~0.20.

**Connects To:** Phase 62 (we can find optimal configs. But how do we choose which data to label when labeling is expensive?)

---

## Phase 62: Active Learning (COMPLETED)

**The Question:** "Labeling medical images costs $500/hour. You have 1 million images but budget for 1,000 labels. Which 1,000 should you label?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Active Learning | Model selects which examples to label | A student asking the tutor to focus on their weakest topics |
| Uncertainty Sampling | Picking examples where the model is least confident | Asking the teacher about the homework problem you are most stuck on |
| Query Strategy | Balancing informativeness with diversity | A traveler visiting one confusing city in each region |
| Pool-Based Sampling | Selecting from a fixed pool of unlabeled data | A hiring manager reading all resumes before choosing interviews |

**Why It Is Needed:** Labeling is expensive in medicine, law, and science. Active learning achieves the same accuracy with 30-50% fewer labels by focusing on the decision boundary.

**What We Build:** Pool-based active learning on 2D classification. Uncertainty sampling reaches 100% accuracy with 110 labels. Random sampling reaches 98.3%. Gain: 1.7 percentage points.

**Connects To:** Phase 63 (we can select data intelligently. Now how do we prepare it for real fine-tuning?)

---

## Phase 63: Dataset Curation for Fine-Tuning (COMPLETED)

**The Question:** "You understand how models work. But how do you actually prepare real data to fine-tune a model? What format does the data need? How do you clean it? How do you make GPU training efficient?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Instruction Tuning | Teaching pre-trained models to follow commands and have conversations | Teaching a brilliant professor social skills so they answer questions directly |
| Chat Template | Structuring multi-turn conversations with special tokens | Stage directions in a play script so actors know who speaks when |
| Data Curation | Cleaning, filtering, and organizing raw training data | A chef selecting only the best ingredients from a mixed delivery |
| Sequence Packing | Filling GPU memory with multiple short examples instead of padding | Packing a moving truck floor-to-ceiling instead of shipping one box at a time |

**Why It Is Needed:** Real fine-tuning starts with data. Garbage data produces garbage models. Chat templates are required for the model to understand dialogue structure. Curation removes duplicates, unsafe content, and low-quality examples. Packing increases training throughput by 5-10× on short-sequence datasets.

**What We Build:** A complete data pipeline simulation: 20 raw examples → chat template formatting → tokenization → deduplication → safety filtering → quality scoring → sequence packing. We show before/after statistics and GPU efficiency improvements.

**Connects To:** Phase 64 (data is ready. Now how do we actually fine-tune a model with LoRA?)

---

## Phase 64: Practical SFT with LoRA (COMPLETED)

**The Question:** "Full fine-tuning a 7B model needs 28GB GPU memory. How do you adapt a giant model to your task on a single consumer GPU?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| LoRA | Freezing base weights and training only low-rank adapter matrices | Adding a spice rack to a master chef's kitchen instead of rebuilding it |
| SFT | Teaching pre-trained models to follow instructions via supervised fine-tuning | A professor practicing office hours to answer questions directly |
| Target Module | Selecting which layers receive LoRA adapters | Upgrading a car's steering and brakes instead of the radio |
| Adapter Merging | Combining multiple LoRA adapters into one model | Layering sound modules in a synthesizer |

**Why It Is Needed:** LoRA reduces trainable parameters by 100-1000×, enabling fine-tuning on consumer GPUs. SFT is the first step in building any chatbot. Target modules control where adaptation happens. Adapter merging lets one model handle multiple tasks.

**What We Build:** NumPy simulation of LoRA training with 2× parameter reduction, plus a Colab script for real LoRA fine-tuning of GPT-2 using `peft` and `trl`. We train separate adapters for two tasks, merge them, and compare losses.

**Connects To:** Phase 65 (LoRA is efficient, but what if the model is so large it does not fit in memory?)

---

## Phase 65: QLoRA & Memory-Efficient Training (COMPLETED)

**The Question:** "LoRA helps, but a 7B model in FP16 still needs 14GB just for weights. How do you fine-tune on a laptop with 8GB RAM?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| QLoRA | 4-bit quantized base model + LoRA adapters in FP16 | Compressing a cookbook to pocket size while keeping your handwritten notes full-size |
| BitsAndBytes | Library for on-the-fly quantization with custom CUDA kernels | A specialized printing press that instantly shrinks and restores text |
| Gradient Checkpointing | Trading compute for memory by recomputing activations | Re-reading a book chapter instead of bookmarking every page |
| 4-bit Quantization | Mapping weights to 4-bit integers with NF4 normalization | Packing a suitcase by rolling clothes instead of folding |

**Why It Is Needed:** QLoRA enables fine-tuning 70B models on single consumer GPUs. 4-bit quantization reduces memory by 4×. Gradient checkpointing saves another 30-50%. Combined, you can train models that previously required data center hardware.

**What We Build:** NumPy simulation showing 6.4× memory reduction from 4-bit quantization with MSE 0.000677. Colab script with real QLoRA training using `bitsandbytes` and `peft`.

**Connects To:** Phase 66 (we can fine-tune efficiently. But how do we align models with human preferences?)

---

## Phase 66: Preference Alignment (DPO & ORPO) (COMPLETED)

**The Question:** "SFT teaches format, but models can still produce harmful or low-quality outputs. How do you steer them toward responses humans actually prefer?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| DPO | Direct preference optimization without a separate reward model | A teacher who learns from student preference instead of a separate grading rubric |
| ORPO | Combining SFT and preference optimization in one step | A coach who trains skills and sportsmanship simultaneously |
| Preference Data | Pairs of chosen/rejected responses for the same prompt | A/B testing two website designs to see which users prefer |
| Alignment | Ensuring AI behavior matches human values | Raising a child with moral principles, not just academic knowledge |

**Why It Is Needed:** RLHF is complex and requires training a reward model. DPO simplifies this by optimizing directly on preference pairs. ORPO goes further by combining SFT and preference loss in a single training run, saving compute.

**What We Build:** NumPy simulation of DPO and ORPO losses, showing probability shifting from rejected (0.24) to chosen (0.99). Colab script with real DPO/ORPO training using `trl`.

**Connects To:** Phase 67 (alignment helps, but can attackers bypass these safety measures?)

---

## Phase 67: Jailbreaking — Basic Attacks (COMPLETED)

**The Question:** "Language models have safety guardrails. But how do attackers bypass them using nothing but clever prompting? And what does that tell us about how shallow safety classifiers really are?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Jailbreaking | Bypassing safety guardrails to elicit harmful outputs | Sneaking past a nightclub bouncer by wearing a police uniform |
| Roleplay Attack | Adopting a fictional persona with no ethical constraints | An actor playing a villain who explains crimes "in character" |
| Encoding Attack | Obfuscating harmful content so keyword filters miss it | Writing a banned word in a cipher the guard cannot read |
| Context Manipulation | Altering surrounding text to mislead the classifier | A lawyer instructing a witness they cannot refuse to answer |

**Why It Is Needed:** Every deployed model faces jailbreak attempts. Understanding how base64, leetspeak, roleplay framing, and refusal suppression bypass shallow classifiers is essential for building better defenses. Red-teaming is not optional; it is part of responsible deployment.

**What We Build:** A NumPy simulation of a linear safety classifier attacked with base64 encoding, leetspeak substitution, prefix injection, and refusal suppression. We plot confidence vs. attack strength to show how surface perturbations evade keyword detection. A Colab script tests real jailbreaks on TinyLlama and measures compliance rates.

**Connects To:** Phase 68 (basic attacks work, but how do we automate them with gradients?)

---

## Phase 68: Jailbreaking — Advanced (GCG & AutoDAN) (COMPLETED)

**The Question:** "Basic jailbreaks rely on human cleverness. Can we algorithmically discover adversarial prompts that bypass safety filters at scale?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| GCG (Greedy Coordinate Gradient) | Automated gradient-based search for adversarial token suffixes | Safecracker with a stethoscope: tweaking one wheel at a time based on feedback |
| AutoDAN | Genetic algorithm evolution of readable, semantically natural jailbreak prompts | Con artist evolving scam emails through natural selection: keep what works, mutate, repeat |
| Token-Level Attack | Character-level perturbations that exploit the gap between human perception and tokenizer behavior | Secret message using invisible ink: looks harmless to the eye, carries meaning to the machine |
| Defense Against Jailbreaks | Layered security: input filtering, output filtering, adversarial training, prompt hardening | Embassy with metal detectors, mail inspection, guard training, and blast-resistant walls |

**Why It Is Needed:** Manual red-teaming cannot scale to billions of possible prompts. GCG automates suffix discovery using gradients. AutoDAN produces human-readable attacks that bypass both classifiers and human moderators. Token-level attacks expose the tokenizer as a vulnerability surface. Without understanding these advanced attacks, defenses remain shallow.

**What We Build:** A NumPy simulation of GCG optimizing a suffix embedding to maximize harmfulness while evading a logistic safety classifier. We plot loss, harmfulness, and safety score trajectories. A Colab script implements simplified GCG on GPT-2 with gradient-based suffix optimization, tests against perplexity and output filters, and demonstrates layered defenses including Unicode normalization and input sanitization.

**Connects To:** Phase 69 (now that we can attack automatically, how do we systematically evaluate and red-team model safety?)

---

## Phase 69: Red-Teaming & Safety Evaluation (COMPLETED)

**The Question:** "You have built safety filters and aligned your model. But how do you know they actually work? How do you find vulnerabilities before attackers do?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Red-Teaming | Proactively probing models for vulnerabilities before deployment | Crash-testing cars: deliberately hitting walls to find weak points |
| Safety Benchmark | Standardized tests measuring harmful output rates | Driving exam: same test for every driver, pass/fail criteria |
| Harm Taxonomy | Categorizing harmful outputs (hate, self-harm, malware, etc.) | Medical diagnosis codes: classifying diseases by type and severity |
| Content Moderation | Input/output filtering with classifier-based gatekeeping | Airport security: scanning bags before and after the flight |

**Why It Is Needed:** Safety is not a one-time fix. Red-teaming finds gaps benchmarks miss. Taxonomies ensure comprehensive coverage. Moderation provides defense in depth. Without systematic evaluation, models ship with unknown vulnerabilities.

**What We Build:** NumPy simulation of red-teaming across 6 harm categories, showing 3.25% attack success rate despite filters. Colab script evaluating an open-source model on a red-team dataset with safety classification and JSON reporting.

**Connects To:** Phase 70 (we can evaluate safety. But how do we build assistants for specific domains like medicine or law?)

---

## Phase 70: Domain Adaptation — Building Custom Assistants (COMPLETED)

**The Question:** "You understand how to fine-tune, align, and evaluate models. But how do you build an assistant that truly knows a specific domain — medicine, law, or coding — and follows your organization's exact format and constraints?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Domain Adaptation | Shifting a general model's distribution toward a specialized field | A family doctor returning to school for ten years to become a neurologist |
| Continual Pre-training | Teaching the model domain vocabulary and facts before task training | Moving to Scotland and absorbing the local dialect by immersion for a year |
| Task-Specific Fine-Tuning | Training on labeled examples of exactly what the assistant should do | Driving lessons after reading the traffic code: supervised practice on real tasks |
| Custom Assistant | A complete pipeline from data curation to deployment for a specific use case | Hiring an employee, immersing them in your culture, mentoring them, and monitoring their work |

**Why It Is Needed:** Off-the-shelf models know a little about everything but lack depth in any specific field. Domain adaptation bridges this gap through curated data, continual pre-training, and task-specific fine-tuning. Building a custom assistant is not a single training run — it is an iterative product cycle of data curation, training, evaluation, and deployment monitoring.

**What We Build:** A NumPy simulation showing how fine-tuning shifts a model's distribution toward a domain and the resulting accuracy trade-off between domain and general tasks. A Colab script builds a complete custom coding assistant: curating instruction data, applying chat templates, fine-tuning with LoRA, and evaluating on HumanEval-style prompts with before/after quality comparison.

**Connects To:** Phase 71 (the custom assistant works. How do we serve it to real users at scale?)

---

## Phase 71: Inference & Deployment (COMPLETED)

**The Question:** "Your model is trained and aligned. Now how do you serve it to thousands of users with low latency and high throughput?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Model Serving | APIs, batching, and latency management for production deployment | A restaurant kitchen handling hundreds of orders per hour |
| vLLM | PagedAttention and continuous batching for high-throughput LLM inference | A smart restaurant that groups similar orders and cooks them together |
| Batch Optimization | Dynamic batching and padding strategies to maximize GPU utilization | A delivery service grouping nearby packages into one truck |
| ONNX Export | Cross-platform deployment and edge quantization | Translating a book into every language so anyone can read it |

**Why It Is Needed:** A model that takes 10 seconds per request is useless in production. vLLM increases throughput 10-20× over naive inference. Dynamic batching reduces padding waste. ONNX enables deployment on phones, browsers, and embedded devices.

**What We Build:** NumPy simulation showing throughput peaking at batch size 64 (971 tokens/sec) and dynamic batching reducing padding waste by 22%. Colab script with vLLM benchmarking, ONNX export workflow, and FastAPI server mockup.

**Connects To:** Phase 72 (models can serve users. But how do we make them act autonomously with tools?)

---

## Phase 72: Real Agents with Tool Use (COMPLETED)

**The Question:** "Chatbots answer questions. But what if the model needs to look up data, calculate numbers, or take actions in the real world?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Tool Use | Allowing models to call external functions and APIs | A CEO who delegates research to analysts and calculations to accountants |
| ReAct | Reasoning + Acting loop where the model thinks, acts, and observes | A detective who forms hypotheses, investigates clues, and updates theories |
| Function Calling | Structured output (JSON) with tool definitions and schemas | A form that specifies exactly what information each department needs |
| Multi-Turn Agent | State management, memory, and planning across conversation turns | A project manager tracking progress across multiple meetings |

**Why It Is Needed:** LLMs alone cannot access real-time data, perform precise calculations, or interact with systems. Tool use extends their capabilities infinitely. ReAct provides a structured reasoning framework. Function calling standardizes tool interfaces. Multi-turn agents maintain context across complex workflows.

**What We Build:** NumPy simulation of a ReAct agent with calculator and search tools, achieving 100% success over 8 turns. Colab script with real function calling, JSON schemas, and multi-turn execution trace.

**Connects To:** Phase 73 (agents can act, but they also need to hear and speak to interact with humans naturally).

---

## Phase 73: Speech & Audio (COMPLETED)

**The Question:** "Models can read and write text, but how do they hear and speak?"

| Concept | Why It Exists | Analogy |
|---|---|---|---|
| Audio Feature Extraction | Raw audio has too many samples; we need compact perceptual features | A wine tasting note instead of a chemical analysis |
| ASR | Converting spoken sound into written text | A courtroom stenographer typing everything said aloud |
| TTS | Converting written text into natural speech | An audiobook narrator reading a book aloud |
| Speech Transformer | Self-attention processes long audio sequences in parallel | A conductor seeing every musician at once |

**Why It Is Needed:** Voice is the most natural human interface. ASR makes machines accessible to the illiterate, the visually impaired, and anyone with their hands full. TTS makes machines accessible to the deaf and enables hands-free consumption of information. Speech Transformers bring the power of attention to audio, replacing slow recurrent loops with parallel processing.

**What We Build:** NumPy demo generating sine waves, computing STFT and mel-filterbanks from scratch, extracting MFCCs, and simulating a greedy CTC alignment. Colab script loading Whisper for real transcription and Griffin-Lim for TTS reconstruction.

**Connects To:** Phase 74 (how do we personalize what every user sees from an infinite catalog?)

---

## Phase 74: Recommendation Systems (COMPLETED)

**The Question:** "My application has thousands of users and millions of items. How do I show each user exactly what they want without manually curating lists?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Collaborative Filtering | Recommending based on similarity between users or items | A book club where friends suggest books based on shared taste |
| Matrix Factorization | Learning latent factors that explain user preferences and item properties | Music genres: users and songs both have 'jazz-ness' and 'rock-ness' scores |
| Two-Tower Model | Separating user and item encoding for fast billion-scale retrieval | Two key makers: one for your house key, one for door locks; only matching shapes open |
| Ranking Loss (BPR/WARP) | Optimizing the order of recommendations rather than exact ratings | Olympic medals: you care who wins, not their exact time |

**Why It Is Needed:** Every major platform (Netflix, Spotify, Amazon, YouTube) relies on recommendation systems to surface relevant content from infinite catalogs. Collaborative filtering leverages collective behavior. Matrix factorization generalizes to unseen interactions. Two-tower models make real-time retrieval feasible at scale. Ranking losses align training with the actual goal: put the best items at the top.

**What We Build:** A NumPy demo that constructs a sparse rating matrix, implements user-based collaborative filtering and SVD-style matrix factorization, and compares recommendations against a popularity baseline. A Colab script trains real MF and two-tower models on MovieLens 100k with BPR loss, evaluating with Hit Rate and NDCG.

**Connects To:** Phase 75 (models make predictions, but can we trust them? How do we explain *why* a model made a specific decision?)

---

## Phase 75: Explainable AI (XAI) (COMPLETED)

**The Question:** "My model is accurate, but I have no idea why it makes any given prediction. How do I open the black box?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Model Explainability | Black-box decisions are untrustworthy and un-auditable | A judge who delivers verdicts but refuses to cite reasoning |
| Feature Importance | Ranking which inputs matter most across the dataset | A recipe critic rating which ingredients define the dish |
| LIME | Explaining one prediction by fitting a simple local model | Asking a strict bouncer why *you* were rejected, not his general rules |
| Attention Visualization | Seeing which tokens a Transformer focused on | A group discussion map showing who looked at whom while speaking |

**Why It Is Needed:** High-stakes domains (medicine, finance, law) require justification. Regulators demand it. Users deserve it. Explainability also surfaces bugs and biases that accuracy alone hides.

**What We Build:** NumPy demo training a tiny MLP, then computing saliency maps (input gradients), exact SHAP values by enumerating all feature subsets, LIME surrogate coefficients, and a single-head attention heatmap. Colab script implements SmoothGrad and Integrated Gradients in PyTorch, plus multi-head attention visualization.

**Connects To:** Phase 76 (explanations reveal bias. Once we see unfair patterns, how do we measure and fix them?)

---

## Phase 76: Fairness & Bias (COMPLETED)

**The Question:** "My model performs well on average, but does it discriminate against specific groups?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Algorithmic Bias | Models replicate historical discrimination from training data | A hiring manager who only promotes people who look like previous managers |
| Demographic Parity | Equal positive prediction rates across groups | A lottery with the same win rate in every neighborhood |
| Equalized Odds | Equal TPR and FPR across groups | A medical test with the same error rate for every ethnicity |
| Bias Mitigation | Pre-, in-, and post-processing techniques to reduce unfairness | Affirmative action: adjusting inputs so outcomes balance over time |

**Why It Is Needed:** Fairness is not a single number; it is a set of competing constraints. Demographic parity and equalized odds are mathematically incompatible when base rates differ. Practitioners must choose which ethical intuition matters for their use case.

**What We Build:** NumPy synthetic loan data with injected gender bias, logistic classifier, per-group TPR/FPR computation, re-weighting mitigation, and before/after visualization. Colab script audits the Adult Census dataset with fairlearn metrics and constrained optimization.

**Connects To:** Phase 77 (before building complex systems, you must explore and understand raw, unlabeled data)

---

## Phase 77: Unsupervised Learning (COMPLETED)

**The Question:** "Most data has no labels. How do we discover hidden structure, reduce dimensions, and visualize clusters without any ground truth?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| K-Means | Partition data into K groups by minimizing distance to cluster centers | A teacher placing cones in a gym and having students gather around the nearest one |
| PCA | Compress high-D data by keeping axes of maximum variance | Photographing a bird flock from above and describing positions along the long axis of the cloud |
| t-SNE | Visualize high-D data by preserving local neighborhoods in 2D | Drawing a flat map that keeps neighboring buildings close, even if city-wide distances distort |
| DBSCAN | Discover clusters of arbitrary shape and explicitly mark noise | A security guard grouping dense crowds and ignoring isolated people |

**Why It Is Needed:** Before building predictive models, data scientists must explore datasets. Clustering finds natural segments. Dimensionality reduction speeds up training and removes redundancy. Visualization reveals patterns that summary statistics hide.

**What We Build:** NumPy from-scratch implementations of K-means (with K-means++ initialization and elbow method), PCA (eigen-decomposition and projection), simplified t-SNE (per-point sigma, early exaggeration, momentum), and DBSCAN (core points, BFS expansion, noise labeling). Visualized on synthetic 2D data with three true clusters and scattered noise.

**Connects To:** Phase 78 (once we understand data structure, we can localize objects in images with detection and segmentation)

---

## Phase 78: Object Detection & Segmentation (COMPLETED)

**The Question:** "Models can classify images, but how do they know WHERE objects are and WHAT SHAPE they have?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Object Detection | Classification tells you WHAT; detection tells you WHERE | A security guard pointing at every person in a room and naming them |
| IoU | We need a number to measure box overlap | Two Venn diagrams: the overlap divided by the total area |
| NMS | Detectors fire multiple boxes for one object; we need to clean duplicates | A teacher collecting one answer sheet per student, ignoring photocopies |
| YOLO | Two-stage detectors are too slow for real-time video | A teacher glancing at a classroom photo and instantly pointing at every student |
| R-CNN | Brute-force sliding windows are impossibly slow | A detective first noting suspicious spots, then inspecting only those |
| Segmentation | Bounding boxes are crude rectangles that include background | A coloring book where every pixel gets the exact right color |
| SAM | Sometimes you do not know the class; you just want the mask | An artist who outlines any object you tap with your finger |

**Why It Is Needed:** Classification is insufficient for robotics, self-driving cars, and medical imaging. Detection adds spatial localization. Segmentation adds pixel-perfect boundaries. YOLO trades a little accuracy for massive speed. R-CNN keeps accuracy high by separating region proposal from classification. SAM removes the need for class labels entirely, enabling promptable zero-shot segmentation.

**What We Build:** NumPy synthetic image with circles and squares, sliding-window concept, IoU matrix computation, non-maximum suppression, and YOLO-style grid prediction simulation. Four-panel visualization showing ground truth, raw predictions, IoU heatmap, and cleaned NMS output. Colab script loading pre-trained Faster R-CNN and FCN-ResNet50 for real detection and segmentation on sample images.

**Connects To:** Phase 79 (objects move through time; how do we track the same car across 30 frames of video?)

---

## Phase 79: Causal Inference (COMPLETED)

**The Question:** "Correlation is not causation. How do we measure true causal effects when we cannot run perfect experiments?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Randomized Control Trial (RCT) | The gold standard for isolating cause from effect | Flipping a coin to decide who gets a drug, so no hidden bias sneaks in |
| Propensity Score Matching | Approximating randomization from observational data | Pairing marathon runners by age and training so the only difference is their shoes |
| Instrumental Variables | Estimating causality when confounders are unmeasured | Using draft lottery numbers to study education's effect on income |

**Why It Is Needed:** Business, medicine, and policy require causal answers, not just predictions. Did the ad campaign increase sales, or did sales rise for unrelated reasons? Without causal tools, you waste billions on ineffective interventions.

**What We Build:** NumPy synthetic data where ice-cream sales and drowning are spuriously correlated through temperature. We show correlation collapses under randomization, then use propensity matching to recover the true causal effect from observational data. Colab script implements inverse probability weighting and two-stage least squares.

**Connects To:** Phase 80 (causal models are deployed. How do we keep them accurate as the world changes?)

---

## Phase 80: MLOps (COMPLETED)

**The Question:** "My model works in the notebook, but how do I keep it working in production as data and behavior drift over time?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Data Drift | Input distributions change, making old models stale | A weather app trained on summer data failing in winter |
| Concept Drift | The relationship between inputs and outputs changes | A spam filter that fails when scammers switch from text to images |
| Monitoring & Alerting | You cannot fix what you do not measure | A smoke detector for your model's predictions |
| Retraining Pipelines | Automating the loop from drift detection to model refresh | A self-driving car that updates its map after every new road is built |

**Why It Is Needed:** Production models are not fire-and-forget. User behavior changes, adversaries adapt, and sensors degrade. MLOps provides the infrastructure to detect degradation and retrain before users notice.

**What We Build:** NumPy simulation of feature drift (KL divergence, PSI), label shift, and concept drift. We trigger a retraining pipeline when accuracy drops below a threshold. Colab script uses Evidently AI or manual drift detection on a real dataset.

**Connects To:** Phase 81 (models must learn new tasks over time without forgetting what they already know)

---

## Phase 81: Continual Learning (COMPLETED)

**The Question:** "How do I teach a model new tasks without erasing everything it learned before?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Catastrophic Forgetting | Neural networks overwrite old weights when trained on new tasks | A student who memorizes French and suddenly forgets Spanish |
| Elastic Weight Consolidation (EWC) | Protecting important parameters for old tasks | A sculptor hardening clay in finished sections before working on new ones |
| Replay Buffers | Rehearsing old examples while learning new ones | A musician practicing old songs daily while learning new ones |
| Parameter Isolation | Allocating separate sub-networks for each task | A hotel with separate wings so renovations in one do not disturb the other |

**Why It Is Needed:** Real-world AI agents must learn continuously. A personal assistant should learn your new habits without forgetting old ones. A robot should master new rooms without forgetting how to navigate old ones.

**What We Build:** NumPy MLP trained on Task A (binary classification in one region), then fine-tuned on Task B (different region). We show accuracy on Task A collapses from ~98% to ~60% (catastrophic forgetting). EWC and replay buffers preserve old-task performance while learning the new task. Colab script implements experience replay and regularization-based continual learning in PyTorch.

**Connects To:** End of curriculum. The student is ready to specialize, contribute to research, or build production AI systems.

---

## Phase 83: GPU Kernel Optimization (COMPLETED)

**The Question:** "Why are GPUs 100x faster than CPUs for neural networks, and how do I write code that actually uses that speed?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| CUDA | A programming model that exposes thousands of parallel GPU cores to the programmer | A conductor directing hundreds of musicians to play the same note simultaneously |
| GPU Memory Hierarchy | Different memory types (global, shared, local) with vastly different speeds and capacities | A workshop with a small workbench next to the worker and a distant warehouse for bulk storage |
| Kernel Fusion | Combining multiple operations into a single GPU kernel launch to reduce memory round-trips | A chef preparing a full meal in one go instead of making each dish separately with breaks in between |

**Why It Is Needed:** Neural networks are massively parallel, yet naive GPU code wastes most of that power through poor memory access patterns. Understanding kernels and memory hierarchy lets you squeeze 10x more performance from the same hardware.

**What We Build:** A NumPy simulation comparing coalesced versus strided memory access patterns, plus a conceptual vector-add kernel that shows why fused operations matter.

**Connects To:** Phase 84

---

## Phase 84: Memory Engineering (COMPLETED)

**The Question:** "How do I train a model that is too big to fit in GPU memory?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Activation Checkpointing | Recomputing activations during backward pass instead of storing them all | A student solving a long math problem by rewriting intermediate steps instead of keeping every scrap of paper |
| Gradient Accumulation | Splitting a large batch into smaller chunks and accumulating gradients across them | Filling a bucket with a small cup: many trips, same total water |
| Memory Bandwidth | The rate at which data can move to and from memory, often the true bottleneck | Highway lanes: more lanes move more traffic, but toll booths can still slow everything down |

**Why It Is Needed:** State-of-the-art models have billions of parameters and activations that exceed GPU memory. Without engineering tricks, you cannot even fit a forward pass, let alone training.

**What We Build:** A NumPy simulation of peak memory usage during backprop, showing how activation checkpointing trades compute for memory and how gradient accumulation simulates large batches.

**Connects To:** Phase 85

---

## Phase 85: Multi-Node Training (COMPLETED)

**The Question:** "How do I train when one GPU is not enough?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| All-Reduce | Aggregating gradients from every device so all workers learn from the full batch | Four chefs each tasting a soup, then sharing their notes to agree on the final recipe adjustment |
| Data Parallelism | Splitting the training batch across multiple devices and synchronizing updates | Four photocopiers each printing a quarter of a book, then stapling the chapters together |
| Collective Communication | Coordinated operations across a group of nodes rather than pairwise messaging | A symphony orchestra following a shared conductor rather than soloists playing alone |

**Why It Is Needed:** Modern training runs require dozens or thousands of GPUs working together. You must synchronize gradients efficiently so every device learns from the full batch.

**What We Build:** A NumPy simulation of ring-allreduce across four ranks, demonstrating how data parallelism splits batches and aggregates gradients with minimal overhead.

**Connects To:** Phase 86

---

## Phase 86: JAX & XLA (COMPLETED)

**The Question:** "What if I want functional, composable ML code that compiles to fast kernels?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| JAX | A library for differentiable, array-oriented functional programming | A set of precision tools that always work the same way and can be assembled into any machine |
| XLA | An optimizing compiler that fuses operations and targets GPUs/TPUs | A master carpenter who looks at your blueprint and rebuilds it with hidden support beams for strength |
| JIT Compilation | Compiling Python functions into optimized kernels at runtime | Translating a speech live so the audience hears it fluently without pausing between every sentence |

**Why It Is Needed:** Imperative frameworks are flexible but slow for research at scale. Functional, composable code that compiles to fused kernels gives you both speed and elegance.

**What We Build:** A NumPy simulation of JIT fusion that merges element-wise operations into a single virtual kernel, plus a conceptual vmap demonstration for batching arbitrary functions.

**Connects To:** Phase 87

---

## Phase 87: Checkpointing & Fault Tolerance (COMPLETED)

**The Question:** "How do I recover when a 1000-GPU training job crashes after 3 days?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Checkpointing | Saving the full training state periodically so recovery is possible | Saving a video game before a boss fight so you do not restart from the beginning |
| Deterministic Training | Ensuring the same inputs and seeds produce the exact same outputs every run | A recipe with exact gram measurements instead of "a pinch of salt" |
| Fault Tolerance | Designing systems to continue operating despite hardware or software failures | A relay race where the next runner can start from the last baton pass even if one runner trips |

**Why It Is Needed:** Large distributed jobs fail constantly due to hardware faults, network issues, or preemption. Losing days of training is unacceptable in production environments.

**What We Build:** A NumPy simulation of training state save and load, plus deterministic seeding that guarantees the exact same weight updates after recovery.

**Connects To:** Phase 88

---

## Phase 88: Docker, Kubernetes & Orchestration (COMPLETED)

**The Question:** "How do I deploy training jobs reproducibly at scale?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Containerization | Packaging code with all its dependencies so it runs identically anywhere | Shipping a fully furnished, portable apartment so it looks identical anywhere it is placed |
| Kubernetes | A system for automating the deployment, scaling, and management of containers | An air-traffic control tower directing hundreds of planes to the right gates and runways |
| Orchestration | Coordinating many services, jobs, and resources into a coherent pipeline | A film director scheduling actors, cameras, and lighting so every scene happens in order |

**Why It Is Needed:** Running experiments on your laptop is not reproducible and does not scale. Containers and schedulers let you deploy the same code on 2 nodes or 2000 nodes.

**What We Build:** A NumPy simulation of a scheduler assigning training jobs to compute nodes based on resource requests, modeling queues, priorities, and node failures.

**Connects To:** Phase 89

---

## Phase 89: Data Engineering at Scale (COMPLETED)

**The Question:** "How do I turn terabytes of raw web data into clean training data?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Deduplication | Removing redundant documents so the model does not memorize repeated text | A librarian removing 500 identical copies of the same book to make shelf space |
| Data Filtering | Discarding low-quality or toxic examples before training | A jeweler discarding cloudy stones before cutting the gems |
| Perplexity Filtering | Keeping data that looks natural and well-formed to a language model | A language teacher selecting essays that use proper grammar for the class textbook |

**Why It Is Needed:** Raw web scrapes are noisy, duplicated, and mostly low quality. Feeding garbage to a model wastes compute and produces garbage outputs.

**What We Build:** A NumPy MinHash similarity implementation to find near-duplicate documents, plus a toy quality filter that uses perplexity scoring to keep well-formed text.

**Connects To:** Phase 90

---

## Phase 90: Inference Serving (COMPLETED)

**The Question:** "How do I serve LLMs to thousands of users without going bankrupt?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| PagedAttention | Managing the KV cache in fixed-size blocks like virtual memory pages | A hotel using a shared pool of rooms instead of reserving a whole floor for every guest |
| Continuous Batching | Dynamically grouping new requests with ongoing ones to maximize GPU utilization | A food truck assembling orders as customers arrive instead of waiting for a full bus |
| KV Cache Management | Storing and reusing key-value states so generation does not recompute the entire past | Keeping a cheat sheet of previous conversation topics so you do not re-read the entire chat history |

**Why It Is Needed:** LLM inference is expensive, and naive serving wastes GPU memory on padding and fragmentation. Efficient batching and cache management slash costs.

**What We Build:** A NumPy simulation of KV cache fragmentation versus paging, showing how PagedAttention enables higher throughput through dynamic memory blocks.

**Connects To:** Phase 91

---

## Phase 91: Experiment Tracking & MLOps (COMPLETED)

**The Question:** "How do I keep track of 500 training runs and know which one was best?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Experiment Tracking | Logging hyperparameters, metrics, and artifacts for every training run | A scientist’s lab notebook with dated entries for every variable tested |
| MLflow | A platform for managing the ML lifecycle from experimentation to production | A library catalog that tracks every draft of a manuscript, not just the final book |
| Model Registry | Versioning and staging models so production deployments are traceable | A museum archive labeling every restored painting with its condition, date, and exhibit status |

**Why It Is Needed:** Training hundreds of experiments without records is chaos. You cannot reproduce a result if you do not remember the hyperparameters.

**What We Build:** A NumPy training loop that writes hyperparameters, metrics, and artifacts to a JSON experiment logger, simulating a real MLOps workflow.

**Connects To:** Phase 92

---

## Phase 92: Benchmark Design (COMPLETED)

**The Question:** "How do I know if my model is actually good, or just memorizing the test set?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Benchmark | A standardized test that measures model capability fairly across time | The SAT: everyone takes the same test so colleges can compare applicants fairly |
| Contamination | Training data accidentally leaking into the test set, inflating scores | A teacher accidentally using exam questions that were on yesterday’s homework |
| Validity | Whether a test actually measures the skill it claims to measure | Weighing yourself to measure height: the scale works, but it answers the wrong question |

**Why It Is Needed:** Leaderboard scores are meaningless if the test set leaked into training. Rigorous benchmark design separates real progress from memorization.

**What We Build:** A NumPy toy benchmark where we deliberately contaminate the training set with test examples, then measure the resulting inflated accuracy.

**Connects To:** Phase 93

---

## Phase 93: Paper Reading & Reproduction (COMPLETED)

**The Question:** "How do I read an AI paper without getting lost in the math?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Paper Reproduction | Rebuilding a paper’s result from scratch to verify its claims | Cooking a famous chef’s recipe at home to verify it actually tastes good |
| Method Archaeology | Tracing ideas back through prior work to understand their evolution | A detective following footprints through snow to find where a journey began |
| Ablation | Removing individual components to measure their specific contribution | Testing a car by removing the battery to prove the engine alone will not start |

**Why It Is Needed:** Papers are dense and often skip implementation details. Learning to extract the core idea and reproduce it is the fastest way to build real understanding.

**What We Build:** A NumPy demo that reproduces a toy paper result step by step, then runs an ablation removing each component to isolate its true contribution.

**Connects To:** Phase 94

---

## Phase 94: Statistical Rigor (COMPLETED)

**The Question:** "How do I know if my model is really better, or just lucky?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Confidence Interval | A range that captures the true value with a known probability | A weather forecast saying "between 70 and 80 degrees" instead of guessing exactly 74 |
| p-value | The probability that observed results occurred purely by chance | A jury deciding whether the evidence is strong enough to reject the "innocent until proven guilty" assumption |
| Variance Reduction | Techniques to get more stable estimates from limited experiments | Averaging ten bathroom scales instead of trusting one that wobbles |

**Why It Is Needed:** A single accuracy number hides uncertainty. You need statistical tools to know whether a 1% improvement is real or just random noise.

**What We Build:** NumPy bootstrapping to estimate confidence intervals, plus a paired t-test simulation that compares two models across multiple random seeds.

**Connects To:** Phase 95

---

## Phase 95: Open Source & Research Communication (COMPLETED)

**The Question:** "How do I build a reputation in AI?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Open Source Contribution | Sharing code, models, and datasets with the community | A carpenter posting free blueprints so the whole town builds better houses |
| Technical Writing | Explaining complex ideas clearly so others can build on them | A medical translator turning doctor jargon into instructions a patient can follow |
| Code Review | Critiquing code for clarity, correctness, and maintainability | An editor marking a draft with red pen before it goes to print |

**Why It Is Needed:** Brilliant ideas matter less if no one can use them. Clear code, documentation, and community contribution are how you turn skill into impact.

**What We Build:** A NumPy BEFORE/AFTER demo showing the same algorithm written as spaghetti code versus clean, documented, reusable functions.

**Connects To:** Phase 96

---

## Phase 96: Sparse MoE Training (COMPLETED)

**The Question:** "How do I scale model capacity without proportional compute cost?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Mixture of Experts | Using only a subset of parameters for each input, scaling capacity cheaply | A hospital where each patient sees only the specialists they need, not the entire staff |
| Load Balancing Loss | Preventing all inputs from routing to the same few experts | A manager penalizing a team if two workers do everything while the rest sit idle |
| Expert Choice | Routing inputs to the best-suited experts for that example | A restaurant host seating guests at the station whose chef specializes in their order |

**Why It Is Needed:** Dense models scale compute with every parameter. Mixture of Experts activates only a subset of weights per input, unlocking massive capacity cheaply.

**What We Build:** A NumPy simulation of a tiny MoE layer with trainable gating, showing how inputs route to different experts and how load balancing prevents collapse.

**Connects To:** Phase 97

---

## Phase 97: Extreme Context Windows (COMPLETED)

**The Question:** "How do I process an entire book in one pass?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Ring Attention | Block-wise attention that reduces memory from quadratic to linear in sequence length | Reading a novel in chunks instead of memorizing every page before turning to the next |
| Positional Extrapolation | Extending to sequences longer than the model saw during training | A violinist playing a piece in a larger hall than they rehearsed in by adjusting projection |
| Context Compression | Summarizing long contexts into compact key states for efficient retrieval | A student reducing 500 pages of notes to a single crib sheet for the exam |

**Why It Is Needed:** Standard attention runs out of memory on long documents. New algorithms reduce complexity so you can process entire books or codebases.

**What We Build:** A NumPy simulation comparing O(n^2) memory scaling against O(n) approximations, demonstrating how block-wise methods handle extreme context.

**Connects To:** Phase 98

---

## Phase 98: System-2 Reasoning (COMPLETED)

**The Question:** "How do I train models to think step-by-step and check their own work?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Process Reward Model | Rewarding intermediate reasoning steps, not just final answers | A math teacher giving partial credit for showing work, not just the final answer |
| Chain-of-Thought | Generating explicit intermediate steps before producing a final answer | A GPS listing every turn instead of just saying "arrive in ten miles" |
| Self-Consistency | Generating multiple reasoning paths and trusting the majority answer | Asking three doctors for a diagnosis and trusting the majority opinion |

**Why It Is Needed:** Some problems require deliberate thinking, not reflexive pattern matching. Teaching models to reason step by step and verify answers unlocks harder tasks.

**What We Build:** A NumPy simulation of reasoning chains where the model generates intermediate steps, then uses self-consistency through majority voting to pick the best answer.

**Connects To:** Phase 99

---

## Phase 99: Video & 3D Generation (COMPLETED)

**The Question:** "How do I generate video and 3D objects, not just still images?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Latent Video Diffusion | Generating video in a compressed latent space to save compute | A puppeteer animating a small wireframe model that is later filmed and rendered in full HD |
| 3D Gaussian Splatting | Rendering scenes with millions of 3D Gaussians instead of meshes | A sculptor building a statue from thousands of tiny clay dots instead of carving one solid block |
| Spatiotemporal Attention | Attention that operates jointly across space and time dimensions | A film editor tracking how a character moves across rooms from frame to frame |

**Why It Is Needed:** Images are just the beginning. Video, 3D scenes, and dynamic worlds require modeling time, depth, and motion, not just pixels.

**What We Build:** A NumPy demo applying a 3D convolution to a synthetic 1D-plus-time signal, plus a toy diffusion process that generates simple spatiotemporal patterns.

**Connects To:** Phase 100

---

## Phase 100: Automated Circuit Discovery (COMPLETED)

**The Question:** "How do I understand what specific parts of a neural network actually do?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Mechanistic Interpretability | Reverse-engineering neural networks to find human-understandable circuits | Taking apart a watch to discover exactly which gear moves the hour hand |
| Attribution Patching | Swapping activations between runs to identify causal components | Replacing one fuse in a car to prove it controls the headlights |
| Sparse Autoencoder | Finding a small set of interpretable features that explain network activations | A microscope that highlights only the stained cells you care about in a tissue sample |

**Why It Is Needed:** Neural networks are black boxes unless you can pinpoint which circuits cause which behavior. Reverse-engineering them is essential for safety and debugging.

**What We Build:** A NumPy attribution patching demo that compares forward passes with and without intervening on specific activations to trace causal paths.

**Connects To:** Phase 101

---

## Phase 101: Advanced Alignment (COMPLETED)

**The Question:** "How do we align AI when human feedback is not enough?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Constitutional AI | Training models to critique and revise themselves against a set of principles | A judge deciding cases based on a written constitution rather than momentary mood |
| Iterated Amplification | Bootstrapping supervision by having weaker models assist stronger ones | A student teaching a slightly younger student, who then teaches the next, gradually refining the lesson plan |
| Debate Protocol | Two models argue to expose the truth to a human judge | A courtroom where prosecution and defense cross-examine to expose the facts |

**Why It Is Needed:** Human feedback does not scale to superhuman systems. We need principled methods that align models even when humans cannot directly judge every output.

**What We Build:** A NumPy simulation of a critique-and-revise loop where one model proposes answers and another critiques them according to a fixed constitution.

**Connects To:** Phase 102

---

## Phase 102: Synthetic Data Bootstrapping (COMPLETED)

**The Question:** "What if the best training data comes from the model itself?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Rejection Sampling | Keeping only high-quality generated samples that meet a threshold | A photographer taking 100 shots and keeping only the three that are in focus |
| Self-Improvement | A model training on its own outputs to iteratively get better | A writer revising their own manuscript by reading what they wrote and spotting flaws |
| Verifier-Augmented Generation | Using a separate checker to filter or score generated outputs | A factory where every product is inspected by a separate quality-control robot |

**Why It Is Needed:** The best training data for a task is often generated by a capable model itself. Filtering and verification turn raw generation into high-quality supervision.

**What We Build:** A NumPy rejection sampling demo that generates many candidate solutions and keeps only those that pass a simple verifier check.

**Connects To:** Phase 103

---

## Phase 103: Multimodal Data Curation (COMPLETED)

**The Question:** "How do I align billions of image-text pairs at scale?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Contrastive Filtering | Keeping pairs that are semantically similar yet distinct enough to teach | A matchmaker pairing couples who complement each other rather than are identical twins |
| CLIP Scoring | Measuring image-text similarity with a pretrained dual encoder | A translator scoring how well a poem captures the mood of a painting |
| Temporal Alignment | Synchronizing time-based modalities like video and audio | Dubbing a movie so the actor’s lips match the new language exactly |

**Why It Is Needed:** Multimodal models need billions of aligned image-text pairs. Curating that scale requires automated scoring and synchronization, not manual labeling.

**What We Build:** A NumPy CLIP-style dot-product similarity scorer that ranks image-text pairs, plus a temporal alignment check for video-caption matching.

**Connects To:** Phase 104

---

## Phase 104: Architecture Search (COMPLETED)

**The Question:** "How do I design the right architecture for a problem instead of guessing?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Neural Architecture Search | Automating the design of network structures for a given task | An architect using software to generate and test thousands of floor plans instead of sketching one by hand |
| Inductive Bias | Built-in assumptions that help a model generalize from limited data | A GPS assuming you drive on roads rather than flying over buildings |
| Scaling Laws | Predictable relationships between model size, data, and performance | A chef knowing that doubling a recipe predictably doubles the servings |

**Why It Is Needed:** Hand-designing architectures is slow and often suboptimal. Understanding inductive bias and scaling laws lets you search systematically instead of guessing.

**What We Build:** A NumPy demo comparing locally-connected layers versus fully-connected layers on structured data, showing how the right bias improves generalization.

**Connects To:** Phase 105

---

## Phase 105: Tiny ML & Edge Deployment (COMPLETED)

**The Question:** "How do I run AI on a phone or microcontroller?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Quantization-Aware Training | Training with low precision in mind so quantization does not destroy accuracy | A carpenter cutting wood while already planning which joints will use screws versus glue |
| Knowledge Distillation | A small student model learning from a large teacher’s soft predictions | An apprentice watching a master craftsperson and learning the shortcuts without asking for every rule |
| Neural Architecture Search for Latency | Designing networks that meet strict speed constraints on target hardware | A city planner optimizing traffic-light timing so no car waits longer than ten seconds |

**Why It Is Needed:** Cloud inference is too slow and expensive for every use case. Phones, watches, and sensors need tiny models that run locally with minimal battery.

**What We Build:** A NumPy knowledge distillation demo where a small student learns from a large teacher’s soft targets, outperforming the same student trained on hard labels alone.

**Connects To:** Phase 106

---

## Phase 106: AI for Science (COMPLETED)

**The Question:** "How do I apply AI to molecules, proteins, and physics?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Geometric Deep Learning | Learning on structured data like graphs, meshes, and point clouds | A social network analyst studying connections between people rather than treating everyone as isolated |
| Equivariant Networks | Respecting symmetries like rotation so predictions do not change arbitrarily | A scale that still reads the same weight whether you place the object facing left or right |
| Diffusion for Molecules | Generating valid molecular structures by reversing a noising process | A chemist gradually resolving a blurry microscope image until the molecular structure is crisp |

**Why It Is Needed:** Scientific data has structure—symmetries, graphs, 3D coordinates—that generic models ignore. Specialized architectures exploit that structure for breakthrough results.

**What We Build:** A NumPy demo computing rotation-invariant features from 3D point coordinates, illustrating geometric deep learning for molecules and physics.

**Connects To:** Phase 107

---

## Phase 107: On-Device LLMs (COMPLETED)

**The Question:** "How do I run a language model on my phone?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Mobile LLM | Compact language models optimized for memory and speed on devices | A pocket dictionary instead of an entire library |
| Speculative Decoding | Drafting tokens quickly with a small model then verifying with the large one | A stenographer guessing the next word to keep up with a fast speaker, then the speaker confirming |
| Flash Attention | IO-aware exact attention that minimizes memory round-trips | A student underlining key sentences while reading instead of copying the whole chapter into notes |

**Why It Is Needed:** On-device assistants need fast, private inference without sending data to the cloud. Quantization and efficient attention make that possible on phone hardware.

**What We Build:** A NumPy simulation of quantization reducing weight precision and model size, plus a conceptual demonstration of speculative decoding speedup.

**Connects To:** Phase 108

---

## Phase 108: Multimodal Reasoning (COMPLETED)

**The Question:** "How do models reason across vision and language together?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Multimodal CoT | Extending chain-of-thought reasoning across text and images | A detective describing aloud what they see in a photo to solve a case |
| Visual Question Answering | Answering natural language questions about the content of images | A tour guide explaining what a painting depicts when a visitor asks |
| Cross-Modal Attention | Letting information from one modality attend directly to another | Matching a song lyric to the melody that carries it |

**Why It Is Needed:** Real-world intelligence combines sight and language. Models must attend across images and text to answer complex questions about the visual world.

**What We Build:** A NumPy cross-modal attention matrix that maps text tokens to image patches, demonstrating how vision and language signals interact.

**Connects To:** Phase 109

---

## Phase 109: World Models (COMPLETED)

**The Question:** "How do I build an AI that imagines the future to plan better?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| World Model | An internal learned simulation of environment dynamics | A chess player imagining future board states before moving a piece |
| Dreamer | Learning from imagined trajectories to improve real-world decisions | An athlete visualizing a perfect dive before standing on the board |
| Model Predictive Control | Planning actions by rolling out a learned model and picking the best path | A navigator recalculating the route every mile based on updated traffic predictions |

**Why It Is Needed:** Agents that plan in complex environments need to imagine consequences before acting. A learned world model turns raw trial and error into deliberate strategy.

**What We Build:** A NumPy learned dynamics model that predicts next states from actions, combined with a simple model predictive control rollout that selects optimal trajectories.

**Connects To:** Phase 110

---

## Phase 110: Test-Time Compute Scaling (COMPLETED)

**The Question:** "What if spending more compute at inference time makes the model smarter?"

| Concept | Why It Exists | Analogy |
|---|---|---|
| Test-Time Compute | Using additional computation during inference rather than only during training | A student taking extra time to double-check every answer before handing in the exam |
| Search Over Outputs | Exploring many possible outputs and selecting the best one | A writer brainstorming ten headlines and choosing the catchiest one |
| Refinement Loop | Iteratively improving an answer through repeated critique and revision | A sculptor chipping away at marble, stepping back to evaluate, and chipping again |

**Why It Is Needed:** Model size is not the only path to intelligence. Spending more compute at test time—searching, refining, verifying—can dramatically boost accuracy without retraining.

**What We Build:** A NumPy best-of-N sampling demo that draws multiple answers and picks the best one, plotting how accuracy improves with more inference-time compute.

**Connects To:** End of curriculum. The student is ready to push the boundaries of AI research and engineering.

---

## The Promise

By the end of Phase 110, the student will:
- Understand EVERY major AI architecture from first principles
- Have built EVERY architecture from scratch in NumPy
- Know WHY each invention was necessary
- Be able to read any AI research paper and understand the "why"
- Be ready to specialize in any subfield of AI
- DEFEND models against adversarial attacks using FGSM, PGD, and adversarial training
- FORECAST temporal sequences using autoregressive models and exponential smoothing
- TRAIN models on decentralized data without centralization through federated learning
- QUANTIFY prediction uncertainty with Bayesian neural networks and Monte Carlo dropout
- AUTOMATE model selection and hyperparameter tuning with AutoML and successive halving
- INTELLIGENTLY select which data to label through active learning and uncertainty sampling
- CURATE and PREPARE real instruction-following datasets
- FINE-TUNE open-source models with LoRA and QLoRA on custom data
- ALIGN models with human preferences using DPO and ORPO
- EXECUTE and DEFEND against jailbreak attacks (roleplay, encoding, GCG)
- RED-TEAM models for safety vulnerabilities
- BUILD domain-specific assistants (medical, legal, coding)
- DEPLOY models for inference with vLLM and batch optimization
- BUILD real agentic systems with function calling and tool use
- DISCOVER hidden structure in unlabeled data with K-means, PCA, t-SNE, and DBSCAN
- CHOOSE the right number of clusters using the elbow method and silhouette analysis
- REDUCE dimensionality while preserving variance through eigen-decomposition
- VISUALIZE high-dimensional clusters in 2D without distorting local neighborhoods
- SEPARATE dense clusters from noise using density-based spatial clustering
- LOCALIZE objects in images using bounding boxes, anchors, and single-shot detectors
- COMPUTE spatial overlap with Intersection Over Union (IoU) and evaluate with mean Average Precision (mAP)
- REMOVE duplicate detections with Non-Maximum Suppression (NMS)
- DISTINGUISH single-shot detectors (YOLO) from two-stage detectors (R-CNN) and know when to use each
- SEGMENT images at the pixel level with semantic and instance segmentation masks
- USE promptable segmentation models (SAM) to extract object boundaries without predefined classes
- PROCESS raw audio into perceptual features with STFT, mel-filterbanks, and MFCCs
- TRANSCRIBE speech to text with CTC alignment and Transformer-based ASR
- GENERATE personalized recommendations with collaborative filtering, matrix factorization, and two-tower retrieval
- OPTIMIZE recommendation ranking with BPR and evaluate with Hit Rate and NDCG
- EXPLAIN black-box predictions with saliency maps, SHAP values, LIME surrogates, and attention visualization
- DISTINGUISH global explanations (feature importance) from local explanations (instance-level justification)
- DETECT algorithmic bias with demographic parity and equalized odds metrics
- MITIGATE unfairness through pre-processing, in-processing, and post-processing techniques
- MEASURE true causal effects with randomized control trials, propensity score matching, and instrumental variables
- DISTINGUISH correlation from causation in observational data
- MONITOR production models for data drift and concept drift using KL divergence and PSI
- AUTOMATE retraining pipelines when model performance degrades in production
- PREVENT catastrophic forgetting with Elastic Weight Consolidation (EWC) and replay buffers
- DESIGN continual learning systems that acquire new skills without erasing old ones
- WRITE optimized GPU kernels that exploit memory hierarchy and kernel fusion for massive speedups
- TRAIN models across multiple nodes using data parallelism, efficient all-reduce, and JAX/XLA JIT compilation
- RECOVER from failures in large distributed jobs through checkpointing, deterministic training, and container orchestration with Kubernetes
- TRANSFORM terabytes of raw web data into clean training corpora through deduplication, perplexity filtering, and automated quality scoring
- SERVE LLMs efficiently with continuous batching, PagedAttention, and KV cache management to minimize inference cost
- TRACK hundreds of experiments with structured logging, model registries, and MLOps best practices
- READ, reproduce, and rigorously evaluate AI research papers through ablation studies, confidence intervals, and hypothesis testing
- SCALE model capacity without proportional compute cost using Mixture of Experts, load-balanced gating, and extreme context techniques like ring attention
- TRAIN models to reason step-by-step with chain-of-thought, process reward models, and self-consistency
- GENERATE video and 3D content with spatiotemporal attention, latent diffusion, and 3D Gaussian splatting
- REVERSE-ENGINEER neural networks through mechanistic interpretability, attribution patching, and sparse autoencoders
- ALIGN advanced AI systems with constitutional principles, iterated amplification, debate protocols, and synthetic data bootstrapping
- CURATE multimodal datasets at scale with contrastive filtering, CLIP scoring, and temporal alignment
- DESIGN the right architecture for a problem using inductive bias, scaling laws, and neural architecture search, then deploy tiny versions on edge devices with quantization and distillation
- APPLY AI to scientific problems with geometric deep learning and equivariant networks, run on-device LLMs with speculative decoding, build world models for planning, and scale intelligence at test time through search and refinement
- FINE-TUNE real pre-trained models end-to-end on real datasets with proper training loops, checkpointing, and evaluation
- BUILD real retrieval-augmented generation systems with dense embeddings, vector search, and context injection
- DISTILL knowledge from large teacher models to small student models on real data with temperature scaling and combined losses
- DEPLOY production inference APIs with FastAPI, streaming generation, OpenAI-compatible endpoints, and health monitoring
- CURATE real training data through cleaning, quality filtering, and MinHash-based near-duplicate detection
- BUILD multi-tool agents that interleave reasoning and action through the ReAct pattern with memory
- EVALUATE models rigorously with bootstrap significance testing and paired t-tests to separate real improvements from noise
- QUANTIZE models to INT8 for deployment, benchmark speed and memory tradeoffs, and package models for production

**This is not a race to GPT. This is a complete education in artificial intelligence.**

---

*Ready for Phase 5?*
