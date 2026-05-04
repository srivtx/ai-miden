Why it exists
-------------
Early zero-knowledge proofs were interactive and impractical for
blockchains. They required back-and-forth communication between prover and
verifier, which is impossible in an asynchronous distributed system. ZK-
SNARKs exist to solve this by making proofs short, non-interactive, and
fast to verify. A SNARK proof can be generated once, posted on-chain, and
verified by anyone in milliseconds. This makes scalability and privacy
practical on public blockchains. Without SNARKs, concepts like zkRollups
and private transactions would be too slow and too large to fit in blocks.

Definition
----------
A ZK-SNARK is a Zero-Knowledge Succinct Non-Interactive Argument of
Knowledge. Zero-knowledge means it reveals nothing beyond the statement's
truth. Succinct means the proof is tiny, often just a few hundred bytes,
and verification is extremely fast. Non-interactive means the prover
generates the proof without any real-time communication with the verifier.
Argument of knowledge means it is computationally infeasible to create a
valid proof without actually knowing the secret witness. SNARKs use
sophisticated mathematics including elliptic curve pairings, polynomial
commitments, and structured reference strings to achieve these properties.

Real-life analogy
-----------------
Imagine a university exam where students must prove they studied. In an
interactive system, the professor asks each student questions back and forth
for an hour. This works for one student but not for ten thousand. A SNARK is
like a standardized scantron test. Each student fills out a small bubble
sheet once. The professor runs it through a machine that verifies every
answer in seconds. The sheet reveals nothing about how the student studied,
only that they know the material. The proof is small, the verification is
fast, and no conversation is needed. That is exactly what a SNARK does for
computation.

Tiny numeric example
--------------------
A zkRollup wants to prove that 1,000 transactions are valid and update the
state root correctly.

Without a SNARK:
- Post all 1,000 transactions on-chain.
- Every node re-executes all 1,000 transactions to verify.
- Gas cost: massive. Verification time: proportional to transaction count.

With a SNARK:
- Prover generates a 200-byte proof off-chain after processing the 1,000
  transactions.
- Prover posts the proof, the old state root, and the new state root on-
  chain.
- Verifier contract checks the proof in 2 milliseconds using a fixed number
  of elliptic curve operations.
- Gas cost: tiny and constant regardless of transaction count.

The SNARK proves "I know a valid sequence of 1,000 transactions that
transforms the old root into the new root" without revealing the
transactions or re-executing them.

Common confusion
----------------
- SNARKs require a trusted setup. Most SNARK constructions need a one-time
  ceremony to generate parameters. If the setup is compromised, fake proofs
  can be created. Newer schemes reduce or eliminate this requirement.
- SNARKs are not quantum-resistant. They rely on elliptic curve
  cryptography, which quantum computers could break. STARKs are a quantum-
  resistant alternative.
- SNARK proof generation is slow and memory-intensive. The prover may need
  powerful hardware. The benefit is fast verification, not fast proving.
- SNARKs do not hide the statement being proven. They hide the witness, but
  the public inputs are visible.
- Not all SNARKs are zero-knowledge. Some SNARKs are used only for
  succinctness without privacy. The ZK prefix specifically denotes privacy.
- SNARKs are not magic. They prove computational statements. If the
  underlying program has bugs, the proof is still valid for what the program
  actually does.
- SNARK verification is cheap, but on-chain verification still costs gas.
  The savings come from compressing many operations into one proof.

Where it appears in our code
----------------------------
`src_web3/phase49/zk_privacy_api.ts` implements an Express API that
simulates SNARK-style proof generation, verification, and the dramatic
compression of verification work compared to naive re-execution.

Key properties
--------------
- Succinct: Proofs are tiny, often under 1 kilobyte.
- Fast verification: Verification time is constant or logarithmic in the
  computation size.
- Non-interactive: Prover generates the proof without verifier involvement.
- Zero-knowledge: Witness data remains hidden.
- Trusted setup: Most SNARKs require secure parameter generation.
- Computationally sound: Forging proofs without the witness is infeasible.
