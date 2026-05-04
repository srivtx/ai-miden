use sha2::{Sha256, Digest}; // We import SHA-256 to create tamper-evident fingerprints that cryptographically link each block.
use std::time::{SystemTime, UNIX_EPOCH}; // We import time utilities to record when each block was created for chronological ordering.

// PHASE 1: Toy Blockchain in Rust
// This file implements a minimal blockchain to demonstrate hash chaining and validation.

/// A single block in the chain containing transactions and a link to the previous block.
/// We use a struct because blocks are discrete units with well-defined fields.
#[derive(Debug, Clone)]
struct Block {
    index: u64, // Index records the block's position so we can detect missing or reordered blocks.
    timestamp: u64, // Timestamp proves when the block was created and prevents replay attacks.
    transactions: Vec<String>, // Transactions hold the actual data payload that the blockchain exists to record.
    previous_hash: String, // Previous hash cryptographically links this block to its ancestor, forming the chain.
    hash: String, // Hash of this block's contents serves as a unique fingerprint for integrity verification.
}

impl Block {
    fn calculate_hash(index: u64, timestamp: u64, transactions: &[String], previous_hash: &str) -> String { // Computes SHA-256 hash of the block's fields to produce an immutable fingerprint.
        let data = format!("{}{:?}{}{}", index, timestamp, transactions.join(","), previous_hash); // We concatenate fields into a string because the hasher operates on byte streams.
        let mut hasher = Sha256::new(); // Creates a new SHA-256 hasher instance.
        hasher.update(data.as_bytes()); // Feeds the concatenated data bytes into the hasher.
        format!("{:x}", hasher.finalize()) // Converts the hash output to a lowercase hex string for readability.
    }

    fn new(index: u64, transactions: Vec<String>, previous_hash: String) -> Self { // Creates a new block linking to a previous hash so the chain remains intact.
        let timestamp = SystemTime::now() // Capture current time to establish chronological ordering of events.
            .duration_since(UNIX_EPOCH) // Calculates elapsed time since the Unix epoch.
            .expect("Time went backwards") // Panics if the system clock is somehow behind the epoch.
            .as_secs(); // Converts the duration to whole seconds.
        let hash = Self::calculate_hash(index, timestamp, &transactions, &previous_hash); // Compute hash after all other fields are known so the fingerprint covers everything.
        Self { index, timestamp, transactions, previous_hash, hash } // Returns the constructed block with all fields populated.
    }

    fn is_valid(&self) -> bool { // Validates that the stored hash matches a fresh computation, detecting any tampering.
        self.hash == Self::calculate_hash(self.index, self.timestamp, &self.transactions, &self.previous_hash) // Recomputes the hash and compares it to the stored value.
    }
}

/// The blockchain holds an ordered list of blocks and enforces validation rules.
/// We use a struct to encapsulate chain state and provide methods for manipulation.
struct Blockchain {
    chain: Vec<Block>, // The ordered vector stores blocks sequentially because chain order matters for validation.
}

impl Blockchain {
    fn new() -> Self { // Creates a new blockchain with a genesis block so there is always a valid starting point.
        let genesis = Block::new(0, vec!["Genesis".to_string()], "0".to_string()); // Creates the first block with index zero and a placeholder previous hash.
        Self { chain: vec![genesis] } // Initializes the chain with only the genesis block.
    }

    fn latest(&self) -> &Block { // Returns the latest block so new blocks can reference its hash as the previous link.
        self.chain.last().expect("Chain always has at least genesis") // Returns the last element, panicking only if the chain is empty (which should never happen).
    }

    fn add_block(&mut self, transactions: Vec<String>) { // Appends a new block after setting its previous hash to maintain cryptographic linkage.
        let prev = self.latest(); // Gets the most recent block to extract its hash.
        let new_block = Block::new(prev.index + 1, transactions, prev.hash.clone()); // Creates a new block with the next index and the previous block's hash.
        self.chain.push(new_block); // Adds the new block to the end of the chain.
    }

    fn is_valid(&self) -> bool { // Validates the entire chain by checking every block's hash and its link to the predecessor.
        for i in 1..self.chain.len() { // Iterates from the second block to the end.
            let current = &self.chain[i]; // Gets a reference to the current block.
            let previous = &self.chain[i - 1]; // Gets a reference to the previous block.
            if !current.is_valid() { // Reject the chain if any block's internal hash does not match recomputation.
                return false; // Returns false immediately on the first invalid block.
            }
            if current.previous_hash != previous.hash { // Reject the chain if the previous_hash pointer does not match the actual previous block.
                return false; // Returns false immediately on the first broken link.
            }
        }
        true // Returns true if all blocks and links are valid.
    }
}

fn main() {
    let mut blockchain = Blockchain::new(); // Initialize the blockchain so we have a working ledger.
    blockchain.add_block(vec!["Alice sends 5 SOL to Bob".to_string()]); // Add the first real block to simulate recording actual transactions.
    blockchain.add_block(vec!["Bob sends 2 SOL to Charlie".to_string()]); // Add a second block to demonstrate multiple links in the chain.

    for block in &blockchain.chain { // Print the entire chain so we can inspect hashes and linkages visually.
        println!("Block {}: {}", block.index, block.hash); // Prints the block index and its hash.
        println!("  Prev: {}", block.previous_hash); // Prints the previous hash to show the chain link.
        println!("  Tx: {:?}", block.transactions); // Prints the transactions contained in this block.
    }

    println!("\nChain valid: {}", blockchain.is_valid()); // Verify chain integrity to prove the cryptographic links hold.

    if let Some(block) = blockchain.chain.get_mut(1) { // Simulate tampering by mutating a transaction to show immutability in action.
        block.transactions[0] = "Alice sends 500 SOL to Bob".to_string(); // Changes a transaction amount to simulate an attack.
    }

    println!("Chain valid after tampering: {}", blockchain.is_valid()); // Re-validate after tampering to demonstrate that the chain detects corruption.
}
