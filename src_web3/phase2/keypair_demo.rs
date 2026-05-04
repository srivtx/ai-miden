use ed25519_dalek::{Keypair, PublicKey, SecretKey, Signature, Signer, Verifier};
// We import ed25519-dalek types to perform high-security elliptic curve signing and verification.
use rand::rngs::OsRng;
// We import OsRng to access the operating system's cryptographically secure random number generator.

// PHASE 2: Keypair Demo in Rust
// This file demonstrates Ed25519 key generation, signing, and verification.

fn main() {
    // Initialize a cryptographically secure random number generator from the OS.
    // We use OsRng because hardware-derived entropy is safer than software pseudo-randomness for key generation.
    let mut csprng = OsRng;

    // Generate a new Ed25519 keypair containing a secret key and its corresponding public key.
    // The keypair is generated locally with no network interaction because cryptography happens entirely offline.
    let keypair: Keypair = Keypair::generate(&mut csprng);

    // Extract the public key so we can share it with others as our receiving address.
    let public_key: PublicKey = keypair.public;

    // Define a message to sign so we can prove authorship of a specific statement.
    let message: &[u8] = b"Alice sends 5 SOL to Bob";

    // Sign the message using the secret key to produce a cryptographic proof of approval.
    // The signature binds to both the message and the keypair; it cannot be reused elsewhere.
    let signature: Signature = keypair.sign(message);

    // Print the public key in hex so we can see the 32-byte identifier that others will use to verify.
    println!("Public Key: {:x?}", public_key.as_bytes());

    // Print the signature length to confirm it matches the Ed25519 standard of 64 bytes.
    println!("Signature length: {} bytes", signature.to_bytes().len());

    // Verify the signature against the public key to prove the message came from the matching secret key.
    // Verification is performed by anyone with only the public key, demonstrating trustless authentication.
    match public_key.verify(message, &signature) {
        Ok(()) => println!("Signature is VALID"),
        Err(e) => println!("Signature is INVALID: {}", e),
    }

    // Tamper with the message to simulate an attacker altering transaction details.
    let tampered_message: &[u8] = b"Alice sends 500 SOL to Bob";

    // Attempt to verify the original signature against the tampered message.
    // This MUST fail because the signature is cryptographically bound to the exact original bytes.
    match public_key.verify(tampered_message, &signature) {
        Ok(()) => println!("Tampered message verified (BUG!)"),
        Err(_) => println!("Tampered message correctly REJECTED"),
    }

    // Create a second keypair to demonstrate that signatures are signer-specific.
    let attacker_keypair: Keypair = Keypair::generate(&mut csprng);
    let attacker_signature: Signature = attacker_keypair.sign(message);

    // Verify the attacker's signature against the original public key.
    // This MUST fail because only the matching public key can verify a signature.
    match public_key.verify(message, &attacker_signature) {
        Ok(()) => println!("Attacker verified (BUG!)"),
        Err(_) => println!("Attacker signature correctly REJECTED"),
    }
}
