# What Is a Verifiable Credential

## The Problem

Proving who you are or what you have achieved usually involves paper documents, manual checks, and trusted third parties. Employers call universities to verify degrees. Banks request utility bills to confirm addresses. These processes are slow, expensive, and privacy-invasive because they expose more data than necessary. Verifiable credentials solve this by packaging claims into cryptographically signed documents that can be checked instantly without contacting the issuer every time.

## Definition

A verifiable credential is a tamper-evident digital document that attests to a claim about a subject. It is issued by a trusted party, stored by the subject, and presented to a verifier who can cryptographically confirm its authenticity without contacting the issuer.

## How It Works (Step-by-Step)

1. The issuer defines a credential payload containing claims about the subject, such as a degree title, issue date, and subject identifier.
2. The issuer hashes the payload and signs the hash with their private key, producing a cryptographic proof that is appended to the credential.
3. The issuer delivers the signed credential to the subject (holder), usually through a secure wallet connection or direct download.
4. The holder stores the credential in a personal vault or wallet and retains full control over when and where it is shared.
5. The holder presents the credential to a verifier, who resolves the issuer's DID to retrieve the public key from the issuer's DID document.
6. The verifier checks the cryptographic signature against the public key to confirm the credential was not altered, then queries the issuer's revocation registry to ensure the credential is still valid.

## Real-life analogy

Think of a digitally signed diploma. The university issues a PDF, signs it with its private key, and emails it to the graduate. When the graduate applies for a job, they send the PDF to the employer. The employer uses the university's public key to verify the signature, checks the date, and confirms the degree is real. The employer never needs to call the university registrar. A verifiable credential is that diploma, but standardized and machine-readable.

## Tiny numeric example

A university issues a credential to a student.

| Field | Value | Purpose |
|-------|-------|---------|
| Issuer DID | did:ethr:0xuniversityA789... | Identifies the university |
| Subject DID | did:ethr:0xstudentB123... | Identifies the student |
| Claim | degree: "BSc Computer Science", GPA: 3.85 | The actual assertions |
| Issuance date | 2024-06-15 (timestamp 1718409600) | When the credential was created |
| Expiration date | 2029-06-15 | When the credential becomes invalid |
| Signature | 0x7d3e8f2a1b4c... | Cryptographic proof from the issuer |
| Revocation status | valid (status list index 42, bit 0) | Whether the issuer has revoked it |

When the student presents this credential to an employer, the employer resolves the issuer DID, extracts the public key, and verifies the signature against the credential hash `0x2c4f...`. The signature check passes in 8 milliseconds. The employer then queries the revocation list and confirms the credential is still valid. The entire process completes without contacting the university directly.

## Common confusion

- No, a verifiable credential is not stored on the blockchain by default; the issuer's DID is on-chain, but the credential itself is usually held privately by the subject.
- No, the word "verifiable" does not mean the claim is true; it means the signature is valid and the issuer is authenticated. The verifier must still trust the issuer.
- No, selective disclosure is not automatic; the credential format must support zero-knowledge proofs or redaction for the subject to hide unnecessary fields.
- No, a verifiable credential is not permanently valid; issuers can publish revocation lists or status registries so verifiers can check if a credential is still valid.
- No, a self-issued credential is not equivalent to third-party verification; a claim signed by the subject about themselves is not independent verification.
- No, a verifiable credential is not an NFT; it is not designed for transfer or speculation, and it usually is not traded.

## Key properties

- Cryptographically signed: the issuer's private key creates a tamper-evident seal that proves the credential was issued by the claimed source.
- Offline verifiable: the verifier does not need to contact the issuer in real time; only the issuer's public key and a revocation list are required.
- Selectively disclosable: the holder can share only the necessary fields using zero-knowledge proofs or redaction.
- Revocable: issuers can invalidate credentials through status lists or registries without deleting the original data.
- Privacy-preserving: verifiers learn only the claims presented, not the holder's full identity or unrelated credentials.

## Where it appears in our code

Verifiable credentials are modeled in `src_web3/phase38/did_api.ts` where the `/issue` endpoint creates a signed credential, the `/verify` endpoint checks the cryptographic signature, and the `/present` endpoint simulates selective disclosure to a third party.
