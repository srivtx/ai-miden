import { createHash } from "crypto"; // We import createHash to compute SHA-256 fingerprints that link blocks together cryptographically.

// PHASE 1: Toy Blockchain in TypeScript
// This file implements the same hash-linked chain using Node.js crypto primitives.

/// Represents a single block with cryptographic linkage to its predecessor.
/// We use a class because each block encapsulates its own validation logic.
class Block {
    index: number; // Numeric position in the chain so we can detect gaps or reordering.
    timestamp: number; // Unix timestamp proving when the block was constructed.
    transactions: string[]; // Array of transaction strings carrying the ledger's actual payload.
    previousHash: string; // Hash of the previous block that forms the cryptographic chain link.
    hash: string; // Hash of this block's content serving as an integrity fingerprint.

    constructor(index: number, transactions: string[], previousHash: string) { // Builds a block and computes its hash so the fingerprint covers all fields.
        this.index = index; // Stores the block index.
        this.timestamp = Math.floor(Date.now() / 1000); // Captures current Unix time in seconds.
        this.transactions = transactions; // Stores the array of transaction strings.
        this.previousHash = previousHash; // Stores the previous block's hash.
        this.hash = this.calculateHash(); // Hash must be computed last because it depends on all other fields.
    }

    calculateHash(): string { // Computes SHA-256 over concatenated fields to create a tamper-evident fingerprint.
        const data = `${this.index}${this.timestamp}${this.transactions.join(",")}${this.previousHash}`; // Concatenates all fields into a single string.
        return createHash("sha256").update(data).digest("hex"); // Returns the hex-encoded SHA-256 digest.
    }

    isValid(): boolean { // Recomputes the hash to verify that no field has been altered since creation.
        return this.hash === this.calculateHash(); // Compares stored hash to a fresh computation.
    }
}

/// Manages an ordered list of blocks and enforces chain-wide validation.
/// We use a class to encapsulate chain state and provide safe mutation methods.
class Blockchain {
    chain: Block[]; // Stores blocks in an array because order is critical for hash linkage.

    constructor() { // Initializes the chain with a genesis block so validation always has a root.
        this.chain = [new Block(0, ["Genesis"], "0")]; // Creates the first block with index zero and a placeholder previous hash.
    }

    latest(): Block { // Returns the most recent block so new blocks can link to it.
        return this.chain[this.chain.length - 1]; // Returns the last element of the array.
    }

    addBlock(transactions: string[]): void { // Creates and appends a new block, preserving the cryptographic link to history.
        const prev = this.latest(); // Gets the most recent block to extract its hash.
        const newBlock = new Block(prev.index + 1, transactions, prev.hash); // Creates a new block with the next index and the previous block's hash.
        this.chain.push(newBlock); // Adds the new block to the end of the chain.
    }

    isValid(): boolean { // Validates every block's internal hash and its pointer to the previous block.
        for (let i = 1; i < this.chain.length; i++) { // Iterates from the second block to the end.
            const current = this.chain[i]; // Gets the current block.
            const previous = this.chain[i - 1]; // Gets the previous block.
            if (!current.isValid()) { // If any block's stored hash mismatches recomputation, the chain is corrupted.
                return false; // Returns false immediately on the first invalid block.
            }
            if (current.previousHash !== previous.hash) { // If the previous hash pointer breaks, the chain link is severed.
                return false; // Returns false immediately on the first broken link.
            }
        }
        return true; // Returns true if all blocks and links are valid.
    }
}

const blockchain = new Blockchain(); // Create a new blockchain instance to begin the simulation.
blockchain.addBlock(["Alice sends 5 SOL to Bob"]); // Add a block with a real transaction to simulate ledger activity.
blockchain.addBlock(["Bob sends 2 SOL to Charlie"]); // Add another block to create a longer chain for richer validation.

for (const block of blockchain.chain) { // Iterate and print every block so hashes and linkages are visible.
    console.log(`Block ${block.index}: ${block.hash}`); // Prints the block index and its hash.
    console.log(`  Prev: ${block.previousHash}`); // Prints the previous hash to show the chain link.
    console.log(`  Tx: ${block.transactions}`); // Prints the transactions contained in this block.
}

console.log(`\nChain valid: ${blockchain.isValid()}`); // Validate the chain before tampering to establish a baseline of truth.

blockchain.chain[1].transactions[0] = "Alice sends 500 SOL to Bob"; // Tamper with a transaction to simulate an attack on ledger integrity.

console.log(`Chain valid after tampering: ${blockchain.isValid()}`); // Re-validate to prove that the chain detects and rejects tampered data.
