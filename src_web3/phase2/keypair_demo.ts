import * as nacl from "tweetnacl";
// We import TweetNaCl to perform Ed25519 cryptography in pure JavaScript without native dependencies.

// PHASE 2: Keypair Demo in TypeScript
// This file demonstrates Ed25519 key generation, signing, and verification using TweetNaCl.

// Generate a new random keypair using TweetNaCl's secure random generator.
// This happens entirely in memory without any server because key generation is local cryptography.
const keypair = nacl.sign.keyPair();

// Extract the public key so it can be shared as a Solana-style address.
const publicKey = keypair.publicKey;

// Extract the secret key so we can sign messages; this must never leave the local machine.
const secretKey = keypair.secretKey;

// Define a message as UTF-8 bytes to simulate a transaction or statement.
const message = new TextEncoder().encode("Alice sends 5 SOL to Bob");

// Sign the message with the secret key to create a cryptographic proof of approval.
// The signature covers the exact bytes of the message, making it tamper-evident.
const signature = nacl.sign.detached(message, secretKey);

// Print the public key length to confirm it matches Ed25519's 32-byte standard.
console.log(`Public Key length: ${publicKey.length} bytes`);

// Print the signature length to confirm the 64-byte Ed25519 output.
console.log(`Signature length: ${signature.length} bytes`);

// Verify the signature using only the public key to demonstrate trustless authentication.
// Anyone with the public key can run this check without knowing the secret.
const isValid = nacl.sign.detached.verify(message, signature, publicKey);
console.log(`Signature valid: ${isValid}`);

// Tamper with the message to simulate an attacker changing transaction details.
const tamperedMessage = new TextEncoder().encode("Alice sends 500 SOL to Bob");

// Verify the original signature against the tampered message to test integrity enforcement.
// This MUST return false because the signature is bound to the original message bytes.
const isTamperedValid = nacl.sign.detached.verify(tamperedMessage, signature, publicKey);
console.log(`Tampered signature valid: ${isTamperedValid}`);

// Generate an attacker's keypair to demonstrate that signatures are identity-specific.
const attackerKeypair = nacl.sign.keyPair();

// Sign the original message with the attacker's secret key.
const attackerSignature = nacl.sign.detached(message, attackerKeypair.secretKey);

// Verify the attacker's signature against the original public key.
// This MUST return false because the keypair math prevents cross-verification.
const isAttackerValid = nacl.sign.detached.verify(message, attackerSignature, publicKey);
console.log(`Attacker signature valid: ${isAttackerValid}`);

// Encode the public key in base64 to show how addresses are displayed for sharing.
// We use standard base64 here because base58 requires an extra dependency.
const publicKeyBase64 = Buffer.from(publicKey).toString("base64");
console.log(`Public Key (Base64): ${publicKeyBase64}`);
