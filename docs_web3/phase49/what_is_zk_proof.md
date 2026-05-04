Why it exists
-------------
Blockchains are transparent. Every transaction, balance, and interaction is
visible to anyone. This is great for auditability but terrible for privacy.
Users do not want the world to know their salary, their medical payments,
or their political donations. Zero-knowledge proofs exist to solve this by
allowing someone to prove a statement is true without revealing the
underlying data. With ZK proofs, you can prove you are over 18 without
showing your birthdate. You can prove you have enough collateral without
revealing your wallet balance. You can prove you voted without revealing
your choice. Without zero-knowledge techniques, privacy on public
blockchains would be impossible.

Definition
----------
A zero-knowledge proof is a cryptographic method by which one party, the
prover, can convince another party, the verifier, that a statement is true
without revealing any information beyond the truth of that statement. The
proof must satisfy three properties: completeness, meaning an honest prover
can always convince an honest verifier; soundness, meaning a dishonest
prover cannot convince a verifier of a false statement; and zero-knowledge,
meaning the verifier learns nothing beyond the statement's validity. In
blockchain contexts, ZK proofs are used to verify transactions, identity
claims, and computations while keeping sensitive data hidden.

Real-life analogy
-----------------
Imagine you have a locked safe and you want to prove to a friend that you
know the combination without telling them what it is. You ask your friend to
write a secret message on a piece of paper, place it inside the safe, and
lock it. You then turn your back, open the safe with your combination,
retrieve the paper, and show it to your friend. Your friend is convinced you
know the combination because you opened the safe, but they never saw the
numbers you entered. Zero-knowledge proofs work similarly: the prover
demonstrates knowledge of a secret without revealing the secret itself.

Tiny numeric example
--------------------
Alice wants to prove she knows two numbers, x and y, such that x + y = 100,
without revealing x or y.

Using a simple ZK protocol:
1. Alice commits to x and y using cryptographic hashes.
2. The verifier checks that the commitment to x plus the commitment to y
   equals the commitment to 100.
3. Alice opens the commitments in a way that proves consistency without
   revealing the raw numbers.

In a real ZK system, this would involve polynomials, elliptic curves, and
pairing equations. The key takeaway is that the verifier ends up convinced
that x + y = 100, but learns nothing about the individual values of x and y.
Alice could have used x = 30 and y = 70, or x = 1 and y = 99, and the
verifier would not know.

Common confusion
----------------
- Zero-knowledge proofs are not encryption. Encryption hides data for later
  decryption. ZK proofs prove facts without revealing data at all.
- Zero-knowledge proofs do not make transactions invisible. They prove
  validity without exposing the details that traditional verification needs.
- ZK proofs are not only for privacy. They are also used to verify large
  computations compactly, which is called a validity proof.
- Not all ZK proofs are the same. SNARKs, STARKs, and Bulletproofs have
  different trade-offs in size, speed, and trust assumptions.
- ZK proofs do not require a trusted third party to hold secrets. The
  verifier checks the proof mathematically without trusting the prover.
- Creating a ZK proof is computationally expensive. Verification is fast,
  but proof generation can take significant time and memory.
- ZK proofs do not prove anything about the real world by themselves. They
  prove mathematical statements. Connecting those statements to reality
  requires trusted inputs.

Where it appears in our code
----------------------------
`src_web3/phase49/zk_privacy_api.ts` implements an Express API that
simulates ZK proof generation, verification, and privacy-preserving
credential checks without revealing underlying secrets.

Key properties
--------------
- Privacy-preserving: Verifiers learn nothing beyond the statement's truth.
- Sound: Dishonest provers cannot forge valid proofs of false statements.
- Complete: Honest provers can always generate convincing proofs.
- Compact: Proofs are small and fast to verify compared to re-executing the
  computation.
- Universal: Applicable to identity, finance, voting, and beyond.
