Why it exists
-------------
In everyday life, we constantly need to prove things about ourselves. We
prove our age to buy alcohol, our income to rent an apartment, and our
citizenship to cross borders. Traditional proof requires revealing far more
information than necessary. A driver's license shows your exact birthdate,
address, and even organ donor status when all the bartender needs is a
boolean: over 21 or not. Zero-knowledge as a concept exists to solve this
by separating proof from disclosure. It allows you to answer yes-no
questions without handing over your entire identity file. On blockchains,
where everything is public, this separation is not just convenient. It is
essential for human dignity and financial safety.

Definition
----------
Zero-knowledge is a property of certain cryptographic protocols where the
verifier gains no additional knowledge beyond the fact that the statement is
true. Formally, a protocol has the zero-knowledge property if the
interaction between prover and verifier can be simulated by a machine that
does not know the secret, and the simulated transcript is indistinguishable
from a real one. This means the verifier could have generated the same
data themselves without talking to the prover. Therefore, the verifier
learns nothing from the prover except the validity of the claim. Zero-
knowledge is the foundational property that makes ZK proofs private.

Real-life analogy
-----------------
Imagine a cave shaped like a ring with a magic door in the middle. Alice
claims she knows the secret word that opens the door. Bob wants proof but
does not want to learn the word. They play a game. Bob stands outside and
calls "left" or "right." Alice enters the cave from the front and must exit
from the side Bob called. If she knows the secret word, she can open the
door and cross. If she does not, she has a 50% chance of guessing
 correctly. They repeat this 20 times. After 20 successful exits, Bob is
convinced Alice knows the word, but he still has no idea what the word is.
This is the zero-knowledge property: conviction without disclosure.

Tiny numeric example
--------------------
Alice wants to prove she knows the discrete logarithm of a public value
without revealing the exponent.

Public parameters:
- Generator g = 2
- Prime modulus p = 17
- Public value h = 2^x mod 17 = 9 (Alice knows x = 6)

Alice picks a random r = 3 and sends a = g^r mod 17 = 8.
The verifier sends a challenge c = 5.
Alice computes z = r + c * x = 3 + 5 * 6 = 33.
The verifier checks that g^z mod 17 = a * h^c mod 17.

Left side: 2^33 mod 17 = 15.
Right side: 8 * 9^5 mod 17 = 8 * 6 mod 17 = 48 mod 17 = 15.

The equation holds, so the verifier is convinced. But the challenge c was
random, and z reveals nothing about x because r masked it. If Alice did not
know x, she could not consistently pass the check for arbitrary c.

Common confusion
----------------
- Zero-knowledge does not mean the prover reveals nothing at all. The
  verifier learns that the statement is true.
- Zero-knowledge is not anonymity. Anonymity hides who you are. Zero-
  knowledge hides what you know while still proving something.
- Zero-knowledge protocols can be interactive or non-interactive.
  Non-interactive ZK proofs are more common on blockchains because they do
  not require real-time back-and-forth.
- Zero-knowledge does not protect against false inputs. If the prover lies
  about the input data, the proof is still valid for that false input.
  Garbage in, garbage out.
- Zero-knowledge is not a single algorithm. It is a property that many
  different cryptographic constructions can achieve.
- Zero-knowledge proofs can be computationally convincing or statistically
  convincing. Most blockchain applications use computational security.
- Zero-knowledge does not mean untraceable. A proof can be linked to a
  specific credential or identity if the underlying system is designed that
  way.

Where it appears in our code
----------------------------
`src_web3/phase49/zk_privacy_api.ts` implements an Express API that
demonstrates the zero-knowledge property through simulated proof generation
and verification flows where no secret values are exposed to the verifier.

Key properties
--------------
- Non-disclosure: The verifier learns only the truth of the statement.
- Simulatability: The proof transcript can be faked by a simulator without
  the secret.
- Transferable: Once generated, a proof can be verified by anyone without
  further interaction with the prover.
- Composable: Zero-knowledge proofs can be combined to prove complex
  statements about multiple secrets.
