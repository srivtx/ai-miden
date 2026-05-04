# What Is a Verifiable Credential

## Why It Exists

Proving who you are or what you have achieved usually involves paper documents, manual checks, and trusted third parties. Employers call universities to verify degrees. Banks request utility bills to confirm addresses. These processes are slow, expensive, and privacy-invasive because they expose more data than necessary. Verifiable credentials solve this by packaging claims into cryptographically signed documents that can be checked instantly without contacting the issuer every time.

## Definition

A verifiable credential is a tamper-evident digital document that attests to a claim about a subject. It is issued by a trusted party, stored by the subject, and presented to a verifier who can cryptographically confirm its authenticity without contacting the issuer.

## Real-Life Analogy

Think of a digitally signed diploma. The university issues a PDF, signs it with its private key, and emails it to the graduate. When the graduate applies for a job, they send the PDF to the employer. The employer uses the university's public key to verify the signature, checks the date, and confirms the degree is real. The employer never needs to call the university registrar. A verifiable credential is that diploma, but standardized and machine-readable.

## Tiny Numeric Example

A university issues a credential to a student.

| Field | Value | Purpose |
|-------|-------|---------|
| Issuer DID | did:ethr:0xuniv789... | Identifies the university |
| Subject DID | did:ethr:0xstu123... | Identifies the student |
| Claim | degree: "BSc Computer Science" | The actual assertion |
| Issuance date | 2024-06-15 | When the credential was created |
| Signature | 0x3f2a... | Cryptographic proof from the issuer |

When the student presents this credential to an employer, the employer verifies the signature against the issuer's public key in the DID document. The check takes milliseconds and reveals no other personal information.

## Common Confusion

- A verifiable credential is not stored on the blockchain by default; the issuer's DID is on-chain, but the credential itself is usually held privately by the subject.
- Verifiable does not mean the claim is true; it means the signature is valid and the issuer is authenticated. The verifier must still trust the issuer.
- Selective disclosure is not automatic; the credential format must support zero-knowledge proofs or redaction for the subject to hide unnecessary fields.
- Revocation is possible; issuers can publish revocation lists or status registries so verifiers can check if a credential is still valid.
- Self-issued credentials exist but carry less weight; a claim signed by the subject about themselves is not independent verification.
- Verifiable credentials are not NFTs; they are not designed for transfer or speculation, and they usually are not traded.
- The verifier does not need a direct relationship with the issuer; they only need access to the issuer's public key, which is published via the DID document.

## Key Properties

## Where It Appears in Our Code

Verifiable credentials are modeled in `src_web3/phase38/did_api.ts` where the `/issue` endpoint creates a signed credential, the `/verify` endpoint checks the cryptographic signature, and the `/present` endpoint simulates selective disclosure to a third party.
