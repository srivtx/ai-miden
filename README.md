# AI-MIDEN: From Absolute Zero to Production

> **A complete AI and Web3 curriculum built from scratch.**
>
> **158 AI phases.** Built in Python and NumPy. Every neuron, every gradient, every matrix multiplication visible.
>
> **71 Web3 phases.** Built in Rust and TypeScript. Every instruction, every CPI call, every signature verified.
>
> **No black boxes. No shortcuts. Nothing skipped.**

---

## Start Here — Pick Your Path

| If you want to... | Start here |
|---|---|
| **Learn AI from zero** | [Phase 0: What is AI?](docs/phase0/) → [Phase 1: First Model](docs/phase1/) → [Phase 4: Neural Networks](docs/phase4/) |
| **Understand how ChatGPT works** | [Phase 18: Transformer](docs/phase18/) → [Phase 20: GPT](docs/phase20/) → [Phase 23: RLHF](docs/phase23/) |
| **Fine-tune LLMs on your own data** | [Phase 22: SFT](docs/phase22/) → [Phase 35: LoRA](docs/phase35/) → [Phase 151: Fine-Tuning Pipeline](docs/phase151/) |
| **Build agents that use tools** | [Phase 27: Agentic AI](docs/phase27/) → [Phase 72: Real Agents](docs/phase72/) → [Phase 156: Multi-Tool Agent](docs/phase156/) |
| **Make models run faster or smaller** | [Phase 25: Inference Optimization](docs/phase25/) → [Phase 36: Speculative Decoding](docs/phase36/) → [Phase 83: GPU Kernels](docs/phase83/) |
| **Train at scale (multi-GPU, clusters)** | [Phase 55: Distributed Training](docs/phase55/) → [Phase 84: Memory Engineering](docs/phase84/) → [Phase 85: Multi-Node Training](docs/phase85/) |
| **Understand diffusion / image generation** | [Phase 29: VAEs](docs/phase29/) → [Phase 31: Diffusion](docs/phase31/) → [Phase 40: Flow Matching](docs/phase40/) |
| **Do AI research / read papers** | [Phase 93: Paper Reading](docs/phase93/) → [Phase 100: MechInterp](docs/phase100/) → [Phase 104: Architecture Search](docs/phase104/) |
| **Prepare for coding interviews** | [docs_dsa/START_HERE.md](docs_dsa/START_HERE.md) — 19 patterns, 540 problems, 220 flashcards |
| **Build safe / aligned AI** | [Phase 67: Jailbreaking](docs/phase67/) → [Phase 69: Red-Teaming](docs/phase69/) → [Phase 128: Safety](docs/phase128/) |
| **Work with audio, images, or video** | [Phase 73: Speech](docs/phase73/) → [Phase 78: Object Detection](docs/phase78/) → [Phase 99: Video & 3D](docs/phase99/) |
| **Train models from scratch** | [Phase 121: Pretraining](docs/phase121/) → [Phase 122: RLHF](docs/phase122/) → [Phase 125: Long Context](docs/phase125/) |
| **Build production inference systems** | [Phase 129: Inference Engines](docs/phase129/) → [Phase 130: Monitoring](docs/phase130/) → [Phase 154: Inference API](docs/phase154/) |
| **Build real production systems** | [Phase 151: Fine-Tuning](docs/phase151/) → [Phase 152: RAG](docs/phase152/) → [Phase 154: Inference API](docs/phase154/) → [Phase 158: Quantization](docs/phase158/) |
| **Build Web3 / Solana dApps** | [Phase 0: What is Web3?](docs_web3/phase0/) → [Phase 6: First Transaction](docs_web3/phase6/) → [Phase 16: AMM](docs_web3/phase16/) → [Phase 59: Anchor Framework](docs_web3/phase59/) → [Phase 60: Jupiter Integration](docs_web3/phase60/) → [Phase 66: Security Auditing](docs_web3/phase66/) |
| **Build production DeFi protocols** | [Phase 51: Complete DEX](docs_web3/phase51/) → [Phase 52: Lending Protocol](docs_web3/phase52/) → [Phase 54v2: Real DAO](docs_web3/phase54v2/) → [Phase 58v2: Real Launchpad](docs_web3/phase58v2/) |
| **Secure Solana protocols** | [Phase 24: Security](docs_web3/phase24/) → [Phase 61: Production Infrastructure](docs_web3/phase61/) → [Phase 66: Security Auditing](docs_web3/phase66/) |

---

## Course Stats

| | Count |
|---|---|
| AI Phases | **158** |
| Web3 Phases | **71** |
| Total Phases | **229** |
| Documentation files | **1,017** |
| Code files | **653** |
| Terms defined | **743** |
| DSA Patterns | **19** |
| DSA Problems | **540** |
| DSA Flashcards | **220** |

---

## Project Structure

```
ai-miden/
├── docs/                           # AI Course (158 phases)
│   ├── phase0/ ... phase158/       # Each phase: what_is_*.md docs + SUMMARY.md
│   ├── MASTER_CURRICULUM.md        # Full 158-phase AI roadmap
│   └── AI_ROADMAP_FUTURE.md        # Future expansion plans
├── src/                            # AI Code (158 phases)
│   ├── phase0/ ... phase158/       # Each phase: NumPy demo + optional Colab script
│   └── ...
├── docs_web3/                      # Web3 / Solana Course (71 phases)
│   ├── phase0/ ... phase58/        # Concept phases + real projects
│   ├── phase54v2/                  # Real DAO (Anchor + Squads rewrite)
│   ├── phase55v2/                  # Real Yield Farm (Token-2022 rewrite)
│   ├── phase56v2/                  # Real Bridge (Ed25519 rewrite)
│   ├── phase58v2/                  # Real Launchpad (Jupiter rewrite)
│   ├── phase59/ ... phase66/       # Production engineering phases
│   └── MASTER_CURRICULUM.md        # Full Web3 roadmap
├── src_web3/                       # Web3 Code (71 phases)
│   ├── phase0/ ... phase58/        # Rust programs + TypeScript APIs
│   ├── phase54v2/ ... phase58v2/   # Production rewrites
│   ├── phase59/ ... phase66/       # Production engineering
│   └── package.json                # Node.js dependencies
├── docs_dsa/                       # DSA Interview Prep (separate module)
│   ├── START_HERE.md               # Navigate the DSA system
│   ├── 01_arrays_hashing/ ... 18_bit_manipulation/
│   ├── COMPANY_GUIDES/
│   ├── FLASHCARDS.md
│   └── ...
├── AGENT_BRAIN.md                  # Build methodology and patterns
└── README.md                       # This file
```

---

## Quick Start

### AI Track

```bash
# Install dependencies (only numpy and matplotlib needed for local scripts)
pip install numpy matplotlib

# Run the very first phase
python src/phase0/phase0_basics.py

# Run a Transformer built from scratch
python src/phase18/phase18_transformer.py

# Run a tiny GPT that generates text
python src/phase21/phase21_tiny_gpt.py
```

For GPU-heavy phases (15-21, 29-31, 64-72), each phase has a `*_colab.py` script designed for Google Colab T4.

### Web3 Track

```bash
# Install Node.js dependencies
cd src_web3 && npm install

# Run the first Web3 demo
npx ts-node src_web3/phase0/decentralization_demo.ts

# Send your first Solana transaction
npx ts-node src_web3/phase6/first_transaction.ts

# Start the AMM API
npx ts-node src_web3/phase16/amm_api.ts

# Start the Anchor Counter API (Phase 59)
npx ts-node src_web3/phase59/counter_api.ts

# Start the Jupiter Swap API (Phase 60)
npx ts-node src_web3/phase60/jupiter_api.ts
```

---

## How This Course Works

Every phase follows the same structure:

1. **Docs** in `docs/phaseX/` or `docs_web3/phaseX/` — Every new term gets its own file: `what_is_term.md`
   - Why it exists (the problem first)
   - A simple definition
   - A real-life analogy
   - A tiny numeric example
   - Common confusions (6 bullet points, each starting with "No.")
   - Key properties (4-5 bullet points)
   - Where it appears in our code

2. **Code** in `src/phaseX/` or `src_web3/phaseX/` — Runnable scripts that demonstrate the concept
   - **AI track:** NumPy scripts + optional PyTorch Colab scripts
   - **Web3 track:** Rust programs + TypeScript/Express APIs
   - Every line explains WHY, not just WHAT
   - Plots are saved, not shown interactively (AI track)

3. **Summary** in `docs/phaseX/SUMMARY.md` — Recap, connections to other phases, and navigation links

4. **Architecture** in `docs/phaseX/ARCHITECTURE.md` — For real project phases: step-by-step build instructions from scratch

---

## What Makes This Different

- **No black boxes.** Everything is built from scratch in NumPy. You see every weight, every gradient, every matrix multiplication.
- **No jargon without explanation.** Every technical term has its own dedicated doc with an analogy and a numeric example.
- **No math gatekeeping.** If you know algebra, you can follow every phase. Calculus is introduced gradually and visually.
- **Two-script pattern.** Local NumPy scripts teach the concept from scratch. Colab PyTorch scripts run when training is impractical locally.
- **Dual-track Web3.** Every concept has both a Rust on-chain program AND a TypeScript/Express API. You learn both the smart contract and the backend service.
- **Real projects.** Not toy examples. Token vaults, AMMs, escrow, multi-sig, staking, lending, flash loans — all with real code.
- **Production engineering.** Phases 59-66 teach what separates devnet demos from mainnet apps: Anchor, Jupiter, Helius, Token-2022, Blinks, ZK Compression, Drift patterns, and security auditing.
- **v2 rewrites.** When we discovered broken implementations (stubbed functions, fake security, mock APIs), we created v2 phases (54v2, 55v2, 56v2, 58v2) that fix them while preserving the learning journey.
- **DSA included.** `docs_dsa/` contains a complete LeetCode/NeetCode prep system with 19 patterns, 540 problems, and 220 flashcards.
- **Methodology documented.** `AGENT_BRAIN.md` captures how this curriculum was built, so anyone can replicate or extend it.

---

## The AI Journey

**Foundations (0-10)** — Prediction, gradient descent, neural networks, regularization.

**Seeing & Remembering (11-14)** — CNNs, ResNets, RNNs, LSTMs.

**Language & Transformers (15-24)** — Embeddings, attention, Transformer, BERT, GPT, fine-tuning, alignment.

**Making AI Useful (25-28)** — Inference optimization, reasoning, agents, multimodal systems.

**Creating Data (29-31)** — VAEs, GANs, diffusion models.

**The Future (32-46)** — MoE, Mamba, LoRA, speculative decoding, RAG, scaling laws, quantization, mechanistic interpretability.

**Data & Training (47-56)** — Synthetic data, self-supervised learning, RL, GNNs, distributed training, gradient boosting.

**Robustness (57-62)** — Adversarial defense, time series, federated learning, Bayesian NNs, AutoML, active learning.

**Applied AI (63-81)** — Domain adaptation, safety, speech, recommendations, XAI, fairness, object detection, causal inference, continual learning.

**Systems & Scale (83-95)** — GPU kernels, memory engineering, multi-node training, JAX, Kubernetes, data pipelines, inference serving, experiment tracking, benchmarks, statistics, open source.

**Frontier Research (96-110)** — Sparse MoE, extreme context, system-2 reasoning, video/3D generation, automated circuit discovery, advanced alignment, synthetic data bootstrapping, multimodal data curation, architecture search, tiny ML, AI for science, on-device LLMs, world models, test-time compute scaling.

**Frontier Practice (111-120)** — FP8 training, multi-token prediction, KV cache compression, DeepSeek-R1 pipeline, structured generation, automated red-teaming, data mixing laws, native multimodal architectures, advanced speculative decoding, disaggregated serving.

**Production Engineering (121-130)** — Pretraining from scratch, full RLHF pipeline (RM + PPO), model merging at scale, advanced quantization (GPTQ/AWQ/GGUF), long context training (YaRN), tool use training, vision-language fine-tuning, safety RLHF, production inference engines (vLLM), production monitoring and MLOps.

**Real Projects (151-158)** — End-to-end fine-tuning on IMDB, real RAG with MiniLM + GPT-2, knowledge distillation from BERT to tiny BERT, production FastAPI inference server, Wikipedia data curation with MinHash deduplication, multi-tool ReAct agent with calculator/Python/Wikipedia, evaluation harness with bootstrap significance testing, INT8 quantization and deployment benchmarking.

---

## The Web3 Journey

**Web3 Foundations (0-5)** — Blockchain, cryptography, Solana architecture, accounts, dev environment.

**First Transactions (6-10)** — Sending SOL, reading blockchain data, writing programs, state storage, PDAs.

**Token Projects (11-15)** — Cross-program invocation, SPL tokens, token vault, escrow, multi-sig wallets.

**DeFi Primitives (16-20)** — AMM with x*y=k, liquidity pools, staking, lending, time-locked vaults.

**NFTs & Operations (21-25)** — NFT minting, marketplaces, program upgrades, security, testing.

**Backend APIs (26-30)** — Custom RPC services, indexing, payment gateways, composability, flash loans.

**Advanced Topics (31-35)** — DAO governance, oracle integration, MEV protection, account compression, production deployment.

**DeFi Advanced (36-45)** — Subscription payments, token vesting, decentralized identity, quadratic voting, cross-chain bridges, perpetual futures, options, insurance, RWA tokenization, soulbound tokens.

**Infrastructure (46-50)** — Intent-based architecture, account abstraction, restaking, ZK proofs for privacy, DePIN.

**Real Projects (51-58)** — Complete DEX with limit orders and routing, lending protocol with liquidation bots, NFT marketplace with auctions and royalties, DAO platform with treasury and delegation, yield farm with boost NFTs and auto-compounding, cross-chain bridge with guardian network, prediction market with oracle resolution, token launchpad with tiered sales and vesting.

**Production Rewrites (54v2-58v2)** — When we discovered the original phases 54, 55, 56, and 58 had broken implementations (lamport-weighted voting, stubbed reward transfers, fake signatures, in-memory mock APIs), we built v2 phases that fix them using Anchor v1.0, Token-2022, real Ed25519 verification, and Jupiter integration. Each v2 SUMMARY.md compares what changed, why changed, and how changed.

**Production Engineering (59-66)** — Anchor Framework v1.0 deep dive, Jupiter API integration for swaps and routing, Helius RPC with priority fees and versioned transactions, Token-2022 extensions (transfer hooks, metadata pointer), Blinks and Actions for embedded transactions, ZK Compression with Light Protocol for 99% rent reduction, Drift Protocol keeper patterns and cross-collateral, advanced security auditing with vulnerable vs secure side-by-side code.

---

## Core Concepts Index

**AI Core:** gradient descent, backpropagation, neural network, weight, bias, activation, loss function, optimizer, learning rate, batch, epoch, overfitting, underfitting, regularization, dropout, batch normalization, convolution, residual connection, LSTM, attention, self-attention, multi-head attention, Transformer, encoder, decoder, BERT, GPT, vision transformer, U-Net, diffusion transformer, Mamba, RLHF, DPO, LoRA, QLoRA, quantization, KV cache, Flash Attention, speculative decoding

**Web3 Core:** blockchain, hash function, proof of history, accounts model, program derived address, cross-program invocation, SPL token, associated token account, token vault, escrow, multi-signature, automated market maker, liquidity pool, impermanent loss, staking, lending, collateral, liquidation, health factor, NFT, Metaplex, re-entrancy, integer overflow, flash loan, arbitrage, MEV, DAO, oracle, merkle tree, account compression, Anchor, Jupiter, Helius, Token-2022, Blinks, ZK Compression, Drift

**DSA Core:** arrays, hashing, two pointers, sliding window, stack, binary search, linked list, trees, heap, backtracking, tries, graphs, advanced graphs, greedy, intervals, math, bit manipulation

---

## What AI Actually Is

1. Making a guess
2. Measuring how wrong the guess is
3. Figuring out which direction to improve
4. Taking a small step
5. Repeating

That is all AI is. And now you know it from the inside out.

---

## What Web3 Actually Is

1. Shared rules everyone agrees on
2. Cryptographic proof instead of trust
3. Code that runs exactly as written
4. Economic incentives that keep it honest
5. Users who own their own data

That is all Web3 is. And now you know how to build it.

---

**Keep going. You have everything you need.**
